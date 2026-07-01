from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class PlannerAgent(BaseAgent):
    name = "planner"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return lower.startswith(("plane ", "roadmap", "planung", "erstelle plan"))

    def handle(self, prompt: str) -> AgentResult:
        answer = (
            "Planungsmodus 23.0 aktiv.\n"
            "Ablauf: Ziel erfassen → Module prüfen → Aufgaben zerlegen → Fortschritt dokumentieren → Vollversion vorbereiten."
        )
        self.remember("planner.task", prompt, {"agent": self.name})
        return AgentResult(self.name, True, answer)
