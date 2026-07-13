# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class OracleCloudAgent(BaseAgent):
    name = "oracle_cloud"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return lower in {"oraclestatus", "oracle status", "oracle free status", "oracle kostenstatus"} or lower.startswith(
            ("oracle ", "oracle:")
        )

    def handle(self, prompt: str) -> AgentResult:
        tool = self.tools.get("oracle_cloud_tools")
        if not tool:
            return AgentResult(self.name, True, "Oracle-Cloud-Tool ist nicht angebunden.")
        lower = prompt.casefold().strip()
        if lower in {"oraclestatus", "oracle status"}:
            result = tool.status()
        elif lower in {"oracle free status", "oracle kostenstatus"}:
            result = tool.free_tier_status()
        else:
            command = prompt.split(":", 1)[1].strip() if lower.startswith("oracle:") else prompt[7:].strip()
            result = self._execute(tool, command)
        answer = result.get("output") or result.get("message") or "Oracle Cloud lieferte keine Ausgabe."
        self.remember("tool.oracle_cloud", prompt, {"agent": self.name, "ok": bool(result.get("ok", result.get("available")))})
        return AgentResult(self.name, True, answer, result)

    def _execute(self, tool, command: str) -> dict:
        action, _, argument = command.partition(" ")
        action = action.casefold()
        user = self.config.get("conversation", {}).get("user", {})
        if action in {"instanzen", "instances"}:
            return tool.list_instances()
        if action in {"speicher", "buckets"}:
            return tool.list_buckets()
        if action in {"limits", "kontingente"}:
            return tool.limits()
        if action in {"starte", "start"}:
            return tool.change_instance_state("start", argument, user, self.config.get("cost_confirmation_handler"))
        if action in {"stoppe", "stop"}:
            return tool.change_instance_state("stop", argument, user, self.config.get("cost_confirmation_handler"))
        return {
            "ok": False,
            "message": (
                "Oracle-Befehle: oraclestatus, oracle kostenstatus, oracle instanzen, "
                "oracle speicher, oracle limits, oracle starte <Instance-OCID>, oracle stoppe <Instance-OCID>."
            ),
        }
