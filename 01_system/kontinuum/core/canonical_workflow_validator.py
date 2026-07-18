# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
import re
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalWorkflowValidator:
    """Read-only CWF contract validator.

    The validator loads the canonical CWF configuration and schemas, validates
    caller-supplied workflow definitions and runs, and never plans or executes
    workflow steps.
    """

    VERSION = "1.0"
    CONFIG_RELATIVE = Path("24_config/canonical_workflow_framework_1_0.json")
    CAPABILITY_REGISTRY_RELATIVE = Path("24_config/capability_registry_34_1.json")
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
    DEFAULT_ROLES = {
        "workflow_owner",
        "planner",
        "executor",
        "reviewer",
        "approver",
        "auditor",
        "recovery_owner",
        "orchestrator",
    }
    DEFAULT_TRIGGER_TYPES = {"MANUAL", "EVENT", "SCHEDULED", "API", "STATUS_CHANGE", "RECOVERY"}
    DEFAULT_GATE_TYPES = {
        "APPROVAL_GATE",
        "REVIEW_GATE",
        "SECURITY_GATE",
        "RELEASE_GATE",
        "HUMAN_CONFIRMATION_GATE",
    }
    DEFAULT_AUDIT_EVENTS = {
        "workflow_created",
        "workflow_validated",
        "workflow_started",
        "step_started",
        "step_completed",
        "step_failed",
        "approval_requested",
        "approval_granted",
        "approval_rejected",
        "workflow_paused",
        "workflow_resumed",
        "retry_started",
        "rollback_started",
        "rollback_completed",
        "compensation_started",
        "compensation_completed",
        "workflow_aborted",
        "workflow_completed",
        "workflow_verified",
        "workflow_archived",
    }
    ACTIVE_STATES = {"READY", "WAITING", "RUNNING", "PAUSED", "BLOCKED", "RETRYING", "ROLLING_BACK"}
    CLOSED_STATES = {"FAILED", "ABORTED", "VERIFIED", "REJECTED", "ARCHIVED"}
    NON_RETRYABLE_SECURITY_ERRORS = {"AUTHENTICATION_ERROR", "AUTHORIZATION_ERROR", "VALIDATION_ERROR"}

    def __init__(
        self,
        known_capabilities: set[str] | None = None,
        capability_mode: str = "warn",
        max_retry_attempts: int | None = None,
        project_root: str | Path | None = None,
    ):
        if capability_mode not in {"warn", "error"}:
            raise WorkflowValidationError("capability_mode muss 'warn' oder 'error' sein.")
        self.project_root = Path(project_root).resolve() if project_root else self._repository_root()
        self.config_path = self._resolve_path(self.CONFIG_RELATIVE)
        self.config = self._read_json(self.config_path)
        self._validate_framework_config()
        files = self.config["canonical_files"]
        self.states_config = self._read_json(self._resolve_config_reference(files["states"]))
        self.step_types_config = self._read_json(self._resolve_config_reference(files["step_types"]))
        self.transition_config = self._read_json(self._resolve_config_reference(files["transition_rules"]))
        self.error_config = self._read_json(self._resolve_config_reference(files["error_policies"]))
        self.definition_schema = self._read_json(self._resolve_config_reference(files["definition_schema"]))
        self.run_schema = self._read_json(self._resolve_config_reference(files["run_schema"]))
        self.step_schema = self._read_json(self._resolve_config_reference(files["step_schema"]))
        self.schema_documents = {
            str(self.definition_schema.get("$id", "")): self.definition_schema,
            str(self.run_schema.get("$id", "")): self.run_schema,
            str(self.step_schema.get("$id", "")): self.step_schema,
        }
        self.states = set(self.states_config.get("states", self.DEFAULT_STATES))
        self.step_types = set(self.step_types_config.get("step_types", self.DEFAULT_STEP_TYPES))
        self.roles = set(self.config.get("roles", self.DEFAULT_ROLES))
        self.trigger_types = set(self.config.get("trigger_types", self.DEFAULT_TRIGGER_TYPES))
        self.gate_types = set(self.config.get("gate_types", self.DEFAULT_GATE_TYPES))
        self.audit_events = set(self.config.get("audit_events", self.DEFAULT_AUDIT_EVENTS))
        self.timeout_actions = set(self.error_config.get("timeout_actions", self.DEFAULT_TIMEOUT_ACTIONS))
        self.error_classes = set(self.error_config.get("error_classes", []))
        self.error_strategies = set(self.error_config.get("strategies", []))
        retry_config = self.error_config.get("retry", {})
        configured_max = int(retry_config.get("max_attempts_upper_bound", 5))
        self.max_retry_attempts = configured_max if max_retry_attempts is None else int(max_retry_attempts)
        self.transition_rules = [dict(item) for item in self.transition_config.get("transitions", [])]
        self.transition_pairs = {
            (str(item.get("from_state", "")), str(item.get("to_state", ""))): item
            for item in self.transition_rules
        }
        if known_capabilities is None:
            self.known_capabilities = self._load_known_capabilities()
            self.capability_source = "canonical_registry"
        else:
            self.known_capabilities = set(known_capabilities)
            self.capability_source = "caller_supplied"
        self.capability_mode = capability_mode
        self.condition_pattern = re.compile(
            str(self.config.get("condition_reference_pattern", r"^[A-Za-z][A-Za-z0-9_.:-]*$"))
        )

    def validate_file(self, path: str | Path) -> dict[str, Any]:
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            return self._result(
                {},
                [f"definition_file_invalid:{type(exc).__name__}"],
                [],
                ["definition_file"],
                "",
            )
        return self.validate_definition(data)

    def validate_definition(self, definition: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(definition, dict):
            return self._result({}, ["definition_not_object"], [], ["definition_type"], "")
        errors: list[str] = []
        warnings: list[str] = []
        checked: list[str] = []
        definition_hash = self.definition_hash(definition)

        self._check_schema(definition, self.definition_schema, "definition_schema", errors, checked)
        self._check_identity(definition, errors, checked)
        self._check_trigger(definition, errors, checked)
        self._check_steps(definition, errors, warnings, checked)
        self._check_transitions(definition, errors, warnings, checked)
        self._check_capabilities(definition, errors, warnings, checked)
        self._check_audit_requirements(definition, errors, checked)
        self._check_hash(definition, definition_hash, errors, warnings, checked)
        return self._result(definition, errors, warnings, checked, definition_hash)

    def validate_run(
        self,
        workflow_run: dict[str, Any],
        definition: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(workflow_run, dict):
            return self._result({}, ["workflow_run_not_object"], [], ["workflow_run_type"], "")
        errors: list[str] = []
        warnings: list[str] = []
        checked: list[str] = []
        self._check_schema(workflow_run, self.run_schema, "run_schema", errors, checked)
        state = str(workflow_run.get("current_state", ""))
        checked.append("run_state")
        if state not in self.states:
            errors.append(f"unknown_run_state:{state}")
        self._check_run_binding(workflow_run, definition, errors, checked)
        self._check_run_pause_state(workflow_run, errors, checked)
        self._check_run_approvals(workflow_run, errors, checked)
        self._check_run_audit(workflow_run, errors, checked)
        if state in self.ACTIVE_STATES and workflow_run.get("final_status") not in {"", None}:
            errors.append("active_run_must_not_have_final_status")
        if state in self.CLOSED_STATES and not str(workflow_run.get("final_status", "")).strip():
            errors.append("closed_run_requires_final_status")
        return self._result(workflow_run, errors, warnings, checked, str(workflow_run.get("definition_hash", "")))

    def validate_resume(
        self,
        workflow_run: dict[str, Any],
        definition: dict[str, Any],
        *,
        now: datetime | None = None,
        project_state_compatible: bool = True,
        artifacts_available: bool = True,
        permissions_valid: bool = True,
        rollback_point_available: bool = True,
    ) -> dict[str, Any]:
        base = self.validate_run(workflow_run, definition)
        errors = list(base["errors"])
        warnings = list(base["warnings"])
        checked = list(base["checked_rules"])
        checked.append("resume_contract")
        if workflow_run.get("current_state") != "PAUSED":
            errors.append("resume_requires_paused_state")
        checks = {
            "project_state_compatible": project_state_compatible,
            "artifacts_available": artifacts_available,
            "permissions_valid": permissions_valid,
            "rollback_point_available": rollback_point_available,
        }
        for name, ok in checks.items():
            if not ok:
                errors.append(f"resume_check_failed:{name}")
        instant = now or datetime.now(timezone.utc)
        for approval in workflow_run.get("approvals", []):
            if not isinstance(approval, dict) or not approval.get("required", False):
                continue
            gate_id = str(approval.get("gate_id", ""))
            if approval.get("approval_status") != "APPROVED":
                errors.append(f"resume_required_approval_missing:{gate_id}")
                continue
            valid_until = str(approval.get("valid_until", ""))
            if valid_until:
                parsed = self._parse_datetime(valid_until)
                if parsed is None:
                    errors.append(f"resume_approval_expiry_invalid:{gate_id}")
                elif parsed < instant:
                    errors.append(f"resume_approval_expired:{gate_id}")
        return self._result(workflow_run, errors, warnings, checked, str(workflow_run.get("definition_hash", "")))

    def transition_allowed(
        self,
        from_state: str,
        to_state: str,
        transitions: list[dict[str, Any]] | None = None,
        *,
        actor_role: str = "",
        granted_approvals: set[str] | None = None,
        available_capabilities: set[str] | None = None,
        condition_satisfied: bool | None = None,
        verification_evidence: bool = False,
    ) -> dict[str, Any]:
        rows = transitions if transitions is not None else self.transition_rules
        if from_state == "ARCHIVED" and to_state != "ARCHIVED":
            return {"allowed": False, "reason": "archived_run_requires_new_instance"}
        transition = next(
            (
                item
                for item in rows
                if item.get("from_state") == from_state and item.get("to_state") == to_state
            ),
            None,
        )
        if transition is None:
            return {"allowed": False, "reason": "transition_not_declared"}
        if to_state == "VERIFIED" and (from_state != "COMPLETED" or not verification_evidence):
            return {"allowed": False, "reason": "verified_requires_completed_and_evidence"}
        authorized_roles = set(transition.get("authorized_roles", []))
        if authorized_roles and not actor_role:
            return {"allowed": False, "reason": "actor_role_required"}
        if actor_role not in authorized_roles:
            return {"allowed": False, "reason": "actor_role_not_authorized"}
        required_approvals = set(transition.get("required_approvals", []))
        missing_approvals = sorted(required_approvals - set(granted_approvals or set()))
        if missing_approvals:
            return {"allowed": False, "reason": "required_approvals_missing", "missing": missing_approvals}
        required_capabilities = set(transition.get("required_capabilities", []))
        missing_capabilities = sorted(required_capabilities - set(available_capabilities or set()))
        if missing_capabilities:
            return {"allowed": False, "reason": "required_capabilities_missing", "missing": missing_capabilities}
        if transition.get("condition") and condition_satisfied is not True:
            return {"allowed": False, "reason": "transition_condition_not_satisfied"}
        return {"allowed": True, "transition_id": transition.get("transition_id", "")}

    @staticmethod
    def definition_hash(definition: dict[str, Any]) -> str:
        payload = dict(definition)
        payload.pop("definition_hash", None)
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def status(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "framework_id": self.config.get("framework_id", "cwf"),
            "status": self.config.get("status", "implemented_with_limitations"),
            "active": True,
            "mode": "explicit_definition_run_and_resume_validation",
            "config_path": str(self.config_path),
            "states": len(self.states),
            "step_types": len(self.step_types),
            "transition_rules": len(self.transition_rules),
            "schemas": len(self.schema_documents),
            "known_capabilities": len(self.known_capabilities),
            "capability_source": self.capability_source,
            "capability_mode": self.capability_mode,
            "plans": False,
            "executes": False,
            "resolves_capabilities": False,
            "registers_capabilities": False,
            "writes_audit": False,
            "writes_memory": False,
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join(
            [
                "Canonical Workflow Framework 1.0 Status:",
                f"- Modus: {status['mode']}",
                f"- Zustaende: {status['states']}",
                f"- Schrittarten: {status['step_types']}",
                f"- Uebergangsregeln: {status['transition_rules']}",
                f"- Schemas: {status['schemas']}",
                "- plant: nein",
                "- fuehrt aus: nein",
            ]
        )

    def _check_schema(
        self,
        value: Any,
        schema: dict[str, Any],
        rule_name: str,
        errors: list[str],
        checked: list[str],
    ) -> None:
        checked.append(rule_name)
        errors.extend(self._schema_errors(value, schema, "$", schema))

    def _schema_errors(
        self,
        value: Any,
        schema: dict[str, Any],
        path: str,
        root_schema: dict[str, Any],
    ) -> list[str]:
        if "$ref" in schema:
            resolved, resolved_root = self._resolve_schema_ref(str(schema["$ref"]), root_schema)
            if resolved is None:
                return [f"schema:{path}:unresolved_ref:{schema['$ref']}"]
            return self._schema_errors(value, resolved, path, resolved_root)
        errors: list[str] = []
        expected_type = schema.get("type")
        if expected_type and not self._schema_type_matches(value, str(expected_type)):
            return [f"schema:{path}:expected_{expected_type}"]
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"schema:{path}:not_in_enum:{value}")
        if "const" in schema and value != schema["const"]:
            errors.append(f"schema:{path}:const_mismatch")
        if isinstance(value, str):
            if len(value) < int(schema.get("minLength", 0)):
                errors.append(f"schema:{path}:min_length")
            pattern = schema.get("pattern")
            if pattern and re.fullmatch(str(pattern), value) is None:
                errors.append(f"schema:{path}:pattern")
            if schema.get("format") == "date-time" and value and self._parse_datetime(value) is None:
                errors.append(f"schema:{path}:date_time")
        if isinstance(value, int) and not isinstance(value, bool):
            if "minimum" in schema and value < int(schema["minimum"]):
                errors.append(f"schema:{path}:minimum")
            if "maximum" in schema and value > int(schema["maximum"]):
                errors.append(f"schema:{path}:maximum")
        if isinstance(value, list):
            if len(value) < int(schema.get("minItems", 0)):
                errors.append(f"schema:{path}:min_items")
            if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
                errors.append(f"schema:{path}:unique_items")
            item_schema = schema.get("items")
            if isinstance(item_schema, dict):
                for index, item in enumerate(value):
                    errors.extend(self._schema_errors(item, item_schema, f"{path}[{index}]", root_schema))
        if isinstance(value, dict):
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            for field_name in required:
                if field_name not in value:
                    errors.append(f"schema:{path}:missing_required:{field_name}")
            if schema.get("additionalProperties") is False:
                for field_name in sorted(set(value) - set(properties)):
                    errors.append(f"schema:{path}:additional_property:{field_name}")
            for field_name, field_schema in properties.items():
                if field_name in value and isinstance(field_schema, dict):
                    errors.extend(
                        self._schema_errors(value[field_name], field_schema, f"{path}.{field_name}", root_schema)
                    )
        return errors

    def _resolve_schema_ref(
        self,
        reference: str,
        root_schema: dict[str, Any],
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        if reference.startswith("#/"):
            value: Any = root_schema
            for token in reference[2:].split("/"):
                if not isinstance(value, dict):
                    return None, root_schema
                value = value.get(token.replace("~1", "/").replace("~0", "~"))
            return (value if isinstance(value, dict) else None), root_schema
        filename, _, fragment = reference.partition("#")
        document = self.schema_documents.get(filename)
        if document is None:
            return None, root_schema
        if not fragment:
            return document, document
        return self._resolve_schema_ref("#" + fragment, document)

    @staticmethod
    def _schema_type_matches(value: Any, expected_type: str) -> bool:
        mapping = {
            "object": lambda item: isinstance(item, dict),
            "array": lambda item: isinstance(item, list),
            "string": lambda item: isinstance(item, str),
            "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
            "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
            "boolean": lambda item: isinstance(item, bool),
            "null": lambda item: item is None,
        }
        return mapping.get(expected_type, lambda _item: True)(value)

    def _check_identity(self, definition: dict[str, Any], errors: list[str], checked: list[str]) -> None:
        checked.append("workflow_identity")
        workflow_id = str(definition.get("workflow_id", ""))
        if not workflow_id.strip():
            errors.append("workflow_id_empty")
        elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", workflow_id) is None:
            errors.append("workflow_id_invalid")
        version = str(definition.get("workflow_version", ""))
        if re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", version) is None:
            errors.append("workflow_version_invalid")
        if definition.get("status") not in self.states:
            errors.append(f"unknown_definition_state:{definition.get('status')}")

    def _check_trigger(self, definition: dict[str, Any], errors: list[str], checked: list[str]) -> None:
        checked.append("trigger_contract")
        trigger = definition.get("trigger")
        if not isinstance(trigger, dict):
            errors.append("trigger_missing")
            return
        if trigger.get("trigger_type") not in self.trigger_types:
            errors.append(f"unknown_trigger_type:{trigger.get('trigger_type')}")
        if trigger.get("required_authentication") and not str(trigger.get("authorized_actor", "")).strip():
            errors.append("authenticated_trigger_requires_actor")
        if trigger.get("trigger_type") in {"EVENT", "SCHEDULED", "API", "STATUS_CHANGE", "RECOVERY"}:
            if not str(trigger.get("trigger_reference", "")).strip():
                errors.append("non_manual_trigger_requires_reference")
        if not str(trigger.get("idempotency_key", "")).strip():
            errors.append("trigger_requires_idempotency_key")

    def _check_steps(
        self,
        definition: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        checked: list[str],
    ) -> None:
        checked.extend(["step_identity", "step_graph", "step_contracts"])
        steps = definition.get("steps", [])
        if not isinstance(steps, list) or not steps:
            errors.append("steps_missing")
            return
        rows = [step for step in steps if isinstance(step, dict)]
        step_ids = [str(step.get("step_id", "")) for step in rows]
        for duplicate in self._duplicates(step_ids):
            errors.append(f"duplicate_step_id:{duplicate}")
        if any(not step_id for step_id in step_ids):
            errors.append("step_id_empty")
        sequences = [step.get("sequence") for step in rows]
        for duplicate in self._duplicates([str(item) for item in sequences]):
            errors.append(f"duplicate_step_sequence:{duplicate}")
        step_id_set = set(step_ids)
        incoming: set[str] = set()
        for step in rows:
            step_id = str(step.get("step_id", ""))
            next_steps = step.get("next_steps", [])
            if isinstance(next_steps, list):
                for next_step in next_steps:
                    if next_step not in step_id_set:
                        errors.append(f"unknown_next_step:{step_id}:{next_step}")
                    else:
                        incoming.add(str(next_step))
        start_steps = sorted(step_id_set - incoming)
        if len(start_steps) != 1:
            errors.append(f"invalid_start_step_count:{len(start_steps)}")
        declared_start = str(definition.get("start_step_id", ""))
        if declared_start and declared_start not in step_id_set:
            errors.append(f"unknown_declared_start_step:{declared_start}")
        if len(start_steps) == 1 and declared_start and declared_start != start_steps[0]:
            errors.append(f"declared_start_step_mismatch:{declared_start}:{start_steps[0]}")
        end_steps = sorted(str(step.get("step_id", "")) for step in rows if not step.get("next_steps"))
        if not end_steps:
            errors.append("missing_end_step")
        declared_ends = set(str(item) for item in definition.get("end_step_ids", []))
        if declared_ends and declared_ends != set(end_steps):
            errors.append("declared_end_steps_mismatch")
        reachability_start = declared_start if declared_start in step_id_set else (start_steps[0] if len(start_steps) == 1 else "")
        if reachability_start:
            reachable = self._reachable(reachability_start, rows)
            for step_id in sorted(step_id_set - reachable):
                errors.append(f"unreachable_step:{step_id}")
        for cycle in self._cycles(rows):
            errors.append("uncontrolled_cycle:" + "->".join(cycle))

        declared_inputs = {str(item.get("input_id", "")) for item in definition.get("inputs", []) if isinstance(item, dict)}
        declared_outputs = {str(item.get("output_id", "")) for item in definition.get("outputs", []) if isinstance(item, dict)}
        input_ids = [str(item.get("input_id", "")) for item in definition.get("inputs", []) if isinstance(item, dict)]
        output_ids = [str(item.get("output_id", "")) for item in definition.get("outputs", []) if isinstance(item, dict)]
        for duplicate in self._duplicates(input_ids):
            errors.append(f"duplicate_workflow_input:{duplicate}")
        for duplicate in self._duplicates(output_ids):
            errors.append(f"duplicate_workflow_output:{duplicate}")
        produced_outputs = {
            str(item)
            for step in rows
            for item in step.get("produced_outputs", [])
        }
        output_producers: dict[str, list[dict[str, Any]]] = {}
        for step in rows:
            for output_id in step.get("produced_outputs", []):
                output_producers.setdefault(str(output_id), []).append(step)
        for output_id, producers in sorted(output_producers.items()):
            if len(producers) > 1:
                errors.append(f"duplicate_output_producer:{output_id}")
        for output_id in sorted(produced_outputs - declared_outputs):
            errors.append(f"undeclared_workflow_output:{output_id}")
        required_outputs = {
            str(item.get("output_id", ""))
            for item in definition.get("outputs", [])
            if isinstance(item, dict) and item.get("required")
        }
        for output_id in sorted(required_outputs - produced_outputs):
            errors.append(f"required_workflow_output_not_produced:{output_id}")
        available_inputs = declared_inputs | produced_outputs
        for step in rows:
            step_id = str(step.get("step_id", ""))
            if step.get("step_type") not in self.step_types:
                errors.append(f"unknown_step_type:{step_id}:{step.get('step_type')}")
            if step.get("assigned_role") not in self.roles:
                errors.append(f"unknown_role:{step_id}:{step.get('assigned_role')}")
            for input_id in step.get("required_inputs", []):
                if input_id not in available_inputs:
                    errors.append(f"undeclared_step_input:{step_id}:{input_id}")
                    continue
                for producer in output_producers.get(str(input_id), []):
                    producer_sequence = producer.get("sequence")
                    consumer_sequence = step.get("sequence")
                    if (
                        isinstance(producer_sequence, int)
                        and not isinstance(producer_sequence, bool)
                        and isinstance(consumer_sequence, int)
                        and not isinstance(consumer_sequence, bool)
                        and producer_sequence >= consumer_sequence
                    ):
                        errors.append(f"step_input_not_available_yet:{step_id}:{input_id}")
            self._check_condition_references(step, errors)
            self._check_gate(step, errors)
            self._check_error_policy(step, errors)
            self._check_retry(step, errors)
            self._check_timeout(step, errors)
            self._check_rollback(step, errors, warnings)
            if step.get("critical") and not step.get("audit_required"):
                errors.append(f"critical_step_requires_audit:{step_id}")

    def _check_transitions(
        self,
        definition: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        checked: list[str],
    ) -> None:
        checked.append("state_transitions")
        transitions = definition.get("transitions", [])
        if not isinstance(transitions, list) or not transitions:
            errors.append("transitions_missing")
            return
        transition_ids = [str(item.get("transition_id", "")) for item in transitions if isinstance(item, dict)]
        for duplicate in self._duplicates(transition_ids):
            errors.append(f"duplicate_transition_id:{duplicate}")
        for transition in transitions:
            if not isinstance(transition, dict):
                continue
            transition_id = str(transition.get("transition_id", ""))
            from_state = str(transition.get("from_state", ""))
            to_state = str(transition.get("to_state", ""))
            if from_state not in self.states:
                errors.append(f"unknown_from_state:{transition_id}:{from_state}")
            if to_state not in self.states:
                errors.append(f"unknown_to_state:{transition_id}:{to_state}")
            canonical = self.transition_pairs.get((from_state, to_state))
            if canonical is None:
                errors.append(f"transition_not_canonical:{transition_id}:{from_state}:{to_state}")
            else:
                for field_name in ("required_approvals", "required_capabilities"):
                    required = set(canonical.get(field_name, []))
                    supplied = set(transition.get(field_name, []))
                    missing = sorted(required - supplied)
                    if missing:
                        errors.append(f"transition_missing_{field_name}:{transition_id}:{','.join(missing)}")
            if from_state == "DRAFT" and to_state == "VERIFIED":
                errors.append("invalid_transition:DRAFT_to_VERIFIED")
            if from_state == "ARCHIVED" and to_state != "ARCHIVED":
                errors.append(f"invalid_transition_from_archived:{to_state}")
            if to_state == "VERIFIED" and from_state != "COMPLETED":
                errors.append(f"verified_requires_completed:{from_state}")
            for role in transition.get("authorized_roles", []):
                if role not in self.roles:
                    errors.append(f"transition_unknown_role:{transition_id}:{role}")
            condition = str(transition.get("condition", ""))
            if not self._valid_condition(condition):
                errors.append(f"invalid_transition_condition:{transition_id}")
            audit_event = str(transition.get("audit_event", ""))
            if audit_event not in self.audit_events:
                errors.append(f"transition_unknown_audit_event:{transition_id}:{audit_event}")
            elif not audit_event:
                warnings.append(f"transition_without_audit_event:{transition_id}")

    def _check_capabilities(
        self,
        definition: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        checked: list[str],
    ) -> None:
        checked.append("capability_references")
        refs: set[str] = set()
        for step in definition.get("steps", []):
            if isinstance(step, dict):
                refs.update(str(item) for item in step.get("required_capabilities", []))
        for transition in definition.get("transitions", []):
            if isinstance(transition, dict):
                refs.update(str(item) for item in transition.get("required_capabilities", []))
        unknown = sorted(ref for ref in refs if ref and ref not in self.known_capabilities)
        for ref in unknown:
            message = f"capability_gap:{ref}"
            if self.capability_mode == "error":
                errors.append(message)
            else:
                warnings.append(message)

    def _check_audit_requirements(
        self,
        definition: dict[str, Any],
        errors: list[str],
        checked: list[str],
    ) -> None:
        checked.append("audit_requirements")
        requirements = set(str(item) for item in definition.get("audit_requirements", []))
        required_minimum = {"workflow_validated", "workflow_started", "workflow_completed"}
        for event in sorted(requirements - self.audit_events):
            errors.append(f"unknown_audit_requirement:{event}")
        for event in sorted(required_minimum - requirements):
            errors.append(f"missing_audit_requirement:{event}")

    def _check_hash(
        self,
        definition: dict[str, Any],
        calculated_hash: str,
        errors: list[str],
        warnings: list[str],
        checked: list[str],
    ) -> None:
        checked.append("definition_hash")
        declared = str(definition.get("definition_hash", ""))
        if not declared:
            warnings.append("definition_hash_missing")
        elif declared != calculated_hash:
            errors.append("definition_hash_mismatch")

    def _check_condition_references(self, step: dict[str, Any], errors: list[str]) -> None:
        step_id = str(step.get("step_id", ""))
        for field_name in ("preconditions", "postconditions", "success_conditions", "failure_conditions"):
            for condition in step.get(field_name, []):
                if not self._valid_condition(str(condition)):
                    errors.append(f"invalid_condition_reference:{step_id}:{field_name}:{condition}")

    def _check_gate(self, step: dict[str, Any], errors: list[str]) -> None:
        step_id = str(step.get("step_id", ""))
        gate = step.get("approval_gate")
        if step.get("step_type") == "APPROVAL" and not isinstance(gate, dict):
            errors.append(f"approval_step_requires_gate:{step_id}")
            return
        if gate is None:
            if step.get("irreversible"):
                errors.append(f"irreversible_step_requires_gate:{step_id}")
            return
        if not isinstance(gate, dict):
            errors.append(f"approval_gate_invalid:{step_id}")
            return
        if gate.get("gate_type") not in self.gate_types:
            errors.append(f"unknown_gate_type:{step_id}:{gate.get('gate_type')}")
        if gate.get("required_role") not in self.roles:
            errors.append(f"unknown_gate_role:{step_id}:{gate.get('required_role')}")
        if not isinstance(gate.get("required_actor_count"), int) or gate.get("required_actor_count", 0) < 1:
            errors.append(f"gate_requires_actor:{step_id}")
        if gate.get("approval_status") not in {"PENDING", "APPROVED", "REJECTED", "EXPIRED"}:
            errors.append(f"unknown_approval_status:{step_id}:{gate.get('approval_status')}")
        if gate.get("approval_status") == "APPROVED" or gate.get("approved_by") or gate.get("approved_at"):
            errors.append(f"definition_gate_must_not_be_preapproved:{step_id}")
        if step.get("critical") and gate.get("self_approval_allowed", False):
            errors.append(f"critical_step_self_approval_forbidden:{step_id}")

    def _check_error_policy(self, step: dict[str, Any], errors: list[str]) -> None:
        step_id = str(step.get("step_id", ""))
        policy = step.get("error_policy")
        if not isinstance(policy, dict):
            errors.append(f"error_policy_missing:{step_id}")
            return
        strategy = str(policy.get("on_error", ""))
        if self.error_strategies and strategy not in self.error_strategies:
            errors.append(f"unknown_error_strategy:{step_id}:{strategy}")
        for field_name in ("retryable_errors", "non_retryable_errors"):
            for error_class in policy.get(field_name, []):
                if self.error_classes and error_class not in self.error_classes:
                    errors.append(f"unknown_error_class:{step_id}:{error_class}")
        if step.get("critical") and strategy in {"", "SKIP"}:
            errors.append(f"critical_step_requires_stopping_error_strategy:{step_id}")

    def _check_retry(self, step: dict[str, Any], errors: list[str]) -> None:
        retry = step.get("retry_policy") or {}
        step_id = str(step.get("step_id", ""))
        attempts = retry.get("max_attempts")
        if not isinstance(attempts, int) or isinstance(attempts, bool):
            errors.append(f"retry_invalid_max_attempts:{step_id}")
            return
        if attempts < 0:
            errors.append(f"retry_negative_attempts:{step_id}")
        if attempts > self.max_retry_attempts:
            errors.append(f"retry_exceeds_upper_bound:{step_id}")
        retryable = set(retry.get("retryable_errors", retry.get("retry_on", [])))
        forbidden = sorted(retryable & self.NON_RETRYABLE_SECURITY_ERRORS)
        if forbidden:
            errors.append(f"retry_forbidden_error_class:{step_id}:{','.join(forbidden)}")
        protected = bool(
            step.get("idempotent")
            or retry.get("idempotency_key_required")
            or step.get("compensation_supported")
        )
        if attempts > 0 and not protected:
            errors.append(f"non_idempotent_retry_without_protection:{step_id}")

    def _check_timeout(self, step: dict[str, Any], errors: list[str]) -> None:
        timeout = step.get("timeout_policy") or {}
        step_id = str(step.get("step_id", ""))
        if timeout.get("on_timeout") not in self.timeout_actions:
            errors.append(f"invalid_timeout_action:{step_id}:{timeout.get('on_timeout')}")
        seconds = timeout.get("timeout_seconds")
        if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds < 0:
            errors.append(f"invalid_timeout:{step_id}")
        elif seconds == 0 and (step.get("critical") or step.get("step_type") in {"WAIT", "APPROVAL"}):
            errors.append(f"bounded_timeout_required:{step_id}")

    def _check_rollback(
        self,
        step: dict[str, Any],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        step_id = str(step.get("step_id", ""))
        if step.get("rollback_supported") and not step.get("rollback_reference"):
            errors.append(f"rollback_reference_missing:{step_id}")
        if step.get("compensation_supported") and not step.get("compensation_reference"):
            errors.append(f"compensation_reference_missing:{step_id}")
        if step.get("irreversible") and step.get("rollback_supported"):
            errors.append(f"irreversible_step_cannot_rollback:{step_id}")
        if step.get("critical") and not step.get("irreversible"):
            if not step.get("rollback_supported") and not step.get("compensation_supported"):
                errors.append(f"critical_step_requires_recovery:{step_id}")
        if step.get("irreversible") and step.get("assigned_role") not in {"workflow_owner", "approver"}:
            warnings.append(f"irreversible_step_requires_governance_role:{step_id}")

    def _check_run_binding(
        self,
        workflow_run: dict[str, Any],
        definition: dict[str, Any] | None,
        errors: list[str],
        checked: list[str],
    ) -> None:
        checked.append("run_definition_binding")
        if definition is None:
            return
        expected_hash = self.definition_hash(definition)
        if workflow_run.get("workflow_id") != definition.get("workflow_id"):
            errors.append("run_workflow_id_mismatch")
        if workflow_run.get("workflow_version") != definition.get("workflow_version"):
            errors.append("run_workflow_version_mismatch")
        if workflow_run.get("definition_hash") != expected_hash:
            errors.append("run_definition_hash_mismatch")

    def _check_run_pause_state(
        self,
        workflow_run: dict[str, Any],
        errors: list[str],
        checked: list[str],
    ) -> None:
        checked.append("pause_checkpoint")
        if workflow_run.get("current_state") != "PAUSED":
            return
        required = {
            "paused_at",
            "pause_reason",
            "last_completed_step_id",
            "current_step_id",
            "pending_step_ids",
            "inputs",
            "outputs",
            "approvals",
            "rollback_point_reference",
        }
        for field_name in sorted(required):
            value = workflow_run.get(field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"paused_run_missing:{field_name}")

    def _check_run_approvals(
        self,
        workflow_run: dict[str, Any],
        errors: list[str],
        checked: list[str],
    ) -> None:
        checked.append("run_approvals")
        for approval in workflow_run.get("approvals", []):
            if not isinstance(approval, dict):
                continue
            gate_id = str(approval.get("gate_id", ""))
            approved_by = set(str(item) for item in approval.get("approved_by", []))
            requested_by = str(approval.get("requested_by", ""))
            if not approval.get("self_approval_allowed", False) and requested_by and requested_by in approved_by:
                errors.append(f"self_approval_forbidden:{gate_id}:{requested_by}")
            required_count = int(approval.get("required_actor_count", 0))
            if approval.get("approval_status") == "APPROVED" and len(approved_by) < required_count:
                errors.append(f"approval_actor_count_not_met:{gate_id}")
            if approval.get("approval_status") == "REJECTED" and workflow_run.get("current_state") in self.ACTIVE_STATES:
                errors.append(f"rejected_approval_blocks_active_run:{gate_id}")

    def _check_run_audit(
        self,
        workflow_run: dict[str, Any],
        errors: list[str],
        checked: list[str],
    ) -> None:
        checked.append("run_audit_events")
        run_id = str(workflow_run.get("workflow_run_id", ""))
        events = [event for event in workflow_run.get("audit_events", []) if isinstance(event, dict)]
        if not events:
            errors.append("run_audit_events_missing")
            return
        event_ids = [str(event.get("event_id", "")) for event in events]
        for duplicate in self._duplicates(event_ids):
            errors.append(f"duplicate_run_audit_event_id:{duplicate}")
        event_types = {str(event.get("event_type", "")) for event in events}
        for event in events:
            event_id = str(event.get("event_id", ""))
            event_type = str(event.get("event_type", ""))
            if event_type not in self.audit_events:
                errors.append(f"unknown_run_audit_event:{event_id}:{event_type}")
            if event.get("workflow_run_id") != run_id:
                errors.append(f"audit_run_link_mismatch:{event_id}")
            if event.get("workflow_id") != workflow_run.get("workflow_id"):
                errors.append(f"audit_workflow_link_mismatch:{event_id}")
            if event.get("workflow_version") != workflow_run.get("workflow_version"):
                errors.append(f"audit_version_link_mismatch:{event_id}")
            if event_type in {"step_failed", "retry_started"} and not str(event.get("error_reference", "")).strip():
                errors.append(f"audit_error_reference_missing:{event_id}")
            if event_type in {"approval_requested", "approval_granted", "approval_rejected"}:
                if not str(event.get("approval_reference", "")).strip():
                    errors.append(f"audit_approval_reference_missing:{event_id}")
        required_state_events = {
            "PAUSED": "workflow_paused",
            "RETRYING": "retry_started",
            "ROLLING_BACK": "rollback_started",
            "FAILED": "step_failed",
            "ABORTED": "workflow_aborted",
            "COMPLETED": "workflow_completed",
            "VERIFIED": "workflow_verified",
            "ARCHIVED": "workflow_archived",
        }
        required_event = required_state_events.get(str(workflow_run.get("current_state", "")))
        if required_event and required_event not in event_types:
            errors.append(f"run_state_audit_event_missing:{required_event}")
        approval_events = {
            "PENDING": "approval_requested",
            "APPROVED": "approval_granted",
            "REJECTED": "approval_rejected",
            "EXPIRED": "approval_rejected",
        }
        for approval in workflow_run.get("approvals", []):
            if not isinstance(approval, dict):
                continue
            expected = approval_events.get(str(approval.get("approval_status", "")))
            if expected and expected not in event_types:
                errors.append(f"run_approval_audit_event_missing:{approval.get('gate_id', '')}:{expected}")

    def _valid_condition(self, condition: str) -> bool:
        return bool(condition and self.condition_pattern.fullmatch(condition))

    @staticmethod
    def _reachable(start_step: str, steps: list[dict[str, Any]]) -> set[str]:
        graph = {str(step.get("step_id", "")): list(step.get("next_steps", [])) for step in steps}
        reached: set[str] = set()
        pending = [start_step]
        while pending:
            step_id = pending.pop()
            if step_id in reached:
                continue
            reached.add(step_id)
            pending.extend(str(item) for item in graph.get(step_id, []) if item in graph)
        return reached

    @staticmethod
    def _cycles(steps: list[dict[str, Any]]) -> list[list[str]]:
        graph = {str(step.get("step_id", "")): list(step.get("next_steps", [])) for step in steps}
        cycles: list[list[str]] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, path: list[str]) -> None:
            if node in visiting:
                start = path.index(node) if node in path else 0
                cycle = path[start:]
                if cycle not in cycles:
                    cycles.append(cycle)
                return
            if node in visited:
                return
            visiting.add(node)
            for next_step in graph.get(node, []):
                if next_step in graph:
                    visit(str(next_step), path + [str(next_step)])
            visiting.remove(node)
            visited.add(node)

        for step_id in graph:
            visit(step_id, [step_id])
        return cycles

    @staticmethod
    def _duplicates(values: list[str]) -> list[str]:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for value in values:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        return sorted(duplicates)

    def _result(
        self,
        value: dict[str, Any],
        errors: list[str],
        warnings: list[str],
        checked: list[str],
        definition_hash: str,
    ) -> dict[str, Any]:
        return WorkflowValidationResult(
            valid=not errors,
            workflow_id=str(value.get("workflow_id", "")),
            workflow_version=str(value.get("workflow_version", "")),
            errors=self._unique(errors),
            warnings=self._unique(warnings),
            checked_rules=self._unique(checked),
            definition_hash=definition_hash,
            validated_at=datetime.now(timezone.utc).isoformat(),
        ).to_dict()

    def _validate_framework_config(self) -> None:
        required = {
            "framework_id",
            "framework_name",
            "framework_version",
            "status",
            "canonical_files",
            "integration_contracts",
        }
        missing = sorted(required - set(self.config))
        if missing:
            raise WorkflowValidationError("CWF-Konfiguration unvollstaendig: " + ", ".join(missing))
        if self.config.get("framework_version") != self.VERSION:
            raise WorkflowValidationError("CWF-Konfiguration gehoert nicht zu Version 1.0.")
        if not self.config.get("not_runtime_engine", False):
            raise WorkflowValidationError("CWF muss als Nicht-Runtime-Framework konfiguriert sein.")

    def _load_known_capabilities(self) -> set[str]:
        try:
            registry = self._read_json(self._resolve_path(self.CAPABILITY_REGISTRY_RELATIVE))
        except (OSError, ValueError, FileNotFoundError):
            return set()
        return {
            str(item.get("capability_id", ""))
            for item in registry.get("capabilities", [])
            if isinstance(item, dict) and item.get("capability_id")
        }

    def _resolve_config_reference(self, value: str) -> Path:
        return self._resolve_path(Path(value))

    def _resolve_path(self, relative: Path) -> Path:
        primary = self.project_root / relative
        if primary.is_file():
            return primary
        fallback = self._repository_root() / relative
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CWF artifact not found: {relative.as_posix()}")

    @staticmethod
    def _repository_root() -> Path:
        return Path(__file__).resolve().parents[3]

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise WorkflowValidationError(f"JSON object expected: {path}")
        return value

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
