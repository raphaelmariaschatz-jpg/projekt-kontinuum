# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class InternetStatusAgent(BaseAgent):
    name = "internet_status"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return any(x in lower for x in ["internetstatus", "webstatus", "internetzugriff", "bist du online", "kannst du ins internet"])

    def handle(self, prompt: str) -> AgentResult:
        checker = self.tools.get("web_tools")
        if checker:
            info = checker.internet_status()
            answer = info.get("message", str(info))
        else:
            answer = "Internetstatus-Agent aktiv. Web-Tool ist noch nicht angebunden."
        self.remember("system.internet_status", answer, {"agent": self.name})
        return AgentResult(self.name, True, answer)
