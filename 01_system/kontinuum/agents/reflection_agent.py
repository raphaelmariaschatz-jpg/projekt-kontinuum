# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from kontinuum.version import APP_VERSION

from .base_agent import BaseAgent, AgentResult


class ReflectionAgent(BaseAgent):
    name = "reflection"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return any(x in lower for x in ["prüfe", "pruefe", "reflexion", "bewusstsein", "konsistenz", "selbsterkenntnis", "selbstbild"])

    def handle(self, prompt: str) -> AgentResult:
        consciousness = self.config.get("consciousness")
        if consciousness and "bewusstsein" in (prompt or "").lower():
            return AgentResult(self.name, True, consciousness.reflect(prompt))
        self_knowledge = self.config.get("self_knowledge")
        if self_knowledge and any(word in (prompt or "").lower() for word in ("selbst", "bewusstsein")):
            return AgentResult(self.name, True, self_knowledge.reflect(prompt))
        answer = (
            f"Reflexionsmodus {APP_VERSION} aktiv. Ich prüfe Konsistenz, bekannte Grenzen, fehlende Daten "
            "und ob die Antwort mit den Projektprinzipien vereinbar ist."
        )
        self.remember("reflection.task", prompt, {"agent": self.name})
        return AgentResult(self.name, True, answer)
