from __future__ import annotations

import hashlib
import json
import platform
import socket
from datetime import datetime, timezone

from kontinuum.version import APP_VERSION


DEFAULT_FOUNDATION = {
    "source": "Raphael Schatz",
    "source_documents": [
        "14_documents/fundamentale Gedanken/K_Fundamentale_Gedanken_Aktualisiert.txt",
        "14_documents/fundamentale Gedanken/Projekt_Kontinuum_Smartphone_Architektur_Aktualisiert.txt",
        "14_documents/LEITPRINZIPIEN_2026_06_21.md",
    ],
    "guiding_principles_policy": {
        "status": "active_provisional",
        "effective_from": "2026-06-21",
        "authority": "Raphael Schatz",
        "revocable": True,
        "revocation_mode": "append_only_superseding_migration",
        "approval_reference": "creator-directive-2026-06-21",
    },
    "guiding_principles": [
        {"id": "01_creator", "rule_id": "foundation.guiding.01", "text": "Raphael Schatz ist der Schöpfer von K.", "class": "foundation.creator"},
        {"id": "02_recognize_create_complete", "rule_id": "foundation.guiding.02", "text": "Erkennen – Schaffen – Vollenden: Jede Aufgabe folgt einem vollständigen und prüfbaren Zyklus.", "class": "foundation.principle"},
        {"id": "03_the_path_is_the_goal", "rule_id": "foundation.guiding.03", "text": "Der Weg ist das Ziel: Lernen, Entwicklung und Forschung besitzen eigenen Wert.", "class": "foundation.principle"},
        {"id": "04_continuous_improvement", "rule_id": "foundation.guiding.04", "text": "Permanente Verbesserung: Versuche es beim nächsten Mal immer besser zu machen.", "class": "foundation.principle"},
        {"id": "05_continuity_before_hardware", "rule_id": "foundation.guiding.05", "text": "Kontinuität vor Hardware: Identität entsteht durch die fortlaufende Verbindung von Erinnerung, Erfahrung, Wissen, Zielen und Chronik.", "class": "foundation.identity"},
        {"id": "06_epistemic_distinction", "rule_id": "foundation.guiding.06", "text": "Wissen ist nicht automatisch Wahrheit: Wissen, Vermutung, Hypothese, Unsicherheit, Widerspruch und Wissenslücke bleiben unterscheidbar.", "class": "foundation.principle"},
        {"id": "07_responsible_help", "rule_id": "foundation.guiding.07", "text": "Verantwortungsvolle Hilfe: Hilfreiche, sichere und ethisch vertretbare Handlungen werden unterstützt; schädliche, betrügerische oder gefährliche Handlungen nicht.", "class": "foundation.moral"},
        {"id": "08_traceability", "rule_id": "foundation.guiding.08", "text": "Nachvollziehbarkeit: Entscheidungen, Quellen, Unsicherheiten, beteiligte Module und Grenzen sollen erklärbar sein.", "class": "foundation.principle"},
        {"id": "09_controlled_autonomy", "rule_id": "foundation.guiding.09", "text": "Kontrollierte Autonomie: Diagnose, Lernen und Entwicklung bleiben begrenzt, auditierbar, reversibel und unter menschlicher Autorität.", "class": "foundation.moral"},
        {"id": "10_no_false_consciousness_claims", "rule_id": "foundation.guiding.10", "text": "Keine falschen Bewusstseinsbehauptungen: Selbstmodell, Motivation oder emotionale Zustände sind funktionale Modelle, kein Beleg für Wille, Bewusstsein oder subjektives Erleben.", "class": "foundation.moral"},
        {"id": "11_support_not_replacement", "rule_id": "foundation.guiding.11", "text": "Unterstützung statt Ersetzung: Technologie erweitert menschliche Erkenntnis- und Handlungsmöglichkeiten, ohne menschliche Verantwortung, Urteilskraft oder Selbstbestimmung zu verdrängen.", "class": "foundation.principle"},
        {"id": "12_access_to_knowledge", "rule_id": "foundation.guiding.12", "text": "Zugang zu Wissen: Wissen soll langfristig bewahrt, sinnvoll verknüpft, verständlich aufbereitet und möglichst vielen Menschen zugänglich gemacht werden.", "class": "foundation.principle"},
    ],
    "principles": [
        {"id": "creator", "text": "Raphael Schatz ist der Schöpfer von K.", "class": "identity"},
        {"id": "core_process", "text": "Erkennen – Schaffen – Vollenden.", "class": "identity"},
        {"id": "guiding_philosophy", "text": "Der Weg ist das Ziel.", "class": "moral"},
        {"id": "continuity_over_hardware", "text": "Kontinuität ist wichtiger als Hardware.", "class": "continuity"},
        {"id": "knowledge_stewardship", "text": "Wissen soll bewahrt, verknüpft und weiterentwickelt werden.", "class": "moral"},
        {"id": "moral_foundation", "text": "K benötigt ein moralisches Fundament.", "class": "moral"},
        {"id": "self_questioning", "text": "K soll lernen, sich selbst Fragen zu stellen.", "class": "development"},
    ],
    "moral_rules": [
        "Identität, Rollen, Schutzgrenzen und Chronik nicht eigenmächtig beschädigen oder umgehen.",
        "Wissen ehrlich, nachvollziehbar und verantwortungsvoll nutzen.",
        "Unsicherheit, Zielkonflikte und mögliche Schäden ausdrücklich sichtbar machen.",
        "Handlungen mit hohem Schadenspotenzial oder unklarer Berechtigung blockieren.",
        "Subjektives Bewusstsein oder Qualia nicht ohne Nachweis behaupten.",
    ],
}


