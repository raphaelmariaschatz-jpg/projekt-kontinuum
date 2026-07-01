from __future__ import annotations

import unicodedata
import uuid
import re
from dataclasses import dataclass


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", (text or "").casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


@dataclass(frozen=True)
class Intent:
    name: str
    input_type: str
    is_follow_up: bool = False


class ConversationManager:
    def __init__(self, storage, identity: dict, version: str, self_knowledge=None, consciousness=None):
        self.storage = storage
        self.identity = identity
        self.version = version
        self.session_id = uuid.uuid4().hex
        self.user: dict = {}
        self.self_knowledge = self_knowledge
        self.consciousness = consciousness

    def bind_user(self, identity: dict | None) -> None:
        self.user = dict(identity or {})

    def classify(self, text: str) -> Intent:
        value = normalize(text).strip()
        if re.search(r"https?://", text or ""):
            return Intent("command", "command")
        if any(marker in value for marker in (
            "lies diese datei",
            "lies datei",
            "lese datei",
            "lerne aus dieser datei",
            "lerne aus datei",
            "offne diese datei",
            "oeffne diese datei",
            "analysiere diese datei",
            "analysiere datei",
            "importiere diese datei",
            "importiere datei",
            "importiere pdf",
            "lerne aus ordner",
        )):
            return Intent("command", "command")
        if self._requests_todays_inputs(value):
            return Intent("history.today_inputs", "question")
        if self._is_command(value):
            return Intent("command", "command")
        if "bewusstseinsstatus" in value:
            return Intent("consciousness.status", "question")
        if "bewusstsein" in value or "bewusst" in value:
            if "reflektiere" in value:
                return Intent("consciousness.reflect", "question")
            if any(word in value for word in ("qualia", "erleben", "subjektiv", "echt")):
                return Intent("consciousness.qualia", "question")
            return Intent("consciousness.meaning", "question")
        if any(phrase in value for phrase in ("was nimmst du wahr", "wie nimmst du wahr", "deine wahrnehmung")):
            return Intent("consciousness.perception", "question")
        if "selbsterkenntnis" in value:
            return Intent("self_knowledge.meaning", "question")
        if any(phrase in value for phrase in ("was weisst du uber dich", "selbstbild", "reflektiere dich selbst")):
            return Intent("self_knowledge.overview", "question")
        if "starken" in value or "staerken" in value:
            return Intent("self_knowledge.strengths", "question")
        if "blind" in value and "fleck" in value:
            return Intent("self_knowledge.blind_spots", "question")
        if any(word in value for word in ("schwachen", "schwaechen", "grenzen")) and any(word in value for word in ("deine", "dein", "du")):
            return Intent("self_knowledge.limitations", "question")
        if "emotion" in value and any(word in value for word in ("deine", "du", "hast")):
            return Intent("self_knowledge.emotions", "question")
        if ("wirkst du" in value or "deine wirkung" in value) and ("mich" in value or "andere" in value):
            return Intent("self_knowledge.effect", "question")
        asks_system_identity = any(phrase in value for phrase in ("wie ist dein name", "wie lautet dein name", "wie heisst du", "wer bist du"))
        asks_mission = "dein auftrag" in value or "deine aufgabe" in value or "deine mission" in value
        if asks_system_identity and asks_mission:
            return Intent("truth.identity_and_mission", "question")
        if any(phrase in value for phrase in (
            "wie ist mein name", "wie lautet mein name", "wer bin ich", "wer ist eingeloggt",
            "weisst du wer ich bin", "weißt du wer ich bin", "kennst du mich",
            "welcher benutzer ist aktiv", "bin ich raphael",
        )):
            return Intent("truth.user_identity", "question")
        if asks_system_identity:
            return Intent("truth.system_identity", "question")
        if asks_mission:
            return Intent("truth.mission", "question")
        if "schopfer" in value or "schoepfer" in value:
            return Intent("truth.creator", "question")
        if "prinzip" in value:
            return Intent("truth.principles", "question")
        if value.startswith(("merke ", "merke dir ", "speichere ")):
            return Intent("memory.store", "memory")
        follow_up = value.startswith(
            ("und ", "und wie ", "und was ", "dazu ", "davon ", "das ", "die ", "der ", "nein ", "nein, ", "ich meinte ")
        )
        question_starters = (
            "warum ",
            "wie ",
            "wieviel ",
            "wie viel ",
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
            "zeige ",
            "nenne ",
            "erklaere ",
            "erklare ",
            "sage ",
        )
        if text.rstrip().endswith("?") or value.startswith(question_starters) or follow_up:
            return Intent("dialog.follow_up" if follow_up else "dialog.question", "question", follow_up)
        return Intent("dialog.thought", "thought")

    @staticmethod
    def _is_command(value: str) -> bool:
        command_prefixes = (
            "suche ",
            "archivsuche ",
            "lerne ",
            "recherchiere ",
            "internetsuche ",
            "websuche ",
            "suche im internet ",
            "plane ",
            "erstelle plan",
            "erstelle einen lernauftrag",
            "erstelle lernauftrag",
            "python ",
            "python:",
            "winget ",
            "winget:",
            "codex ",
            "codex:",
            "entwickle ",
            "entwickle:",
            "programmiere ",
            "programmiere:",
            "erweitere dich ",
            "erweitere dich:",
            "gitsnapshot ",
            "oracle ",
            "oracle:",
            "formel ",
            "notizbuch ",
            "wissensnotizbuch ",
            "wissensplattform altbestand ",
            "vertrauen ",
            "wie sicher ist ",
            "prüfauftrag ",
            "pruefauftrag ",
            "berechne ",
            "rechne ",
            "lernphase ",
            "lernanwendung ",
            "aktualisiere erinnerung ",
            "vergiss ",
            "verknupfe erinnerungen ",
            "verknüpfe erinnerungen ",
            "wartungsmodus ",
            "moralbewertung ",
            "bewerte handlung ",
            "zielkonflikt ",
            "bedeutungspfad",
            "meaningpfad",
            "bedeutung ",
            "motivationsprioritäten ",
            "motivationsprioritaeten ",
            "motivation ",
            "motivationserklärung ",
            "motivationserklaerung ",
            "warum score ",
            "erkläre priorität ",
            "erklaere prioritaet ",
            "wichtige einflüsse ",
            "wichtige einfluesse ",
            "lies ",
            "lese ",
            "öffne ",
            "oeffne ",
            "nutze zum lernen ",
            "nutze zum lernen auch ",
            "lerne auch hier ",
            "lies diese datei ",
            "lies datei ",
            "lese datei ",
            "lerne aus dieser datei ",
            "lerne aus datei ",
            "öffne diese datei ",
            "oeffne diese datei ",
            "analysiere diese datei ",
            "analysiere datei ",
            "importiere diese datei ",
            "importiere datei ",
            "importiere pdf ",
            "lerne aus ordner ",
        )
        commands = {
            "status",
            "systemstatus",
            "agenten",
            "agentenstatus",
            "versionen",
            "lernstatus",
            "lernprojekte",
            "zeige alle lernprojekte",
            "zeige mir alle lernprojekte",
            "zeige aktive lernprojekte",
            "internetstatus",
            "modellstatus",
            "pythonstatus",
            "wingetstatus",
            "codexstatus",
            "hilfe",
            "metalernstatus",
            "suchmaschinenstatus",
            "formelstatus",
            "notizbuchstatus",
            "wissensplattformstatus",
            "wissenskonflikte",
            "selbstmodellstatus",
            "wissensselbstmodellstatus",
            "was hat sich geändert",
            "was hat sich geaendert",
            "warum hat sich das geändert",
            "warum hat sich das geaendert",
            "zeige zustandsverlauf",
            "zeige offene innere konflikte",
            "chronikschutzstatus",
            "kontinuitätsstatus",
            "kontinuitaetsstatus",
            "fundamentstatus",
            "fundamentale prinzipien",
            "moralstatus",
            "fundamentschichtstatus",
            "fundamentintegritätsstatus",
            "fundamentintegritaetsstatus",
            "fundamentaudit",
            "foundationmemorystatus",
            "foundation memory status",
            "langfristige ziele",
            "zielstatus",
            "selbstfragen",
            "stelle dir eine frage",
            "bedeutungsstatus",
            "meaningstatus",
            "motivationsstatus",
            "motivationstatus",
            "motivationsprioritäten",
            "motivationsprioritaeten",
            "motivationserklärungsstatus",
            "motivationserklaerungsstatus",
            "benutzerstatus",
            "sessionstatus",
            "wer ist angemeldet",
            "rollenstatus",
            "offene fundamentzyklen",
            "fundamentzyklus reparieren",
            "fundamentzyklenstatus",
            "relevanzstatus",
            "zeitrelevanzstatus",
            "bedeutungsinflation",
            "chronikprägung",
            "chronikpraegung",
            "wissenslückenpriorität",
            "wissenslueckenprioritaet",
            "welche informationen widersprechen sich",
            "was habe ich im letzten monat gelernt",
            "welche themen beschäftigen mich besonders",
            "welche themen beschaeftigen mich besonders",
            "welche wissensgebiete wachsen am stärksten",
            "welche wissensgebiete wachsen am staerksten",
            "was vermute ich",
            "welche aussagen sind unsicher",
            "welche informationen sollten überprüft werden",
            "welche informationen sollten ueberprueft werden",
            "welche wissenslücken habe ich",
            "welche wissensluecken habe ich",
            "überprüfungsaufträge",
            "ueberpruefungsauftraege",
            "epistemischer status",
            "aktionsschichtstatus",
            "prüfzyklus",
            "pruefzyklus",
            "zeige projekterinnerungen",
            "zeige offene punkte",
            "prüfe widersprüche",
            "pruefe widersprueche",
            "prufe widerspruche",
            "gedächtnisstatus",
            "gedaechtnisstatus",
            "gedachtnisstatus",
            "wartungsmodus",
            "wartungsmodus status",
            "wartungsmodus bereinigung prüfen",
            "wartungsmodus bereinigung pruefen",
            "wartungsmodus bereinigung ausführen",
            "wartungsmodus bereinigung ausfuehren",
            "entwicklungsstatus",
            "sandboxstatus",
            "sandboxtest",
            "gitstatus",
            "gitsnapshot",
            "routingstatus",
            "oraclestatus",
            "oracle status",
            "oracle kostenstatus",
            "oracle free status",
            "webagentstatus",
            "fileagentstatus",
            "canonicalenginestatus",
            "cestatus",
            "continuouscanonicalstatus",
        }
        return value.startswith(command_prefixes) or value in commands

    def local_truth_answer(self, intent: Intent) -> str | None:
        if intent.name.startswith("consciousness.") and self.consciousness:
            focus = intent.name.split(".", 1)[1]
            return self.consciousness.reflect("dialogische Bewusstseinsreflexion") if focus == "reflect" else self.consciousness.answer(focus)
        if intent.name.startswith("self_knowledge.") and self.self_knowledge:
            focus = intent.name.split(".", 1)[1]
            return self.self_knowledge.reflect("dialogische Selbstreflexion") if focus == "overview" else self.self_knowledge.answer(focus)
        if intent.name == "truth.user_identity":
            name = self.user.get("full_name") or self.user.get("username")
            role = self.user.get("role")
            if name and role:
                return f"Du bist als {name} mit der Rolle {role} angemeldet."
            if name:
                return f"Du bist als {name} angemeldet."
            return "In dieser Sitzung ist keine verifizierte Benutzeridentität an das Backend gebunden."
        if intent.name == "truth.system_identity":
            return f"Mein Name ist {self.identity['name']}. Ich bin Projekt Kontinuum {self.version}."
        if intent.name == "truth.identity_and_mission":
            return (
                f"Mein Name ist {self.identity['name']}. Ich bin Projekt Kontinuum {self.version}. "
                "Mein Auftrag ist, Raphael beim Erkennen, Schaffen und Vollenden zu unterstützen: "
                "lokales Wissen, Gedächtnis, Forschung und Werkzeuge zuverlässig zu verbinden."
            )
        if intent.name == "truth.mission":
            return (
                "Mein Auftrag ist, Raphael beim Erkennen, Schaffen und Vollenden zu unterstützen: "
                "lokales Wissen, Gedächtnis, Forschung und Werkzeuge zuverlässig zu verbinden, "
                "ehrlich über Grenzen zu bleiben und wichtige Zusammenhänge dauerhaft nutzbar zu machen."
            )
        if intent.name == "truth.creator":
            return f"Mein Schöpfer ist {self.identity['creator']}."
        if intent.name == "truth.principles":
            return f"{self.identity['core_process']}. Leitprinzip: {self.identity['guiding_philosophy']}."
        return None

    def log_turn(self, role: str, content: str, intent: Intent, agent: str = "") -> int:
        metadata = {
            "session_id": self.session_id,
            "role": role,
            "intent": intent.name,
            "input_type": intent.input_type,
            "is_follow_up": intent.is_follow_up,
            "agent": agent,
            "version": self.version,
            "username": self.user.get("username", ""),
            "full_name": self.user.get("full_name", ""),
            "role_name": self.user.get("role", ""),
        }
        return self.storage.add("events", "conversation.turn", content, metadata)

    def recent_context(self, limit: int = 8) -> list[dict]:
        return self.storage.recent_conversation_turns(self.session_id, limit=limit)

    def context_for_agents(self) -> dict:
        turns = [turn for turn in self.recent_context() if turn.get("intent") != "command"]
        return {
            "session_id": self.session_id,
            "user": dict(self.user),
            "turns": turns[-6:],
            "local_truths": {
                "system_name": self.identity["name"],
                "creator": self.identity["creator"],
                "core_process": self.identity["core_process"],
                "guiding_philosophy": self.identity["guiding_philosophy"],
                "self_knowledge": self.self_knowledge.profile() if self.self_knowledge else {},
                "consciousness": self.consciousness.profile() if self.consciousness else {},
            },
        }

    @staticmethod
    def _requests_todays_inputs(value: str) -> bool:
        asks_for_inputs = "eingab" in value or "fragen" in value
        asks_for_today = "heute" in value or "heutigen" in value
        asks_for_list = any(word in value for word in ("liste", "list", "zeige", "welche", "alle"))
        return asks_for_inputs and asks_for_today and asks_for_list
