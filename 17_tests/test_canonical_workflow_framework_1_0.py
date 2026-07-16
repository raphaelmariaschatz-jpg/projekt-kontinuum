# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from kontinuum.core.canonical_workflow_validator import CanonicalWorkflowValidator


KNOWN_CAPABILITIES = {
    "governance.architecture",
    "code.inspect",
}


def valid_definition() -> dict:
    return {
        "workflow_id": "cwf.example",
        "workflow_name": "CWF Example",
        "workflow_version": "1.0",
        "workflow_type": "APPROVAL",
        "status": "DRAFT",
        "owner": "workflow_owner",
        "risk_class": "controlled",
        "definition_hash": "",
        "created_at": "2026-07-16T00:00:00Z",
        "updated_at": "2026-07-16T00:00:00Z",
        "inputs": [],
        "outputs": [],
        "audit_requirements": ["workflow_validated"],
        "steps": [
            {
                "step_id": "analyse",
                "step_name": "Analyse",
                "step_type": "VALIDATION",
                "sequence": 1,
                "required_inputs": [],
                "produced_outputs": ["analysis_report"],
                "required_capabilities": ["governance.architecture"],
                "assigned_role": "reviewer",
                "preconditions": ["definition_present"],
                "postconditions": ["analysis_complete"],
                "timeout_policy": {
                    "timeout_seconds": 300,
                    "on_timeout": "FAIL",
                    "timeout_error_code": "TIMEOUT",
                    "escalation_required": False,
                },
                "retry_policy": {
                    "max_attempts": 1,
                    "retry_on": ["TIMEOUT"],
                    "requires_idempotency": True,
                },
                "rollback_supported": False,
                "compensation_supported": False,
                "irreversible": False,
                "idempotent": True,
                "next_steps": ["approval"],
                "audit_required": True,
            },
            {
                "step_id": "approval",
                "step_name": "Approval",
                "step_type": "APPROVAL",
                "sequence": 2,
                "required_inputs": ["analysis_report"],
                "produced_outputs": ["approval_decision"],
                "required_capabilities": ["workflow.verify"],
                "assigned_role": "approver",
                "preconditions": ["analysis_complete"],
                "postconditions": ["approval_recorded"],
                "timeout_policy": {
                    "timeout_seconds": 600,
                    "on_timeout": "ESCALATE",
                    "timeout_error_code": "APPROVAL_TIMEOUT",
                    "escalation_required": True,
                },
                "retry_policy": {
                    "max_attempts": 0,
                    "retry_on": [],
                    "requires_idempotency": True,
                },
                "rollback_supported": False,
                "compensation_supported": False,
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
                "condition": "definition_present",
                "authorized_roles": ["workflow_owner"],
                "required_approvals": [],
                "required_capabilities": ["workflow.validate"],
                "audit_event": "workflow_validated",
                "to_step": "approval",
            }
        ],
    }


def test_valid_definition_warns_about_missing_workflow_capabilities():
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES, capability_mode="warn").validate_definition(valid_definition())
    assert result["valid"] is True
    assert "capability_gap:workflow.validate" in result["warnings"]
    assert "capability_gap:workflow.verify" in result["warnings"]


def test_capability_gap_can_be_error_without_registering_capability():
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES, capability_mode="error").validate_definition(valid_definition())
    assert result["valid"] is False
    assert "capability_gap:workflow.validate" in result["errors"]


def test_missing_workflow_id_is_rejected():
    definition = valid_definition()
    definition["workflow_id"] = ""
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "workflow_id_empty" in result["errors"]


def test_duplicate_step_id_is_rejected():
    definition = valid_definition()
    definition["steps"][1]["step_id"] = "analyse"
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "duplicate_step_id:analyse" in result["errors"]


def test_unknown_step_type_is_rejected():
    definition = valid_definition()
    definition["steps"][0]["step_type"] = "MAGIC"
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "unknown_step_type:analyse:MAGIC" in result["errors"]


def test_invalid_transition_to_verified_is_rejected():
    definition = valid_definition()
    definition["transitions"][0]["from_state"] = "DRAFT"
    definition["transitions"][0]["to_state"] = "VERIFIED"
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "invalid_transition:DRAFT_to_VERIFIED" in result["errors"]


def test_ready_to_running_requires_approval():
    definition = valid_definition()
    definition["transitions"][0]["from_state"] = "READY"
    definition["transitions"][0]["to_state"] = "RUNNING"
    definition["transitions"][0]["required_approvals"] = []
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "ready_to_running_requires_approval" in result["errors"]


def test_archived_cannot_resume_directly():
    definition = valid_definition()
    definition["transitions"][0]["from_state"] = "ARCHIVED"
    definition["transitions"][0]["to_state"] = "RUNNING"
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "invalid_transition_from_archived:RUNNING" in result["errors"]


def test_negative_retry_is_rejected():
    definition = valid_definition()
    definition["steps"][0]["retry_policy"]["max_attempts"] = -1
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "retry_negative_attempts:analyse" in result["errors"]


def test_unbounded_retry_is_rejected_by_upper_bound():
    definition = valid_definition()
    definition["steps"][0]["retry_policy"]["max_attempts"] = 999
    result = CanonicalWorkflowValidator(KNOWN_CAPABILITIES).validate_definition(definition)
    assert "retry_exceeds_upper_bound:analyse" in result["errors"]


def test_validator_does_not_plan_or_execute():
    validator = CanonicalWorkflowValidator(KNOWN_CAPABILITIES)
    assert not hasattr(validator, "plan")
    assert not hasattr(validator, "run")


if __name__ == "__main__":
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"{len(tests)} CWF tests passed")
