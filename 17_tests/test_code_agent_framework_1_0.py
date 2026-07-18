from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.code_agent_framework import CanonicalCodeAgentFramework
from kontinuum.core.system import KontinuumSystem


def task() -> dict:
    return {
        "task_id": "CODEAF-TASK-TEST-001",
        "title": "Inspect framework status",
        "goal": "Produce a read-only architecture report",
        "rationale": "Verify the task contract without execution",
        "initial_state": "Known test fixture",
        "requester": "test-suite",
        "agent_identity": {
            "agent_id": "agent_code",
            "agent_run_id": "agent-run-test-001",
        },
        "agent_role": "ANALYSIS_AGENT",
        "allowed_capabilities": ["code.read", "code.search", "code.analyze", "report.create"],
        "permission_profile": "CODEAF-PERM-READ-ONLY",
        "operating_mode": "READ_ONLY",
        "allowed_scope": ["01_system/kontinuum/core"],
        "excluded_scope": ["02_versions", "09_backups"],
        "canonical_rules": ["deny_by_default"],
        "risk_class": "CODEAF-R0",
        "required_prechecks": ["git_status", "scope_check"],
        "planned_workflow": ["identify", "inspect", "report"],
        "test_requirements": ["schema_test"],
        "documentation_requirements": ["status_report"],
        "audit_requirements": ["task_reference"],
        "abort_conditions": ["scope_conflict"],
        "rollback_point": "not_required_for_read_only",
        "expected_results": ["read_only_report"],
        "approval_process": ["requester_approval"],
        "final_approval_reference": "",
        "final_report": "31_reports/test-only.md",
        "status": "READY",
    }


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.code_agent_framework
        assert isinstance(framework, CanonicalCodeAgentFramework)
        assert system.agent_config["code_agent_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["abbreviation"] == "CODEAF"
        assert status["roles"] == 9
        assert status["capabilities"] == 41
        assert status["permission_profiles"] == 3
        assert status["risk_classes"] == 6
        assert status["control_gates"] == 10
        assert status["agent_runtime_activation"] is False
        assert status["execution_authority"] is False
        assert status["autonomous_write"] is False
        assert status["self_approval"] is False
        assert status["existing_code_agent_changed"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["code_agent_framework"]["active"] is True

        with system.storage.connect() as database:
            memories_before = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        valid = framework.review_task(task())
        duplicate = framework.review_task(task())
        assert valid.review_id == duplicate.review_id
        assert valid.structurally_valid is True
        assert valid.violations == []
        assert len(valid.gate_results) == 10
        assert valid.gate_results[-1] == {
            "gate": "FINAL_APPROVAL_GATE",
            "passed": False,
        }
        assert valid.execution_authorized is False
        assert valid.final_approval_granted is False
        assert valid.task_executed is False
        assert valid.agent_runtime_activated is False
        assert valid.autonomous_write_enabled is False
        assert valid.direct_memory_write is False

        invalid_task = task()
        invalid_task["allowed_capabilities"] = ["code.read", "code.modify", "git.commit"]
        invalid = framework.review_task(invalid_task)
        assert invalid.structurally_valid is False
        assert any(item.startswith("explicitly_denied_capabilities:") for item in invalid.violations)
        assert any(item.startswith("capabilities_outside_profile:") for item in invalid.violations)
        assert any(item.startswith("mode_forbids_capabilities:") for item in invalid.violations)

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        code_agent_status = system.code_agent.status()
        assert code_agent_status["mode"] == "diagnostic_read_only"
        assert code_agent_status["read_only"] is True
    finally:
        system.close()

print("Canonical Code Agent Framework 1.0 tests passed")
