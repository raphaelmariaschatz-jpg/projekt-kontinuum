from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.execution_planner import ExecutionPlanner


def resolution(
    capability_id: str,
    agent: str = "dialogue_agent",
    priority: int = 40,
    governance_level: str = "standard",
    gate_ok: bool = True,
    resolution_priority: str = "normal",
    known: bool = True,
) -> dict:
    capability = None
    if known:
        capability = {
            "capability_id": capability_id,
            "priority": priority,
            "governance_level": governance_level,
        }
    return {
        "text": capability_id,
        "required_capability": capability_id,
        "capability": capability,
        "recommended_agent": agent,
        "candidate_agents": ([{"id": agent, "name": agent}] if agent else []),
        "governance_required": governance_level in {"governance_required", "foundation"},
        "governance_gate": {
            "ok": gate_ok,
            "checks": {
                "foundation_rules_ok": gate_ok,
                "cam_status_ok": gate_ok,
                "ccp_status_ok": gate_ok,
            },
        },
        "priority": resolution_priority,
        "execution_allowed": gate_ok and bool(agent),
        "sources": ["test"],
    }


planner = ExecutionPlanner(schema_path=ROOT / "24_config" / "execution_plan_schema_34_1.json")

plan = planner.plan_from_resolutions(
    [
        resolution("dialogue.answer", "dialogue_agent", 20),
        resolution("file.read", "file_agent", 50),
    ],
    request_id="request-fixture",
    dependencies={"step_002": ["step_001"]},
)
assert plan["status"] == "ready"
assert plan["request_id"] == "request-fixture"
assert plan["required_capabilities"] == ["dialogue.answer", "file.read"]
assert plan["order"] == ["step_001", "step_002"]
assert plan["parallel_groups"] == [["step_001"], ["step_002"]]
assert plan["estimated_priority"] == "high"
assert plan["governance_level"] == "standard"
assert plan["validation"]["ok"]

parallel = planner.plan_from_resolutions(
    [
        resolution("file.read", "file_agent"),
        resolution("git.status", "git_agent"),
    ],
    request_id="request-parallel",
)
assert parallel["status"] == "ready"
assert parallel["parallel_groups"] == [["step_001", "step_002"]]

blocked = planner.plan_from_resolutions(
    [resolution("git.status", "git_agent", gate_ok=False, resolution_priority="blocked_by_governance")],
    request_id="request-blocked",
)
assert blocked["status"] == "blocked"
assert blocked["validation"]["blocked_governance"] == ["step_001"]
assert not blocked["validation"]["checks"]["capability_resolution_complete"]

unknown = planner.plan_from_resolutions(
    [resolution("capability.not_registered", "", known=False, resolution_priority="fallback_required")],
    request_id="request-unknown",
)
assert unknown["status"] == "blocked"
assert unknown["validation"]["unknown_capabilities"] == ["step_001"]

missing_agent = planner.plan_from_resolutions(
    [resolution("dialogue.answer", "")],
    request_id="request-missing-agent",
)
assert missing_agent["status"] == "blocked"
assert missing_agent["validation"]["missing_agents"] == ["step_001"]

cyclic = planner.plan_from_resolutions(
    [
        resolution("file.read", "file_agent"),
        resolution("code.inspect", "code_agent"),
    ],
    request_id="request-cycle",
    dependencies={"step_001": ["step_002"], "step_002": ["step_001"]},
)
assert cyclic["status"] == "blocked"
assert cyclic["validation"]["cycles"]

empty = planner.plan_from_resolutions([], request_id="request-empty")
assert empty["status"] == "empty"
assert empty["required_capabilities"] == []
assert empty["validation"]["empty_plan"]


class FakeCRE:
    def __init__(self):
        self.resolve_many_called = False
        self.execute_called = False

    def resolve_many(self, text, intents=None):
        self.resolve_many_called = True
        return [resolution("dialogue.answer", "dialogue_agent")]

    def execute(self):
        self.execute_called = True
        raise AssertionError("ExecutionPlanner must not execute agents.")


fake_cre = FakeCRE()
cre_planner = ExecutionPlanner(
    capability_resolution_engine=fake_cre,
    schema_path=ROOT / "24_config" / "execution_plan_schema_34_1.json",
)
cre_plan = cre_planner.plan("Hallo", request_id="request-no-execution")
assert cre_plan["status"] == "ready"
assert fake_cre.resolve_many_called
assert not fake_cre.execute_called
assert cre_planner.status()["executes_agents"] is False

schema = (ROOT / "24_config" / "execution_plan_schema_34_1.json").read_text(encoding="utf-8-sig")
assert "ExecutionPlan" in schema
assert '"executes_agents": false' in schema

print("Execution Planner 1.0 tests passed")
