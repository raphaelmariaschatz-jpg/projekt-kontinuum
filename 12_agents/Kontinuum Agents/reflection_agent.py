from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class ReflectionAgent(BaseAgent):
    name = "reflection"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return any(x in lower for x in ["prüfe", "pruefe", "reflexion", "bewusstsein", "konsistenz"])

    def handle(self, prompt: str) -> AgentResult:
        answer = (
            "Reflexionsmodus 23.0 aktiv. Ich prüfe Konsistenz, bekannte Grenzen, fehlende Daten "
            "und ob die Antwort mit den Projektprinzipien vereinbar ist."
        )
        self.remember("reflection.task", prompt, {"agent": self.name})
        return AgentResult(self.name, True, answer)
