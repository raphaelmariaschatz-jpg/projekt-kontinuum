from __future__ import annotations

from dataclasses import dataclass

from .dialogue_agent import DialogueAgent
from .research_agent import ResearchAgent
from .learning_agent import LearningAgent
from .autonomous_learning_agent import AutonomousLearningAgent
from .internet_status_agent import InternetStatusAgent
from .system_monitor_agent import SystemMonitorAgent
from .memory_agent import MemoryAgent
from .knowledge_agent import KnowledgeAgent
from .planner_agent import PlannerAgent
from .reflection_agent import ReflectionAgent
from .codex_agent import CodexAgent
from .python_agent import PythonAgent
from .winget_agent import WingetAgent
from .formula_agent import FormulaAgent
from .development_agent import DevelopmentAgent
from .oracle_cloud_agent import OracleCloudAgent
from .notebook_agent import NotebookAgent
from .maintenance_agent import MaintenanceAgent
from .foundation_agent import FoundationAgent
from .internal_diagnostic_agent import InternalDiagnosticAgent
from .change_agent import ChangeAgent
from .vision_agent import VisionAgent
from .git_agent import GitAgent
from .canonical_git_agent import CanonicalGitAgent
from .code_agent import CodeAgent
from .chemistry_agent import ChemistryAgent


@dataclass(frozen=True)
class AgentRoute:
    agent_class: type
    priority: int
    intents: tuple[str, ...] = ()


AGENT_ROUTES = [
    AgentRoute(ChangeAgent, 5),
    AgentRoute(VisionAgent, 8),
    AgentRoute(CanonicalGitAgent, 9),
    AgentRoute(CodexAgent, 10, ("command",)),
    AgentRoute(GitAgent, 12),
    AgentRoute(CodeAgent, 14),
    AgentRoute(ChemistryAgent, 16, ("command", "dialog.question", "dialog.follow_up", "dialog.thought")),
    AgentRoute(PythonAgent, 20, ("command",)),
    AgentRoute(WingetAgent, 30, ("command",)),
    AgentRoute(MaintenanceAgent, 32, ("command",)),
    AgentRoute(InternalDiagnosticAgent, 33, ("command",)),
    AgentRoute(MemoryAgent, 35, ("command", "memory.store", "dialog.question")),
    AgentRoute(FoundationAgent, 38, ("command", "dialog.question", "dialog.thought")),
    AgentRoute(FormulaAgent, 40, ("command", "dialog.question", "dialog.follow_up", "dialog.thought")),
    AgentRoute(NotebookAgent, 45, ("command",)),
    AgentRoute(DevelopmentAgent, 50, ("command",)),
    AgentRoute(OracleCloudAgent, 60, ("command",)),
    AgentRoute(InternetStatusAgent, 70, ("command",)),
    AgentRoute(SystemMonitorAgent, 80, ("command",)),
    AgentRoute(AutonomousLearningAgent, 90, ("command", "dialog.thought")),
    AgentRoute(LearningAgent, 100, ("command", "dialog.thought", "dialog.question", "dialog.follow_up")),
    AgentRoute(ResearchAgent, 110, ("command", "dialog.question", "dialog.follow_up")),
    AgentRoute(KnowledgeAgent, 130, ("command", "dialog.question", "dialog.follow_up", "dialog.thought")),
    AgentRoute(PlannerAgent, 140, ("command", "dialog.question", "dialog.thought")),
    AgentRoute(ReflectionAgent, 150, ("command", "dialog.thought")),
    AgentRoute(DialogueAgent, 1000),
]
AGENT_CLASSES = [route.agent_class for route in AGENT_ROUTES]


class AgentRouter:
    def __init__(self, agents):
        by_name = {agent.name: agent for agent in agents}
        self.routes = [
            (route, by_name[route.agent_class.name])
            for route in sorted(AGENT_ROUTES, key=lambda item: item.priority)
            if route.agent_class.name in by_name
        ]

    def candidates(self, prompt: str, intent_name: str | None = None) -> list:
        candidates = []
        for route, agent in self.routes:
            if route.intents and intent_name and intent_name not in route.intents:
                continue
            if agent.can_handle(prompt):
                candidates.append(agent)
        return candidates

    def route(self, prompt: str, intent_name: str | None = None):
        candidates = self.candidates(prompt, intent_name)
        return candidates[0].handle(prompt) if candidates else None

    def diagnose(self, prompt: str, intent_name: str | None = None) -> dict:
        candidates = self.candidates(prompt, intent_name)
        return {
            "intent": intent_name or "",
            "selected": candidates[0].name if candidates else "",
            "candidates": [agent.name for agent in candidates],
            "conflict": len(candidates) > 1 and candidates[0].name != "dialogue",
        }


def build_agents(storage=None, tools=None, config=None):
    return [route.agent_class(storage=storage, tools=tools, config=config) for route in AGENT_ROUTES]


def route_prompt(prompt: str, agents, intent_name: str | None = None):
    return AgentRouter(agents).route(prompt, intent_name)
