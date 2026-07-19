# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_workflow_validator import CanonicalWorkflowValidator


KNOWN_CAPABILITIES = {"governance.architecture"}


def valid_definition() -> dict:
    return {
        "workflow_id": "cwf.example",
        "workflow_name": "CWF Example",
        "workflow_version": "1.0",
        "workflow_type": "APPROVAL",
        "description": "Read-only validation example.",
        "status": "DRAFT",
        "owner": "workflow_owner",
        "risk_class": "controlled",
        "definition_hash": "",
        "created_at": "2026-07-18T00:00:00Z",
        "updated_at": "2026-07-18T00:00:00Z",
        "trigger": {
            "trigger_type": "MANUAL",
            "trigger_reference": "",
            "authorized_actor": "workflow-owner-1",
            "required_authentication": True,
            "input_contract": "cwf.input.1",
            "idempotency_key": "cwf-example-manual",
        },
        "start_step_id": "analyse",
        "end_step_ids": ["approval"],
        "preconditions": ["source.available"],
        "postconditions": ["approval.recorded"],
        "inputs": [
            {
                "input_id": "source_document",
                "input_type": "artifact_reference",
                "schema_reference": "",
                "required": True,
                "source": "caller",
            }
        ],
        "outputs": [
            {
                "output_id": "analysis_report",
                "output_type": "artifact_reference",
                "schema_reference": "",
                "artifact_reference": "",
                "required": True,
            },
            {
                "output_id": "approval_decision",
                "output_type": "approval_record",
                "schema_reference": "",
                "artifact_reference": "",
                "required": True,
            },
        ],
        "audit_requirements": ["workflow_validated", "workflow_started", "workflow_completed"],
        "steps": [
            {
                "step_id": "analyse",
                "step_name": "Analyse",
                "step_type": "VALIDATION",
                "description": "Validate the supplied source.",
                "sequence": 1,
                "required_inputs": ["source_document"],
                "produced_outputs": ["analysis_report"],
                "required_capabilities": ["governance.architecture"],
                "assigned_role": "reviewer",
                "preconditions": ["source.available"],
                "postconditions": ["analysis.complete"],
                "success_conditions": ["analysis.valid"],
                "failure_conditions": ["analysis.invalid"],
                "critical": False,
                "timeout_policy": {
                    "timeout_seconds": 300,
                    "on_timeout": "FAIL",
                    "timeout_error_code": "TIMEOUT",
                    "escalation_required": False,
                },
                "retry_policy": {
                    "max_attempts": 1,
                    "delay_seconds": 1,
                    "backoff_strategy": "FIXED",
                    "retryable_errors": ["TIMEOUT"],
                    "non_retryable_errors": ["VALIDATION_ERROR", "AUTHORIZATION_ERROR"],
                    "reset_timeout_on_retry": True,
                    "requires_idempotency": True,
                    "idempotency_key_required": False,
                },
                "error_policy": {
                    "on_error": "STOP",
                    "retryable_errors": ["TIMEOUT"],
                    "non_retryable_errors": ["VALIDATION_ERROR", "AUTHORIZATION_ERROR"],
                    "escalate_to": "workflow_owner",
                },
                "rollback_supported": False,
                "rollback_reference": "",
                "compensation_supported": False,
                "compensation_reference": "",
                "irreversible": False,
                "idempotent": True,
                "next_steps": ["approval"],
                "audit_required": True,
            },
            {
                "step_id": "approval",
                "step_name": "Approval",
                "step_type": "APPROVAL",
                "description": "Request a controlled approval.",
                "sequence": 2,
                "required_inputs": ["analysis_report"],
                "produced_outputs": ["approval_decision"],
                "required_capabilities": ["workflow.verify"],
                "assigned_role": "approver",
                "preconditions": ["analysis.complete"],
                "postconditions": ["approval.recorded"],
                "success_conditions": ["approval.granted"],
                "failure_conditions": ["approval.rejected"],
                "critical": False,
                "timeout_policy": {
                    "timeout_seconds": 600,
                    "on_timeout": "ESCALATE",
                    "timeout_error_code": "TIMEOUT",
                    "escalation_required": True,
                },
                "retry_policy": {
                    "max_attempts": 0,
                    "delay_seconds": 0,
                    "backoff_strategy": "NONE",
                    "retryable_errors": [],
                    "non_retryable_errors": ["APPROVAL_REJECTED"],
                    "reset_timeout_on_retry": False,
                    "requires_idempotency": True,
                    "idempotency_key_required": True,
                },
                "error_policy": {
                    "on_error": "ESCALATE",
                    "retryable_errors": [],
                    "non_retryable_errors": ["APPROVAL_REJECTED"],
                    "escalate_to": "workflow_owner",
                },
                "approval_gate": {
                    "gate_id": "governance_gate",
                    "gate_type": "APPROVAL_GATE",
                    "required_role": "approver",
                    "required_actor_count": 1,
                    "approval_status": "PENDING",
                    "approved_by": [],
                    "approved_at": "",
                    "rejection_reason": "",
                    "self_approval_allowed": False,
                },
                "rollback_supported": False,
                "rollback_reference": "",
                "compensation_supported": False,
                "compensation_reference": "",
                "irreversible": False,
                "idempotent": False,
                "next_steps": [],
                "audit_required": True,
            },
        ],
        "transitions": [
            {
                "transition_id": "draft_to_validating",
                "from_state": "DRAFT",
                "to_state": "VALIDATING",
                "condition": "definition.present",
                "authorized_roles": ["workflow_owner"],
                "required_approvals": [],
                "required_capabilities": ["workflow.validate"],
                "audit_event": "workflow_validated",
            }
        ],
    }


