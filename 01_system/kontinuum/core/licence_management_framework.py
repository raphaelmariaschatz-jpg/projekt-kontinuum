# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LicenceDeclarationReview:
    review_id: str
    licence_id: str
    licence_type: str
    lifecycle_status: str
    licence_assurance_level: str
    checked_at: str
    structurally_valid: bool
    findings: list[str]
    validation_dimensions: list[str]
    enforcement_performed: bool = False
    licence_issued: bool = False
    authorization_granted: bool = False
    authentication_performed: bool = False
    legal_decision_made: bool = False
    registry_mutated: bool = False
    direct_memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalLicenceManagementSystemFramework:
    """Structural licence declaration review without rights or enforcement."""

    VERSION = "1.0"
    CONFIG_RELATIVE = Path(
        "24_config/canonical_licence_management_system_framework_1_0.json"
    )
    SECRET_KEYS = frozenset(
        {
            "password",
            "password_hash",
            "recovery_key",
            "token",
            "access_token",
            "secret",
            "secret_key",
            "private_key",
            "payment_card",
        }
    )

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self._resolve_config_path()
        self._config = self._read_json(self.config_path)
        self._validate_config()
        identity = self._config["licence_identity"]
        self._required_fields = list(identity["required_fields"])
        self._licence_types = set(identity["starter_licence_types"])
        self._subject_types = set(identity["licensed_subject_types"])
        self._statuses = list(self._config["lifecycle_statuses"])
        self._assurance_levels = list(self._config["licence_assurance_levels"])
        self._dimensions = list(self._config["validation_dimensions"])

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Licence Management System Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_structural_declaration_review_only",
            "required_fields": len(self._required_fields),
            "starter_licence_types": len(self._licence_types),
            "lifecycle_statuses": len(self._statuses),
            "licence_assurance_levels": len(self._assurance_levels),
            "licence_enforcement": False,
            "licence_issuance": False,
            "authorization": False,
            "authentication": False,
            "legal_decision": False,
            "registry_mutation": False,
            "direct_memory_write": False,
        }

    def list_lifecycle_statuses(self) -> list[str]:
        return list(self._statuses)

    def list_policy_groups(self) -> list[str]:
        return list(self._config["policy_groups"])

    def review_declaration(
        self,
        *,
        declaration: dict[str, Any],
        checked_at: str,
        licence_assurance_level: str,
    ) -> LicenceDeclarationReview:
        if not isinstance(declaration, dict):
            raise ValueError("CLMSF declaration must be an object")
        checked_time = self._parse_time(checked_at, "checked_at")
        assurance = (licence_assurance_level or "").strip().upper()
        if assurance not in self._assurance_levels:
            raise ValueError(f"Unknown CLMSF licence assurance level: {licence_assurance_level}")

        findings: list[str] = []
        missing = sorted(set(self._required_fields) - set(declaration))
        if missing:
            findings.append("missing_fields:" + ",".join(missing))
        secret_path = self._find_secret_path(declaration)
        if secret_path:
            findings.append("forbidden_secret_field:" + secret_path)

        licence_id = str(declaration.get("licence_id") or "").strip().upper()
        licence_type = str(declaration.get("licence_type") or "").strip().upper()
        lifecycle_status = str(declaration.get("status") or "").strip().upper()
        if not licence_id.startswith("LIC-"):
            findings.append("invalid_licence_id")
        if licence_type not in self._licence_types:
            findings.append("unregistered_licence_type")
        if lifecycle_status not in self._statuses:
            findings.append("invalid_lifecycle_status")
        if str(declaration.get("schema_version") or "") != self.VERSION:
            findings.append("schema_version_mismatch")

        subject = declaration.get("licensed_subject")
        if not isinstance(subject, dict):
            findings.append("licensed_subject_must_be_object")
        else:
            subject_type = str(subject.get("subject_type") or "").strip().upper()
            subject_id = str(subject.get("subject_id") or "").strip()
            if subject_type not in self._subject_types:
                findings.append("invalid_licensed_subject_type")
            if not subject_id:
                findings.append("missing_licensed_subject_id")
        if not isinstance(declaration.get("scope"), list):
            findings.append("scope_must_be_array")
        if not isinstance(declaration.get("constraints"), list):
            findings.append("constraints_must_be_array")
        if not isinstance(declaration.get("provenance"), dict):
            findings.append("provenance_must_be_object")
        if not isinstance(declaration.get("integrity"), dict):
            findings.append("integrity_must_be_object")

        valid_from = self._try_parse_time(declaration.get("valid_from"), "valid_from", findings)
        valid_until = self._try_parse_time(declaration.get("valid_until"), "valid_until", findings)
        if valid_from and valid_until and valid_until <= valid_from:
            findings.append("invalid_validity_window")
        if lifecycle_status in {"ACTIVE", "REINSTATED", "EXPIRING"}:
            if valid_from and checked_time < valid_from:
                findings.append("not_yet_valid_at_check_time")
            if valid_until and checked_time >= valid_until:
                findings.append("expired_at_check_time")

        normalized_findings = list(dict.fromkeys(findings))
        payload = {
            "licence_id": licence_id,
            "licence_type": licence_type,
            "lifecycle_status": lifecycle_status,
            "licence_assurance_level": assurance,
            "checked_at": self._format_time(checked_time),
            "structurally_valid": not normalized_findings,
            "findings": normalized_findings,
            "validation_dimensions": list(self._dimensions),
        }
        review_payload = {
            "review": payload,
            "framework_version": self.VERSION,
        }
        review_id = "CLMSF-REVIEW-" + sha256(
            json.dumps(review_payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return LicenceDeclarationReview(review_id=review_id, **payload)

    def _validate_config(self) -> None:
        information = self._config.get("framework_information", {})
        if information.get("version") != self.VERSION or information.get("abbreviation") != "CLMSF":
            raise ValueError("CLMSF framework identity must be CLMSF 1.0")
        identity = self._config.get("licence_identity", {})
        if len(identity.get("required_fields", [])) != 17:
            raise ValueError("CLMSF licence identity must define seventeen required fields")
        if len(identity.get("starter_licence_types", [])) != 6:
            raise ValueError("CLMSF must define six starter licence types")
        expected_statuses = [
            "DRAFT",
            "PROPOSED",
            "APPROVED",
            "ACTIVE",
            "SUSPENDED",
            "REINSTATED",
            "EXPIRING",
            "EXPIRED",
            "REVOKED",
            "ARCHIVED",
        ]
        if self._config.get("lifecycle_statuses") != expected_statuses:
            raise ValueError("CLMSF lifecycle statuses do not match the 1.0 contract")
        if self._config.get("licence_assurance_levels") != [
            "LOW",
            "MEDIUM",
            "HIGH",
            "CANONICAL",
        ]:
            raise ValueError("CLMSF licence assurance levels do not match the 1.0 contract")
        if len(self._config.get("validation_dimensions", [])) != 8:
            raise ValueError("CLMSF must define eight validation dimensions")
        if len(self._config.get("policy_groups", [])) != 9:
            raise ValueError("CLMSF must define nine policy groups")

    def _try_parse_time(
        self,
        value: Any,
        field: str,
        findings: list[str],
    ) -> datetime | None:
        try:
            return self._parse_time(str(value or ""), field)
        except ValueError:
            findings.append(f"invalid_{field}")
            return None

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
            raise ValueError(f"CLMSF {field} must be an ISO-8601 timestamp") from exc
        if parsed.tzinfo is None:
            raise ValueError(f"CLMSF {field} must include a timezone")
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
        raise FileNotFoundError(f"CLMSF configuration not found: {self.CONFIG_RELATIVE}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy(value: Any) -> Any:
        return json.loads(json.dumps(value, ensure_ascii=True))
