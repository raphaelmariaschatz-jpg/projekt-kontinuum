# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CanonicalAuthenticationObservation:
    authentication_event_id: str
    identity_id: str
    identity_type: str
    authentication_method_id: str
    method_class: str
    assurance_level: str
    authenticated_at: str
    valid_until: str
    session_id: str
    security_context: dict[str, Any]
    device_context: dict[str, Any]
    origin: dict[str, Any]
    result: str
    failure_reason_code: str
    policy_version: str
    framework_version: str
    audit_reference: str
    schema_version: str
    issuer_attested: bool = False
    authentication_performed: bool = False
    authorization_usable: bool = False
    secret_material_present: bool = False
    direct_memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalAuthenticationFramework:
    """Non-authoritative CAF observation contract without authentication."""

    VERSION = "1.0"
    CONFIG_RELATIVE = Path("24_config/canonical_authentication_framework_1_0.json")
    RESULTS = frozenset({"success", "failure"})
    SECRET_KEYS = frozenset(
        {
            "password",
            "password_hash",
            "recovery_key",
            "recovery_code",
            "token",
            "access_token",
            "refresh_token",
            "secret",
            "secret_key",
            "private_key",
        }
    )

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self._resolve_config_path()
        self._config = self._read_json(self.config_path)
        self._validate_config()
        self._identity_types = set(self._config["identity_model"]["identity_types"])
        self._methods = {
            item["method_class"]: item for item in self._config["authentication_methods"]
        }
        self._assurance_ids = [item["id"] for item in self._config["assurance_levels"]]

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Authentication Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "non_authoritative_observation_contract_only",
            "identity_types": len(self._identity_types),
            "authentication_methods": len(self._methods),
            "assurance_levels": len(self._assurance_ids),
            "login_replacement": False,
            "authentication_execution": False,
            "session_creation": False,
            "authorization": False,
            "credential_storage": False,
            "direct_memory_write": False,
        }

    def list_identity_types(self) -> list[str]:
        return list(self._config["identity_model"]["identity_types"])

    def list_authentication_methods(self) -> list[dict[str, Any]]:
        return self._copy(self._config["authentication_methods"])

    def build_observation(
        self,
        *,
        identity_id: str,
        identity_type: str,
        authentication_method_id: str,
        method_class: str,
        assurance_level: str,
        authenticated_at: str,
        valid_until: str,
        session_id: str,
        security_context: dict[str, Any],
        device_context: dict[str, Any],
        origin: dict[str, Any],
        result: str,
        failure_reason_code: str = "",
        policy_version: str = "unattested",
        audit_reference: str = "",
    ) -> CanonicalAuthenticationObservation:
        normalized_identity_id = (identity_id or "").strip()
        normalized_identity_type = (identity_type or "").strip().upper()
        normalized_method_id = (authentication_method_id or "").strip()
        normalized_method_class = (method_class or "").strip().upper()
        normalized_assurance = (assurance_level or "").strip().upper()
        normalized_session = (session_id or "").strip()
        normalized_result = (result or "").strip().casefold()
        if not normalized_identity_id or not normalized_method_id or not normalized_session:
            raise ValueError("CAF identity, method and session identifiers must not be empty")
        if normalized_identity_type not in self._identity_types:
            raise ValueError(f"Unknown CAF identity type: {identity_type}")
        if normalized_method_class not in self._methods:
            raise ValueError(f"Unknown CAF authentication method class: {method_class}")
        if normalized_assurance not in self._assurance_ids:
            raise ValueError(f"Unknown CAF assurance level: {assurance_level}")
        if normalized_result not in self.RESULTS:
            raise ValueError(f"Unknown CAF reported result: {result}")
        if normalized_result == "failure" and not (failure_reason_code or "").strip():
            raise ValueError("CAF failure observations require a reason code")
        if normalized_result == "success" and (failure_reason_code or "").strip():
            raise ValueError("CAF success observations must not include a failure reason")
        if self._assurance_rank(normalized_assurance) < self._assurance_rank(
            self._methods[normalized_method_class]["minimum_assurance_level"]
        ):
            raise ValueError("CAF assurance level is below the method minimum")

        authenticated_time = self._parse_time(authenticated_at, "authenticated_at")
        valid_until_time = self._parse_time(valid_until, "valid_until")
        if valid_until_time <= authenticated_time:
            raise ValueError("CAF valid_until must be after authenticated_at")
        contexts = {
            "security_context": security_context,
            "device_context": device_context,
            "origin": origin,
        }
        if any(not isinstance(value, dict) for value in contexts.values()):
            raise ValueError("CAF context and origin values must be objects")
        secret_path = self._find_secret_path(contexts)
        if secret_path:
            raise ValueError(f"CAF observation contains forbidden secret field: {secret_path}")

        payload = {
            "identity_id": normalized_identity_id,
            "identity_type": normalized_identity_type,
            "authentication_method_id": normalized_method_id,
            "method_class": normalized_method_class,
            "assurance_level": normalized_assurance,
            "authenticated_at": self._format_time(authenticated_time),
            "valid_until": self._format_time(valid_until_time),
            "session_id": normalized_session,
            "security_context": self._copy(security_context),
            "device_context": self._copy(device_context),
            "origin": self._copy(origin),
            "result": normalized_result,
            "failure_reason_code": (failure_reason_code or "").strip().upper(),
            "policy_version": (policy_version or "unattested").strip(),
            "framework_version": self.VERSION,
            "audit_reference": (audit_reference or "").strip(),
            "schema_version": self.VERSION,
        }
        event_id = "CAF-OBS-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return CanonicalAuthenticationObservation(
            authentication_event_id=event_id,
            **payload,
        )

    def _validate_config(self) -> None:
        information = self._config.get("framework_information", {})
        if information.get("version") != self.VERSION or information.get("abbreviation") != "CAF":
            raise ValueError("CAF framework identity must be CAF 1.0")
        identity_types = self._config.get("identity_model", {}).get("identity_types")
        if not isinstance(identity_types, list) or len(identity_types) != 10:
            raise ValueError("CAF must define exactly ten identity types")
        methods = self._config.get("authentication_methods")
        if not isinstance(methods, list) or len(methods) != 8:
            raise ValueError("CAF must define exactly eight authentication method classes")
        assurance = self._config.get("assurance_levels")
        if not isinstance(assurance, list) or [item.get("id") for item in assurance] != [
            f"AAL-{index}" for index in range(5)
        ]:
            raise ValueError("CAF assurance levels must be ordered from AAL-0 to AAL-4")
        expected_fields = [
            "authentication_event_id",
            "identity_id",
            "identity_type",
            "authentication_method_id",
            "assurance_level",
            "authenticated_at",
            "valid_until",
            "session_id",
            "security_context",
            "device_context",
            "origin",
            "result",
            "failure_reason_code",
            "policy_version",
            "framework_version",
            "audit_reference",
            "schema_version",
        ]
        if self._config.get("canonical_authentication_result_fields") != expected_fields:
            raise ValueError("CAF canonical result fields do not match the 1.0 contract")

    def _assurance_rank(self, assurance_level: str) -> int:
        try:
            return self._assurance_ids.index(assurance_level)
        except ValueError as exc:
            raise ValueError(f"Unknown CAF assurance level: {assurance_level}") from exc

    @classmethod
    def _find_secret_path(cls, value: Any, prefix: str = "") -> str:
        if isinstance(value, dict):
            for key, item in value.items():
                normalized = str(key).strip().casefold()
                path = f"{prefix}.{key}" if prefix else str(key)
                if normalized in cls.SECRET_KEYS:
                    return path
                found = cls._find_secret_path(item, path)
                if found:
                    return found
        elif isinstance(value, list):
            for index, item in enumerate(value):
                found = cls._find_secret_path(item, f"{prefix}[{index}]")
                if found:
                    return found
        return ""

    @staticmethod
    def _parse_time(value: str, field: str) -> datetime:
        normalized = (value or "").strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"CAF {field} must be an ISO-8601 timestamp") from exc
        if parsed.tzinfo is None:
            raise ValueError(f"CAF {field} must include a timezone")
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _format_time(value: datetime) -> str:
        return value.isoformat().replace("+00:00", "Z")

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CAF configuration not found: {self.CONFIG_RELATIVE}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy(value: Any) -> Any:
        return json.loads(json.dumps(value, ensure_ascii=True))