def valid_paused_run(definition: dict) -> dict:
    definition_hash = CanonicalWorkflowValidator.definition_hash(definition)
    return {
        "workflow_run_id": "run-001",
        "workflow_id": definition["workflow_id"],
        "workflow_version": definition["workflow_version"],
        "definition_hash": definition_hash,
        "execution_plan_id": "plan-001",
        "trigger_type": "MANUAL",
        "trigger_reference": "",
        "initiated_by": "workflow-owner-1",
        "current_state": "PAUSED",
        "current_step_id": "approval",
        "last_completed_step_id": "analyse",
        "pending_step_ids": ["approval"],
        "inputs": {"source_document": "artifact:source-1"},
        "outputs": {"analysis_report": "artifact:analysis-1"},
        "approvals": [
            {
                "gate_id": "resume_gate",
                "gate_type": "HUMAN_CONFIRMATION_GATE",
                "required_role": "approver",
                "required_actor_count": 1,
                "approval_status": "APPROVED",
                "requested_by": "workflow-owner-1",
                "approved_by": ["approver-1"],
                "requested_at": "2026-07-18T00:01:00Z",
                "approved_at": "2026-07-18T00:02:00Z",
                "valid_until": "2026-07-19T00:00:00Z",
                "rejection_reason": "",
                "self_approval_allowed": False,
                "required": True,
            }
        ],
        "rollback_point_reference": "checkpoint:analyse",
        "started_at": "2026-07-18T00:00:00Z",
        "paused_at": "2026-07-18T00:03:00Z",
        "pause_reason": "approval.required",
        "resumed_at": "",
        "completed_at": "",
        "final_status": "",
        "audit_events": [
            {
                "event_id": "event-001",
                "event_type": "workflow_paused",
                "workflow_run_id": "run-001",
                "workflow_id": definition["workflow_id"],
                "workflow_version": definition["workflow_version"],
                "step_id": "approval",
                "actor": "workflow-owner-1",
                "actor_role": "workflow_owner",
                "timestamp": "2026-07-18T00:03:00Z",
                "previous_state": "RUNNING",
                "new_state": "PAUSED",
                "inputs_reference": "run:run-001:inputs",
                "outputs_reference": "run:run-001:outputs",
                "artifact_references": ["artifact:analysis-1"],
                "error_reference": "",
                "approval_reference": "resume_gate",
                "execution_plan_reference": "plan-001",
            },
            {
                "event_id": "event-002",
                "event_type": "approval_granted",
                "workflow_run_id": "run-001",
                "workflow_id": definition["workflow_id"],
                "workflow_version": definition["workflow_version"],
                "step_id": "approval",
                "actor": "approver-1",
                "actor_role": "approver",
                "timestamp": "2026-07-18T00:02:00Z",
                "previous_state": "PAUSED",
                "new_state": "PAUSED",
                "inputs_reference": "run:run-001:inputs",
                "outputs_reference": "run:run-001:outputs",
                "artifact_references": ["artifact:analysis-1"],
                "error_reference": "",
                "approval_reference": "resume_gate",
                "execution_plan_reference": "plan-001",
            },
        ],
    }


