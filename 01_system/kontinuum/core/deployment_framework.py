# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DeploymentProfileValidation:
    validation_id: str
    profile_id: str
    valid: bool
    errors: list[str]
    required_validations: list[str]
    enabled_optional_framework_ids: list[str]
    license_profile: str
    resource_profile: str
    integration_profile: str
    deployment_performed: bool = False
    configuration_mutated: bool = False
    source_fork_created: bool = False
    decision_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalDeploymentFramework:
    """Read-only deployment-profile validation without deployment execution."""

    VERSION = "1.0"
    FRAMEWORK_CONFIG = Path("24_config/canonical_deployment_framework_1_0.json")
    PROFILE_CONFIG = Path("24_config/deployment_profiles_1_0.json")

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.framework_path = self._resolve_config_path(self.FRAMEWORK_CONFIG)
        self.profile_path = self._resolve_config_path(self.PROFILE_CONFIG)
        self._framework = self._read_json(self.framework_path)
        self._profile_data = self._read_json(self.profile_path)
        self._validate_configs()
        self._core = list(self._framework["canonical_core"])
        self._optional = list(self._framework["optional_frameworks"])
        self._profiles = list(self._profile_data["profiles"])
        self._core_ids = {item["id"] for item in self._core}
        self._optional_by_id = {item["id"]: item for item in self._optional}
        self._profiles_by_id = {item["id"]: item for item in self._profiles}

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Deployment Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "read_only_profile_validation_only",
            "canonical_core_entries": len(self._core),
            "deployment_profiles": len(self._profiles),
            "optional_frameworks": len(self._optional),
            "deployment_execution": False,
            "configuration_mutation": False,
            "source_forks": False,
            "license_enforcement": False,
            "decision_authority": False,
            "direct_memory_write": False,
        }

    def list_profiles(self) -> list[dict[str, Any]]:
        return self._copy(self._profiles)

    def list_canonical_core(self) -> list[dict[str, Any]]:
        return self._copy(self._core)

    def validate_profile(
        self,
        *,
        profile_id: str,
        enabled_optional_framework_ids: list[str] | None = None,
        disabled_core_ids: list[str] | None = None,
        license_profile: str = "",
    ) -> DeploymentProfileValidation:
        normalized_profile = (profile_id or "").strip().upper()
        if normalized_profile not in self._profiles_by_id:
            raise ValueError(f"Unknown CDFX deployment profile: {profile_id}")
        profile = self._profiles_by_id[normalized_profile]
        optional_ids = self._normalize_ids(enabled_optional_framework_ids)
        disabled_ids = self._normalize_ids(disabled_core_ids)
        normalized_license = (license_profile or profile["license_profile"]).strip()
        errors: list[str] = []

        unknown_optional = sorted(set(optional_ids) - set(self._optional_by_id))
        if unknown_optional:
            errors.append("unknown_optional_frameworks:" + ",".join(unknown_optional))
        unknown_core = sorted(set(disabled_ids) - self._core_ids)
        if unknown_core:
            errors.append("unknown_core_components:" + ",".join(unknown_core))
        protected_core = sorted(set(disabled_ids) & self._core_ids)
        if protected_core:
            errors.append("canonical_core_disable_forbidden:" + ",".join(protected_core))

        profile_key = self._profile_key(normalized_profile)
        for optional_id in optional_ids:
            item = self._optional_by_id.get(optional_id)
            if item is None:
                continue
            allowed = {str(value).casefold() for value in item["allowed_profiles"]}
            if profile_key not in allowed and f"{profile_key}_optional" not in allowed:
                errors.append(f"framework_not_allowed:{optional_id}:{profile_key}")
        if normalized_license != profile["license_profile"]:
            errors.append("license_profile_mismatch")

        payload = {
            "profile_id": normalized_profile,
            "valid": not errors,
            "errors": errors,
            "required_validations": list(profile["required_validations"]),
            "enabled_optional_framework_ids": optional_ids,
            "license_profile": normalized_license,
            "resource_profile": profile["resource_profile"],
            "integration_profile": profile["integration_profile"],
        }
        validation_id = "CDFX-VAL-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return DeploymentProfileValidation(validation_id=validation_id, **payload)

    def _validate_configs(self) -> None:
        information = self._framework.get("framework_information", {})
        if information.get("version") != self.VERSION or information.get("abbreviation") != "CDFX":
            raise ValueError("CDFX framework identity must be CDFX 1.0")
        core = self._framework.get("canonical_core")
        optional = self._framework.get("optional_frameworks")
        if not isinstance(core, list) or len(core) != 16:
            raise ValueError("CDFX must define exactly sixteen canonical core entries")
        if [item.get("id") for item in core] != [f"CDFX-CORE-{index:03d}" for index in range(1, 17)]:
            raise ValueError("CDFX canonical core ids must be ordered")
        if not all(item.get("core_required") is True for item in core):
            raise ValueError("Every CDFX canonical core entry must be required")
        if not isinstance(optional, list) or [item.get("id") for item in optional] != [
            f"CDFX-OPT-{index:03d}" for index in range(1, 9)
        ]:
            raise ValueError("CDFX optional framework ids must be ordered")

        collection = self._profile_data.get("profile_collection", {})
        profiles = self._profile_data.get("profiles")
        if collection.get("framework") != "CDFX" or collection.get("version") != self.VERSION:
            raise ValueError("CDFX profile collection identity must be CDFX 1.0")
        expected_profiles = [
            "CDFX-PROFILE-PERSONAL-1-0",
            "CDFX-PROFILE-ENTERPRISE-1-0",
            "CDFX-PROFILE-RESEARCH-1-0",
        ]
        if not isinstance(profiles, list) or [item.get("id") for item in profiles] != expected_profiles:
            raise ValueError("CDFX must define the three ordered canonical profiles")
        for profile in profiles:
            policy = profile.get("core_policy", {})
            if policy.get("may_disable_canonical_core") is not False:
                raise ValueError("CDFX profiles must never disable the canonical core")
            if policy.get("profile_inheritance_allowed") is not False:
                raise ValueError("CDFX 1.0 profile inheritance must remain disabled")

    @staticmethod
    def _profile_key(profile_id: str) -> str:
        return profile_id.removeprefix("CDFX-PROFILE-").removesuffix("-1-0").casefold()

    @staticmethod
    def _normalize_ids(values: list[str] | None) -> list[str]:
        return list(
            dict.fromkeys(
                text.strip().upper()
                for value in (values or [])
                if (text := str(value)).strip()
            )
        )

    def _resolve_config_path(self, relative_path: Path) -> Path:
        primary = self.project_root / relative_path
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / relative_path
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CDFX configuration not found: {relative_path}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy(value: Any) -> Any:
        return json.loads(json.dumps(value, ensure_ascii=True))
