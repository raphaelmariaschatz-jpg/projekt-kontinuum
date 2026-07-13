# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path


class IdentityValidationError(ValueError):
    pass


class CanonicalIdentityManager:
    VERSION = "1.0"
    FILE_NAME = "canonical_identity.json"
    LEGACY_FILE_NAME = "canonical_identity_34_1.json"
    VALID_ROLES = {
        "creator",
        "super_admin",
        "system_owner",
        "admin",
        "user",
        "assistant",
        "foundation_ai",
        "system",
        "agent",
    }
    CREATOR_PERMISSIONS = [
        "full_system_control",
        "configuration_write",
        "governance_approval",
        "foundation_approval",
        "architecture_approval",
        "agent_management",
    ]
    DEFAULT_DATA = {
        "schema_version": "1.0",
        "creator": {"id": "creator_001", "name": "Raphael Schatz"},
        "user": {"preferred_address": "Raphael"},
        "assistant": {"name": "Kontinuum", "short_name": "K"},
        "roles": {
            "creator": ["super_admin", "system_owner"],
            "assistant": ["foundation_ai"],
        },
        "permissions": {
            "creator": CREATOR_PERMISSIONS,
        },
        "system_identity": {
            "foundation_component": "Canonical Identity Manager",
            "version": VERSION,
        },
        "identity_versions": [],
    }

    def __init__(self, path_tools, storage=None):
        self.path_tools = path_tools
        self.storage = storage
        self.logger = logging.getLogger("IdentityManager")
        self.config_dir = path_tools.paths()["config"]
        self.path = self.config_dir / self.FILE_NAME
        self.legacy_path = self.config_dir / self.LEGACY_FILE_NAME
        self.history_dir = self.config_dir / "history" / "canonical_identity_history"
        self.data = self.load()

    def load(self) -> dict:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        for candidate in (self.path, self.legacy_path):
            if not candidate.exists():
                continue
            try:
                data = json.loads(candidate.read_text(encoding="utf-8-sig"))
                canonical = self._normalize_payload(data)
                self.validate(canonical)
                if candidate != self.path:
                    self.path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                self._write_legacy_view(canonical)
                self._notify("load", "Canonical Identity geladen.", {"path": str(candidate), "hash": self.identity_hash(canonical)})
                return canonical
            except (OSError, ValueError, IdentityValidationError) as exc:
                self.logger.error("Canonical Identity aus %s ungültig: %s", candidate, exc)
        canonical = json.loads(json.dumps(self.DEFAULT_DATA, ensure_ascii=False))
        self.validate(canonical)
        self.path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._write_legacy_view(canonical)
        self._write_history_event({"timestamp": self._now(), "actor": "system", "change": "initialize", "hash": self.identity_hash(canonical), "result": "created"})
        self._notify("initialize", "Canonical Identity initialisiert.", {"path": str(self.path), "hash": self.identity_hash(canonical)})
        return canonical

    def can_handle(self, text: str) -> bool:
        value = (text or "").casefold()
        return (
            bool(re.search(r"(?im)^\s*(identity|creator|preferred_address|assistant|role|roles)\s*:", text or ""))
            or all(marker in value for marker in ("creator:", "user:", "assistant:"))
        )

    def save_from_text(self, text: str, actor: str = "system") -> dict:
        incoming = self._parse_identity_payload(text)
        return self.save(incoming, actor=actor, change="structured_identity_payload")

    def save(self, incoming: dict, actor: str = "system", change: str = "identity.update") -> dict:
        current = self.data or self.load()
        old_hash = self.identity_hash(current)
        merged = self._deep_merge(current, self._extract_payload(incoming))
        self.validate(merged)
        archive = self._archive_current(current)
        new_hash = self.identity_hash(merged)
        self.path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._write_legacy_view(merged)
        self.data = merged
        event = {
            "timestamp": self._now(),
            "actor": actor,
            "change": change,
            "old_values": current,
            "new_values": merged,
            "old_hash": old_hash,
            "hash": new_hash,
            "history_file": str(archive) if archive else "",
            "result": "stored",
        }
        self._write_history_event(event)
        self._record_governance(event)
        self._notify("save", "Canonical Identity gespeichert.", event)
        return {"ok": True, "path": str(self.path), "backup": str(archive) if archive else "", "hash": new_hash, "identity": self._legacy_payload(merged)["identity"]}

    def validate(self, data: dict | None = None) -> bool:
        value = data or self.data
        if not isinstance(value, dict):
            raise IdentityValidationError("Canonical Identity muss ein JSON-Objekt sein.")
        if value.get("schema_version") != "1.0":
            raise IdentityValidationError("schema_version 1.0 fehlt.")
        for section in ("creator", "user", "assistant", "roles"):
            if not isinstance(value.get(section), dict):
                raise IdentityValidationError(f"Abschnitt {section} fehlt oder ist ungültig.")
        creator = value["creator"]
        assistant = value["assistant"]
        if not creator.get("id") or not creator.get("name"):
            raise IdentityValidationError("Creator benötigt id und name.")
        if not assistant.get("name") or not assistant.get("short_name"):
            raise IdentityValidationError("Assistant benötigt name und short_name.")
        ids = [str(creator["id"])]
        if len(ids) != len(set(ids)):
            raise IdentityValidationError("Identitäts-IDs müssen eindeutig sein.")
        for owner, roles in value.get("roles", {}).items():
            if not isinstance(roles, list) or not roles:
                raise IdentityValidationError(f"Rollen für {owner} müssen eine nichtleere Liste sein.")
            invalid = [role for role in roles if role not in self.VALID_ROLES]
            if invalid:
                raise IdentityValidationError(f"Ungültige Rollen für {owner}: {', '.join(invalid)}")
        return True

    def get_creator(self) -> dict:
        return dict(self.data.get("creator", {}))

    def get_creator_name(self) -> str:
        return str(self.get_creator().get("name", ""))

    def get_user(self) -> dict:
        return dict(self.data.get("user", {}))

    def get_preferred_address(self) -> str:
        return str(self.get_user().get("preferred_address", ""))

    def get_assistant(self) -> dict:
        return dict(self.data.get("assistant", {}))

    def get_roles(self, identity: str | None = None):
        roles = self.data.get("roles", {})
        return list(roles.get(identity, [])) if identity else json.loads(json.dumps(roles, ensure_ascii=False))

    def has_role(self, identity: str, role: str) -> bool:
        return role in self.get_roles(identity)

    def is_creator(self, identity_id_or_name: str = "") -> bool:
        creator = self.get_creator()
        value = (identity_id_or_name or creator.get("id") or "").casefold()
        return value in {str(creator.get("id", "")).casefold(), str(creator.get("name", "")).casefold(), "creator"}

    def is_super_admin(self, identity: str = "creator") -> bool:
        return self.has_role(identity, "super_admin")

    def memory_view(self) -> dict:
        return {
            "creator": self.get_creator(),
            "user": self.get_user(),
            "assistant": self.get_assistant(),
            "roles": self.get_roles(),
            "path": str(self.path),
            "hash": self.identity_hash(self.data),
        }

    def status(self) -> dict:
        self.validate(self.data)
        return {
            "version": self.VERSION,
            "creator": self.get_creator_name(),
            "preferred_address": self.get_preferred_address(),
            "assistant_name": self.get_assistant().get("name", "Kontinuum"),
            "short_name": self.get_assistant().get("short_name", "K"),
            "path": str(self.path),
            "legacy_path": str(self.legacy_path),
            "last_modified": self._last_modified(self.path),
            "history": str(self.history_dir),
            "hash": self.identity_hash(self.data),
            "valid": True,
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Canonical Identity Manager 1.0 Status:",
            f"- Creator: {status['creator']}",
            f"- bevorzugte Anrede: {status['preferred_address']}",
            f"- Assistant-Name: {status['assistant_name']}",
            f"- Short Name: {status['short_name']}",
            f"- Speicherpfad: {status['path']}",
            f"- letzter Änderungszeitpunkt: {status['last_modified']}",
            f"- Hash: {status['hash']}",
        ])

    def to_legacy_identity(self) -> dict:
        return {
            "name": self.get_assistant().get("name", "Kontinuum"),
            "creator": self.get_creator_name() or "Raphael Schatz",
            "core_process": "Erkennen - Schaffen - Vollenden",
            "guiding_philosophy": "Der Weg ist das Ziel",
            "address_user_as": self.get_preferred_address() or "Raphael",
        }

    @staticmethod
    def identity_hash(data: dict) -> str:
        payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _normalize_payload(self, payload: dict) -> dict:
        base = json.loads(json.dumps(self.DEFAULT_DATA, ensure_ascii=False))
        return self._deep_merge(base, self._extract_payload(payload))

    def _extract_payload(self, payload: dict) -> dict:
        if "identity" in payload and isinstance(payload["identity"], dict):
            payload = payload["identity"]
        mapped = {}
        for key in ("creator", "user", "assistant", "roles", "permissions", "system_identity", "identity_versions"):
            if key in payload:
                mapped[key] = payload[key]
        if "preferred_address" in payload:
            mapped.setdefault("user", {})["preferred_address"] = payload["preferred_address"]
        return mapped

    def _parse_identity_payload(self, text: str) -> dict:
        stripped = (text or "").strip()
        if stripped.startswith("{"):
            return json.loads(stripped)
        return self._simple_yaml(stripped)

    def _archive_current(self, current: dict) -> Path | None:
        if not current:
            return None
        self.history_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive = self.history_dir / f"canonical_identity_{stamp}.json"
        archive.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return archive

    def _write_history_event(self, event: dict) -> None:
        self.history_dir.mkdir(parents=True, exist_ok=True)
        with (self.history_dir / "canonical_identity_governance.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def _record_governance(self, event: dict) -> None:
        if self.storage:
            self.storage.add("audit_events", "canonical_identity.change", event.get("change", ""), event)

    def _notify(self, kind: str, content: str, metadata: dict) -> None:
        if self.storage:
            self.storage.add("foundation_memory", f"canonical_identity.{kind}", content, {"cim": self.VERSION, **metadata})

    def _write_legacy_view(self, data: dict) -> None:
        self.legacy_path.write_text(json.dumps(self._legacy_payload(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _legacy_payload(data: dict) -> dict:
        return {
            "identity": {
                "creator": data.get("creator", {}),
                "user": data.get("user", {}),
                "assistant": data.get("assistant", {}),
            }
        }

    @staticmethod
    def _simple_yaml(text: str) -> dict:
        root: dict = {}
        stack: list[tuple[int, dict]] = [(-1, root)]
        for raw_line in (text or "").splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            line = raw_line.strip()
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().strip("\"'")
            value = value.strip().strip("\"'")
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            if value:
                parent[key] = value
            else:
                child: dict = {}
                parent[key] = child
                stack.append((indent, child))
        return root

    @classmethod
    def _deep_merge(cls, base: dict, incoming: dict) -> dict:
        merged = json.loads(json.dumps(base, ensure_ascii=False))
        for key, value in incoming.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = cls._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    @staticmethod
    def _last_modified(path: Path) -> str:
        if not path.exists():
            return "nicht gespeichert"
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
