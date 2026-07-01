from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class KnowledgeAgent(BaseAgent):
    name = "knowledge"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return lower.startswith("suche ") or any(x in lower for x in ["was ist", "erkläre", "erklaere", "definition"])

    def handle(self, prompt: str) -> AgentResult:
        search = self.tools.get("search_tools")
        if search and prompt.lower().startswith("suche "):
            term = prompt[6:].strip()
            result = search.search_all(term)
            answer = result.get("answer", "Keine Treffer.")
        else:
            answer = (
                "Wissensagent 23.0: Ich suche künftig zuerst in 04_knowledge, "
                "dann in 03_memory, 06_learning, 32_data, Chronicle und zuletzt Legacy."
            )
        self.remember("knowledge.query", prompt, {"agent": self.name})
        return AgentResult(self.name, True, answer)
