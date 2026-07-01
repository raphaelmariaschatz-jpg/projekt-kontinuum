from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class ChangeAgent(BaseAgent):
    name = "change_agent"

    def can_handle(self, prompt: str) -> bool:
        service = self.config.get("change_agent")
        lower = (prompt or "").casefold().strip(" .!?")
        return lower == "changeagentstatus" or bool(service and service.is_change_request(prompt))

    def handle(self, prompt: str) -> AgentResult:
        service = self.config.get("change_agent")
        if not service:
            return AgentResult(self.name, True, "ChangeAgent ist nicht angebunden.")
        lower = (prompt or "").casefold().strip(" .!?")
        if lower == "changeagentstatus":
            return AgentResult(self.name, True, service.format_status())
        request = service.process(prompt)
        return AgentResult(self.name, True, service.format_response(request), {"change_request": request.__dict__})
