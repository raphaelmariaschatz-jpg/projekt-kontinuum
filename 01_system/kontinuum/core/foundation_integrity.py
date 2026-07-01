from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


class FoundationIntegrityCore:
    """Immutable registry and audit boundary for protected foundation knowledge."""

    VERSION = "2.0"
    KNOWLEDGE_CLASS = "foundation_knowledge"
    BLOCKED_ORIGINS = {
        "dialogue", "learning", "research", "notebook", "memory", "report",
        "status", "audit", "diagnostic", "self_extension", "autonomous_learning",
    }

    def __init__(self, storage, identity: dict, foundation: dict, foundation_decision=None):
        self.storage = storage
        self.identity = identity
        self.foundation = foundation
        self.foundation_decision = foundation_decision
        self.foundation_memory = None
        self._seed_registry()
        self._record_guiding_policy_activation()
        self._quarantine_legacy_foundation_knowledge()
        self._deactivate_foundation_learning_tasks()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _digest(payload: dict) -> str:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def canonical_items(self) -> list[dict]:
        source = self.foundation.get("source", self.identity.get("creator", "Raphael Schatz"))
        documents = list(self.foundation.get("source_documents", []))
        items = [
            {
                "key": "identity.creator",
                "value": self.identity.get("creator", "Raphael Schatz"),
                "foundation_kind": "creator_principle",
            },
            {
                "key": "identity.core_process",
                "value": self.identity.get("core_process", "Erkennen – Schaffen – Vollenden"),
                "foundation_kind": "foundation_principle",
            },
            {
                "key": "identity.guiding_philosophy",
                "value": self.identity.get("guiding_philosophy", "Der Weg ist das Ziel"),
                "foundation_kind": "foundation_principle",
            },
            {
                "key": "moral.rules",
                "value": list(self.foundation.get("moral_rules", [])),
                "foundation_kind": "moral_foundation",
            },
            {
                "key": "identity.continuity_boundaries",
                "value": [
                    row for row in self.foundation.get("principles", [])
                    if row.get("class") in {"identity", "continuity"}
                ],
                "foundation_kind": "foundation_identity",
            },
            {
                "key": "guiding.principles",
                "value": {
                    "policy": dict(self.foundation.get("guiding_principles_policy", {})),
                    "principles": list(self.foundation.get("guiding_principles", [])),
                },
                "foundation_kind": "guiding_principles",
            },
        ]
        return [
            {
                **item,
                "knowledge_class": self.KNOWLEDGE_CLASS,
                "source": source,
                "source_documents": documents,
                "protection_version": self.VERSION,
            }
            for item in items
        ]

    def _seed_registry(self) -> None:
        with self.storage.connect() as database:
            for item in self.canonical_items():
                digest = self._digest(item)
                exists = database.execute(
                    """SELECT id FROM foundation_knowledge
                       WHERE kind = 'foundation.knowledge'
                         AND content = ?
                         AND json_extract(metadata, '$.integrity_hash') = ? LIMIT 1""",
                    (item["key"], digest),
                ).fetchone()
                if exists:
                    continue
                metadata = {
                    **item,
                    "integrity_hash": digest,
                    "protected": True,
                    "protected_foundation": True,
                    "immutable": True,
                    "introduced_at": self._now(),
                }
                database.execute(
                    "INSERT INTO foundation_knowledge(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    ("foundation.knowledge", item["key"], json.dumps(metadata, ensure_ascii=False), self._now()),
                )
            database.commit()

    def _quarantine_legacy_foundation_knowledge(self) -> None:
        from .foundation_knowledge_guard import FoundationKnowledgeGuard
        guard = FoundationKnowledgeGuard()
        changed = []
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM knowledge_items WHERE kind = 'knowledge.integrated'"
            ).fetchall()
            for row in rows:
                metadata = self._metadata(row["metadata"])
                if metadata.get("excluded_from_domain_knowledge") or not guard.is_foundation(row["content"]):
                    continue
                metadata.update({
                    "knowledge_class": self.KNOWLEDGE_CLASS,
                    "protected_foundation": True,
                    "excluded_from_domain_knowledge": True,
                    "migration": "foundation_knowledge_protection_2.0",
                    "migration_at": self._now(),
                })
                database.execute(
                    "UPDATE knowledge_items SET metadata = ? WHERE id = ?",
                    (json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
                changed.append(int(row["id"]))
            database.commit()
        if changed:
            self._audit("foundation.legacy_knowledge.quarantined", "Legacy-Fundamentwissen getrennt", {
                "knowledge_ids": changed,
                "count": len(changed),
            })

    def _record_guiding_policy_activation(self) -> None:
        policy = dict(self.foundation.get("guiding_principles_policy", {}))
        approval_reference = str(policy.get("approval_reference", "")).strip()
        if policy.get("status") != "active_provisional" or not approval_reference:
            return
        with self.storage.connect() as database:
            exists = database.execute(
                """SELECT id FROM audit_events
                   WHERE kind = 'foundation.change.activated'
                     AND content = 'guiding.principles'
                     AND json_extract(metadata, '$.approval_reference') = ? LIMIT 1""",
                (approval_reference,),
            ).fetchone()
        if exists:
            return
        self._audit("foundation.change.activated", "guiding.principles", {
            "key": "guiding.principles",
            "actor": policy.get("authority", self.identity.get("creator", "Raphael Schatz")),
            "role": "CREATOR",
            "authorization_basis": "explicit_creator_directive",
            "approval_reference": approval_reference,
            "status": policy.get("status"),
            "effective_from": policy.get("effective_from"),
            "revocable": bool(policy.get("revocable", True)),
            "revocation_mode": policy.get("revocation_mode", "append_only_superseding_migration"),
            "principle_count": len(self.foundation.get("guiding_principles", [])),
            "activated_at": self._now(),
        })

    def _deactivate_foundation_learning_tasks(self) -> None:
        from .foundation_knowledge_guard import FoundationKnowledgeGuard
        guard = FoundationKnowledgeGuard()
        changed = []
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM learning_tasks WHERE COALESCE(json_extract(metadata, '$.active'), 1) != 0"
            ).fetchall()
            for row in rows:
                metadata = self._metadata(row["metadata"])
                values = [row["content"], metadata.get("subject", ""), *metadata.get("meta_learning", {}).get("open_gaps", [])]
                if not any(guard.is_foundation(str(value)) for value in values if value):
                    continue
                metadata.update({
                    "active": False,
                    "terminal": True,
                    "terminal_outcome": "skipped_foundation_knowledge",
                    "knowledge_class": self.KNOWLEDGE_CLASS,
                    "reason": "Fundamentwissen ist keine Lern-, Prüf- oder Wissenslücke.",
                    "updated_at": self._now(),
                })
                database.execute(
                    "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                    (json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
                changed.append(int(row["id"]))
            database.commit()
        if changed:
            self._audit("foundation.learning_tasks.deactivated", "Fundament-Lernaufträge deaktiviert", {
                "task_ids": changed,
                "count": len(changed),
            })

    def integration_decision(self, text: str, origin: str, guard) -> dict:
        protected = guard.is_foundation(text)
        if self.foundation_memory:
            protected = protected or self.foundation_memory.classify(text, guard)["is_foundation"]
        if not protected:
            return {"allowed": True, "classification": "knowledge"}
        normalized_origin = str(origin or "").casefold()
        reason = (
            "Fundamentwissen besitzt eine eigene unveränderliche Schutzklasse und darf nicht "
            "über Dialog-, Lern-, Recherche-, Bericht-, Diagnose- oder Self-Extension-Pfade integriert werden."
        )
        self._audit("foundation.integration.blocked", text, {
            "origin": normalized_origin,
            "reason": reason,
            "knowledge_class": self.KNOWLEDGE_CLASS,
        })
        return {
            "allowed": False,
            "classification": self.KNOWLEDGE_CLASS,
            "reason": reason,
            "origin": normalized_origin,
        }

    def authorize_change(self, key: str, proposed_value, authorization: dict | None = None) -> dict:
        auth = dict(authorization or {})
        required = {
            "explicit": auth.get("explicit") is True,
            "authenticated": auth.get("authenticated") is True,
            "creator": auth.get("actor") == self.identity.get("creator", "Raphael Schatz"),
            "superadmin": str(auth.get("role", "")).upper() == "SUPERADMIN",
            "reason": bool(str(auth.get("reason", "")).strip()),
            "approval_reference": bool(str(auth.get("approval_reference", "")).strip()),
        }
        if key not in {item["key"] for item in self.canonical_items()} or not all(required.values()):
            result = {
                "ok": False,
                "decision": "block",
                "key": key,
                "requirements": required,
                "reason": "Fundamentänderung nicht ausdrücklich und vollständig durch Creator/SUPERADMIN autorisiert.",
            }
            self._audit("foundation.change.blocked", key, result)
            return result

        action = f"Autorisierte Fundamentänderung prüfen: {key}"
        decision = self.foundation_decision.begin(action, {
            "foundation_change": True,
            "actor": auth["actor"],
            "approval_reference": auth["approval_reference"],
        }) if self.foundation_decision else {"decision": "allow", "decision_id": None, "reason": "Explizite Autorisierung geprüft."}
        if decision["decision"] == "block":
            if self.foundation_decision:
                self.foundation_decision.complete_blocked(int(decision["decision_id"]), decision["reason"])
            result = {"ok": False, "decision": "block", "key": key, "reason": decision["reason"]}
            self._audit("foundation.change.blocked", key, result)
            return result

        proposal = {
            "key": key,
            "proposed_value": proposed_value,
            "knowledge_class": self.KNOWLEDGE_CLASS,
            "protection_version": self.VERSION,
            "actor": auth["actor"],
            "role": "SUPERADMIN",
            "reason": auth["reason"],
            "approval_reference": auth["approval_reference"],
            "foundation_decision_id": decision.get("decision_id"),
            "status": "authorized_pending_migration",
            "created_at": self._now(),
        }
        proposal["integrity_hash"] = self._digest(proposal)
        proposal_id = self.storage.add("foundation_knowledge", "foundation.change.authorized", key, proposal)
        if self.foundation_decision:
            outcome = f"Fundamentänderung {key} als autorisierter, noch nicht aktivierter Migrationsauftrag {proposal_id} dokumentiert."
            self.foundation_decision.mark_created(int(decision["decision_id"]), "foundation_integrity", outcome)
            self.foundation_decision.complete(int(decision["decision_id"]), "foundation_integrity", outcome)
        result = {"ok": True, "decision": "authorized_pending_migration", "proposal_id": proposal_id, "key": key}
        self._audit("foundation.change.authorized", key, {**proposal, **result})
        return result

    def verify(self) -> dict:
        expected = {item["key"]: item for item in self.canonical_items()}
        issues = []
        verified = 0
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM foundation_knowledge WHERE kind = 'foundation.knowledge' ORDER BY id"
            ).fetchall()
        by_key: dict[str, list] = {}
        for row in rows:
            by_key.setdefault(row["content"], []).append(row)
        for key, item in expected.items():
            matches = by_key.get(key, [])
            if not matches:
                issues.append({"key": key, "reason": "geschützter Datensatz fehlt"})
                continue
            valid = False
            current_ids = []
            historical = []
            for row in matches:
                try:
                    metadata = json.loads(row["metadata"])
                except (TypeError, ValueError):
                    issues.append({"key": key, "record_id": int(row["id"]), "reason": "ungültige Metadaten"})
                    continue
                stored_payload = {name: metadata.get(name) for name in item}
                stored_hash = metadata.get("integrity_hash", "")
                if stored_hash != self._digest(stored_payload):
                    issues.append({"key": key, "record_id": int(row["id"]), "reason": "Integritätshash verletzt"})
                elif stored_payload == item:
                    valid = True
                    current_ids.append(int(row["id"]))
                else:
                    historical.append(int(row["id"]))
            if valid:
                verified += 1
                first_current = min(current_ids)
                for record_id in historical:
                    if record_id > first_current:
                        issues.append({
                            "key": key,
                            "record_id": record_id,
                            "reason": "Nicht autorisierte abweichende Version nach aktuellem Foundation-Datensatz",
                        })
            elif historical:
                issues.append({"key": key, "reason": "Aktuelle Foundation-Version fehlt; nur historische Version vorhanden"})
        contamination = self.contamination_findings()
        return {
            "ok": not issues and not contamination,
            "version": self.VERSION,
            "knowledge_class": self.KNOWLEDGE_CLASS,
            "protected_records": len(expected),
            "verified_records": verified,
            "issues": issues,
            "contamination": contamination,
        }

    def contamination_findings(self) -> list[dict]:
        findings = []
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, content, metadata FROM learning_tasks WHERE COALESCE(json_extract(metadata, '$.active'), 1) != 0"
            ).fetchall()
        from .foundation_knowledge_guard import FoundationKnowledgeGuard
        guard = FoundationKnowledgeGuard()
        for row in rows:
            metadata = self._metadata(row["metadata"])
            values = [row["content"], metadata.get("subject", ""), *metadata.get("meta_learning", {}).get("open_gaps", [])]
            if any(guard.is_foundation(str(value)) for value in values if value):
                findings.append({"table": "learning_tasks", "id": int(row["id"]), "reason": "Fundamentwissen als aktive Lern- oder Wissenslücke"})
        return findings

    def status(self) -> dict:
        return self.verify()

    def bind_memory_layer(self, foundation_memory) -> None:
        self.foundation_memory = foundation_memory

    def run_audit(self, trigger: str = "manual") -> dict:
        result = self.verify()
        memory_result = self.foundation_memory.verify() if self.foundation_memory else None
        if memory_result:
            result = {**result, "ok": result["ok"] and memory_result["ok"], "foundation_memory": memory_result}
        checked_at = self._now()
        payload = {
            **result,
            "trigger": trigger,
            "checked_at": checked_at,
        }
        self._audit(
            "foundation.integrity.checked",
            "Foundation Knowledge Protection intakt" if result["ok"] else "Foundation Knowledge Protection verletzt",
            payload,
        )
        return payload

    def audit_report(self) -> str:
        current = self.run_audit("user.command.fundamentaudit")
        with self.storage.connect() as database:
            last_change = database.execute(
                """SELECT content, metadata, created_at FROM audit_events
                   WHERE kind IN ('foundation.change.authorized', 'foundation.change.activated')
                   ORDER BY id DESC LIMIT 1"""
            ).fetchone()
            contamination_attempts = int(database.execute(
                "SELECT COUNT(*) FROM audit_events WHERE kind = 'foundation.integration.blocked'"
            ).fetchone()[0])
            blocked_accesses = int(database.execute(
                "SELECT COUNT(*) FROM audit_events WHERE kind LIKE 'foundation.%.blocked'"
            ).fetchone()[0])
        if last_change:
            change_metadata = self._metadata(last_change["metadata"])
            last_change_text = (
                f"{self._display_time(last_change['created_at'])} – {change_metadata.get('key') or last_change['content']} "
                f"({change_metadata.get('decision', change_metadata.get('status', 'autorisiert'))})"
            )
        else:
            last_change_text = "keine autorisierte Änderung dokumentiert"
        checksum = (
            f"intakt ({current['verified_records']}/{current['protected_records']} gültig)"
            if current["verified_records"] == current["protected_records"] and not current["issues"]
            else f"verletzt ({current['verified_records']}/{current['protected_records']} gültig, {len(current['issues'])} Befunde)"
        )
        memory = current.get("foundation_memory") or {}
        memory_checksum = (
            f"intakt ({memory.get('verified_records', 0)}/{memory.get('protected_records', 0)} gültig)"
            if memory.get("ok")
            else f"verletzt ({memory.get('verified_records', 0)}/{memory.get('protected_records', 0)} gültig)"
        )
        return "\n".join((
            "Foundation Audit 3.0",
            f"Schutzstatus: {'INTAKT' if current['ok'] else 'VERLETZT'}",
            f"Prüfsummenstatus: {checksum}",
            f"Foundation-Memory-Prüfsummen: {memory_checksum}",
            f"Letzte Prüfung: {self._display_time(current['checked_at'])}",
            f"Letzte autorisierte Änderung: {last_change_text}",
            f"Kontaminationsversuche: {contamination_attempts}",
            f"Blockierte Zugriffe: {blocked_accesses}",
        ))

    @staticmethod
    def _display_time(value: str) -> str:
        try:
            return datetime.fromisoformat(value).astimezone().isoformat(timespec="seconds")
        except (TypeError, ValueError):
            return str(value or "unbekannt")

    def _audit(self, kind: str, content: str, metadata: dict) -> None:
        self.storage.add("audit_events", kind, str(content)[:500], {
            **metadata,
            "protection_version": self.VERSION,
            "audited_at": self._now(),
        })

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
