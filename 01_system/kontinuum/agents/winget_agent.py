from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class WingetAgent(BaseAgent):
    name = "winget"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return lower == "wingetstatus" or lower.startswith(("winget ", "winget:"))

    def handle(self, prompt: str) -> AgentResult:
        tool = self.tools.get("winget_tools")
        if not tool:
            return AgentResult(self.name, True, "winget-Tool ist nicht angebunden.")
        lower = prompt.casefold().strip()
        if lower == "wingetstatus":
            result = tool.status()
        else:
            command = prompt.split(":", 1)[1].strip() if lower.startswith("winget:") else prompt[7:].strip()
            result = self._execute_command(tool, command)
        answer = result.get("output") or result.get("message") or "winget lieferte keine Ausgabe."
        self.remember("tool.winget", prompt, {"agent": self.name, "ok": bool(result.get("ok"))})
        return AgentResult(self.name, True, answer, result)

    @staticmethod
    def _execute_command(tool, command: str) -> dict:
        action, _, argument = command.partition(" ")
        action = action.casefold()
        argument = argument.strip()
        if action in {"suche", "search"} and argument:
            return tool.search(argument)
        if action in {"zeige", "show"} and argument:
            return tool.show(argument)
        if action in {"installiert", "list"}:
            return tool.list_installed()
        if action in {"updates", "upgrade"} and not argument:
            return tool.list_upgrades()
        if action in {"installiere", "installieren", "aktualisiere", "aktualisieren", "deinstalliere", "deinstallieren"} and argument:
            normalized = {
                "installiere": "installieren",
                "installieren": "installieren",
                "aktualisiere": "aktualisieren",
                "aktualisieren": "aktualisieren",
                "deinstalliere": "deinstallieren",
                "deinstallieren": "deinstallieren",
            }[action]
            return tool.change(normalized, argument)
        return {
            "available": True,
            "ok": False,
            "message": (
                "winget-Befehle: wingetstatus, winget suche <Begriff>, winget zeige <Paket-ID>, "
                "winget installiert, winget updates."
            ),
        }
