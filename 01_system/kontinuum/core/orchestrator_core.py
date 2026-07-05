from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OrchestratorError(ValueError):
    pass


class OrchestratorRuntimeError(OrchestratorError):
    pass


@dataclass
class ExecutionTask:
    task_id: str
    step_id: str
    capability_id: str
    expected_agent: str
    actual_agent: str = ""
    status: str = "pending"
    governance_decision: str = "pending"
    fallback_allowed: bool = False
    fallback_used: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionResult:
    task_id: str
    step_id: str
    capability_id: str
    expected_agent: str
    actual_agent: str
    status: str
    handled: bool
    answer: str = ""
    error: str = ""
    fallback_used: str = ""
    governance_decision: str = "allowed"
    review_handoff_ready: bool = False
    cmm_handoff_ready: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionRun:
    run_id: str
    plan_id: str
    request_id: str
    started_at: str
    finished_at: str
    status: str
    tasks: list[dict]
    results: list[dict]
    errors: list[dict]
    fallbacks: list[dict]
    governance_decisions: list[dict]
    review_handoff_ready: bool
    cmm_handoff_ready: bool
    parallel_groups: list[list[str]]
    started_steps: list[str]
    agent_status: dict[str, str]
    runtime_mode: str
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class ExecutionStepRun(ExecutionResult):
    """Compatibility alias for early Orchestrator Core 1.0 reports."""


