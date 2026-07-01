from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class AutonomousLearningAgent(BaseAgent):
    name = "autonomous_learning"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower().strip()
        return lower in {"autostatus", "autonomiestatus", "autonom lernen"} or lower.startswith(("lerne selbständig", "lerne selbstaendig", "erweitere alle wissensgebiete"))

    def handle(self, prompt: str) -> AgentResult:
        lower = prompt.lower().strip()
        if lower in {"autostatus", "autonomiestatus"}:
            answer = "Autonomes Lernen 23.0 ist vorbereitet. Schreibziel: 18_autonomous_learning und 06_learning."
        else:
            subjects = ["Mathematik", "Physik", "Chemie", "Biologie", "Informatik"]
            for s in subjects:
                self.remember("autonomous.project", f"Autonomes Lernprojekt: {s}", {"subject": s, "version": "23.0"})
            answer = "Autonomer Lernzyklus vorbereitet für: " + ", ".join(subjects)
        return AgentResult(self.name, True, answer)
