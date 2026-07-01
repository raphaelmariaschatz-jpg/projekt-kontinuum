from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class SystemMonitorAgent(BaseAgent):
    name = "system_monitor"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower().strip()
        return lower in {"status", "systemstatus"} or any(
            x in lower for x in ["festplatte", "speicherplatz"]
        )

    def handle(self, prompt: str) -> AgentResult:
        path_tools = self.tools.get("path_tools")
        if path_tools:
            root = path_tools.project_root()
            answer = f"Systemstatus 23.0: Projektwurzel {root}. Ordnerstruktur wird überwacht."
        else:
            answer = "Systemstatus 23.0: Systemmonitor aktiv."
        return AgentResult(self.name, True, answer)
