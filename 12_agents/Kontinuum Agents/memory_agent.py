from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class MemoryAgent(BaseAgent):
    name = "memory"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return lower.startswith(("merke ", "speichere ")) or "gedächtnis" in lower or "gedaechtnis" in lower

    def handle(self, prompt: str) -> AgentResult:
        text = prompt.strip()
        if text.lower().startswith("merke "):
            content = text[6:].strip()
        elif text.lower().startswith("speichere "):
            content = text[10:].strip()
        else:
            content = text
        self.remember("memory.user_note", content, {"agent": self.name, "target": "03_memory"})
        return AgentResult(self.name, True, "Ich habe es im Memory-Bereich 03_memory vorgemerkt.")
