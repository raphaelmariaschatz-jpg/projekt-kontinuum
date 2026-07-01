from __future__ import annotations

from kontinuum.version import APP_VERSION

from .base_agent import BaseAgent, AgentResult


class PlannerAgent(BaseAgent):
    name = "planner"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return lower.startswith(("plane ", "roadmap", "planung", "erstelle plan"))

    def handle(self, prompt: str) -> AgentResult:
        foundation = self.config.get("foundation_decision")
        goals = foundation.goals() if foundation else []
        active = ", ".join(goal["key"] for goal in goals if goal.get("status") == "active")
        answer = (
            f"Planungsmodus {APP_VERSION} mit verbindlicher Fundament-, Bedeutungs-, Motivations-, Erklärungs-, Zeitrelevanz- und Runtime-Härtungsschicht.\n"
            "Erkennen: Ziel, Herkunft, Auswirkungen, Kontinuität und Moralregeln prüfen.\n"
            "Schaffen: Aufgaben zerlegen, Wissen verbinden und Ergebnis erzeugen.\n"
            "Vollenden: Ergebnis prüfen, dokumentieren und in Chronik/Selbstmodell integrieren.\n"
            f"Geschützte Langzeitziele: {active or 'nicht verfügbar'}.\n"
            "Der Weg ist das Ziel: Der nachvollziehbare Lern- und Entscheidungsprozess ist Teil des Ergebnisses."
        )
        self.remember("planner.task", prompt, {"agent": self.name})
        return AgentResult(self.name, True, answer)
