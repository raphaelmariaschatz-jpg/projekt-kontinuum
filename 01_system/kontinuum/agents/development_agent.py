from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class DevelopmentAgent(BaseAgent):
    name = "development"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return lower in {
            "entwicklungsstatus",
            "sandboxstatus",
            "sandboxtest",
            "gitstatus",
            "gitsnapshot",
        } or lower.startswith(
            ("entwickle:", "entwickle ", "programmiere:", "programmiere ", "erweitere dich:", "erweitere dich ", "gitsnapshot ")
        )

    def handle(self, prompt: str) -> AgentResult:
        tool = self.tools.get("development_tools")
        if not tool:
            return AgentResult(self.name, True, "Entwicklungssandbox ist nicht angebunden.")
        lower = prompt.casefold().strip()
        if lower in {"entwicklungsstatus", "sandboxstatus"}:
            result = tool.status()
        elif lower == "sandboxtest":
            result = tool.test()
        elif lower == "gitstatus":
            result = tool.git_status()
        elif lower.startswith("gitsnapshot"):
            result = tool.git_snapshot(prompt[len("gitsnapshot") :].strip())
        elif lower.startswith(("programmiere:", "programmiere ", "erweitere dich:", "erweitere dich ")):
            if ":" in prompt:
                task = prompt.split(":", 1)[1].strip()
            elif lower.startswith("programmiere "):
                task = prompt[len("programmiere ") :].strip()
            else:
                task = prompt[len("erweitere dich ") :].strip()
            user = self.config.get("conversation", {}).get("user", {})
            result = tool.self_extend(task, user)
        else:
            task = prompt.split(":", 1)[1].strip() if lower.startswith("entwickle:") else prompt[len("entwickle ") :].strip()
            result = tool.develop(task)
        answer = result.get("output") or result.get("message") or str(result)
        self.remember("tool.development", prompt, {"agent": self.name, "ok": bool(result.get("ok", result.get("available")))})
        return AgentResult(self.name, True, answer, result)
