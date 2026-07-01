from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class PythonAgent(BaseAgent):
    name = "python"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return lower in {"pythonstatus", "python status"} or lower.startswith(("python:", "python "))

    def handle(self, prompt: str) -> AgentResult:
        python_tool = self.tools.get("python_tools")
        if not python_tool:
            return AgentResult(self.name, True, "Python-Tool ist nicht angebunden.")

        lower = prompt.casefold().strip()
        if lower in {"pythonstatus", "python status"}:
            info = python_tool.status()
            return AgentResult(self.name, True, info.get("message", str(info)), info)

        code = prompt.split(":", 1)[1].strip() if lower.startswith("python:") else prompt[7:].strip()
        result = python_tool.execute(code)
        answer = result.get("output") or result.get("message") or "Python lieferte keine Ausgabe."
        self.remember(
            "tool.python_execution",
            code,
            {"agent": self.name, "ok": bool(result.get("ok")), "returncode": result.get("returncode")},
        )
        return AgentResult(self.name, True, answer, result)
