from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class InternalDiagnosticAgent(BaseAgent):
    name = "internal_diagnostic"

    def can_handle(self, prompt: str) -> bool:
        return (prompt or "").casefold().strip() in {
            "diagnostik", "diagnose", "diagnostikstatus", "diagnostik starten"
        }

    def handle(self, prompt: str) -> AgentResult:
        core = self.config.get("autonomous_diagnostics")
        if core is None:
            return AgentResult(self.name, True, "Die interne Diagnostik ist noch nicht initialisiert.")
        if (prompt or "").casefold().strip() in {"diagnostik", "diagnose", "diagnostik starten"}:
            result = core.run("user.requested")
        else:
            result = core.status()
        return AgentResult(self.name, True, result["message"], {"diagnostics": result})