def validator(mode: str = "warn") -> CanonicalWorkflowValidator:
    return CanonicalWorkflowValidator(KNOWN_CAPABILITIES, capability_mode=mode)


def test_valid_definition_executes_all_contract_checks_and_reports_capability_gaps():
    result = validator().validate_definition(valid_definition())
    assert result["valid"] is True
    assert "definition_schema" in result["checked_rules"]
    assert "step_graph" in result["checked_rules"]
    assert "capability_gap:workflow.validate" in result["warnings"]
    assert "capability_gap:workflow.verify" in result["warnings"]


def test_capability_gap_can_be_an_error_without_registering_capability():
    result = validator("error").validate_definition(valid_definition())
    assert result["valid"] is False
    assert "capability_gap:workflow.validate" in result["errors"]
    assert validator().status()["registers_capabilities"] is False


def test_schema_rejects_missing_and_additional_definition_fields():
    definition = valid_definition()
    del definition["trigger"]
    definition["free_form_command"] = "execute"
    errors = validator().validate_definition(definition)["errors"]
    assert "schema:$:missing_required:trigger" in errors
    assert "schema:$:additional_property:free_form_command" in errors


def test_schema_rejects_invalid_version_unknown_state_and_missing_identity():
    definition = valid_definition()
    definition["workflow_id"] = ""
    definition["workflow_version"] = "latest"
    definition["status"] = "UNKNOWN"
    errors = validator().validate_definition(definition)["errors"]
    assert "workflow_id_empty" in errors
    assert "workflow_version_invalid" in errors
    assert "unknown_definition_state:UNKNOWN" in errors


def test_graph_rejects_duplicate_unreachable_unknown_and_cyclic_steps():
    definition = valid_definition()
    definition["steps"][1]["step_id"] = "analyse"
    assert "duplicate_step_id:analyse" in validator().validate_definition(definition)["errors"]

    definition = valid_definition()
    definition["steps"][0]["next_steps"] = ["missing"]
    errors = validator().validate_definition(definition)["errors"]
    assert "unknown_next_step:analyse:missing" in errors
    assert "unreachable_step:approval" in errors

    definition = valid_definition()
    definition["steps"][1]["next_steps"] = ["analyse"]
    errors = validator().validate_definition(definition)["errors"]
    assert any(error.startswith("uncontrolled_cycle:") for error in errors)


def test_graph_requires_exactly_one_start_and_at_least_one_end():
    definition = valid_definition()
    definition["steps"][0]["next_steps"] = []
    errors = validator().validate_definition(definition)["errors"]
    assert "invalid_start_step_count:2" in errors

    definition = valid_definition()
    definition["steps"][1]["next_steps"] = ["analyse"]
    errors = validator().validate_definition(definition)["errors"]
    assert "invalid_start_step_count:0" in errors
    assert "missing_end_step" in errors


def test_step_io_conditions_roles_and_types_are_validated():
    definition = valid_definition()
    definition["steps"][0]["required_inputs"] = ["undeclared", "approval_decision"]
    definition["steps"][0]["produced_outputs"] = ["undeclared_output"]
    definition["steps"][0]["preconditions"] = ["invalid condition"]
    definition["steps"][0]["assigned_role"] = "root"
    definition["steps"][0]["step_type"] = "SHELL"
    errors = validator().validate_definition(definition)["errors"]
    assert "undeclared_step_input:analyse:undeclared" in errors
    assert "step_input_not_available_yet:analyse:approval_decision" in errors
    assert "undeclared_workflow_output:undeclared_output" in errors
    assert "invalid_condition_reference:analyse:preconditions:invalid condition" in errors
    assert "unknown_role:analyse:root" in errors
    assert "unknown_step_type:analyse:SHELL" in errors


