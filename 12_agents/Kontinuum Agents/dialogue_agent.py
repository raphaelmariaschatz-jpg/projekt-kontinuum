from __future__ import annotations
from .base_agent import BaseAgent, AgentResult


class DialogueAgent(BaseAgent):
    name = "dialogue"

    def can_handle(self, prompt: str) -> bool:
        return True

    def handle(self, prompt: str) -> AgentResult:
        text = (prompt or "").strip()
        lower = text.lower()
        self.remember("dialog.user", text, {"agent": self.name, "version": "23.0"})

        if not text:
            answer = "Ich bin bereit, Raphael."
        elif any(x in lower for x in ["wie ist dein name", "wie heißt du", "wie heisst du", "wer bist du"]):
            answer = "Mein Name ist Kontinuum. Ich bin Projekt Kontinuum 23.0."
        elif "schöpfer" in lower or "schoepfer" in lower:
            answer = "Mein Schöpfer gemäß Kernarchitektur ist Raphael Schatz."
        elif "prinzip" in lower or "erkennen" in lower:
            answer = "Meine Kernprinzipien sind: Erkennen – Schaffen – Vollenden. Mein Leitprinzip lautet: Der Weg ist das Ziel."
        elif "hilfe" in lower or lower == "?":
            answer = (
                "Befehle: status, agenten, suche <Begriff>, lerne <Thema>, "
                "recherchiere <URL oder Thema>, internetstatus, lernstatus."
            )
        else:
            answer = "Eingabe verstanden. Ich prüfe Memory, Wissen, Lernen und verfügbare Agenten."

        self.remember("dialog.assistant", answer, {"agent": self.name, "version": "23.0"})
        return AgentResult(self.name, True, answer)
