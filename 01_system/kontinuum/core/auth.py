# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .password_security import PasswordSecurity


class AuthenticationError(RuntimeError):
    pass


class AuthManager:
    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
        self.auth_file = self.project_root / "32_data" / "auth_config.json"
        self.master_file = self.project_root / "10_security" / "auth_security_master.json"
        self.audit_file = self.project_root / "27_logs" / "auth_audit.log"
        self.password_security = PasswordSecurity()

    def status(self) -> dict:
        try:
            active = self._load_active()
            master = self._load_master_user()
        except AuthenticationError as exc:
            return {"configured": False, "message": str(exc)}
        consistent = (
            active.get("username") == master.get("username")
            and active.get("password_hash") == master.get("password_hash")
            and active.get("role") == master.get("role")
        )
        return {
            "configured": True,
            "consistent": consistent,
            "password_scheme": "argon2id" if self.password_security.is_argon2id(str(active.get("password_hash") or "")) else "legacy_sha256",
            "migration_pending": self._is_legacy_sha256(str(active.get("password_hash") or "")),
            "username": active.get("username"),
            "full_name": active.get("full_name"),
            "role": active.get("role"),
            "is_superadmin": bool(active.get("is_superadmin")),
            "message": "Superadmin-Zugang ist gespeichert." if consistent else "Aktive Auth-Daten und Sicherheits-Master widersprechen sich.",
        }

    def verify_login(self, username: str, password: str) -> dict | None:
        try:
            active = self._load_active()
            master = self._load_master_user()
        except AuthenticationError as exc:
            self._audit("login_configuration_error", False, str(exc))
            return None

        normalized_username = (username or "").strip()
        expected_username = str(active.get("username") or "")
        expected_hash = str(active.get("password_hash") or "")
        master_hash = str(master.get("password_hash") or "")
        consistent = hmac.compare_digest(expected_hash, master_hash)
        valid = (
            consistent
            and hmac.compare_digest(normalized_username, expected_username)
            and self._verify_password(expected_hash, password)
        )
        self._audit("login", valid, normalized_username)
        if not valid:
            return None
        if self._is_legacy_sha256(expected_hash) or self.password_security.needs_rehash(expected_hash):
            self._migrate_password(password)
        return {
            "authenticated": True,
            "username": expected_username,
            "full_name": active.get("full_name", expected_username),
            "role": active.get("role", ""),
            "is_superadmin": bool(active.get("is_superadmin")),
            "permissions": active.get("permissions", {}),
        }

    def verify_superadmin_confirmation(self, identity: dict | None, password: str, purpose: str = "") -> bool:
        identity = identity or {}
        username = str(identity.get("username") or "")
        privileged_session = (
            bool(identity.get("authenticated"))
            and bool(identity.get("is_superadmin"))
            and str(identity.get("role") or "").upper() == "SUPERADMIN"
            and bool((identity.get("permissions") or {}).get("can_execute_admin_commands"))
        )
        if not privileged_session:
            self._audit("superadmin_confirmation", False, f"{username} | invalid_session | {purpose}")
            return False
        try:
            active = self._load_active()
            master = self._load_master_user()
        except AuthenticationError as exc:
            self._audit("superadmin_confirmation", False, f"{username} | {exc}")
            return False
        valid = (
            hmac.compare_digest(username, str(active.get("username") or ""))
            and hmac.compare_digest(str(active.get("password_hash") or ""), str(master.get("password_hash") or ""))
            and self._verify_password(str(active.get("password_hash") or ""), password)
        )
        if valid and self._is_legacy_sha256(str(active.get("password_hash") or "")):
            self._migrate_password(password)
        self._audit("superadmin_confirmation", valid, f"{username} | {purpose}")
        return valid

    def _load_active(self) -> dict:
        data = self._read_json(self.auth_file, "Aktive Auth-Datei fehlt oder ist unlesbar.")
        if not self._valid_user(data):
            raise AuthenticationError("Aktive Auth-Datei ist unvollstaendig.")
        return data

    def _load_master_user(self) -> dict:
        data = self._read_json(self.master_file, "Sicherheits-Master fehlt oder ist unlesbar.")
        candidates = [
            item
            for item in data.get("security_entries", [])
            if isinstance(item, dict) and item.get("username") and item.get("password_hash") not in {None, "created_on_first_start"}
        ]
        if not candidates or not self._valid_user(candidates[0]):
            raise AuthenticationError("Kein gueltiger Benutzer im Sicherheits-Master.")
        return candidates[0]

    def _valid_user(self, data: dict) -> bool:
        password_hash = str(data.get("password_hash") or "")
        return bool(data.get("username")) and (
            self.password_security.is_argon2id(password_hash) or self._is_legacy_sha256(password_hash)
        )

    def _verify_password(self, encoded_hash: str, password: str) -> bool:
        if self.password_security.is_argon2id(encoded_hash):
            return self.password_security.verify(encoded_hash, password)
        if self._is_legacy_sha256(encoded_hash):
            supplied_hash = hashlib.sha256((password or "").encode("utf-8")).hexdigest()
            return hmac.compare_digest(supplied_hash, encoded_hash)
        return False

    @staticmethod
    def _is_legacy_sha256(encoded_hash: str) -> bool:
        value = str(encoded_hash or "").casefold()
        return len(value) == 64 and all(character in "0123456789abcdef" for character in value)

    def _migrate_password(self, password: str) -> None:
        active = self._read_json(self.auth_file, "Aktive Auth-Datei fehlt oder ist unlesbar.")
        master = self._read_json(self.master_file, "Sicherheits-Master fehlt oder ist unlesbar.")
        new_hash = self.password_security.hash(password)
        active["password_hash"] = new_hash
        updated = False
        for entry in master.get("security_entries", []):
            if isinstance(entry, dict) and entry.get("username") == active.get("username"):
                entry["password_hash"] = new_hash
                updated = True
        if not updated:
            raise AuthenticationError("Sicherheits-Master enthält den aktiven Benutzer nicht.")
        self._write_json(self.auth_file, active)
        self._write_json(self.master_file, master)
        self._audit("password_hash_migrated", True, str(active.get("username") or ""))

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)

    @staticmethod
    def _read_json(path: Path, error_message: str) -> dict:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        raise AuthenticationError(error_message)

    def _audit(self, event: str, success: bool, detail: str) -> None:
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        safe_detail = (detail or "").replace("\r", " ").replace("\n", " ")[:120]
        line = f"{datetime.now(timezone.utc).isoformat()} | {event} | success={success} | {safe_detail}\n"
        try:
            with self.audit_file.open("a", encoding="utf-8") as handle:
                handle.write(line)
        except OSError:
            pass
