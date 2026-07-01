from __future__ import annotations

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


AGENT_CLASSES = [
    CodexAgent,
    InternetStatusAgent,
    SystemMonitorAgent,
    AutonomousLearningAgent,
    LearningAgent,
    ResearchAgent,
    MemoryAgent,
    KnowledgeAgent,
    PlannerAgent,
    ReflectionAgent,
    DialogueAgent,
]


def build_agents(storage=None, tools=None, config=None):
    return [cls(storage=storage, tools=tools, config=config) for cls in AGENT_CLASSES]


def route_prompt(prompt: str, agents):
    for agent in agents:
        if agent.can_handle(prompt):
            return agent.handle(prompt)
    return None
