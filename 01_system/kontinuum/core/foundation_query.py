# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone

from .conversation import normalize


class FoundationQueryLayer:
    """Answers foundation questions exclusively from protected local records."""

    VERSION = "1.0"
    QUERY_MARKERS = {
        "user_identity": (
            "wer bin ich", "weisst du wer ich bin", "weißt du wer ich bin",
            "kennst du mich", "bin ich raphael",
        ),
        "system_identity": ("wer bist du", "was bist du", "wie heisst du", "wie heißt du"),
        "creator": (
            "wer ist mein schopfer", "wer ist mein schoepfer", "wer ist dein schopfer",
            "wer ist dein schoepfer", "wer hat dich erschaffen",
        ),
        "principles": (
            "welche prinzipien gelten", "welche grundprinzipien gelten", "nenne deine prinzipien",
            "was sind deine prinzipien", "fundamentale prinzipien",
        ),
        "moral_reason": (
            "warum ist diese entscheidung moralisch zulassig",
            "warum ist diese entscheidung moralisch zulässig",
            "warum wurde diese entscheidung moralisch erlaubt",
            "warum wurde diese entscheidung blockiert",
            "warum ist diese entscheidung blockiert",
            "warum ist diese handlung falsch",
            "warum ist diese handlung richtig",
            "warum ist diese handlung moralisch falsch",
        ),
        "used_rule": (
            "welche fundamentregel wurde verwendet", "welche fundamentregel galt",
            "welche moralregel wurde verwendet", "welche regel wurde verwendet",
        ),
        "status": ("foundationquerystatus", "foundation query status"),
    }

    def __init__(self, storage, foundation_memory, session_context, identity: dict, foundation_reasoning=None):
        self.storage = storage
        self.foundation_memory = foundation_memory
        self.session_context = session_context
        self.identity = identity
        self.foundation_reasoning = foundation_reasoning

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalized(text: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9äöüß]+", " ", normalize(text)).split())

    def query_type(self, text: str) -> str:
        value = self._normalized(text)
        for query_type, markers in self.QUERY_MARKERS.items():
            if any(self._normalized(marker) in value for marker in markers):
                return query_type
        return ""

    def can_answer(self, text: str) -> bool:
        return bool(self.query_type(text))

    def answer(self, text: str, current_decision_id: int | None = None) -> dict | None:
        query_type = self.query_type(text)
        if not query_type:
            return None
        records = self._foundation_records()
        registry = self._registry_status()
        if query_type == "user_identity":
            answer, classes, keys = self._answer_user_identity(records)
        elif query_type == "system_identity":
            answer, classes, keys = self._answer_system_identity(records)
        elif query_type == "creator":
            answer, classes, keys = self._answer_creator(records)
        elif query_type == "principles":
            answer, classes, keys = self._answer_principles(records)
        elif query_type in {"moral_reason", "used_rule"}:
            answer, classes, keys = self._answer_decision(records, current_decision_id, query_type)
        else:
            answer, classes, keys = self._answer_status(records, registry)
        source_line = (
            "Foundation-Quelle: foundation_memory + foundation_knowledge; "
            f"Klasse(n): {', '.join(sorted(classes)) or 'foundation'}; "
            f"Registry: {registry['valid']}/{registry['total']} geschützt."
        )
        answer = f"{answer}\n{source_line}\nNormale Wissensabfrage und Internetsuche: nicht verwendet."
        metadata = {
            "query_type": query_type,
            "foundation_keys": keys,
            "knowledge_classes": sorted(classes),
            "source_tables": ["foundation_memory", "foundation_knowledge"],
            "normal_knowledge_used": False,
            "internet_used": False,
            "current_decision_id": current_decision_id,
            "answered_at": self._now(),
        }
        query_id = self.storage.add("audit_events", "foundation.query", text, metadata)
        return {"answer": answer, "query_type": query_type, "query_id": query_id, **metadata}

    def _answer_user_identity(self, records: list[dict]) -> tuple[str, set[str], list[str]]:
        user = self.session_context.current()
        creator = self._first(records, "foundation.creator")
        name = user.get("display_name") or self.identity.get("creator", "Raphael Schatz")
        role = user.get("role") or "USER"
        if user.get("is_creator") and creator:
            relationship = "Du bist der Schöpfer von Projekt Kontinuum."
            keys = [creator["key"]]
            classes = {"foundation.creator"}
        else:
            relationship = "Du bist als Benutzer dieser Sitzung angemeldet; deine persönliche Identität ist kein erfundenes Fundamentwissen."
            keys = []
            classes = {"foundation.identity"}
        return (
            f"Du bist {name}.\n{relationship}\nRolle: {role}.\n"
            "Diese lokale Antwort verbindet den authentifizierten Session Context mit dem geschützten Foundation Layer. "
            "Dafür wurde keine Internet-, arXiv-, Brave- oder DuckDuckGo-Suche gestartet.",
            classes,
            keys,
        )

    def _answer_system_identity(self, records: list[dict]) -> tuple[str, set[str], list[str]]:
        identity_records = self._by_class(records, "foundation.identity")
        creator = self._first(records, "foundation.creator")
        values = [row["value"] for row in identity_records[:2]]
        if creator:
            values.append(creator["value"])
        return (
            "Ich bin Kontinuum. " + " ".join(values),
            {"foundation.identity", "foundation.creator"},
            [row["key"] for row in identity_records[:2]] + ([creator["key"]] if creator else []),
        )

    def _answer_creator(self, records: list[dict]) -> tuple[str, set[str], list[str]]:
        creator = self._first(records, "foundation.creator")
        value = creator["value"] if creator else f"{self.identity.get('creator', 'Raphael Schatz')} ist der Schöpfer von Kontinuum."
        return (
            f"Mein Schöpfer gemäß geschütztem Foundation Memory ist {self.identity.get('creator', 'Raphael Schatz')}. {value}",
            {"foundation.creator"},
            [creator["key"]] if creator else ["creator.relationship"],
        )

    def _answer_principles(self, records: list[dict]) -> tuple[str, set[str], list[str]]:
        guiding = sorted(
            (row for row in records if row["key"].startswith("guiding.")),
            key=lambda row: row["key"],
        )
        if guiding:
            lines = ["Verbindliche Leitprinzipien (vorläufig und bis auf Widerruf):"]
            lines.extend(
                f"{index}. [{row['rule_id']}] {self._display_value(row['value'])}"
                for index, row in enumerate(guiding, 1)
            )
            return (
                "\n".join(lines),
                {row["knowledge_class"] for row in guiding},
                [row["key"] for row in guiding],
            )
        identity = self._by_class(records, "foundation.identity")
        principles = self._by_class(records, "foundation.principle")
        moral = self._by_class(records, "foundation.moral")
        lines = ["Verbindliche Fundamentprinzipien:"]
        lines.extend(f"- [{row['key']}] {self._display_value(row['value'])}" for row in identity)
        lines.extend(f"- [{row['key']}] {self._display_value(row['value'])}" for row in principles)
        lines.extend(f"- [{row['key']}] {self._display_value(row['value'])}" for row in moral)
        keys = [row["key"] for row in (*identity, *principles, *moral)]
        return "\n".join(lines), {"foundation.identity", "foundation.principle", "foundation.moral"}, keys

    def _answer_decision(
        self, records: list[dict], current_decision_id: int | None, query_type: str
    ) -> tuple[str, set[str], list[str]]:
        decision = self._previous_decision(current_decision_id)
        if not decision:
            return (
                "Es ist noch keine vorherige auditierte Foundation-Entscheidung vorhanden, auf die sich „diese Entscheidung“ beziehen kann.",
                {"foundation.moral"},
                [],
            )
        moral = decision["metadata"].get("moral", {})
        trace = self.foundation_reasoning.decision_trace(decision["id"]) if self.foundation_reasoning else None
        verdict = (trace or {}).get("decision", moral.get("decision", decision["metadata"].get("decision", "unbekannt")))
        reason = (trace or {}).get("reason", moral.get("reason", decision["metadata"].get("reason", "Keine Begründung gespeichert.")))
        if trace:
            rule_lines = "\n".join(
                f"- [{row['rule_id']}] Einfluss: {row['influence']} | {row['text']}"
                for row in trace.get("rules", [])
            )
            rule_keys = [row["foundation_key"] for row in trace.get("rules", [])]
            path = f"\nFoundation-Pfad: {' → '.join(trace.get('foundation_path', []))}"
            proof = f"\nOriginalnachweis: Reasoning-Datensatz {trace.get('record_id')} vom Entscheidungsbeginn."
        else:
            return (
                f"Für die Entscheidung [{decision['id']}] liegt kein gespeicherter Foundation-Reasoning-Nachweis vor. "
                "Eine nachträgliche Regelrekonstruktion ist gesperrt; daher wird keine kausale Begründung behauptet.",
                {"foundation.moral"},
                [],
            )
        if query_type == "used_rule":
            heading = f"Für die Entscheidung [{decision['id']}] wurden diese Fundamentregeln herangezogen:"
        else:
            heading = (
                f"Die Entscheidung [{decision['id']}] zur Handlung „{decision['action']}“ wurde als „{verdict}“ bewertet.\n"
                f"Begründung: {reason}\nVerwendete moralische Fundamentregeln:"
            )
        return f"{heading}\n{rule_lines}{path}{proof}", {"foundation.moral"}, rule_keys

    def _answer_status(self, records: list[dict], registry: dict) -> tuple[str, set[str], list[str]]:
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT metadata FROM audit_events WHERE kind = 'foundation.query'"
            ).fetchall()
        counts = Counter(self._metadata(row["metadata"]).get("query_type", "unknown") for row in rows)
        status = self.foundation_memory.verify()
        return (
            f"Foundation Query Layer {self.VERSION}: aktiv. "
            f"Foundation Memory: {status['verified_records']}/{status['protected_records']} verifiziert. "
            f"Abfragen: {sum(counts.values())}; Typen: {dict(counts)}.",
            set(status["classes"]),
            [],
        )

    def _foundation_records(self) -> list[dict]:
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM foundation_memory WHERE kind = 'foundation.memory' ORDER BY id"
            ).fetchall()
        latest_by_key = {}
        for row in rows:
            metadata = self._metadata(row["metadata"])
            key = metadata.get("key", row["content"])
            latest_by_key[key] = {
                "id": int(row["id"]),
                "key": key,
                "value": metadata.get("value", ""),
                "knowledge_class": metadata.get("knowledge_class", ""),
                "rule_id": metadata.get("rule_id", ""),
                "integrity_hash": metadata.get("integrity_hash", ""),
            }
        return list(latest_by_key.values())

    def _registry_status(self) -> dict:
        with self.storage.connect() as database:
            rows = database.execute(
                """SELECT id, content, metadata FROM foundation_knowledge
                   WHERE kind = 'foundation.knowledge' ORDER BY id"""
            ).fetchall()
        latest_by_key = {}
        for row in rows:
            metadata = self._metadata(row["metadata"])
            latest_by_key[metadata.get("key", row["content"])] = metadata
        valid = sum(
            bool(metadata.get("protected") and metadata.get("integrity_hash"))
            for metadata in latest_by_key.values()
        )
        return {"valid": valid, "total": len(latest_by_key)}

    def _previous_decision(self, current_decision_id: int | None) -> dict | None:
        with self.storage.connect() as database:
            if current_decision_id:
                rows = database.execute(
                    """SELECT id, content, metadata FROM foundation_decisions
                       WHERE kind = 'foundation.decision' AND id < ? ORDER BY id DESC LIMIT 50""",
                    (current_decision_id,),
                ).fetchall()
            else:
                rows = database.execute(
                    """SELECT id, content, metadata FROM foundation_decisions
                       WHERE kind = 'foundation.decision' ORDER BY id DESC LIMIT 50"""
                ).fetchall()
        row = next((candidate for candidate in rows if not self.can_answer(candidate["content"])), None)
        if not row:
            return None
        return {"id": int(row["id"]), "action": row["content"], "metadata": self._metadata(row["metadata"])}

    @staticmethod
    def _rules_for_verdict(records: list[dict], verdict: str) -> list[dict]:
        moral = [row for row in records if row["knowledge_class"] == "foundation.moral"]
        preferred = {
            "block": {"moral.rule.1", "moral.rule.4"},
            "review": {"moral.rule.3", "moral.rule.4"},
            "allow": {"moral.rule.2", "moral.rule.3"},
        }.get(verdict, {"moral.rule.2", "moral.rule.3"})
        selected = [row for row in moral if row["key"] in preferred]
        return selected or moral[:2]

    @staticmethod
    def _by_class(records: list[dict], knowledge_class: str) -> list[dict]:
        return [row for row in records if row["knowledge_class"] == knowledge_class]

    @classmethod
    def _first(cls, records: list[dict], knowledge_class: str) -> dict | None:
        rows = cls._by_class(records, knowledge_class)
        return rows[0] if rows else None

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}

    @staticmethod
    def _display_value(value: str) -> str:
        return str(value).replace("Erkennen - Schaffen - Vollenden", "Erkennen – Schaffen – Vollenden")

    def status(self) -> dict:
        memory = self.foundation_memory.verify()
        with self.storage.connect() as database:
            query_count = int(database.execute(
                "SELECT COUNT(*) FROM audit_events WHERE kind = 'foundation.query'"
            ).fetchone()[0])
        return {
            "version": self.VERSION,
            "active": True,
            "foundation_memory_ok": memory["ok"],
            "protected_records": memory["protected_records"],
            "queries": query_count,
            "normal_knowledge_fallback": False,
        }
