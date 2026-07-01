from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class CodeAgent(BaseAgent):
    name = "code_agent"

    def can_handle(self, prompt: str) -> bool:
        service = self.config.get("code_agent")
        return bool(service and service.looks_like_code_command(prompt))

    def handle(self, prompt: str) -> AgentResult:
        service = self.config.get("code_agent")
        if not service:
            return AgentResult(self.name, True, "CodeAgent ist nicht angebunden.")
        result = service.handle_command(prompt)
        return AgentResult(self.name, True, result.get("message", "CodeAgent konnte den Auftrag nicht verarbeiten."), result)