def test_approval_gate_requires_pending_separated_approval():
    definition = valid_definition()
    definition["steps"][1]["approval_gate"]["approval_status"] = "APPROVED"
    definition["steps"][1]["approval_gate"]["approved_by"] = ["approver-1"]
    errors = validator().validate_definition(definition)["errors"]
    assert "definition_gate_must_not_be_preapproved:approval" in errors

    definition = valid_definition()
    definition["steps"][1]["critical"] = True
    definition["steps"][1]["approval_gate"]["self_approval_allowed"] = True
    errors = validator().validate_definition(definition)["errors"]
    assert "critical_step_self_approval_forbidden:approval" in errors


def test_approval_step_requires_gate_and_rejection_blocks_active_run():
    definition = valid_definition()
    del definition["steps"][1]["approval_gate"]
    assert "approval_step_requires_gate:approval" in validator().validate_definition(definition)["errors"]

    definition = valid_definition()
    run = valid_paused_run(definition)
    run["approvals"][0]["approval_status"] = "REJECTED"
    run["approvals"][0]["approved_by"] = []
    run["approvals"][0]["rejection_reason"] = "risk.not.accepted"
    assert "rejected_approval_blocks_active_run:resume_gate" in validator().validate_run(run)["errors"]


def test_retry_is_bounded_security_aware_and_idempotency_protected():
    definition = valid_definition()
    retry = definition["steps"][0]["retry_policy"]
    retry["max_attempts"] = 6
    retry["retryable_errors"] = ["AUTHORIZATION_ERROR"]
    definition["steps"][0]["idempotent"] = False
    retry["idempotency_key_required"] = False
    errors = validator().validate_definition(definition)["errors"]
    assert "retry_exceeds_upper_bound:analyse" in errors
    assert "retry_forbidden_error_class:analyse:AUTHORIZATION_ERROR" in errors
    assert "non_idempotent_retry_without_protection:analyse" in errors


def test_negative_retry_is_rejected_and_valid_bounded_retry_is_accepted():
    definition = valid_definition()
    definition["steps"][0]["retry_policy"]["max_attempts"] = -1
    assert "retry_negative_attempts:analyse" in validator().validate_definition(definition)["errors"]

    errors = validator().validate_definition(valid_definition())["errors"]
    assert not any(error.startswith("retry_") for error in errors)


def test_timeout_and_recovery_contracts_are_enforced():
    definition = valid_definition()
    step = definition["steps"][0]
    step["critical"] = True
    step["timeout_policy"]["timeout_seconds"] = -1
    errors = validator().validate_definition(definition)["errors"]
    assert "invalid_timeout:analyse" in errors
    assert "critical_step_requires_recovery:analyse" in errors

    definition = valid_definition()
    step = definition["steps"][0]
    step["rollback_supported"] = True
    step["irreversible"] = True
    errors = validator().validate_definition(definition)["errors"]
    assert "rollback_reference_missing:analyse" in errors
    assert "irreversible_step_cannot_rollback:analyse" in errors


def test_valid_rollback_or_compensation_protects_critical_reversible_step():
    definition = valid_definition()
    step = definition["steps"][0]
    step["critical"] = True
    step["rollback_supported"] = True
    step["rollback_reference"] = "rollback:analyse"
    errors = validator().validate_definition(definition)["errors"]
    assert "critical_step_requires_recovery:analyse" not in errors
    assert "rollback_reference_missing:analyse" not in errors

    definition = valid_definition()
    step = definition["steps"][0]
    step["critical"] = True
    step["compensation_supported"] = True
    step["compensation_reference"] = "compensate:analyse"
    errors = validator().validate_definition(definition)["errors"]
    assert "critical_step_requires_recovery:analyse" not in errors
    assert "compensation_reference_missing:analyse" not in errors


def test_irreversible_step_requires_explicit_governance_gate():
    definition = valid_definition()
    definition["steps"][0]["irreversible"] = True
    assert "irreversible_step_requires_gate:analyse" in validator().validate_definition(definition)["errors"]


