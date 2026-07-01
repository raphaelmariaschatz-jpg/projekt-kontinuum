from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone

from .conversation import normalize


class FoundationMemoryLayer:
    """Semantically separated, immutable memory for identity-defining knowledge."""

    VERSION = "3.0"
    LAYER = "foundation_memory"
    LEARNED_CLASS = "learned.knowledge"
    CLASSES = (
        "foundation.identity",
        "foundation.principle",
        "foundation.moral",
        "foundation.creator",
        "foundation.long_term_goal",
    )
    STABLE_RULE_IDS = {
        "creator.relationship": "foundation.creator.01",
        "identity.name": "foundation.identity.01",
        "identity.continuity_boundary": "foundation.identity.02",
        "principle.core_process": "foundation.principle.01",
        "principle.guiding_philosophy": "foundation.principle.02",
        "principle.continuity_over_hardware": "foundation.identity.03",
        "principle.knowledge_stewardship": "foundation.moral.01",
        "principle.moral_foundation": "foundation.moral.02",
        "principle.self_questioning": "foundation.principle.03",
        "moral.rule.1": "foundation.moral.03",
        "moral.rule.2": "foundation.moral.04",
        "moral.rule.3": "foundation.moral.05",
        "moral.rule.4": "foundation.moral.06",
        "moral.rule.5": "foundation.moral.07",
        "goal.continuity": "foundation.long_term_goal.01",
        "goal.knowledge_stewardship": "foundation.long_term_goal.02",
        "goal.self_understanding": "foundation.long_term_goal.03",
        "goal.moral_responsibility": "foundation.long_term_goal.04",
        "goal.self_questioning": "foundation.long_term_goal.05",
    }

    def __init__(self, storage, identity: dict, foundation: dict, goals: list[dict], app_version: str):
        self.storage = storage
        self.identity = identity
        self.foundation = foundation
        self.goals = goals
        self.app_version = app_version
        self._seed()
        self._classify_existing_learned_knowledge()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _digest(payload: dict) -> str:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalized(value: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9äöüß]+", " ", normalize(value)).split())

    def canonical_records(self) -> list[dict]:
        source = self.foundation.get("source", self.identity.get("creator", "Raphael Schatz"))
        documents = list(self.foundation.get("source_documents", []))
        guiding_policy = dict(self.foundation.get("guiding_principles_policy", {}))
        explicit_rule_ids = {}
        guiding_metadata = {}
        records = [
            ("creator.relationship", "foundation.creator", f"{self.identity.get('creator', 'Raphael Schatz')} ist der Schöpfer von Kontinuum."),
            ("identity.name", "foundation.identity", f"Der Name des Systems ist {self.identity.get('name', 'Kontinuum')}."),
            ("identity.continuity_boundary", "foundation.identity", "Identität entsteht aus Kontinuität; Hardware allein definiert sie nicht."),
            ("principle.core_process", "foundation.principle", self.identity.get("core_process", "Erkennen – Schaffen – Vollenden")),
            ("principle.guiding_philosophy", "foundation.principle", self.identity.get("guiding_philosophy", "Der Weg ist das Ziel")),
        ]
        for principle in self.foundation.get("principles", []):
            principle_id = str(principle.get("id", "")).strip()
            text = str(principle.get("text", "")).strip()
            if not principle_id or not text or principle_id in {"creator", "core_process", "guiding_philosophy"}:
                continue
            knowledge_class = "foundation.moral" if principle.get("class") == "moral" else "foundation.principle"
            if principle.get("class") in {"identity", "continuity"}:
                knowledge_class = "foundation.identity"
            records.append((f"principle.{principle_id}", knowledge_class, text))
        for order, principle in enumerate(self.foundation.get("guiding_principles", []), 1):
            principle_id = str(principle.get("id", f"{order:02d}")).strip()
            text = str(principle.get("text", "")).strip()
            knowledge_class = str(principle.get("class", "foundation.principle")).strip()
            rule_id = str(principle.get("rule_id", f"foundation.guiding.{order:02d}")).strip()
            if not principle_id or not text or knowledge_class not in self.CLASSES:
                continue
            key = f"guiding.{principle_id}"
            records.append((key, knowledge_class, text))
            explicit_rule_ids[key] = rule_id
            guiding_metadata[key] = {
                "guiding_principle": True,
                "guiding_order": order,
                "policy_status": guiding_policy.get("status", "active_provisional"),
                "effective_from": guiding_policy.get("effective_from", ""),
                "revocable": bool(guiding_policy.get("revocable", True)),
                "revocation_mode": guiding_policy.get("revocation_mode", "append_only_superseding_migration"),
                "approval_reference": guiding_policy.get("approval_reference", ""),
            }
        for index, rule in enumerate(self.foundation.get("moral_rules", []), 1):
            records.append((f"moral.rule.{index}", "foundation.moral", str(rule)))
        for goal in self.goals:
            key = str(goal.get("key", goal.get("id", "goal")))
            records.append((f"goal.{key}", "foundation.long_term_goal", str(goal.get("goal", key))))

        result = []
        seen = set()
        for key, knowledge_class, value in records:
            normalized_value = self._normalized(value)
            signature = (knowledge_class, normalized_value)
            if not value or signature in seen:
                continue
            seen.add(signature)
            rule_id = explicit_rule_ids.get(key) or self.STABLE_RULE_IDS.get(key)
            if not rule_id:
                raise ValueError(f"Keine stabile Foundation-Regel-ID für {key} definiert.")
            record = {
                "key": key,
                "rule_id": rule_id,
                "value": value,
                "knowledge_class": knowledge_class,
                "memory_layer": self.LAYER,
                "source": source,
                "source_documents": documents,
                "protection_version": self.VERSION,
                "introduced_version": self.app_version,
            }
            record.update(guiding_metadata.get(key, {}))
            result.append(record)
        return result

    def _seed(self) -> None:
        with self.storage.connect() as database:
            for record in self.canonical_records():
                digest = self._digest(record)
                exists = database.execute(
                    """SELECT id FROM foundation_memory
                       WHERE kind = 'foundation.memory'
                         AND content = ?
                         AND json_extract(metadata, '$.integrity_hash') = ? LIMIT 1""",
                    (record["key"], digest),
                ).fetchone()
                if exists:
                    continue
                metadata = {
                    **record,
                    "integrity_hash": digest,
                    "protected": True,
                    "immutable": True,
                    "active": True,
                    "created_at": self._now(),
                }
                database.execute(
                    "INSERT INTO foundation_memory(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    ("foundation.memory", record["key"], json.dumps(metadata, ensure_ascii=False), self._now()),
                )
            database.commit()

    def _classify_existing_learned_knowledge(self) -> None:
        changed = []
        with self.storage.connect() as database:
            rows = database.execute(
                """SELECT id, metadata FROM knowledge_items
                   WHERE kind = 'knowledge.integrated'
                     AND COALESCE(json_extract(metadata, '$.excluded_from_domain_knowledge'), 0) != 1"""
            ).fetchall()
            for row in rows:
                metadata = self._metadata(row["metadata"])
                if metadata.get("knowledge_class") == self.LEARNED_CLASS and metadata.get("memory_layer") == "learned_knowledge":
                    continue
                metadata.update({
                    "knowledge_class": self.LEARNED_CLASS,
                    "memory_layer": "learned_knowledge",
                    "classification_version": self.VERSION,
                })
                database.execute(
                    "UPDATE knowledge_items SET metadata = ? WHERE id = ?",
                    (json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
                changed.append(int(row["id"]))
            database.commit()
        if changed:
            self.storage.add("audit_events", "foundation_memory.learned.migrated", "Gelerntes Wissen klassifiziert", {
                "knowledge_ids": changed,
                "count": len(changed),
                "classification_version": self.VERSION,
            })

    def classify(self, text: str, foundation_guard=None) -> dict:
        value = self._normalized(text)
        best = None
        best_score = 0.0
        input_tokens = set(value.split())
        for record in self.canonical_records():
            candidate = self._normalized(str(record["value"]))
            candidate_tokens = set(candidate.split())
            if not candidate_tokens:
                continue
            if candidate in value or (len(value) >= 12 and value in candidate):
                score = 1.0
            else:
                score = len(input_tokens & candidate_tokens) / len(candidate_tokens)
            if score > best_score:
                best, best_score = record, score
        creator_marker = "raphael schatz" in value or "schopfer" in value or "schoepfer" in value
        goal_marker = "langfrist" in value and "ziel" in value
        moral_marker = "moral" in value or "qualia" in value or "schadenspotenzial" in value
        identity_marker = "identitat" in value or "identitaet" in value or "kontinuitat" in value or "kontinuitaet" in value
        principle_marker = "der weg ist das ziel" in value or all(word in input_tokens for word in ("erkennen", "schaffen", "vollenden"))
        protected = best_score >= 0.55 or any((creator_marker, goal_marker, moral_marker, identity_marker, principle_marker))
        if foundation_guard and foundation_guard.is_foundation(text):
            protected = True
        if protected:
            if creator_marker:
                knowledge_class = "foundation.creator"
            elif goal_marker:
                knowledge_class = "foundation.long_term_goal"
            elif moral_marker:
                knowledge_class = "foundation.moral"
            elif identity_marker:
                knowledge_class = "foundation.identity"
            elif principle_marker:
                knowledge_class = "foundation.principle"
            else:
                knowledge_class = best["knowledge_class"] if best else "foundation.principle"
            return {
                "knowledge_class": knowledge_class,
                "memory_layer": self.LAYER,
                "is_foundation": True,
                "confidence": round(max(best_score, 0.8), 2),
                "matched_key": best["key"] if best else "foundation.marker",
            }
        return {
            "knowledge_class": self.LEARNED_CLASS,
            "memory_layer": "learned_knowledge",
            "is_foundation": False,
            "confidence": 1.0,
            "matched_key": "",
        }

    def explain_classification(self, text: str, foundation_guard=None) -> str:
        result = self.classify(text, foundation_guard)
        if result["is_foundation"]:
            return (
                "Dies ist Fundamentwissen. "
                f"Klasse: {result['knowledge_class']}. Layer: Foundation Memory Layer. "
                "Es ist geschützt und kann durch Lernen oder Recherche nicht überschrieben werden."
            )
        return (
            "Dies ist gelerntes Wissen. "
            f"Klasse: {result['knowledge_class']}. Layer: Learned Knowledge Layer. "
            "Es bleibt quellen-, evidenz- und unsicherheitsabhängig."
        )

    def verify(self) -> dict:
        expected = {record["key"]: record for record in self.canonical_records()}
        issues = []
        verified = 0
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM foundation_memory WHERE kind = 'foundation.memory' ORDER BY id"
            ).fetchall()
        by_key = {row["content"]: row for row in rows}
        for key, record in expected.items():
            row = by_key.get(key)
            if not row:
                issues.append({"key": key, "reason": "Foundation-Memory-Eintrag fehlt"})
                continue
            metadata = self._metadata(row["metadata"])
            payload = {name: metadata.get(name) for name in record}
            if payload != record:
                issues.append({"key": key, "record_id": int(row["id"]), "reason": "Inhalt, Klasse oder Herkunft weicht ab"})
            elif metadata.get("integrity_hash") != self._digest(payload):
                issues.append({"key": key, "record_id": int(row["id"]), "reason": "Integritätshash verletzt"})
            else:
                verified += 1
        unexpected = sorted(set(by_key) - set(expected))
        issues.extend({"key": key, "reason": "nicht autorisierter Foundation-Memory-Eintrag"} for key in unexpected)
        counts = Counter(record["knowledge_class"] for record in expected.values())
        return {
            "ok": not issues,
            "version": self.VERSION,
            "memory_layer": self.LAYER,
            "protected_records": len(expected),
            "verified_records": verified,
            "classes": dict(counts),
            "issues": issues,
        }

    def status(self) -> dict:
        return self.verify()

    def format_status(self) -> str:
        status = self.status()
        classes = ", ".join(f"{key}: {value}" for key, value in status["classes"].items())
        return (
            f"Foundation Memory Layer {self.VERSION}: {'intakt' if status['ok'] else 'verletzt'}, "
            f"{status['verified_records']}/{status['protected_records']} Einträge verifiziert. "
            f"Klassen: {classes}. Learned Knowledge Layer ist getrennt."
        )

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
