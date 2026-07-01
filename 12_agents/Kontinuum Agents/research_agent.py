from __future__ import annotations
import re
from .base_agent import BaseAgent, AgentResult


class ResearchAgent(BaseAgent):
    name = "research"

    TRIGGERS = ["recherchiere", "recherche", "forsche", "untersuche", "quelle", "studie", "publikation", "paper"]

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return any(t in lower for t in self.TRIGGERS) or bool(re.search(r"https?://", prompt or ""))

    def handle(self, prompt: str) -> AgentResult:
        web = self.tools.get("web_tools")
        urls = re.findall(r"https?://[^\s]+", prompt or "")
        if urls and web:
            reports = []
            for url in urls[:3]:
                result = web.fetch_text(url)
                reports.append(result.get("summary", result.get("error", "Keine Antwort")))
                if self.storage and hasattr(self.storage, "add_source"):
                    self.storage.add_source(
                        url,
                        {
                            "title": result.get("title", ""),
                            "agent": self.name,
                            "status": "error" if result.get("error") else "retrieved",
                        },
                    )
            answer = "\n\n".join(reports)
        else:
            topic = re.sub(r"^(recherchiere|recherche|forsche|untersuche)\s+", "", prompt.strip(), flags=re.I)
            self.remember("research.topic", topic, {"agent": self.name, "content_policy": "references_only"})
            answer = (
                f"Forschungsauftrag gespeichert: {topic}\n"
                "Für echte Webrecherche wird der Web-Connector genutzt, sofern Internetzugriff erlaubt ist."
            )
        return AgentResult(self.name, True, answer)
