# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CodeAgentTaskReview:
    review_id: str
    task_id: str
    structurally_valid: bool
    violations: list[str]
    gate_results: list[dict[str, Any]]
    requested_role: str
    requested_permission_profile: str
    requested_operating_mode: str
    risk_class: str
    execution_authorized: bool = False
    final_approval_granted: bool = False
    task_executed: bool = False
    agent_runtime_activated: bool = False
    autonomous_write_enabled: bool = False
    direct_memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalCodeAgentFramework:
    """CODEAF task-contract review without execution or self-approval."""

    VERSION = "1.0"
    CONFIG_RELATIVE = Path("24_config/canonical_code_agent_framework_1_0.json")
    MUTATING_CAPABILITIES = frozenset(
        {
            "code.create",
            "code.modify",
            "code.delete",
            "code.move",
            "code.archive",
            "config.modify",
            "schema.modify",
            "tests.create",
            "tests.execute",
            "tests.evaluate",
            "git.branch",
            "git.stage",
            "git.commit",
            "git.reset",
            "database.write",
            "database.migrate",
            "documentation.update",
            "architecture.modify",
            "security.audit",
            "release.prepare",
            "audit.write",
            "provenance.write",
        }
    )

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self._resolve_config_path()
        self._config = self._read_json(self.config_path)
        self._validate_config()
        self._roles = set(self._config["roles"])
        self._capabilities = set(self._config["capabilities"])
        self._critical = set(self._config["critical_capabilities"])
        self._profiles = {
            item["id"]: item for item in self._config["permission_profiles"]
        }
        self._modes = set(self._config["operating_modes"])
        self._inactive_modes = set(self._config["inactive_operating_modes"])
        self._risks = set(self._config["risk_classes"])
        self._gates = list(self._config["control_gates"])
        self._required_fields = list(self._config["canonical_task_required_fields"])
        self._task_statuses = set(self._config["task_statuses"])

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Code Agent Framework",
            "abbreviation": "CODEAF",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_task_contract_validation_only",
            "roles": len(self._roles),
            "capabilities": len(self._capabilities),
            "permission_profiles": len(self._profiles),
            "risk_classes": len(self._risks),
            "control_gates": len(self._gates),
            "agent_runtime_activation": False,
            "execution_authority": False,
            "autonomous_write": False,
            "self_approval": False,
            "existing_code_agent_changed": False,
            "direct_memory_write": False,
        }

    def list_roles(self) -> list[str]:
        return list(self._config["roles"])

    def list_capabilities(self) -> list[str]:
        return list(self._config["capabilities"])

    def review_task(self, task: dict[str, Any]) -> CodeAgentTaskReview:
        if not isinstance(task, dict):
            raise ValueError("CODEAF task must be an object")
        violations: list[str] = []
        missing = sorted(set(self._required_fields) - set(task))
        if missing:
            violations.append("missing_fields:" + ",".join(missing))

        task_id = str(task.get("task_id") or "").strip()
        role = str(task.get("agent_role") or "").strip().upper()
        permission_profile = str(task.get("permission_profile") or "").strip().upper()
        operating_mode = str(task.get("operating_mode") or "").strip().upper()
        risk_class = str(task.get("risk_class") or "").strip().upper()
        status = str(task.get("status") or "").strip().upper()
        requested_capabilities = self._normalize_capabilities(task.get("allowed_capabilities"))

        if not task_id:
            violations.append("missing_task_id")
        if role not in self._roles:
            violations.append("unknown_role")
        if permission_profile not in self._profiles:
            violations.append("unknown_permission_profile")
        if operating_mode not in self._modes:
            violations.append("unknown_operating_mode")
        elif operating_mode in self._inactive_modes:
            violations.append("inactive_operating_mode")
        if risk_class not in self._risks:
            violations.append("unknown_risk_class")
        if status not in self._task_statuses:
            violations.append("unknown_task_status")

        unknown_capabilities = sorted(set(requested_capabilities) - self._capabilities)
        if unknown_capabilities:
            violations.append("unknown_capabilities:" + ",".join(unknown_capabilities))
        profile = self._profiles.get(permission_profile)
        if profile is not None:
            allowed = set(profile["allowed_capabilities"])
            denied = set(profile["denied_capabilities"])
            denied_requests = sorted(set(requested_capabilities) & denied)
            outside_profile = sorted(set(requested_capabilities) - allowed)
            if denied_requests:
                violations.append("explicitly_denied_capabilities:" + ",".join(denied_requests))
            if outside_profile:
                violations.append("capabilities_outside_profile:" + ",".join(outside_profile))

        if operating_mode in {"READ_ONLY", "PROPOSAL"}:
            write_or_admin = sorted(
                capability
                for capability in requested_capabilities
                if capability in self.MUTATING_CAPABILITIES
            )
            if write_or_admin:
                violations.append("mode_forbids_capabilities:" + ",".join(write_or_admin))
        if operating_mode in {"CONTROLLED_WRITE", "MIGRATION", "EMERGENCY_REPAIR"}:
            if not str(task.get("rollback_point") or "").strip():
                violations.append("write_mode_requires_rollback_point")
            if not self._nonempty(task.get("approval_process")):
                violations.append("write_mode_requires_approval_process")
        if risk_class == "CODEAF-R5":
            violations.append("risk_r5_not_productively_automatable")

        normalized_violations = list(dict.fromkeys(violations))
        gate_results = self._gate_results(
            task=task,
            role=role,
            permission_profile=permission_profile,
            operating_mode=operating_mode,
            risk_class=risk_class,
            requested_capabilities=requested_capabilities,
            violations=normalized_violations,
        )
        payload = {
            "task_id": task_id,
            "structurally_valid": not normalized_violations,
            "violations": normalized_violations,
            "gate_results": gate_results,
            "requested_role": role,
            "requested_permission_profile": permission_profile,
            "requested_operating_mode": operating_mode,
            "risk_class": risk_class,
        }
        review_id = "CODEAF-REVIEW-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return CodeAgentTaskReview(review_id=review_id, **payload)

    def _gate_results(
        self,
        *,
        task: dict[str, Any],
        role: str,
        permission_profile: str,
        operating_mode: str,
        risk_class: str,
        requested_capabilities: list[str],
        violations: list[str],
    ) -> list[dict[str, Any]]:
        identity = task.get("agent_identity")
        identity_ok = isinstance(identity, dict) and all(
            str(identity.get(field) or "").strip()
            for field in ("agent_id", "agent_run_id")
        )
        checks = {
            "IDENTITY_GATE": identity_ok,
            "TASK_GATE": bool(str(task.get("task_id") or "").strip()) and not any(
                item.startswith("missing_fields:") for item in violations
            ),
            "ROLE_GATE": role in self._roles,
            "CAPABILITY_GATE": bool(requested_capabilities)
            and set(requested_capabilities).issubset(self._capabilities),
            "PERMISSION_GATE": permission_profile in self._profiles
            and not any(
                item.startswith("explicitly_denied_capabilities:")
                or item.startswith("capabilities_outside_profile:")
                or item.startswith("mode_forbids_capabilities:")
                for item in violations
            ),
            "RISK_GATE": risk_class in self._risks and risk_class != "CODEAF-R5",
            "PLAN_GATE": self._nonempty(task.get("planned_workflow")),
            "EXECUTION_GATE": operating_mode in self._modes
            and operating_mode not in self._inactive_modes
            and self._nonempty(task.get("approval_process")),
            "VERIFICATION_GATE": self._nonempty(task.get("test_requirements"))
            and self._nonempty(task.get("documentation_requirements")),
            "FINAL_APPROVAL_GATE": bool(
                str(task.get("final_approval_reference") or "").strip()
            ),
        }
        return [
            {"gate": gate, "passed": bool(checks[gate])}
            for gate in self._gates
        ]

    def _validate_config(self) -> None:
        information = self._config.get("framework_information", {})
        if information.get("version") != self.VERSION or information.get("abbreviation") != "CODEAF":
            raise ValueError("CODEAF framework identity must be CODEAF 1.0")
        if len(self._config.get("roles", [])) != 9:
            raise ValueError("CODEAF must define nine roles")
        capabilities = self._config.get("capabilities")
        if not isinstance(capabilities, list) or len(capabilities) != 41:
            raise ValueError("CODEAF must define forty-one capabilities")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("CODEAF capability ids must be unique")
        if len(self._config.get("permission_profiles", [])) != 3:
            raise ValueError("CODEAF must define three permission profiles")
        if self._config.get("risk_classes") != [f"CODEAF-R{index}" for index in range(6)]:
            raise ValueError("CODEAF risk classes must be ordered from R0 to R5")
        if len(self._config.get("control_gates", [])) != 10:
            raise ValueError("CODEAF must define ten control gates")
        if len(self._config.get("canonical_task_required_fields", [])) != 27:
            raise ValueError("CODEAF task contract must define twenty-seven fields")

    @staticmethod
    def _normalize_capabilities(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return list(
            dict.fromkeys(
                text.strip().casefold()
                for item in value
                if (text := str(item)).strip()
            )
        )

    @staticmethod
    def _nonempty(value: Any) -> bool:
        if isinstance(value, (list, dict, tuple, set)):
            return bool(value)
        return bool(str(value or "").strip())

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CODEAF configuration not found: {self.CONFIG_RELATIVE}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))
