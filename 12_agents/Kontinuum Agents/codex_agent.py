from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class CodexAgent(BaseAgent):
    name = "codex"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower().strip()
        return lower in {"codexstatus", "codex status"} or lower.startswith(("codex: ", "codex "))

    def handle(self, prompt: str) -> AgentResult:
        codex = self.tools.get("codex_tools")
        if not codex:
            return AgentResult(self.name, True, "Codex-Tool ist nicht angebunden.")
        lower = prompt.lower().strip()
        if lower in {"codexstatus", "codex status"}:
            info = codex.status()
            return AgentResult(self.name, True, info.get("message", str(info)), info)
        task = prompt.split(":", 1)[1].strip() if prompt.lower().startswith("codex:") else prompt[6:].strip()
        result = codex.execute(task)
        answer = result.get("answer") or result.get("message") or "Codex lieferte keine Antwort."
        return AgentResult(self.name, True, answer, result)
