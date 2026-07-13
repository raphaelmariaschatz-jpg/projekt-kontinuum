# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from .conversation import normalize


class KnowledgeIntelligence:
    """Evidence-based trust, conflict detection, and knowledge self-model."""

    ORIGIN_BASE = {"research": 0.62, "notebook": 0.58, "memory": 0.52, "learning": 0.48, "dialogue": 0.42}
    STOPWORDS = {
        "aber", "alle", "auch", "aus", "das", "dass", "dem", "den", "der", "die", "ein", "eine",
        "einer", "eines", "für", "fuer", "hat", "ist", "mit", "nicht", "oder", "sich", "sind", "und",
        "von", "wird", "wissen", "kontinuum", "quelle", "projekt", "version",
    }
    HYPOTHESIS_MARKERS = (
        "vielleicht", "vermutlich", "wahrscheinlich", "möglicherweise", "moeglicherweise",
        "ich vermute", "hypothese", "könnte", "koennte", "scheint",
    )

    def __init__(self, storage, foundation_guard=None):
        self.storage = storage
        self.foundation_guard = foundation_guard

    def bind_foundation_guard(self, foundation_guard) -> None:
        self.foundation_guard = foundation_guard

    def refresh(self) -> dict:
        rows = self._knowledge_rows()
        claims = self._claim_groups(rows)
        updated = 0
        for row in rows:
            metadata = dict(row["metadata"])
            claim = self._claim(row["content"])
            conflicts = self._conflicts_for(row, claim, claims)
            source_keys = self._independent_sources(metadata)
            source_quality = self._source_quality(metadata)
            confirmations = self._confirmations_for(row, claim, claims)
            base = self.ORIGIN_BASE.get(metadata.get("origin", ""), 0.4)
            score = min(0.98, base + min(0.3, 0.1 * source_quality["weight_sum"]) + min(0.18, 0.04 * confirmations))
            score = max(0.05, score - min(0.55, 0.18 * len(conflicts)))
            metadata["trust"] = {
                "score": round(score, 2),
                "level": self._level(score),
                "confirming_sources": len(source_keys),
                "source_quality_weight": round(source_quality["weight_sum"], 2),
                "source_classes": source_quality["classes"],
                "confirming_knowledge": confirmations,
                "contradictions": len(conflicts),
                "contradicting_knowledge_ids": conflicts,
                "last_confirmation": self._last_confirmation(row, claim, claims),
                "reason": self._reason(
                    metadata.get("origin", ""), len(source_keys), source_quality["weight_sum"], confirmations, len(conflicts)
                ),
            }
            metadata["epistemic"] = self._epistemic_state(row["content"], metadata["trust"])
            self._update_metadata(row["id"], metadata)
            self._ensure_review_task(row["id"], row["content"], metadata["epistemic"])
            updated += 1
        sanitized = self.sanitize_review_tasks()
        detected_conflicts = self.conflicts()
        return {
            "updated": updated,
            "sanitized_review_tasks": sanitized,
            "conflicts": len(detected_conflicts),
            "states": dict(Counter(row["metadata"].get("epistemic", {}).get("state", "unbewertet") for row in self._knowledge_rows())),
        }

    def sanitize_review_tasks(self) -> int:
        changed = 0
        now = datetime.now(timezone.utc).isoformat()
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM learning_tasks WHERE kind = 'epistemic.review' ORDER BY id"
            ).fetchall()
            for row in rows:
                metadata = self._metadata(row["metadata"])
                content = row["content"]
                reason = ""
                state = ""
                if self._is_foundation_knowledge(content):
                    state = "foundation_knowledge"
                    reason = "Geschütztes Fundamentwissen wird nicht als offene Wissenslücke behandelt."
                elif metadata.get("classification") == "report" or self._is_report_output(content):
                    state = "report_output"
                    reason = "Status-, Bericht-, Lernprojekt- und Erklärungsausgaben werden nicht als Weltwissen geprüft."
                if not state:
                    continue
                if metadata.get("active") is False and metadata.get("terminal_outcome") == "skipped_protected_or_report":
                    continue
                metadata.update({
                    "active": False,
                    "terminal": True,
                    "terminal_outcome": "skipped_protected_or_report",
                    "state": state,
                    "classification": "report" if state == "report_output" else metadata.get("classification", ""),
                    "reason": reason,
                    "updated_at": now,
                })
                database.execute(
                    "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                    (json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
                changed += 1
            database.commit()
        return changed

    def epistemic_items(self, state: str | None = None) -> list[dict]:
        rows = self._knowledge_rows()
        result = []
        for row in rows:
            epistemic = row["metadata"].get("epistemic", {})
            if state and epistemic.get("state") != state:
                continue
            result.append({
                "id": row["id"],
                "content": row["content"],
                "state": epistemic.get("state", "unbewertet"),
                "reason": epistemic.get("reason", ""),
                "priority": epistemic.get("review_priority", "none"),
                "should_review": epistemic.get("should_review", False),
                "trust": row["metadata"].get("trust", {}),
            })
        return result

    def format_epistemic(self, focus: str) -> str:
        mapping = {
            "hypotheses": ("hypothesis", "Hypothesen"),
            "uncertain": ("uncertain", "Unsichere Aussagen"),
            "review": (None, "Zu überprüfende Informationen"),
        }
        state, title = mapping[focus]
        rows = self.epistemic_items(state)
        if focus == "review":
            rows = [row for row in rows if row["should_review"]]
            rows.sort(key=lambda row: (self._priority_rank(row["priority"]), -row["trust"].get("score", 0)), reverse=True)
        if not rows:
            return f"{title}: keine Einträge."
        lines = [f"{title} ({len(rows)}):"]
        for row in rows[:30]:
            lines.append(f"- [{row['id']}] {row['content']} | Priorität {row['priority']} | {row['reason']}")
        return "\n".join(lines)

    def knowledge_gaps(self) -> list[dict]:
        self.sanitize_review_tasks()
        gaps = []
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM learning_tasks WHERE kind = 'epistemic.review' ORDER BY id"
            ).fetchall()
            learning_rows = database.execute(
                "SELECT id, content, metadata FROM learning_tasks WHERE kind = 'continuous.task' ORDER BY id"
            ).fetchall()
        for row in rows:
            metadata = self._metadata(row["metadata"])
            if metadata.get("knowledge_class") == "foundation_knowledge" or metadata.get("protected_foundation"):
                continue
            if self._is_foundation_knowledge(row["content"]):
                continue
            if metadata.get("classification") == "report" or self._is_report_output(row["content"]):
                continue
            if metadata.get("active", True):
                gaps.append({
                    "id": int(row["id"]),
                    "subject": row["content"],
                    "priority": metadata.get("priority", "medium"),
                    "reason": metadata.get("reason", ""),
                    "knowledge_id": metadata.get("knowledge_id"),
                })
        for row in learning_rows:
            metadata = self._metadata(row["metadata"])
            if self._is_foundation_knowledge(row["content"]):
                continue
            for gap in metadata.get("meta_learning", {}).get("open_gaps", []):
                if self._is_foundation_knowledge(str(gap)):
                    continue
                gaps.append({
                    "id": int(row["id"]),
                    "subject": f"{row['content']}: {gap}",
                    "priority": "medium",
                    "reason": "Offene Lücke aus dem Meta-Lernsystem.",
                    "knowledge_id": None,
                })
        gaps.sort(key=lambda item: (self._priority_rank(item["priority"]), item["subject"]), reverse=True)
        return gaps

    def format_gaps(self) -> str:
        gaps = self.knowledge_gaps()
        if not gaps:
            return "Wissenslücken: keine ausdrücklich erkannten offenen Prüf- oder Lernlücken."
        lines = [f"Wissenslücken und Prüfaufträge ({len(gaps)}):"]
        for gap in gaps[:30]:
            lines.append(f"- {gap['subject']} | Priorität {gap['priority']} | {gap['reason']}")
        return "\n".join(lines)

    def explain_uncertainty(self, term: str) -> str:
        needle = self._normalize(term)
        rows = [row for row in self.epistemic_items() if needle in self._normalize(row["content"])]
        if not rows:
            return f"Für „{term}“ wurde keine integrierte Aussage gefunden."
        lines = [f"Unsicherheitsbegründung für „{term}“:"]
        for row in rows[:10]:
            trust = row["trust"]
            lines.append(
                f"- [{row['id']}] Zustand {row['state']}, Vertrauen {trust.get('score', 0):.2f}: "
                f"{row['reason']} Bewertungsgrund: {trust.get('reason', '')}"
            )
        return "\n".join(lines)

    def conflicts(self) -> list[dict]:
        groups = self._claim_groups(self._knowledge_rows())
        result = []
        for subject, group in groups.items():
            if len(group["values"]) <= 1 or not self._group_has_conflict(group):
                continue
            result.append({
                "subject": subject,
                "values": [
                    {"value": value, "knowledge_ids": [row["id"] for row in rows]}
                    for value, rows in group["values"].items()
                ],
            })
        return result

    def format_conflicts(self) -> str:
        conflicts = self.conflicts()
        if not conflicts:
            return "Wissenskonfliktprüfung: keine explizit vergleichbaren widersprüchlichen Angaben gefunden."
        lines = [f"Wissenskonfliktprüfung: {len(conflicts)} widersprüchliche Themen."]
        for conflict in conflicts[:20]:
            values = "; ".join(
                f"{item['value']} (Wissen {', '.join(str(value) for value in item['knowledge_ids'])})"
                for item in conflict["values"]
            )
            lines.append(f"- {conflict['subject'].capitalize()}: {values}")
        return "\n".join(lines)

    def self_model(self, days: int = 30) -> dict:
        now = datetime.now(timezone.utc)
        recent_start = now - timedelta(days=max(1, days))
        prior_start = recent_start - timedelta(days=max(1, days))
        rows = self._knowledge_rows()
        recent = [row for row in rows if self._date(row) >= recent_start]
        prior = [row for row in rows if prior_start <= self._date(row) < recent_start]
        recent_topics = self._topics(recent)
        prior_topics = self._topics(prior)
        growth = []
        for topic, count in recent_topics.items():
            previous = prior_topics.get(topic, 0)
            growth.append({"topic": topic, "recent": count, "previous": previous, "growth": count - previous})
        growth.sort(key=lambda item: (item["growth"], item["recent"], item["topic"]), reverse=True)
        origins = Counter(row["metadata"].get("origin", "legacy") for row in recent)
        return {
            "period_days": days,
            "learned": len(recent),
            "origins": dict(origins),
            "top_topics": [{"topic": topic, "count": count} for topic, count in recent_topics.most_common(10)],
            "growth": growth[:10],
            "conflicts": len(self.conflicts()),
            "average_trust": round(
                sum(row["metadata"].get("trust", {}).get("score", 0) for row in recent) / len(recent), 2
            ) if recent else 0,
            "epistemic_states": dict(Counter(row["metadata"].get("epistemic", {}).get("state", "unbewertet") for row in recent)),
            "knowledge_gaps": len(self.knowledge_gaps()),
        }

    def format_self_model(self, focus: str = "overview") -> str:
        model = self.self_model()
        topics = ", ".join(f"{item['topic']} ({item['count']})" for item in model["top_topics"][:8]) or "noch keine"
        growth = ", ".join(
            f"{item['topic']} (+{item['growth']})" for item in model["growth"][:8] if item["growth"] > 0
        ) or "noch keine belastbare Wachstumsentwicklung"
        if focus == "learned":
            return f"In den letzten {model['period_days']} Tagen habe ich {model['learned']} Wissenseinheiten integriert. Ursprünge: {model['origins']}."
        if focus == "topics":
            return f"Meine derzeit besonders behandelten Themen: {topics}."
        if focus == "growth":
            return f"Am stärksten wachsende Wissensgebiete: {growth}."
        return (
            f"Selbstmodell 1.0: In den letzten {model['period_days']} Tagen wurden {model['learned']} Wissenseinheiten "
            f"integriert. Häufige Themen: {topics}. Wachstum: {growth}. "
            f"Offene Wissenskonflikte: {model['conflicts']}. Durchschnittliches Vertrauen: {model['average_trust']:.2f}."
            f" Epistemische Zustände: {model['epistemic_states']}. Wissenslücken: {model['knowledge_gaps']}."
        )

    def _epistemic_state(self, content: str, trust: dict) -> dict:
        lower = content.casefold()
        if self._is_foundation_knowledge(content):
            return {
                "state": "foundation_knowledge",
                "reason": "Geschütztes Fundamentwissen wird nicht als offene Wissenslücke behandelt.",
                "should_review": False,
                "review_priority": "none",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }
        if self._is_report_output(content):
            return {
                "state": "report_output",
                "reason": "Status-, Bericht- und Erklärungsausgaben werden nicht als Weltwissen geprüft.",
                "should_review": False,
                "review_priority": "none",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }
        hypothesis = any(marker in lower for marker in self.HYPOTHESIS_MARKERS)
        conflicts = int(trust.get("contradictions", 0))
        score = float(trust.get("score", 0))
        sources = int(trust.get("confirming_sources", 0))
        confirmations = int(trust.get("confirming_knowledge", 0))
        if conflicts:
            state, priority, reason = "review_required", "high", f"{conflicts} widersprechende Aussagen erkannt."
        elif hypothesis:
            state, priority, reason = "hypothesis", "medium", "Aussage enthält sprachliche Vermutungsmarker."
        elif score < 0.55 or (sources == 0 and confirmations == 0):
            state, priority, reason = "uncertain", "medium", "Aussage ist schwach belegt oder besitzt keine unabhängige Bestätigung."
        else:
            state, priority, reason = "knowledge", "none", "Aussage ist ausreichend belegt und konfliktfrei."
        return {
            "state": state,
            "reason": reason,
            "should_review": state != "knowledge",
            "review_priority": priority,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _ensure_review_task(self, knowledge_id: int, content: str, epistemic: dict) -> None:
        if epistemic.get("state") in {"foundation_knowledge", "report_output"}:
            self._deactivate_review_task(knowledge_id, epistemic.get("reason", "Geschützter oder nicht integrierbarer Wissenszustand."))
            return
        subject = f"Wissen {knowledge_id} überprüfen: {content[:180]}"
        with self.storage.connect() as database:
            row = database.execute(
                "SELECT id, metadata FROM learning_tasks WHERE kind = 'epistemic.review' AND json_extract(metadata, '$.knowledge_id') = ? LIMIT 1",
                (knowledge_id,),
            ).fetchone()
            metadata = {
                "knowledge_id": knowledge_id,
                "state": epistemic["state"],
                "priority": epistemic["review_priority"],
                "reason": epistemic["reason"],
                "active": bool(epistemic["should_review"]),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if row:
                previous = self._metadata(row["metadata"])
                for key in (
                    "action_attempts",
                    "last_action_at",
                    "last_action_outcome",
                    "last_source_ids",
                    "resolved_at",
                    "terminal",
                    "terminal_outcome",
                ):
                    if key in previous:
                        metadata[key] = previous[key]
                if previous.get("terminal"):
                    metadata["active"] = False
                database.execute(
                    "UPDATE learning_tasks SET content = ?, metadata = ? WHERE id = ?",
                    (subject, json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
            elif epistemic["should_review"]:
                database.execute(
                    "INSERT INTO learning_tasks(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    ("epistemic.review", subject, json.dumps(metadata, ensure_ascii=False), datetime.now(timezone.utc).isoformat()),
                )
            database.commit()

    def _deactivate_review_task(self, knowledge_id: int, reason: str) -> None:
        with self.storage.connect() as database:
            row = database.execute(
                "SELECT id, metadata FROM learning_tasks WHERE kind = 'epistemic.review' AND json_extract(metadata, '$.knowledge_id') = ? LIMIT 1",
                (knowledge_id,),
            ).fetchone()
            if not row:
                return
            metadata = self._metadata(row["metadata"])
            metadata.update({
                "active": False,
                "terminal": True,
                "terminal_outcome": "skipped_protected_or_report",
                "reason": reason,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            database.execute(
                "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), row["id"]),
            )
            database.commit()

    def _knowledge_rows(self) -> list[dict]:
        with self.storage.connect() as database:
            rows = database.execute(
                """SELECT id, content, metadata, created_at FROM knowledge_items
                   WHERE kind = 'knowledge.integrated'
                     AND COALESCE(json_extract(metadata, '$.excluded_from_domain_knowledge'), 0) != 1
                   ORDER BY id"""
            ).fetchall()
        return [
            {"id": int(row["id"]), "content": row["content"], "metadata": self._metadata(row["metadata"]), "created_at": row["created_at"]}
            for row in rows
        ]

    def _is_foundation_knowledge(self, content: str) -> bool:
        if self.foundation_guard:
            return self.foundation_guard.is_foundation(content)
        value = normalize(content)
        markers = (
            "raphael schatz",
            "schopfer",
            "schoepfer",
            "erkennen",
            "schaffen",
            "vollenden",
            "der weg ist das ziel",
            "kontinuitat ist wichtiger als hardware",
            "kontinuitaet ist wichtiger als hardware",
            "moralisches fundament",
            "kernidentitaet",
            "leitprinzip",
        )
        return any(marker in value for marker in markers)

    @staticmethod
    def _is_report_output(content: str) -> bool:
        value = normalize(content)
        markers = (
            "systemstatus",
            "sessionstatus",
            "motivation core",
            "motivation explanation core",
            "meaning core",
            "temporal relevance core",
            "continuity core",
            "persistent self model core",
            "foundation decision layer",
            "wissensplattformstatus",
            "bedeutungspfad",
            "motivationsprioritäten",
            "motivationserklärung",
            "motivationserklarung",
            "wichtige einflüsse",
            "wichtige einfluesse",
            "kein wille",
            "kein bewusstsein",
            "teilantwort",
            "zeitbudget",
            "quellenseiten konnten nicht rechtzeitig abgerufen werden",
            "automatische zusammenfassung war nicht verfugbar",
            "bibtex formatted citation",
            "priorisierte wissenslucken",
            "wissenslucken und prufauftrage",
            "lernprojekt",
            "existiert bereits",
            "vorhandenes lernprojekt aktualisiert",
            "mein name ist kontinuum",
            "ich bin projekt kontinuum",
            "dialogantwort",
            "du bist raphael",
            "ich lerne zuerst python",
            "regelbasiert",
        )
        return any(marker in value for marker in markers)

    def _claim_groups(self, rows: list[dict]) -> dict:
        groups: dict[str, dict] = {}
        for row in rows:
            claim = self._claim(row["content"])
            if not claim:
                continue
            subject, value = claim
            group = groups.setdefault(subject, {"values": {}})
            group["values"].setdefault(value, []).append(row)
        return groups

    def _conflicts_for(self, row: dict, claim: tuple[str, str] | None, groups: dict) -> list[int]:
        if not claim:
            return []
        subject, value = claim
        return [
            other["id"]
            for other_value, rows in groups[subject]["values"].items()
            if other_value != value for other in rows
            if not self._version_transition(row, other)
        ]

    def _confirmations_for(self, row: dict, claim: tuple[str, str] | None, groups: dict) -> int:
        if not claim:
            return 0
        subject, value = claim
        return max(0, len(groups[subject]["values"].get(value, [])) - 1)

    def _group_has_conflict(self, group: dict) -> bool:
        values = list(group["values"].items())
        for index, (_, rows) in enumerate(values):
            for _, other_rows in values[index + 1:]:
                if any(not self._version_transition(first, second) for first in rows for second in other_rows):
                    return True
        return False

    @staticmethod
    def _version_transition(first: dict, second: dict) -> bool:
        first_versions = re.findall(r"\b\d+\.\d+\b", first["content"])
        second_versions = re.findall(r"\b\d+\.\d+\b", second["content"])
        if not first_versions or not second_versions:
            return False
        first_intro = first["metadata"].get("introduced_version")
        second_intro = second["metadata"].get("introduced_version")
        return bool(first_intro and second_intro and first_intro != second_intro)

    def _last_confirmation(self, row: dict, claim: tuple[str, str] | None, groups: dict) -> str:
        if not claim:
            return row["created_at"]
        subject, value = claim
        dates = [item["created_at"] for item in groups[subject]["values"].get(value, [])]
        return max(dates) if dates else row["created_at"]

    def _independent_sources(self, metadata: dict) -> set[str]:
        source_ids = metadata.get("source_record_ids") or []
        if not source_ids and metadata.get("source_record_id"):
            source_ids = [metadata["source_record_id"]]
        values = set()
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            with self.storage.connect() as database:
                rows = database.execute(
                    f"SELECT content FROM sources WHERE id IN ({placeholders})", tuple(source_ids)
                ).fetchall()
            for row in rows:
                values.add(self._source_key(row["content"]))
        elif metadata.get("source_locator") and metadata.get("origin") in {"research", "notebook"}:
            values.add(self._source_key(metadata["source_locator"]))
        return {value for value in values if value}

    def _source_quality(self, metadata: dict) -> dict:
        source_ids = metadata.get("source_record_ids") or []
        if not source_ids and metadata.get("source_record_id"):
            source_ids = [metadata["source_record_id"]]
        weights: dict[str, float] = {}
        classes = Counter()
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            with self.storage.connect() as database:
                rows = database.execute(
                    f"SELECT content, metadata FROM sources WHERE id IN ({placeholders})", tuple(source_ids)
                ).fetchall()
            for row in rows:
                source_metadata = self._metadata(row["metadata"])
                domain = self._source_key(row["content"])
                quality = source_metadata.get("quality", {})
                weight = float(source_metadata.get("quality_weight", quality.get("weight", 0.4)))
                source_class = source_metadata.get("source_class", quality.get("class", "unknown"))
                weights[domain or f"source:{len(weights)}"] = max(weights.get(domain, 0), weight)
                classes[source_class] += 1
        return {"weight_sum": sum(weights.values()), "classes": dict(classes)}

    @staticmethod
    def _source_key(locator: str) -> str:
        parsed = urlparse(locator or "")
        if parsed.scheme in {"http", "https"}:
            return parsed.netloc.casefold().removeprefix("www.")
        return str(Path(locator).resolve()).casefold() if locator else ""

    @classmethod
    def _claim(cls, content: str) -> tuple[str, str] | None:
        clean = " ".join((content or "").split()).strip(" .")
        match = re.match(r"^(.{2,120}?)\s+(?:ist|sind|beträgt|betraegt|lautet)\s+(.{1,220})$", clean, re.I)
        if not match:
            return None
        return cls._normalize(match.group(1)), cls._normalize(match.group(2))

    @classmethod
    def _topics(cls, rows: list[dict]) -> Counter:
        counter = Counter()
        for row in rows:
            words = re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9-]{3,}", row["content"])
            counter.update(cls._normalize(word) for word in words if cls._normalize(word) not in cls.STOPWORDS)
        return counter

    @staticmethod
    def _date(row: dict) -> datetime:
        value = row["metadata"].get("learned_at") or row["created_at"]
        return datetime.fromisoformat(value)

    @staticmethod
    def _level(score: float) -> str:
        if score >= 0.8:
            return "hoch"
        if score >= 0.55:
            return "mittel"
        return "niedrig"

    @staticmethod
    def _priority_rank(priority: str) -> int:
        return {"high": 3, "medium": 2, "low": 1, "none": 0}.get(priority, 0)

    @staticmethod
    def _reason(origin: str, sources: int, quality_weight: float, confirmations: int, conflicts: int) -> str:
        return (
            f"Ursprung {origin or 'unbekannt'}, {sources} unabhängige Quellen mit Qualitätsgewicht "
            f"{quality_weight:.2f}, {confirmations} Bestätigungen, {conflicts} Widersprüche."
        )

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", (value or "").casefold().replace("ß", "ss"))
        return " ".join("".join(character for character in decomposed if not unicodedata.combining(character)).split())

    def _update_metadata(self, knowledge_id: int, metadata: dict) -> None:
        with self.storage.connect() as database:
            database.execute(
                "UPDATE knowledge_items SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), knowledge_id),
            )
            database.commit()

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