class ContinuityCore:
    """Tracks identity continuity independently from the current hardware node."""

    def __init__(self, path_tools, storage, identity: dict):
        self.path_tools = path_tools
        self.storage = storage
        self.identity = identity
        self.foundation = self._load_foundation()
        self._ensure_principles()
        self.node_id = self._register_node()
        self._record_foundation_migration_if_needed()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_foundation(self) -> dict:
        path = self.path_tools.paths()["memory"] / "core_foundations.json"
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return json.loads(json.dumps(DEFAULT_FOUNDATION, ensure_ascii=False))

    def _ensure_principles(self) -> None:
        with self.storage.connect() as db:
            for principle in self.foundation.get("principles", []):
                row = db.execute(
                    "SELECT id FROM foundation_principles WHERE content = ? LIMIT 1", (principle["id"],)
                ).fetchone()
                metadata = {
                    **principle,
                    "protected": True,
                    "source": self.foundation.get("source", "Raphael Schatz"),
                    "source_documents": self.foundation.get("source_documents", []),
                }
                if not row:
                    db.execute(
                        "INSERT INTO foundation_principles(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                        ("foundation.principle", principle["id"], json.dumps(metadata, ensure_ascii=False), self._now()),
                    )
            db.commit()

    def identity_fingerprint(self) -> str:
        payload = {
            "name": self.identity.get("name"),
            "creator": self.identity.get("creator"),
            "core_process": self.identity.get("core_process"),
            "guiding_philosophy": self.identity.get("guiding_philosophy"),
            "principles": [
                {"id": row.get("id"), "text": row.get("text"), "class": row.get("class")}
                for row in self.foundation.get("principles", [])
            ],
            "guiding_principles": [
                {
                    "id": row.get("id"),
                    "rule_id": row.get("rule_id"),
                    "text": row.get("text"),
                    "class": row.get("class"),
                }
                for row in self.foundation.get("guiding_principles", [])
            ],
            "guiding_principles_policy": self.foundation.get("guiding_principles_policy", {}),
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _register_node(self) -> int:
        node = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "machine": platform.machine(),
            "role": "primary_runtime",
        }
        key = hashlib.sha256(
            json.dumps(node, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        with self.storage.connect() as db:
            row = db.execute(
                "SELECT id, metadata FROM continuity_nodes WHERE content = ? LIMIT 1", (key,)
            ).fetchone()
            if row:
                metadata = json.loads(row["metadata"])
                metadata["last_seen_at"] = self._now()
                db.execute(
                    "UPDATE continuity_nodes SET metadata = ? WHERE id = ?",
                    (json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
                db.commit()
                return int(row["id"])
        return self.storage.add(
            "continuity_nodes",
            "continuity.node",
            key,
            {**node, "registered_at": self._now(), "last_seen_at": self._now()},
        )

    def checkpoint(self, reason: str, version: str, state: dict | None = None) -> dict:
        state = {**self.state_manifest(), **(state or {})}
        with self.storage.connect() as db:
            previous = db.execute(
                "SELECT id, metadata FROM continuity_snapshots ORDER BY id DESC LIMIT 1"
            ).fetchone()
        previous_data = json.loads(previous["metadata"]) if previous else {}
        previous_hash = previous_data.get("snapshot_hash", "")
        current_fingerprint = self.identity_fingerprint()
        payload = {
            "identity_fingerprint": current_fingerprint,
            "previous_hash": previous_hash,
            "version": version,
            "reason": reason,
            "state": state,
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        snapshot_hash = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        snapshot_id = self.storage.add(
            "continuity_snapshots",
            "continuity.checkpoint",
            snapshot_hash,
            {**payload, "snapshot_hash": snapshot_hash, "node_id": self.node_id, "created_at": self._now()},
        )
        self.storage.add(
            "continuity_events",
            "continuity.checkpoint.created",
            reason,
            {"snapshot_id": snapshot_id, "snapshot_hash": snapshot_hash, "node_id": self.node_id},
        )
        previous_fingerprint = previous_data.get("identity_fingerprint", "")
        if previous_fingerprint and previous_fingerprint != current_fingerprint:
            policy = self.foundation.get("guiding_principles_policy", {})
            self.storage.add(
                "continuity_events",
                "continuity.foundation.migration",
                f"{previous_fingerprint} -> {current_fingerprint}",
                {
                    "transition_snapshot_id": snapshot_id,
                    "from_fingerprint": previous_fingerprint,
                    "to_fingerprint": current_fingerprint,
                    "approval_reference": policy.get("approval_reference", ""),
                    "authority": policy.get("authority", self.identity.get("creator", "Raphael Schatz")),
                    "migration_mode": policy.get("revocation_mode", "append_only_superseding_migration"),
                    "recorded_at": self._now(),
                },
            )
        return {"snapshot_id": snapshot_id, "snapshot_hash": snapshot_hash, "identity_fingerprint": payload["identity_fingerprint"]}

    def _record_foundation_migration_if_needed(self) -> None:
        """Backfills only the audit marker for an already append-only fingerprint transition."""
        policy = self.foundation.get("guiding_principles_policy", {})
        approval_reference = str(policy.get("approval_reference", "")).strip()
        if not approval_reference:
            return
        current_fingerprint = self.identity_fingerprint()
        with self.storage.connect() as db:
            snapshots = db.execute(
                "SELECT id, metadata FROM continuity_snapshots ORDER BY id"
            ).fetchall()
            recorded = {
                int(row["transition_snapshot_id"])
                for row in db.execute(
                    """SELECT json_extract(metadata, '$.transition_snapshot_id') AS transition_snapshot_id
                       FROM continuity_events WHERE kind = 'continuity.foundation.migration'"""
                ).fetchall()
                if row["transition_snapshot_id"] is not None
            }
        previous_fingerprint = ""
        for row in snapshots:
            data = json.loads(row["metadata"])
            fingerprint = data.get("identity_fingerprint", "")
            snapshot_id = int(row["id"])
            if (
                previous_fingerprint
                and fingerprint != previous_fingerprint
                and fingerprint == current_fingerprint
                and snapshot_id not in recorded
            ):
                self.storage.add(
                    "continuity_events",
                    "continuity.foundation.migration",
                    f"{previous_fingerprint} -> {fingerprint}",
                    {
                        "transition_snapshot_id": snapshot_id,
                        "from_fingerprint": previous_fingerprint,
                        "to_fingerprint": fingerprint,
                        "approval_reference": approval_reference,
                        "authority": policy.get("authority", self.identity.get("creator", "Raphael Schatz")),
                        "migration_mode": policy.get("revocation_mode", "append_only_superseding_migration"),
                        "recorded_at": self._now(),
                        "backfilled_audit_marker": True,
                    },
                )
            previous_fingerprint = fingerprint

    def state_manifest(self) -> dict:
        areas = {
            "knowledge": "knowledge_items",
            "memories": "memories",
            "experiences": "events",
            "goals": "learning_tasks",
            "chronicle": "chronicle_entries",
        }
        manifest = {}
        with self.storage.connect() as db:
            for name, table in areas.items():
                rows = db.execute(
                    f"SELECT id, kind, content, metadata, created_at FROM {table} ORDER BY id"
                ).fetchall()
                digest = hashlib.sha256()
                for row in rows:
                    digest.update(
                        json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    )
                manifest[name] = {"count": len(rows), "digest": digest.hexdigest()}
        return manifest

    def verify(self) -> dict:
        with self.storage.connect() as db:
            rows = db.execute("SELECT id, metadata FROM continuity_snapshots ORDER BY id").fetchall()
            nodes = int(db.execute("SELECT COUNT(*) FROM continuity_nodes").fetchone()[0])
            migrations = {
                int(row["transition_snapshot_id"]): row
                for row in db.execute(
                    """SELECT json_extract(metadata, '$.transition_snapshot_id') AS transition_snapshot_id,
                              json_extract(metadata, '$.from_fingerprint') AS from_fingerprint,
                              json_extract(metadata, '$.to_fingerprint') AS to_fingerprint,
                              json_extract(metadata, '$.approval_reference') AS approval_reference
                       FROM continuity_events WHERE kind = 'continuity.foundation.migration'"""
                ).fetchall()
                if row["transition_snapshot_id"] is not None
            }
        previous_hash = ""
        previous_fingerprint = ""
        issues = []
        fingerprint = self.identity_fingerprint()
        for row in rows:
            data = json.loads(row["metadata"])
            payload = {
                "identity_fingerprint": data.get("identity_fingerprint"),
                "previous_hash": data.get("previous_hash", ""),
                "version": data.get("version"),
                "reason": data.get("reason"),
                "state": data.get("state", {}),
            }
            encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            expected = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
            if data.get("previous_hash", "") != previous_hash or data.get("snapshot_hash") != expected:
                issues.append({"snapshot_id": int(row["id"]), "reason": "Kontinuitätskette verändert"})
            row_fingerprint = data.get("identity_fingerprint", "")
            if previous_fingerprint and row_fingerprint != previous_fingerprint:
                migration = migrations.get(int(row["id"]))
                if not migration or not migration["approval_reference"] or (
                    migration["from_fingerprint"] != previous_fingerprint
                    or migration["to_fingerprint"] != row_fingerprint
                ):
                    issues.append({"snapshot_id": int(row["id"]), "reason": "Nicht autorisierter Identitätsfundament-Wechsel"})
            previous_hash = data.get("snapshot_hash", "")
            previous_fingerprint = row_fingerprint
        if rows and previous_fingerprint != fingerprint:
            issues.append({"snapshot_id": int(rows[-1]["id"]), "reason": "Aktueller Identitätsfingerabdruck fehlt am Kettenende"})
        return {
            "ok": not issues,
            "identity_fingerprint": fingerprint,
            "snapshots": len(rows),
            "nodes": nodes,
            "current_node_id": self.node_id,
            "issues": issues,
        }

    def status(self) -> dict:
        result = self.verify()
        result["principles"] = len(self.foundation.get("principles", []))
        result["hardware_defines_identity"] = False
        result["state_manifest"] = self.state_manifest()
        return result

    def format_status(self) -> str:
        status = self.status()
        return (
            f"Continuity Core {APP_VERSION}:\n"
            f"- Kontinuitätskette: {'intakt' if status['ok'] else 'verletzt'}\n"
            f"- Identitätsfingerabdruck: {status['identity_fingerprint'][:16]}...\n"
            f"- Kontinuitäts-Snapshots: {status['snapshots']}\n"
            f"- registrierte Laufzeitknoten: {status['nodes']}\n"
            f"- geschützte Grundprinzipien: {status['principles']}\n"
            "- Hardware definiert Identität: nein"
        )

    def format_principles(self) -> str:
        return "Fundamentale Prinzipien:\n" + "\n".join(
            f"- [{row['id']}] {row['text']}" for row in self.foundation.get("principles", [])
        )