class OrchestratorCore:
    """Execution runtime for validated ExecutionPlans.

    The core does not resolve capabilities, build plans, or freely search
    agents. It only executes expected agents named by validated plan steps.
    """

    VERSION = "1.0"
    SCHEMA_FILE = "orchestrator_runtime_schema_34_1.json"
    REQUIRED_PLAN_FIELDS = {
        "plan_id",
        "request_id",
        "status",
        "steps",
        "parallel_groups",
        "validation",
    }
    REQUIRED_STEP_FIELDS = {
        "step_id",
        "capability_id",
        "parallel_group",
        "expected_agent",
        "status",
        "validation",
    }

    def __init__(
        self,
        agents: list[Any] | tuple[Any, ...] | dict[str, Any] | None = None,
        fallback_registry: dict[str, list[str]] | None = None,
        governance_context: dict | None = None,
        timeout_seconds: float = 10.0,
        schema_path: str | Path | None = None,
    ):
        self.agents = self._agent_map(agents)
        self.fallback_registry = fallback_registry or {}
        self.governance_context = governance_context or {}
        self.timeout_seconds = float(timeout_seconds)
        self.schema_path = Path(schema_path) if schema_path else None
        self.last_run: dict = {}

    def run(self, execution_plan: dict, payload: dict | str | None = None) -> dict:
        validation = self.validate_plan(execution_plan)
        started_at = self._now()
        if not validation["ok"]:
            run = self._blocked_run(execution_plan, validation, started_at)
            self.last_run = run
            return run

        steps_by_id = {step["step_id"]: step for step in execution_plan.get("steps", [])}
        tasks: list[dict] = []
        results: list[dict] = []
        errors: list[dict] = []
        fallbacks: list[dict] = []
        governance_decisions: list[dict] = []
        agent_status: dict[str, str] = {}
        started_steps: list[str] = []

        for group in execution_plan.get("parallel_groups", []):
            for step_id in group:
                step = steps_by_id.get(step_id)
                if not step:
                    errors.append({"step_id": step_id, "error": "step_missing_from_plan"})
                    continue
                task, result = self._execute_step(step, payload)
                tasks.append(task.to_dict())
                results.append(result.to_dict())
                started_steps.append(step_id)
                agent_name = result.actual_agent or result.expected_agent
                if agent_name:
                    agent_status[agent_name] = result.status
                governance_decisions.append({
                    "step_id": step_id,
                    "decision": result.governance_decision,
                    "governance_level": step.get("governance_level", "standard"),
                })
                if result.error:
                    errors.append({"step_id": step_id, "agent": agent_name, "error": result.error})
                if result.fallback_used:
                    fallbacks.append({
                        "step_id": step_id,
                        "from": result.expected_agent,
                        "to": result.fallback_used,
                        "status": result.status,
                    })

        status = self._overall_status(results, errors)
        finished_at = self._now()
        review_ready = status == "completed"
        run = ExecutionRun(
            run_id=self._run_id(execution_plan.get("plan_id", ""), started_at),
            plan_id=str(execution_plan.get("plan_id", "")),
            request_id=str(execution_plan.get("request_id", "")),
            started_at=started_at,
            finished_at=finished_at,
            status=status,
            tasks=tasks,
            results=results,
            errors=errors,
            fallbacks=fallbacks,
            governance_decisions=governance_decisions,
            review_handoff_ready=review_ready,
            cmm_handoff_ready=False,
            parallel_groups=[list(group) for group in execution_plan.get("parallel_groups", [])],
            started_steps=started_steps,
            agent_status=agent_status,
            runtime_mode="validated_execution_plan_runtime",
            sources=["ExecutionPlan", "OrchestratorCore"],
        ).to_dict()
        self.last_run = run
        return run

    def validate_plan(self, execution_plan: dict) -> dict:
        if not isinstance(execution_plan, dict):
            return self._invalid("plan_not_dict")
        missing = sorted(self.REQUIRED_PLAN_FIELDS - set(execution_plan))
        if missing:
            return self._invalid("missing_plan_fields", missing=missing)
        if not execution_plan.get("plan_id") or not execution_plan.get("request_id"):
            return self._invalid("missing_plan_identity")
        if execution_plan.get("status") != "ready":
            return self._invalid("plan_not_ready", status=execution_plan.get("status", ""))
        validation = execution_plan.get("validation") or {}
        if not validation.get("ok", False):
            return self._invalid("plan_validation_not_ok")
        steps = execution_plan.get("steps")
        if not isinstance(steps, list) or not steps:
            return self._invalid("empty_plan")
        parallel_groups = execution_plan.get("parallel_groups")
        if not isinstance(parallel_groups, list) or not parallel_groups:
            return self._invalid("empty_or_invalid_parallel_groups")
        known_step_ids = {step.get("step_id") for step in steps if isinstance(step, dict)}
        grouped_step_ids = {step_id for group in parallel_groups if isinstance(group, list) for step_id in group}
        if known_step_ids != grouped_step_ids:
            return self._invalid("parallel_groups_do_not_match_steps")
        for step in steps:
            if not isinstance(step, dict):
                return self._invalid("step_not_dict")
            step_missing = sorted(self.REQUIRED_STEP_FIELDS - set(step))
            if step_missing:
                return self._invalid("missing_step_fields", step_id=step.get("step_id", ""), missing=step_missing)
            if step.get("status") == "blocked":
                return self._invalid("blocked_step", step_id=step.get("step_id", ""))
            if not step.get("expected_agent"):
                return self._invalid("missing_expected_agent", step_id=step.get("step_id", ""))
            step_validation = step.get("validation") or {}
            if step_validation.get("governance_ok") is False:
                return self._invalid("step_governance_blocked", step_id=step.get("step_id", ""))
            if step_validation.get("execution_allowed_by_resolution") is False:
                return self._invalid("execution_not_allowed_by_plan", step_id=step.get("step_id", ""))
        if not self._governance_context_ok():
            return self._invalid("runtime_governance_blocked")
        return {"ok": True, "reason": "validated", "errors": []}

    def status(self) -> dict:
        return {
            "version": self.VERSION,
            "mode": "validated_execution_plan_runtime",
            "schema_path": str(self.schema_path) if self.schema_path else "",
            "schema_present": bool(self.schema_path and self.schema_path.exists()),
            "agents_registered": sorted(self.agents),
            "executes_only_validated_plans": True,
            "plans_itself": False,
            "calls_cre": False,
            "free_agent_search": False,
            "writes_cmm": False,
            "implements_review_logic": False,
            "last_run_id": self.last_run.get("run_id", ""),
            "last_run_status": self.last_run.get("status", ""),
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Orchestrator Core 1.0 Status:",
            f"- Modus: {status['mode']}",
            f"- Schema: {status['schema_path']}",
            f"- Schema vorhanden: {'ja' if status['schema_present'] else 'nein'}",
            f"- registrierte Agenten: {len(status['agents_registered'])}",
            f"- plant selbst: {'ja' if status['plans_itself'] else 'nein'}",
            f"- ruft CRE auf: {'ja' if status['calls_cre'] else 'nein'}",
            f"- freie Agentensuche: {'ja' if status['free_agent_search'] else 'nein'}",
            f"- letzter Run: {status['last_run_id'] or '-'} ({status['last_run_status'] or '-'})",
        ])

    def _execute_step(self, step: dict, payload: dict | str | None) -> tuple[ExecutionTask, ExecutionResult]:
        started = self._now()
        expected_agent = str(step.get("expected_agent", ""))
        task = ExecutionTask(
            task_id=self._task_id(step),
            step_id=str(step.get("step_id", "")),
            capability_id=str(step.get("capability_id", "")),
            expected_agent=expected_agent,
            governance_decision="allowed" if self._step_governance_ok(step) else "blocked",
            fallback_allowed=self._fallback_allowed(step),
            started_at=started,
        )
        if not self._step_governance_ok(step):
            return self._finish_task(task, step, "", "governance_blocked", False, error="blocked_governance", governance="blocked")

        result = self._call_agent(expected_agent, self._prompt_for_step(step, payload))
        if result["status"] == "completed":
            return self._finish_task(task, step, expected_agent, "completed", True, answer=result["answer"])

        fallback = self._fallback_for(step, expected_agent)
        if fallback:
            fallback_result = self._call_agent(fallback, self._prompt_for_step(step, payload))
            if fallback_result["status"] == "completed":
                return self._finish_task(
                    task,
                    step,
                    fallback,
                    "completed_with_fallback",
                    True,
                    answer=fallback_result["answer"],
                    fallback=fallback,
                )
            return self._finish_task(
                task,
                step,
                fallback,
                "failed",
                False,
                error=fallback_result["error"] or result["error"],
                fallback=fallback,
            )

        return self._finish_task(task, step, expected_agent, "failed", False, error=result["error"])

    def _call_agent(self, agent_name: str, prompt: str) -> dict:
        agent = self.agents.get(agent_name)
        if not agent:
            return {"status": "failed", "handled": False, "answer": "", "error": "missing_agent"}
        if getattr(agent, "available", True) is False:
            return {"status": "failed", "handled": False, "answer": "", "error": "agent_unavailable"}
        started = time.perf_counter()
        try:
            result = agent.handle(prompt)
        except Exception as exc:
            return {"status": "failed", "handled": False, "answer": "", "error": f"agent_error:{exc}"}
        duration = time.perf_counter() - started
        if duration > self.timeout_seconds:
            return {"status": "failed", "handled": False, "answer": "", "error": "timeout"}
        if result is None:
            return {"status": "failed", "handled": False, "answer": "", "error": "agent_no_response"}
        if not hasattr(result, "handled") or not hasattr(result, "answer"):
            return {"status": "failed", "handled": False, "answer": "", "error": "invalid_result"}
        handled = bool(getattr(result, "handled", False))
        answer = str(getattr(result, "answer", "") or "")
        if not handled:
            return {"status": "failed", "handled": False, "answer": answer, "error": "handled_false"}
        if not answer:
            return {"status": "failed", "handled": True, "answer": "", "error": "empty_result"}
        return {"status": "completed", "handled": True, "answer": answer, "error": ""}

    def _fallback_for(self, step: dict, expected_agent: str) -> str:
        if not self._fallback_allowed(step):
            return ""
        keys = [str(step.get("step_id", "")), str(step.get("capability_id", "")), expected_agent]
        for key in keys:
            for fallback in self.fallback_registry.get(key, []):
                if fallback in self.agents and fallback != expected_agent:
                    return fallback
        return ""

    def _fallback_allowed(self, step: dict) -> bool:
        if not self.governance_context.get("fallbacks_allowed", True):
            return False
        if str(step.get("governance_level", "standard")) == "foundation":
            return False
        return self._step_governance_ok(step)

    def _step_governance_ok(self, step: dict) -> bool:
        validation = step.get("validation") or {}
        return bool(validation.get("governance_ok", True)) and self._governance_context_ok()

    def _governance_context_ok(self) -> bool:
        return all(bool(self.governance_context.get(key, True)) for key in (
            "foundation_rules_ok",
            "governance_rules_ok",
            "cam_status_ok",
            "ccp_status_ok",
        ))

    def _prompt_for_step(self, step: dict, payload: dict | str | None) -> str:
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict):
            return str(
                payload.get(step.get("step_id", ""))
                or payload.get(step.get("capability_id", ""))
                or payload.get("text", "")
                or step.get("capability_id", "")
            )
        return str(step.get("capability_id", ""))

    def _finish_task(
        self,
        task: ExecutionTask,
        step: dict,
        actual_agent: str,
        status: str,
        handled: bool,
        answer: str = "",
        error: str = "",
        fallback: str = "",
        governance: str = "allowed",
    ) -> tuple[ExecutionTask, ExecutionResult]:
        finished = self._now()
        task.actual_agent = actual_agent
        task.status = status
        task.finished_at = finished
        task.duration_seconds = max(0.0, self._parse_time(finished) - self._parse_time(task.started_at))
        task.fallback_used = fallback
        task.governance_decision = governance
        result = ExecutionResult(
            task_id=task.task_id,
            step_id=task.step_id,
            capability_id=str(step.get("capability_id", "")),
            expected_agent=task.expected_agent,
            actual_agent=actual_agent,
            status=status,
            handled=handled,
            answer=answer,
            error=error,
            fallback_used=fallback,
            governance_decision=governance,
            review_handoff_ready=bool(handled and not error),
            cmm_handoff_ready=False,
        )
        return task, result

    def _blocked_run(self, plan: dict, validation: dict, started_at: str) -> dict:
        finished_at = self._now()
        run = ExecutionRun(
            run_id=self._run_id(str(plan.get("plan_id", "invalid-plan")) if isinstance(plan, dict) else "invalid-plan", started_at),
            plan_id=str(plan.get("plan_id", "")) if isinstance(plan, dict) else "",
            request_id=str(plan.get("request_id", "")) if isinstance(plan, dict) else "",
            started_at=started_at,
            finished_at=finished_at,
            status="rejected",
            tasks=[],
            results=[],
            errors=[{"error": validation.get("reason", "invalid_plan"), **validation}],
            fallbacks=[],
            governance_decisions=[],
            review_handoff_ready=False,
            cmm_handoff_ready=False,
            parallel_groups=[],
            started_steps=[],
            agent_status={},
            runtime_mode="validated_execution_plan_runtime",
            sources=["ExecutionPlan", "OrchestratorCore"],
        ).to_dict()
        return run

    @staticmethod
    def _agent_map(agents) -> dict[str, Any]:
        if not agents:
            return {}
        if isinstance(agents, dict):
            return dict(agents)
        return {str(agent.name): agent for agent in agents if getattr(agent, "name", "")}

    @staticmethod
    def _overall_status(results: list[dict], errors: list[dict]) -> str:
        if not results:
            return "rejected"
        if errors:
            return "completed_with_errors" if any(item.get("handled") for item in results) else "failed"
        return "completed"

    @staticmethod
    def _invalid(reason: str, **extra) -> dict:
        return {"ok": False, "reason": reason, "errors": [extra] if extra else []}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _parse_time(value: str) -> float:
        try:
            return datetime.fromisoformat(value).timestamp()
        except ValueError:
            return 0.0

    @staticmethod
    def _run_id(plan_id: str, started_at: str) -> str:
        payload = f"{plan_id}|{started_at}"
        return "run-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _task_id(step: dict) -> str:
        return "task-" + str(step.get("step_id", "unknown"))
