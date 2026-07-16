# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkflowValidationError(ValueError):
    pass


@dataclass
class WorkflowValidationResult:
    valid: bool
    workflow_id: str
    workflow_version: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked_rules: list[str] = field(default_factory=list)
    definition_hash: str = ""
    validated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class CanonicalWorkflowValidator:
    """Validates CWF definitions without planning, resolving or executing them."""

    VERSION = "1.0"
    DEFAULT_STATES = {
        "DRAFT",
        "VALIDATING",
        "READY",
        "WAITING",
        "RUNNING",
        "PAUSED",
        "BLOCKED",
        "RETRYING",
        "ROLLING_BACK",
        "FAILED",
        "ABORTED",
        "COMPLETED",
        "VERIFIED",
        "REJECTED",
        "ARCHIVED",
    }
    DEFAULT_STEP_TYPES = {
        "ACTION",
        "VALIDATION",
        "DECISION",
        "APPROVAL",
        "REVIEW",
        "WAIT",
        "NOTIFICATION",
        "CHECKPOINT",
        "RECOVERY",
        "FINALIZATION",
    }
    DEFAULT_TIMEOUT_ACTIONS = {"FAIL", "PAUSE", "RETRY", "ESCALATE", "ABORT"}
    TERMINAL_STATES = {"FAILED", "ABORTED", "COMPLETED", "VERIFIED", "REJECTED", "ARCHIVED"}
    ALLOWED_ROLES = {
        "workflow_owner",
        "planner",
        "executor",
        "reviewer",
        "approver",
        "auditor",
        "recovery_owner",
        "orchestrator",
    }

    def __init__(
        self,
        known_capabilities: set[str] | None = None,
        capability_mode: str = "warn",
        max_retry_attempts: int = 5,
    ):
        if capability_mode not in {"warn", "error"}:
            raise WorkflowValidationError("capability_mode muss 'warn' oder 'error' sein.")
        self.known_capabilities = set(known_capabilities or set())
        self.capability_mode = capability_mode
        self.max_retry_attempts = max_retry_attempts

    def validate_file(self, path: str | Path) -> dict:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return self.validate_definition(data)

    def validate_definition(self, definition: dict[str, Any]) -> dict:
        errors: list[str] = []
        warnings: list[str] = []
        checked: list[str] = []

        workflow_id = str(definition.get("workflow_id", ""))
        workflow_version = str(definition.get("workflow_version", ""))
        definition_hash = self.definition_hash(definition)

        self._check_required(definition, errors, checked)
        self._check_identity(definition, errors, checked)
        self._check_steps(definition, errors, warnings, checked)
        self._check_transitions(definition, errors, warnings, checked)
        self._check_capabilities(definition, errors, warnings, checked)
        self._check_hash(definition, definition_hash, warnings, checked)

        result = WorkflowValidationResult(
            valid=not errors,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            errors=errors,
            warnings=warnings,
            checked_rules=checked,
            definition_hash=definition_hash,
            validated_at=datetime.now(timezone.utc).isoformat(),
        )
        return result.to_dict()

    def transition_allowed(self, from_state: str, to_state: str, transitions: list[dict]) -> dict:
        for transition in transitions:
            if transition.get("from_state") == from_state and transition.get("to_state") == to_state:
                return {"allowed": True, "transition_id": transition.get("transition_id", "")}
        return {"allowed": False, "reason": "transition_not_declared"}

    @staticmethod
    def definition_hash(definition: dict[str, Any]) -> str:
        payload = dict(definition)
        payload.pop("definition_hash", None)
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _check_required(self, definition: dict, errors: list[str], checked: list[str]) -> None:
        checked.append("required_fields")
        required = {
            "workflow_id",
            "workflow_name",
            "workflow_version",
            "workflow_type",
            "status",
            "owner",
            "risk_class",
            "steps",
            "transitions",
            "inputs",
            "outputs",
            "audit_requirements",
        }
        for field_name in sorted(required - set(definition)):
            errors.append(f"missing_required_field:{field_name}")

    def _check_identity(self, definition: dict, errors: list[str], checked: list[str]) -> None:
        checked.append("workflow_identity")
        if not str(definition.get("workflow_id", "")).strip():
            errors.append("workflow_id_empty")
        version = str(definition.get("workflow_version", ""))
        if not version or "." not in version:
            errors.append("workflow_version_invalid")

    def _check_steps(self, definition: dict, errors: list[str], warnings: list[str], checked: list[str]) -> None:
        checked.append("steps")
        steps = definition.get("steps", [])
        if not isinstance(steps, list) or not steps:
            errors.append("steps_missing")
            return
        step_ids = [str(step.get("step_id", "")) for step in steps if isinstance(step, dict)]
        for duplicate in self._duplicates(step_ids):
            errors.append(f"duplicate_step_id:{duplicate}")
        step_id_set = set(step_ids)
        start_steps = [step for step in steps if not self._incoming(step.get("step_id", ""), definition.get("transitions", []))]
        if len(start_steps) != 1:
            errors.append(f"invalid_start_step_count:{len(start_steps)}")
        end_steps = [step for step in steps if not step.get("next_steps")]
        if not end_steps:
            errors.append("missing_end_step")
        for step in steps:
            step_id = str(step.get("step_id", ""))
            if step.get("step_type") not in self.DEFAULT_STEP_TYPES:
                errors.append(f"unknown_step_type:{step_id}:{step.get('step_type')}")
            if step.get("assigned_role") not in self.ALLOWED_ROLES:
                warnings.append(f"unknown_or_external_role:{step_id}:{step.get('assigned_role')}")
            for next_step in step.get("next_steps", []):
                if next_step not in step_id_set:
                    errors.append(f"unknown_next_step:{step_id}:{next_step}")
            self._check_retry(step, errors, warnings)
            self._check_timeout(step, errors)
            self._check_rollback(step, errors, warnings)

    def _check_transitions(self, definition: dict, errors: list[str], warnings: list[str], checked: list[str]) -> None:
        checked.append("transitions")
        transitions = definition.get("transitions", [])
        if not isinstance(transitions, list) or not transitions:
            errors.append("transitions_missing")
            return
        transition_ids = [str(item.get("transition_id", "")) for item in transitions if isinstance(item, dict)]
        for duplicate in self._duplicates(transition_ids):
            errors.append(f"duplicate_transition_id:{duplicate}")
        for transition in transitions:
            from_state = transition.get("from_state")
            to_state = transition.get("to_state")
            if from_state not in self.DEFAULT_STATES:
                errors.append(f"unknown_from_state:{transition.get('transition_id')}:{from_state}")
            if to_state not in self.DEFAULT_STATES:
                errors.append(f"unknown_to_state:{transition.get('transition_id')}:{to_state}")
            if from_state == "DRAFT" and to_state == "VERIFIED":
                errors.append("invalid_transition:DRAFT_to_VERIFIED")
            if from_state == "ARCHIVED" and to_state not in {"ARCHIVED"}:
                errors.append(f"invalid_transition_from_archived:{to_state}")
            if to_state == "VERIFIED" and from_state != "COMPLETED":
                errors.append(f"verified_requires_completed:{from_state}")
            if to_state == "RUNNING" and not transition.get("required_approvals") and from_state == "READY":
                errors.append("ready_to_running_requires_approval")
            if not transition.get("audit_event"):
                warnings.append(f"transition_without_audit_event:{transition.get('transition_id')}")

    def _check_capabilities(self, definition: dict, errors: list[str], warnings: list[str], checked: list[str]) -> None:
        checked.append("capability_references")
        refs = set()
        for step in definition.get("steps", []):
            refs.update(str(item) for item in step.get("required_capabilities", []))
        for transition in definition.get("transitions", []):
            refs.update(str(item) for item in transition.get("required_capabilities", []))
        unknown = sorted(ref for ref in refs if ref and ref not in self.known_capabilities)
        for ref in unknown:
            message = f"capability_gap:{ref}"
            if self.capability_mode == "error":
                errors.append(message)
            else:
                warnings.append(message)

    def _check_hash(self, definition: dict, calculated_hash: str, warnings: list[str], checked: list[str]) -> None:
        checked.append("definition_hash")
        declared = str(definition.get("definition_hash", ""))
        if declared and declared != calculated_hash:
            warnings.append("definition_hash_mismatch")

    def _check_retry(self, step: dict, errors: list[str], warnings: list[str]) -> None:
        retry = step.get("retry_policy") or {}
        attempts = retry.get("max_attempts")
        step_id = step.get("step_id", "")
        if attempts is None:
            errors.append(f"retry_missing_max_attempts:{step_id}")
            return
        if int(attempts) < 0:
            errors.append(f"retry_negative_attempts:{step_id}")
        if int(attempts) > self.max_retry_attempts:
            errors.append(f"retry_exceeds_upper_bound:{step_id}")
        if int(attempts) > 0 and not step.get("idempotent") and retry.get("requires_idempotency", True):
            warnings.append(f"non_idempotent_retry_requires_protection:{step_id}")

    def _check_timeout(self, step: dict, errors: list[str]) -> None:
        timeout = step.get("timeout_policy") or {}
        step_id = step.get("step_id", "")
        if timeout.get("on_timeout") not in self.DEFAULT_TIMEOUT_ACTIONS:
            errors.append(f"invalid_timeout_action:{step_id}:{timeout.get('on_timeout')}")
        if int(timeout.get("timeout_seconds", 0)) < 0:
            errors.append(f"negative_timeout:{step_id}")

    def _check_rollback(self, step: dict, errors: list[str], warnings: list[str]) -> None:
        step_id = step.get("step_id", "")
        if step.get("rollback_supported") and not step.get("rollback_reference"):
            errors.append(f"rollback_reference_missing:{step_id}")
        if step.get("compensation_supported") and not step.get("compensation_reference"):
            errors.append(f"compensation_reference_missing:{step_id}")
        if step.get("irreversible") and step.get("assigned_role") not in {"workflow_owner", "approver"}:
            warnings.append(f"irreversible_step_requires_governance:{step_id}")

    @staticmethod
    def _duplicates(values: list[str]) -> list[str]:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for value in values:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        return sorted(duplicates)

    @staticmethod
    def _incoming(step_id: str, transitions: list[dict]) -> list[dict]:
        return [transition for transition in transitions if transition.get("to_step") == step_id]
