from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class MaintenanceAgent(BaseAgent):
    name = "maintenance"

    def can_handle(self, prompt: str) -> bool:
        return (prompt or "").casefold().strip() in {
            "wartungsmodus",
            "wartungsmodus status",
            "wartungsmodus bereinigung prüfen",
            "wartungsmodus bereinigung pruefen",
            "wartungsmodus bereinigung ausführen",
            "wartungsmodus bereinigung ausfuehren",
        }

    def handle(self, prompt: str) -> AgentResult:
        tool = self.tools.get("maintenance_tools")
        if not tool:
            return AgentResult(self.name, True, "Wartungsmodus ist nicht angebunden.")
        lower = prompt.casefold().strip()
        if lower.endswith(("prüfen", "pruefen")):
            result = tool.inspect()
            answer = self._format_inspection(result)
        elif lower.endswith(("ausführen", "ausfuehren")):
            result = tool.execute()
            answer = result["message"]
        else:
            result = tool.status()
            answer = result["message"]
        return AgentResult(self.name, True, answer, result)

    @staticmethod
    def _format_inspection(result: dict) -> str:
        lines = [result["message"], "Es wurde nichts gelöscht."]
        for row in result["candidates"][:30]:
            lines.append(f"- {row['action']}: {row['relative_path']} | {row['category']} | {row['bytes']} Bytes")
        if result["review_only"]:
            lines.append(f"Manuell zu prüfende Backups: {len(result['review_only'])}.")
        return "\n".join(lines)