def test_transition_contract_requires_canonical_gate_and_capability():
    definition = valid_definition()
    transition = definition["transitions"][0]
    transition["from_state"] = "READY"
    transition["to_state"] = "RUNNING"
    transition["required_capabilities"] = []
    errors = validator().validate_definition(definition)["errors"]
    assert "transition_missing_required_approvals:draft_to_validating:governance_gate" in errors
    assert "transition_missing_required_capabilities:draft_to_validating:workflow.start" in errors


def test_forbidden_verified_and_archived_transitions_are_rejected():
    definition = valid_definition()
    transition = definition["transitions"][0]
    transition["from_state"] = "DRAFT"
    transition["to_state"] = "VERIFIED"
    errors = validator().validate_definition(definition)["errors"]
    assert "invalid_transition:DRAFT_to_VERIFIED" in errors

    definition = valid_definition()
    transition = definition["transitions"][0]
    transition["from_state"] = "ARCHIVED"
    transition["to_state"] = "RUNNING"
    assert "invalid_transition_from_archived:RUNNING" in validator().validate_definition(definition)["errors"]


def test_definition_hash_detects_mutation():
    definition = valid_definition()
    definition["definition_hash"] = CanonicalWorkflowValidator.definition_hash(definition)
    assert validator().validate_definition(definition)["valid"] is True
    definition["description"] = "mutated"
    assert "definition_hash_mismatch" in validator().validate_definition(definition)["errors"]


def test_paused_run_is_schema_valid_and_bound_to_immutable_definition():
    definition = valid_definition()
    run = valid_paused_run(definition)
    result = validator().validate_run(run, definition)
    assert result["valid"] is True
    run["definition_hash"] = "0" * 64
    assert "run_definition_hash_mismatch" in validator().validate_run(run, definition)["errors"]


def test_paused_run_requires_complete_checkpoint_and_linked_audit():
    definition = valid_definition()
    run = valid_paused_run(definition)
    run["rollback_point_reference"] = ""
    run["audit_events"][0]["workflow_run_id"] = "other-run"
    errors = validator().validate_run(run, definition)["errors"]
    assert "paused_run_missing:rollback_point_reference" in errors
    assert "audit_run_link_mismatch:event-001" in errors

    run = valid_paused_run(definition)
    run["audit_events"] = []
    assert "run_audit_events_missing" in validator().validate_run(run, definition)["errors"]


def test_error_retry_approval_and_completion_audit_events_are_typed_and_linked():
    definition = valid_definition()
    for event_type in ("step_failed", "retry_started", "approval_granted", "workflow_completed"):
        run = valid_paused_run(definition)
        event = dict(run["audit_events"][0])
        event["event_id"] = f"event-{event_type}"
        event["event_type"] = event_type
        if event_type in {"step_failed", "retry_started"}:
            event["error_reference"] = "error:001"
        if event_type == "approval_granted":
            event["approval_reference"] = "resume_gate"
        run["audit_events"].append(event)
        result = validator().validate_run(run, definition)
        assert not any(error.startswith("unknown_run_audit_event:") for error in result["errors"])
        assert not any(error.startswith("audit_run_link_mismatch:") for error in result["errors"])


def test_run_approval_separates_requester_and_approver():
    definition = valid_definition()
    run = valid_paused_run(definition)
    run["approvals"][0]["approved_by"] = ["workflow-owner-1"]
    errors = validator().validate_run(run, definition)["errors"]
    assert "self_approval_forbidden:resume_gate:workflow-owner-1" in errors


def test_resume_contract_accepts_verified_checkpoint_and_rejects_expiry_or_gaps():
    definition = valid_definition()
    run = valid_paused_run(definition)
    instant = datetime(2026, 7, 18, 12, tzinfo=timezone.utc)
    assert validator().validate_resume(run, definition, now=instant)["valid"] is True

    run["approvals"][0]["valid_until"] = "2026-07-18T01:00:00Z"
    errors = validator().validate_resume(
        run,
        definition,
        now=instant,
        permissions_valid=False,
        artifacts_available=False,
    )["errors"]
    assert "resume_approval_expired:resume_gate" in errors
    assert "resume_check_failed:permissions_valid" in errors
    assert "resume_check_failed:artifacts_available" in errors


