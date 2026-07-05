from __future__ import annotations

import os
import sys
import time
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.base_agent import AgentResult
from kontinuum.core.orchestrator_core import (
    ExecutionResult,
    ExecutionRun,
    ExecutionTask,
    OrchestratorCore,
    OrchestratorError,
)


class FakeAgent:
    def __init__(
        self,
        name: str,
        handled: bool = True,
        answer: str = "ok",
        delay: float = 0.0,
        fail: bool = False,
        available: bool = True,
        invalid: bool = False,
        no_response: bool = False,
    ):
        self.name = name
        self.handled = handled
        self.answer = answer
        self.delay = delay
        self.fail = fail
        self.available = available
        self.invalid = invalid
        self.no_response = no_response
        self.calls = 0

    def handle(self, prompt: str):
        self.calls += 1
        if self.delay:
            time.sleep(self.delay)
        if self.fail:
            raise RuntimeError("agent failed")
        if self.no_response:
            return None
        if self.invalid:
            return {"handled": True, "answer": "not-an-agent-result"}
        return AgentResult(self.name, self.handled, f"{self.answer}:{prompt}" if self.answer else "")


def step(
    step_id: str,
    capability: str,
    agent: str,
    group: int = 1,
    governance_ok: bool = True,
    execution_allowed: bool = True,
    status: str = "planned",
) -> dict:
    return {
        "step_id": step_id,
        "capability_id": capability,
        "order": int(step_id.rsplit("_", 1)[-1]),
        "parallel_group": group,
        "dependencies": [],
        "governance_level": "standard",
        "expected_agent": agent,
        "status": status,
        "priority": 40,
        "validation": {
            "capability_known": True,
            "governance_ok": governance_ok,
            "foundation_rules_ok": governance_ok,
            "cam_status_ok": governance_ok,
            "ccp_status_ok": governance_ok,
            "resolution_priority": "normal",
            "execution_allowed_by_resolution": execution_allowed,
        },
    }


def plan(*steps: dict, status: str = "ready", validation_ok: bool = True) -> dict:
    groups: dict[int, list[str]] = {}
    for item in steps:
        groups.setdefault(item["parallel_group"], []).append(item["step_id"])
    return {
        "plan_id": "plan-test",
        "request_id": "request-test",
        "created_at": "2026-07-05T00:00:00+00:00",
        "required_capabilities": [item["capability_id"] for item in steps],
        "order": [item["step_id"] for item in steps],
        "parallel_groups": [groups[key] for key in sorted(groups)],
        "estimated_priority": "normal",
        "governance_level": "standard",
        "expected_agents": sorted({item["expected_agent"] for item in steps if item["expected_agent"]}),
        "status": status,
        "steps": list(steps),
        "validation": {
            "ok": validation_ok,
            "checks": {
                "foundation_rules_ok": validation_ok,
                "governance_rules_ok": validation_ok,
                "cam_status_ok": validation_ok,
                "ccp_status_ok": validation_ok,
                "capability_resolution_complete": validation_ok,
                "missing_agents": True,
                "cycles": True,
                "duplicate_steps": True,
                "duplicate_capabilities": True,
            },
        },
        "sources": ["CapabilityResolutionEngine", "ExecutionPlanner"],
    }


assert issubclass(OrchestratorError, ValueError)
assert ExecutionTask.__name__ == "ExecutionTask"
assert ExecutionResult.__name__ == "ExecutionResult"
assert ExecutionRun.__name__ == "ExecutionRun"

primary = FakeAgent("primary_agent", True, "done")
runtime = OrchestratorCore([primary], schema_path=ROOT / "24_config" / "orchestrator_runtime_schema_34_1.json")
valid_plan = plan(step("step_001", "dialogue.answer", "primary_agent"))
run = runtime.run(valid_plan, {"step_001": "hello"})
assert run["status"] == "completed"
assert run["plan_id"] == "plan-test"
assert run["request_id"] == "request-test"
assert run["started_steps"] == ["step_001"]
assert run["tasks"][0]["task_id"] == "task-step_001"
assert run["results"][0]["handled"] is True
assert run["results"][0]["answer"] == "done:hello"
assert run["review_handoff_ready"] is True
assert run["cmm_handoff_ready"] is False
assert primary.calls == 1

empty_run = runtime.run(plan())
assert empty_run["status"] == "rejected"
assert empty_run["errors"][0]["reason"] == "empty_plan"

blocked_plan = plan(step("step_001", "dialogue.answer", "primary_agent"), status="blocked")
blocked_run = runtime.run(blocked_plan)
assert blocked_run["status"] == "rejected"
assert blocked_run["started_steps"] == []

invalid_run = runtime.run({"plan_id": "x"})
assert invalid_run["status"] == "rejected"
assert invalid_run["errors"][0]["reason"] == "missing_plan_fields"

identityless_run = runtime.run({**valid_plan, "plan_id": ""})
assert identityless_run["status"] == "rejected"
assert identityless_run["errors"][0]["reason"] == "missing_plan_identity"

