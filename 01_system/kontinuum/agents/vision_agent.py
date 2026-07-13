# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class VisionAgent(BaseAgent):
    name = "vision_agent"

    def can_handle(self, prompt: str) -> bool:
        service = self.config.get("vision_agent")
        return bool(service and service.looks_like_vision_command(prompt))

    def handle(self, prompt: str) -> AgentResult:
        service = self.config.get("vision_agent")
        if not service:
            return AgentResult(self.name, True, "VisionAgent ist nicht angebunden.")
        result = service.handle_command(prompt)
        return AgentResult(self.name, True, result.get("message", "VisionAgent konnte den Auftrag nicht verarbeiten."), result)