def test_resume_requires_paused_state():
    definition = valid_definition()
    run = valid_paused_run(definition)
    run["current_state"] = "RUNNING"
    assert "resume_requires_paused_state" in validator().validate_resume(run, definition)["errors"]


def test_transition_guard_checks_role_gate_capability_condition_and_evidence():
    check = validator().transition_allowed
    assert check("READY", "RUNNING")["reason"] == "actor_role_required"
    assert check("READY", "RUNNING", actor_role="reviewer")["reason"] == "actor_role_not_authorized"
    assert check("READY", "RUNNING", actor_role="executor")["reason"] == "required_approvals_missing"
    assert check(
        "READY",
        "RUNNING",
        actor_role="executor",
        granted_approvals={"governance_gate"},
    )["reason"] == "required_capabilities_missing"
    assert check(
        "READY",
        "RUNNING",
        actor_role="executor",
        granted_approvals={"governance_gate"},
        available_capabilities={"workflow.start"},
        condition_satisfied=False,
    )["reason"] == "transition_condition_not_satisfied"
    assert check(
        "COMPLETED",
        "VERIFIED",
        actor_role="reviewer",
        granted_approvals={"review_gate"},
        available_capabilities={"workflow.verify"},
    )["reason"] == "verified_requires_completed_and_evidence"
    assert check("ARCHIVED", "RUNNING")["reason"] == "archived_run_requires_new_instance"


def test_transition_guard_allows_fully_authorized_declared_transition():
    result = validator().transition_allowed(
        "READY",
        "RUNNING",
        actor_role="executor",
        granted_approvals={"governance_gate"},
        available_capabilities={"workflow.start"},
        condition_satisfied=True,
    )
    assert result == {"allowed": True, "transition_id": "ready_to_running"}


def test_validator_status_and_surface_are_read_only():
    instance = validator()
    status = instance.status()
    assert status["status"] == "implemented_with_limitations"
    assert status["mode"] == "explicit_definition_run_and_resume_validation"
    assert status["plans"] is False
    assert status["executes"] is False
    assert status["writes_audit"] is False
    assert status["writes_memory"] is False
    assert not hasattr(instance, "plan")
    assert not hasattr(instance, "execute")
    assert not hasattr(instance, "register_capability")


def test_canonical_registry_remains_single_and_workflow_capabilities_are_only_gaps():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads(
        (root / "24_config" / "capability_registry_34_1.json").read_text(encoding="utf-8-sig")
    )
    capability_ids = {
        item["capability_id"]
        for item in registry.get("capabilities", [])
        if isinstance(item, dict) and "capability_id" in item
    }
    assert not any(capability_id.startswith("workflow.") for capability_id in capability_ids)
    assert not (root / "24_config" / "canonical_workflow_capability_registry_1_0.json").exists()


def test_architecture_contracts_reference_existing_owners_without_duplication():
    root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (root / "24_config" / "canonical_workflow_framework_1_0.json").read_text(encoding="utf-8-sig")
    )
    assert set(config["integration_contracts"]) == {
        "cre",
        "execution_planner",
        "orchestrator_core",
        "cdg",
        "codeaf",
        "authentication",
        "cam",
        "audit_provenance",
    }
    assert config["does_not_plan"] is True
    assert config["does_not_execute"] is True
    assert config["does_not_resolve_capabilities"] is True


def test_productive_system_registers_cwf_status_without_runtime_wiring():
    source = (
        Path(__file__).resolve().parents[1]
        / "01_system"
        / "kontinuum"
        / "core"
        / "system.py"
    ).read_text(encoding="utf-8-sig")
    assert "self.canonical_workflow_framework = CanonicalWorkflowValidator(" in source
    assert 'self.agent_config["canonical_workflow_framework"]' in source
    assert '"canonical_workflow_framework": self.canonical_workflow_framework.status()' in source
    assert "self.execution_planner.canonical_workflow" not in source
    assert "self.orchestrator_core.canonical_workflow" not in source


if __name__ == "__main__":
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"{len(tests)} CWF tests passed")