missing_agent_run = OrchestratorCore([]).run(valid_plan)
assert missing_agent_run["status"] == "failed"
assert missing_agent_run["errors"][0]["error"] == "missing_agent"

unavailable_run = OrchestratorCore([FakeAgent("primary_agent", available=False)]).run(valid_plan)
assert unavailable_run["status"] == "failed"
assert unavailable_run["errors"][0]["error"] == "agent_unavailable"

no_response_run = OrchestratorCore([FakeAgent("primary_agent", no_response=True)]).run(valid_plan)
assert no_response_run["status"] == "failed"
assert no_response_run["errors"][0]["error"] == "agent_no_response"

invalid_result_run = OrchestratorCore([FakeAgent("primary_agent", invalid=True)]).run(valid_plan)
assert invalid_result_run["status"] == "failed"
assert invalid_result_run["errors"][0]["error"] == "invalid_result"

unhandled = FakeAgent("primary_agent", False, "no")
fallback = FakeAgent("fallback_agent", True, "fallback")
fallback_runtime = OrchestratorCore(
    [unhandled, fallback],
    fallback_registry={"dialogue.answer": ["fallback_agent"]},
)
fallback_run = fallback_runtime.run(valid_plan, {"text": "fallback prompt"})
assert fallback_run["status"] == "completed"
assert fallback_run["results"][0]["status"] == "completed_with_fallback"
assert fallback_run["fallbacks"][0]["to"] == "fallback_agent"
assert unhandled.calls == 1
assert fallback.calls == 1

no_fallback_run = OrchestratorCore([FakeAgent("primary_agent", False, "no")]).run(valid_plan)
assert no_fallback_run["status"] == "failed"
assert no_fallback_run["errors"][0]["error"] == "handled_false"
assert no_fallback_run["fallbacks"] == []

timeout_agent = FakeAgent("primary_agent", True, "late", delay=0.02)
timeout_run = OrchestratorCore([timeout_agent], timeout_seconds=0.001).run(valid_plan)
assert timeout_run["status"] == "failed"
assert timeout_run["errors"][0]["error"] == "timeout"

governance_plan = plan(step("step_001", "git.status", "primary_agent", governance_ok=False), validation_ok=True)
governance_run = runtime.run(governance_plan)
assert governance_run["status"] == "rejected"
assert governance_run["errors"][0]["reason"] == "step_governance_blocked"

execution_blocked_plan = plan(step("step_001", "git.status", "primary_agent", execution_allowed=False))
execution_blocked_run = runtime.run(execution_blocked_plan)
assert execution_blocked_run["status"] == "rejected"
assert execution_blocked_run["errors"][0]["reason"] == "execution_not_allowed_by_plan"

runtime_blocked_run = OrchestratorCore([primary], governance_context={"governance_rules_ok": False}).run(valid_plan)
assert runtime_blocked_run["status"] == "rejected"
assert runtime_blocked_run["errors"][0]["reason"] == "runtime_governance_blocked"

parallel_plan = plan(
    step("step_001", "file.read", "primary_agent", group=1),
    step("step_002", "git.status", "primary_agent", group=1),
    step("step_003", "code.inspect", "primary_agent", group=2),
)
parallel_run = runtime.run(parallel_plan, {"text": "parallel"})
assert parallel_run["parallel_groups"] == [["step_001", "step_002"], ["step_003"]]
assert parallel_run["started_steps"] == ["step_001", "step_002", "step_003"]

bad_groups = dict(valid_plan)
bad_groups["parallel_groups"] = [["step_999"]]
bad_group_run = runtime.run(bad_groups)
assert bad_group_run["status"] == "rejected"
assert bad_group_run["errors"][0]["reason"] == "parallel_groups_do_not_match_steps"


class ForbiddenCRE:
    def resolve(self, *args, **kwargs):
        raise AssertionError("OrchestratorCore must not call CRE.")


class ForbiddenPlanner:
    def plan(self, *args, **kwargs):
        raise AssertionError("OrchestratorCore must not plan.")


guarded = OrchestratorCore([primary])
guarded.cre = ForbiddenCRE()
guarded.planner = ForbiddenPlanner()
guarded_run = guarded.run(valid_plan, "guarded")
assert guarded_run["status"] == "completed"
assert guarded.status()["plans_itself"] is False
assert guarded.status()["calls_cre"] is False
assert guarded.status()["free_agent_search"] is False
assert guarded.status()["writes_cmm"] is False
assert guarded.status()["implements_review_logic"] is False

unplanned_agent = FakeAgent("unplanned_agent", True, "should-not-run")
strict_run = OrchestratorCore([primary, unplanned_agent]).run(valid_plan, "strict")
assert strict_run["status"] == "completed"
assert primary.calls >= 1
assert unplanned_agent.calls == 0

schema = (ROOT / "24_config" / "orchestrator_runtime_schema_34_1.json").read_text(encoding="utf-8-sig")
assert '"ExecutionTask"' in schema
assert '"ExecutionResult"' in schema
assert '"calls_cre": false' in schema
assert '"plans": false' in schema
assert '"free_agent_search": false' in schema

print("Orchestrator Core 1.0 tests passed")
