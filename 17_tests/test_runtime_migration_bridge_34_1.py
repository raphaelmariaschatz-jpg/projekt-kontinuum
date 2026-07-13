from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.application_services import PromptOrchestrator
from kontinuum.tools.path_tools import PathTools


class FakeConversation:
    def __init__(self):
        self.user = {"username": "Raphael"}
        self.turns = []

    def classify(self, text: str):
        return SimpleNamespace(name="dialogue", input_type="question")

    def log_turn(self, role, text, intent=None, agent=""):
        self.turns.append((role, text, agent))

    def context_for_agents(self):
        return {"turns": len(self.turns)}

    def local_truth_answer(self, intent):
        return None


class FakeMemoryCore:
    def __init__(self):
        self.observed = []

    def observe(self, text: str, owner: str = ""):
        self.observed.append((text, owner))
        return {"ok": True}


class FakeRequestRouter:
    def __init__(self):
        self.records = []
        self.last_decision = None

    def decide(self, text, intent):
        self.last_decision = SimpleNamespace(selected_agent="", request_class="dialogue", sources=[])
        return self.last_decision

    def record(self, text, decision, answer, agent):
        self.records.append((text, list(decision.sources), answer, agent))


class FakeCapabilityResolutionEngine:
    def resolve(self, text, intent, decision):
        return {
            "required_capability": "dialogue.answer",
            "recommended_agent": "dialogue",
            "execution_allowed": True,
        }


class FakeExecutionPlanner:
    def __init__(self, status="ready"):
        self.status = status

    def plan_from_resolutions(self, resolutions):
        return {
            "plan_id": "plan-test",
            "request_id": "request-test",
            "status": self.status,
            "steps": [],
            "parallel_groups": [],
            "validation": {"ok": self.status == "ready"},
        }


class FakeOrchestratorCore:
    def __init__(self, behavior="completed"):
        self.behavior = behavior
        self.called = False
        self.payload = None

    def run(self, plan, payload=None):
        self.called = True
        self.payload = payload
        if self.behavior == "error":
            raise RuntimeError("simulated runtime failure")
        return {
            "status": "completed",
            "results": [
                {
                    "handled": True,
                    "answer": "RUNTIME_PATH",
                    "actual_agent": "dialogue",
                    "expected_agent": "dialogue",
                }
            ],
            "errors": [],
        }


class FakeRecorder:
    def finish(self, answer, agent, intent):
        return f"{agent}:{answer}"


class FakeLocalKnowledge:
    def answer(self, text):
        return "OLD_DIRECT_PATH", "local_knowledge"


class NullAnswer:
    def answer(self, *args, **kwargs):
        return None


class NullIdentityRouter:
    def answer(self, text):
        return None


class NullAgentRouter:
    def route(self, *args, **kwargs):
        return None


class FakeSystem:
    version = "34.1"

    def __init__(self, root: Path, runtime_enabled: bool, plan_status="ready", runtime_behavior="completed"):
        self.path_tools = PathTools(root)
        self.path_tools.ensure_all()
        self.conversation = FakeConversation()
        self.agent_config = {"orchestrator_runtime_enabled": runtime_enabled}
        self.orchestrator_runtime_enabled = runtime_enabled
        self.orchestrator_runtime_fallbacks = []
        self.agents = []
        self.tools = {}
        self.search_mode = "Automatisch"
        self.memory_core = FakeMemoryCore()
        self.foundation_query = NullAnswer()
        self.foundation_memory = SimpleNamespace(explain_classification=lambda *args, **kwargs: "")
        self.foundation_knowledge_guard = object()
        self.identity_router = NullIdentityRouter()
        self._foundation_context = SimpleNamespace(decision_id=None)
        self.capability_resolution_engine = FakeCapabilityResolutionEngine()
        self.execution_planner = FakeExecutionPlanner(plan_status)
        self.orchestrator_core = FakeOrchestratorCore(runtime_behavior)
        self.search_router = SimpleNamespace(search=lambda *args, **kwargs: {"hits": []}, format=lambda result: "")

    def _should_auto_research(self, text, intent):
        return False


def build_orchestrator(runtime_enabled: bool, plan_status="ready", runtime_behavior="completed"):
    temporary = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    system = FakeSystem(Path(temporary.name), runtime_enabled, plan_status, runtime_behavior)
    orchestrator = PromptOrchestrator(system)
    request_router = FakeRequestRouter()
    orchestrator.request_router = request_router
    orchestrator.recorder = FakeRecorder()
    orchestrator.local_knowledge = FakeLocalKnowledge()
    orchestrator.agent_router = NullAgentRouter()
    return temporary, system, orchestrator, request_router


def test_flag_false_keeps_old_direct_path():
    temporary, system, orchestrator, _ = build_orchestrator(False)
    try:
        answer = orchestrator.handle("was ist python")
        assert answer == "local_knowledge:OLD_DIRECT_PATH"
        assert system.orchestrator_core.called is False
    finally:
        temporary.cleanup()


def test_flag_true_ready_plan_uses_orchestrator_core():
    temporary, system, orchestrator, router = build_orchestrator(True)
    try:
        answer = orchestrator.handle("was ist python")
        assert answer == "dialogue:RUNTIME_PATH"
        assert system.orchestrator_core.called is True
        assert system.orchestrator_core.payload["text"] == "was ist python"
        assert "OrchestratorCore:completed" in router.last_decision.sources
    finally:
        temporary.cleanup()


def test_flag_true_non_ready_plan_falls_back():
    temporary, system, orchestrator, router = build_orchestrator(True, plan_status="blocked")
    try:
        answer = orchestrator.handle("was ist python")
        assert answer == "local_knowledge:OLD_DIRECT_PATH"
        assert system.orchestrator_core.called is False
        assert system.last_orchestrator_runtime_fallback["reason"] == "plan_not_ready"
        assert "OrchestratorCore:fallback:plan_not_ready" in router.last_decision.sources
    finally:
        temporary.cleanup()


def test_orchestrator_error_falls_back_and_is_logged():
    temporary, system, orchestrator, router = build_orchestrator(True, runtime_behavior="error")
    try:
        answer = orchestrator.handle("was ist python")
        assert answer == "local_knowledge:OLD_DIRECT_PATH"
        assert system.orchestrator_core.called is True
        assert system.last_orchestrator_runtime_fallback["reason"] == "runtime_error"
        assert "simulated runtime failure" in system.last_orchestrator_runtime_fallback["error"]
        assert "OrchestratorCore:fallback:runtime_error" in router.last_decision.sources
    finally:
        temporary.cleanup()


if __name__ == "__main__":
    test_flag_false_keeps_old_direct_path()
    test_flag_true_ready_plan_uses_orchestrator_core()
    test_flag_true_non_ready_plan_falls_back()
    test_orchestrator_error_falls_back_and_is_logged()
    print("Kontinuum Runtime Migration Bridge 34.1 tests passed")
