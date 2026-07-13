# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .capability_resolution_engine import CapabilityResolutionEngine
from .conversation import Intent
from .request_router import RouteDecision


class ExecutionPlanError(ValueError):
    pass


@dataclass
class ExecutionStep:
    step_id: str
    capability_id: str
    order: int
    parallel_group: int
    dependencies: list[str]
    governance_level: str
    expected_agent: str
    status: str
    priority: int
    validation: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionPlan:
    plan_id: str
    request_id: str
    created_at: str
    required_capabilities: list[str]
    order: list[str]
    parallel_groups: list[list[str]]
    estimated_priority: str
    governance_level: str
    expected_agents: list[str]
    status: str
    steps: list[dict]
    validation: dict
    sources: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class ExecutionPlanner:
    """Deterministic plan builder between CRE and future Orchestrator Core."""

    VERSION = "1.0"
    SCHEMA_FILE = "execution_plan_schema_34_1.json"
    BLOCKING_PRIORITIES = {"blocked_by_governance", "fallback_required", "capability_unresolved"}
    GOVERNANCE_RANK = {
        "standard": 0,
        "controlled": 1,
        "governance_required": 2,
        "foundation": 3,
    }

    def __init__(
        self,
        capability_resolution_engine: CapabilityResolutionEngine | None = None,
        path_tools=None,
        schema_path: str | Path | None = None,
        governance_context: dict | None = None,
    ):
        self.cre = capability_resolution_engine
        self.path_tools = path_tools
        self.schema_path = self._resolve_schema_path(schema_path, path_tools)
        self.governance_context = governance_context or {}
        self.last_plan: dict = {}

    def plan(
        self,
        text: str,
        intent: Intent | str | None = None,
        decision: RouteDecision | None = None,
        request_id: str | None = None,
        dependencies: dict[str, list[str]] | None = None,
    ) -> dict:
        if not self.cre:
            raise ExecutionPlanError("ExecutionPlanner benoetigt eine CapabilityResolutionEngine.")
        if hasattr(self.cre, "resolve_many"):
            resolutions = self.cre.resolve_many(text, [intent] if intent else None)
        else:
            resolutions = [self.cre.resolve(text, intent, decision)]
        if decision and len(resolutions) == 1:
            resolutions[0] = self.cre.resolve(text, intent, decision)
        return self.plan_from_resolutions(resolutions, request_id=request_id, dependencies=dependencies)

    def plan_from_resolutions(
        self,
        resolutions: Iterable[dict],
        request_id: str | None = None,
        dependencies: dict[str, list[str]] | None = None,
    ) -> dict:
        rows = [dict(item) for item in resolutions if item]
        created_at = datetime.now(timezone.utc).isoformat()
        request_id = request_id or self._request_id(rows)
        steps = self._build_steps(rows, dependencies or {})
        validation = self.validate_steps(steps, rows)
        status = "ready" if validation["ok"] and steps else "blocked"
        if not steps:
            status = "empty"
        plan = ExecutionPlan(
            plan_id=self._plan_id(request_id, rows, created_at),
            request_id=request_id,
            created_at=created_at,
            required_capabilities=[step.capability_id for step in steps],
            order=[step.step_id for step in sorted(steps, key=lambda item: item.order)],
            parallel_groups=self._parallel_groups(steps),
            estimated_priority=self._estimated_priority(steps, validation),
            governance_level=self._highest_governance_level(steps),
            expected_agents=sorted({step.expected_agent for step in steps if step.expected_agent}),
            status=status,
            steps=[step.to_dict() for step in steps],
            validation=validation,
            sources=["CapabilityResolutionEngine", "ExecutionPlanner"],
        ).to_dict()
        self.last_plan = plan
        return plan

    def validate_plan(self, plan: dict) -> dict:
        steps = [self._step_from_dict(item) for item in plan.get("steps", [])]
        return self.validate_steps(steps, [])

    def validate_steps(self, steps: list[ExecutionStep], resolutions: list[dict]) -> dict:
        duplicate_steps = self._duplicates([step.step_id for step in steps])
        duplicate_capabilities = self._duplicates([step.capability_id for step in steps])
        unknown_capabilities = [step.step_id for step in steps if step.validation.get("capability_known") is False]
        missing_agents = [step.step_id for step in steps if not step.expected_agent]
        blocked_governance = [step.step_id for step in steps if not step.validation.get("governance_ok", False)]
        unresolved = [step.step_id for step in steps if step.validation.get("resolution_priority") in self.BLOCKING_PRIORITIES]
        cycles = self._cycles(steps)
        checks = {
            "foundation_rules_ok": self._context_bool("foundation_rules_ok", True),
            "governance_rules_ok": self._context_bool("governance_rules_ok", True),
            "cam_status_ok": self._context_bool("cam_status_ok", True),
            "ccp_status_ok": self._context_bool("ccp_status_ok", True),
            "capability_resolution_complete": not unknown_capabilities and not unresolved,
            "missing_agents": not missing_agents,
            "cycles": not cycles,
            "duplicate_steps": not duplicate_steps,
            "duplicate_capabilities": not duplicate_capabilities,
        }
        return {
            "ok": bool(steps) and all(checks.values()) and not blocked_governance,
            "checks": checks,
            "unknown_capabilities": unknown_capabilities,
            "missing_agents": missing_agents,
            "blocked_governance": blocked_governance,
            "cycles": cycles,
            "duplicate_steps": duplicate_steps,
            "duplicate_capabilities": duplicate_capabilities,
            "empty_plan": not steps,
            "resolution_count": len(resolutions),
        }

    def status(self) -> dict:
        return {
            "version": self.VERSION,
            "mode": "deterministic_plan_only",
            "schema_path": str(self.schema_path) if self.schema_path else "",
            "schema_present": bool(self.schema_path and self.schema_path.exists()),
            "cre_connected": self.cre is not None,
            "executes_agents": False,
            "last_plan_id": self.last_plan.get("plan_id", ""),
            "last_plan_status": self.last_plan.get("status", ""),
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Execution Planner 1.0 Status:",
            f"- Modus: {status['mode']}",
            f"- Schema: {status['schema_path']}",
            f"- Schema vorhanden: {'ja' if status['schema_present'] else 'nein'}",
            f"- CRE angebunden: {'ja' if status['cre_connected'] else 'nein'}",
            f"- fuehrt Agenten aus: {'ja' if status['executes_agents'] else 'nein'}",
            f"- letzter Plan: {status['last_plan_id'] or '-'} ({status['last_plan_status'] or '-'})",
        ])

    def _build_steps(self, resolutions: list[dict], dependencies: dict[str, list[str]]) -> list[ExecutionStep]:
        steps: list[ExecutionStep] = []
        for index, resolution in enumerate(resolutions, start=1):
            capability = resolution.get("capability") or {}
            capability_id = resolution.get("required_capability") or capability.get("capability_id") or "unknown"
            step_id = f"step_{index:03d}"
            expected_agent = resolution.get("recommended_agent") or self._first_candidate_name(resolution)
            governance_gate = resolution.get("governance_gate") or {}
            governance_level = capability.get("governance_level") or ("governance_required" if resolution.get("governance_required") else "standard")
            validation = {
                "capability_known": bool(resolution.get("capability")),
                "governance_ok": bool(governance_gate.get("ok", False)),
                "foundation_rules_ok": bool((governance_gate.get("checks") or {}).get("foundation_rules_ok", True)),
                "cam_status_ok": bool((governance_gate.get("checks") or {}).get("cam_status_ok", True)),
                "ccp_status_ok": bool((governance_gate.get("checks") or {}).get("ccp_status_ok", True)),
                "resolution_priority": resolution.get("priority", ""),
                "execution_allowed_by_resolution": bool(resolution.get("execution_allowed", False)),
            }
            steps.append(ExecutionStep(
                step_id=step_id,
                capability_id=capability_id,
                order=index,
                parallel_group=0,
                dependencies=list(dependencies.get(step_id, dependencies.get(capability_id, []))),
                governance_level=governance_level,
                expected_agent=expected_agent,
                status="planned",
                priority=int(capability.get("priority", 100)),
                validation=validation,
            ))
        self._assign_parallel_groups(steps)
        return steps

    def _assign_parallel_groups(self, steps: list[ExecutionStep]) -> None:
        group_for_step: dict[str, int] = {}
        for step in sorted(steps, key=lambda item: item.order):
            if step.dependencies:
                dependency_groups = [group_for_step.get(dep, 0) for dep in step.dependencies]
                step.parallel_group = (max(dependency_groups) if dependency_groups else 0) + 1
            elif step.governance_level in {"governance_required", "foundation"}:
                step.parallel_group = step.order
            else:
                step.parallel_group = 1
            group_for_step[step.step_id] = step.parallel_group

    def _parallel_groups(self, steps: list[ExecutionStep]) -> list[list[str]]:
        groups: dict[int, list[str]] = {}
        for step in steps:
            groups.setdefault(step.parallel_group, []).append(step.step_id)
        return [sorted(groups[key]) for key in sorted(groups)]

    def _cycles(self, steps: list[ExecutionStep]) -> list[list[str]]:
        graph = {step.step_id: list(step.dependencies) for step in steps}
        cycles: list[list[str]] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, path: list[str]) -> None:
            if node in visiting:
                start = path.index(node) if node in path else 0
                cycles.append(path[start:] + [node])
                return
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph.get(node, []):
                if dependency in graph:
                    visit(dependency, path + [dependency])
            visiting.remove(node)
            visited.add(node)

        for step_id in graph:
            visit(step_id, [step_id])
        return cycles

    @staticmethod
    def _first_candidate_name(resolution: dict) -> str:
        candidates = resolution.get("candidate_agents") or []
        if not candidates:
            return ""
        return str(candidates[0].get("name") or candidates[0].get("id") or "")

    def _highest_governance_level(self, steps: list[ExecutionStep]) -> str:
        if not steps:
            return "none"
        return max((step.governance_level for step in steps), key=lambda item: self.GOVERNANCE_RANK.get(item, 0))

    @staticmethod
    def _estimated_priority(steps: list[ExecutionStep], validation: dict) -> str:
        if not steps:
            return "empty"
        if not validation.get("ok"):
            return "blocked"
        highest = min(step.priority for step in steps)
        if highest <= 20:
            return "high"
        if highest <= 50:
            return "normal"
        return "low"

    @staticmethod
    def _duplicates(values: list[str]) -> list[str]:
        seen: set[str] = set()
        duplicated: set[str] = set()
        for value in values:
            if value in seen:
                duplicated.add(value)
            seen.add(value)
        return sorted(duplicated)

    @staticmethod
    def _request_id(rows: list[dict]) -> str:
        text = "|".join(str(row.get("text", "")) for row in rows)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
        return f"request-{digest}"

    @staticmethod
    def _plan_id(request_id: str, rows: list[dict], created_at: str) -> str:
        payload = json.dumps({"request_id": request_id, "rows": rows, "created_at": created_at}, sort_keys=True, ensure_ascii=False)
        return "plan-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _step_from_dict(value: dict) -> ExecutionStep:
        return ExecutionStep(
            step_id=str(value.get("step_id", "")),
            capability_id=str(value.get("capability_id", "")),
            order=int(value.get("order", 0)),
            parallel_group=int(value.get("parallel_group", 0)),
            dependencies=list(value.get("dependencies", [])),
            governance_level=str(value.get("governance_level", "standard")),
            expected_agent=str(value.get("expected_agent", "")),
            status=str(value.get("status", "planned")),
            priority=int(value.get("priority", 100)),
            validation=dict(value.get("validation", {})),
        )

    def _context_bool(self, key: str, default: bool) -> bool:
        return bool(self.governance_context.get(key, default))

    @staticmethod
    def _resolve_schema_path(schema_path: str | Path | None, path_tools) -> Path | None:
        if schema_path:
            return Path(schema_path)
        if path_tools:
            return path_tools.paths()["config"] / ExecutionPlanner.SCHEMA_FILE
        return None