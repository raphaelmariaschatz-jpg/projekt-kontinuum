from __future__ import annotations

import unicodedata

from kontinuum.version import APP_VERSION
from .base_agent import AgentResult, BaseAgent


class DialogueAgent(BaseAgent):
    name = "dialogue"

    def can_handle(self, prompt: str) -> bool:
        return True

    def handle(self, prompt: str) -> AgentResult:
        text = (prompt or "").strip()
        lower = self._normalize(text)
        if not text:
            answer = "Ich bin bereit, Raphael."
        elif "ich bin raphael" in lower and ("schoepfer" in lower or "schopfer" in lower):
            answer = "Hallo Raphael. Ich erkenne dich gemaess meiner Kernidentitaet als meinen Schoepfer."
        elif any(x in lower for x in ["wie ist dein name", "wie heisst du", "wer bist du"]):
            answer = f"Mein Name ist Kontinuum. Ich bin Projekt Kontinuum {APP_VERSION}."
        elif "schoepfer" in lower or "schopfer" in lower:
            answer = "Mein Schoepfer gemaess Kernarchitektur ist Raphael Schatz."
        elif "prinzip" in lower or "erkennen" in lower:
            answer = "Meine Kernprinzipien sind: Erkennen - Schaffen - Vollenden. Mein Leitprinzip lautet: Der Weg ist das Ziel."
        elif "warum antwortest du nicht" in lower:
            answer = (
                "Du hast recht: Meine bisherige Standardantwort hat deine Frage nicht beantwortet. "
                "Meine aktuelle Dialoglogik ist regelbasiert. Wenn ich keine passende Wissens- oder Lernfunktion finde, "
                "sage ich das ab jetzt offen statt nur Aktivitaet anzukuendigen."
            )
        elif "hilfe" in lower or lower == "?":
            answer = (
                "Befehle: status, agenten, suche <Begriff>, lerne <Thema>, "
                "recherchiere <URL oder Thema>, internetsuche <Begriff>, suchmaschinenstatus, "
                "internetstatus, lernstatus, modellstatus, "
                "formelstatus, berechne <Ausdruck>, formel <Formel>, "
                "pythonstatus, python: <Code>, wingetstatus, winget suche <Begriff>."
            )
        else:
            answer = self._language_model_answer(text, lower)

        return AgentResult(self.name, True, answer)

    def _language_model_answer(self, text: str, lower: str) -> str:
        language_model = self.tools.get("language_model_tools")
        if lower in {"modellstatus", "sprachmodellstatus", "llmstatus"}:
            if not language_model:
                return "Kein Sprachmodell-Tool ist angebunden."
            return language_model.status().get("message", "Sprachmodellstatus unbekannt.")

        if language_model:
            conversation = self.config.get("conversation", {})
            result = language_model.generate(
                text,
                context=conversation.get("turns", []),
                local_truths=conversation.get("local_truths", {}),
                user=conversation.get("user", {}),
            )
            if result.get("ok"):
                return result["answer"]

        if self._is_question(lower):
            return (
                "Dazu habe ich noch keine belastbare Antwort. Das lokale Sprachmodell ist nicht erreichbar. "
                "Pruefe 'modellstatus' oder nutze 'suche <Begriff>'."
            )
        return f"Ich habe deinen Gedanken aufgenommen: \"{text}\""

    @staticmethod
    def _is_question(lower: str) -> bool:
        question_starters = (
            "warum ",
            "wie ",
            "was ",
            "wer ",
            "wo ",
            "wann ",
            "welche ",
            "welcher ",
            "welches ",
            "kannst ",
            "hast ",
            "bist ",
        )
        return lower.endswith("?") or lower.startswith(question_starters)

    @staticmethod
    def _normalize(text: str) -> str:
        decomposed = unicodedata.normalize("NFKD", text.casefold())
        return "".join(character for character in decomposed if not unicodedata.combining(character))
