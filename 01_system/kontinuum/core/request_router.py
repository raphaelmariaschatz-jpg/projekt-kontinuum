from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .conversation import Intent, normalize


@dataclass
class RouteDecision:
    request_class: str
    selected_agent: str
    reason: str
    alternatives: list[str] = field(default_factory=list)
    fallbacks: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.perf_counter)


class RequestRouter:
    VERSION = "1.0"
    STATUS_COMMANDS = {
        "lernstatus",
        "internetstatus",
        "webagentstatus",
        "fileagentstatus",
        "changeagentstatus",
        "visionagentstatus",
        "gitagentstatus",
        "cgmstatus",
        "codeagentstatus",
        "agent integration status",
        "caim status",
        "caimstatus",
        "agent registry status",
        "fundamentzyklenstatus",
        "routingstatus",
        "crestatus",
        "cre status",
        "capabilitystatus",
        "executionplanstatus",
        "execution planner status",
        "plannerstatus",
        "orchestratorstatus",
        "orchestrator core status",
        "runtime status",
    }
    CHANGE_MARKERS = (
        "korrigiere",
        "korrektur",
        "ändere",
        "aendere",
        "ersetze",
        "verankere",
        "aktualisiere",
        "setze",
        "speichere als regel",
        "übernimm als neue regel",
        "uebernimm als neue regel",
        "streiche",
        "lösche",
        "losche",
        "loesche",
    )
    CANONICAL_COMMANDS = {"canonicalenginestatus", "cestatus", "continuouscanonicalstatus"}
    GOVERNANCE_MARKERS = (
        "governance",
        "canonical",
        "fundament",
        "foundation",
        "release gate",
        "prüfauftrag",
        "pruefauftrag",
    )
    LEARNING_MARKERS = (
        "lerne",
        "studiere",
        "analysiere",
        "merke dir",
        "erweitere dein wissen",
        "trainiere",
    )
    FILE_MARKERS = (
        "datei",
        "pdf",
        "docx",
        "txt",
        "quellcode",
        "projektordner",
        "lokale dokument",
        "bericht",
        "handbuch",
    )
    VISION_MARKERS = (
        "analysiere bild",
        "beschreibe bild",
        "lies bild",
        "lese bild",
        "vision ",
    )
    GIT_MARKERS = (
        "git status",
        "git repo prüfen",
        "git repo prufen",
        "git repo pruefen",
        "git historie",
        "git snapshot report",
        "gitstatus",
    )
    CGM_MARKERS = (
        "commit bereitschaft prüfen",
        "commit bereitschaft prufen",
        "commit bereitschaft pruefen",
        "release bereitschaft prüfen",
        "release bereitschaft prufen",
        "release bereitschaft pruefen",
        "cgm report",
        "cgm release prüfen",
        "cgm release prufen",
        "cgm release pruefen",
        "cgm chronik vorbereiten",
        "cgm cam abgleich",
        "cgm cde abgleich",
    )
    CODE_MARKERS = (
        "analysiere code",
        "analysiere projekt",
        "erkläre code",
        "erklaere code",
        "finde einstiegspunkte",
        "erstelle projektkarte",
        "welche sprache ist",
        "codeagent ",
    )
    CHEMISTRY_MARKERS = (
        "chemie",
        "chemistry",
        "stoff",
        "summenformel",
        "cas",
        "molekül",
        "molekuel",
        "gefahrstoff",
        "ethanol",
        "natriumchlorid",
    )
    WEB_MARKERS = (
        "webseite",
        "internet",
        "url",
        "link",
        "crawl",
        "online-dokumentation",
        "dokumentation",
        "recherchiere",
        "websuche",
        "internetsuche",
    )
    MEMORY_MARKERS = ("memory", "gedächtnis", "gedaechtnis", "erinnerung", "merke ")
    IDENTITY_MARKERS = ("identity:", "creator:", "assistant:", "preferred_address:", "short_name:", "role:", "roles:")
    CONFIG_MARKERS = ("config:", "configuration:", "settings:", "system:")
    DIAGNOSIS_MARKERS = ("diagnose", "diagnostik", "fehleranalyse", "status prüfen", "status pruefen")
    ADMIN_MARKERS = ("versionen", "agenten", "systemstatus", "wartungsmodus", "gitstatus")
    PROGRAMMING_MARKERS = ("programmiere", "entwickle", "python ", "python:", "code", "skript")
    QUESTION_STARTERS = (
        "was ",
        "was ist ",
        "was sind ",
        "wie funktioniert ",
        "wie lautet ",
        "erkläre ",
        "erklaere ",
        "definiere ",
        "nenne ",
        "welche ",
        "warum ",
    )
    WINDOWS_PATH = re.compile(r"(?i)\b[a-z]:[\\/][^\r\n\"']+")
    FILE_SUFFIX = re.compile(r"(?i)(?:^|[\\/\s\"'])([^\\/\s\"']+\.(?:pdf|docx|txt|md|json|csv|html|htm|py|js|css|log|xlsx))\b")
    IMAGE_SUFFIX = re.compile(r"(?i)(?:^|[\\/\s\"'])([^\\/\s\"']+\.(?:png|jpg|jpeg|webp|bmp|gif|tiff|tif))\b")
    CODE_SUFFIX = re.compile(r"(?i)(?:^|[\\/\s\"'])([^\\/\s\"']+\.(?:py|js|jsx|ts|tsx|html|css|sh|bat|ps1|json|yaml|yml|toml|ini|md|txt|env\.example))\b")
    MATH_EXPRESSION = re.compile(
        r"(?i)(?:\d+(?:[,.]\d+)?)\s*(?:[+\-*/×x·÷^]|prozent|%)\s*(?:\d+(?:[,.]\d+)?|\(|sqrt|wurzel)"
    )

    def __init__(self, path_tools):
        self.path_tools = path_tools
        self.log_path = path_tools.paths()["logs"] / "request_router_1_0.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_decision: dict = {}

    def decide(self, text: str, intent: Intent | None = None) -> RouteDecision:
        raw = text or ""
        value = normalize(raw).strip()
        command_value = value.strip(" .!?")
        lower = raw.casefold().strip()
        if command_value in self.CANONICAL_COMMANDS:
            return RouteDecision("Governance", "canonical_engine", "Canonical-Statusbefehl hat Vorrang.", ["StatusAgent"], ["StatusAgent"])
        if command_value in self.STATUS_COMMANDS:
            return RouteDecision("Statusabfrage", "status_agent", "Statusbefehle haben höchste Priorität.", ["CanonicalEngine"], ["SystemAgent"])
        if self._looks_like_change(raw):
            return RouteDecision(
                "Änderungsauftrag",
                "change_agent",
                "Änderungsverb erkannt; ChangeAgent hat Vorrang vor Wissens- und Foundation-Abfragen.",
                ["FoundationAgent", "KnowledgeAgent", "MemoryAgent"],
                ["StatusAgent"],
            )
        if self._looks_like_math(raw):
            return RouteDecision("Programmierung" if self._looks_like_code(raw) else "Rechenaufgabe", "math_agent", "Mathematischer Ausdruck erkannt.", ["KnowledgeAgent"], [])
        if self._looks_like_vision(raw):
            return RouteDecision("Bildanalyse", "vision_agent", "Bildanalyseauftrag oder Bilddatei erkannt; VisionAgent arbeitet read-only.", ["FileAgent"], ["FileAgent"])
        if self._looks_like_cgm(raw):
            return RouteDecision("Canonical Git Governance", "canonical_git_manager", "CGM-2.0-Governanceauftrag erkannt.", ["GitAgent"], ["StatusAgent"])
        if self._looks_like_git(raw):
            return RouteDecision("Git", "git_agent", "Git-Leseauftrag erkannt; GitAgent arbeitet read-only.", ["CGM 2.0"], ["StatusAgent"])
        if self._looks_like_code_agent(raw):
            return RouteDecision("Codeanalyse", "code_agent", "Code-/Projektanalyseauftrag erkannt; CodeAgent arbeitet read-only.", ["FileAgent", "DevelopmentAgent"], ["FileAgent"])
        chemistry_capability = self._chemistry_capability(raw)
        if chemistry_capability:
            return RouteDecision(
                "Chemie",
                "capability:" + chemistry_capability,
                "Chemie-Capability erkannt; CAIM soll einen aktiven Spezialagenten auswaehlen.",
                ["KnowledgeAgent", "ResearchAgent"],
                ["KnowledgeAgent"],
            )
        if command_value.endswith("status"):
            return RouteDecision("Statusabfrage", "status_agent", "Statusbefehle haben höchste Priorität.", ["CanonicalEngine"], ["SystemAgent"])
        if self._looks_like_file(raw):
            return RouteDecision("Dateioperation", "file_agent", "Datei- oder Pfadangabe erkannt; FileAgent hat Vorrang.", ["LearningAgent", "KnowledgeAgent"], ["KnowledgeAgent"])
        if re.search(r"https?://", raw) or any(marker in value for marker in self.WEB_MARKERS):
            return RouteDecision("Webauftrag", "web_agent", "URL/Web-/Internetauftrag erkannt.", ["LearningAgent"], ["KnowledgeAgent"])
        if any(marker in value for marker in self.LEARNING_MARKERS):
            return RouteDecision("Lernauftrag", "learning_agent", "Lernverb erkannt.", ["WebAgent", "FileAgent"], ["KnowledgeAgent"])
        if self._looks_like_identity_config(raw):
            return RouteDecision(
                "Identity/Config",
                "identity_manager",
                "Strukturierte Identity-/Konfigurationsdaten erkannt.",
                ["MemoryAgent", "ConfigFallback"],
                ["MemoryAgent"],
            )
        if any(marker in value for marker in self.GOVERNANCE_MARKERS):
            return RouteDecision("Governance", "canonical_engine", "Governance/Foundation/Canonical-Bezug erkannt.", ["StatusAgent"], ["KnowledgeAgent"])
        if any(marker in value for marker in self.DIAGNOSIS_MARKERS):
            return RouteDecision("Diagnose", "diagnostic_agent", "Diagnosemarker erkannt.", ["StatusAgent"], ["SystemAgent"])
        if any(marker in value for marker in self.MEMORY_MARKERS):
            return RouteDecision("Memory", "memory_agent", "Memory-/Erinnerungsbezug erkannt.", ["KnowledgeAgent"], ["KnowledgeAgent"])
        if self._looks_like_structured_config(raw):
            return RouteDecision(
                "Konfiguration",
                "config_fallback",
                "Strukturierte YAML/JSON-artige Konfiguration erkannt.",
                ["IdentityManager", "MemoryAgent"],
                ["MemoryAgent"],
            )
        if any(marker in value for marker in self.ADMIN_MARKERS):
            return RouteDecision("Administration", "admin_agent", "Administrationsbefehl erkannt.", ["StatusAgent"], ["SystemAgent"])
        if self._looks_like_code(raw):
            return RouteDecision("Programmierung", "programming_agent", "Programmier-/Codebezug erkannt.", ["KnowledgeAgent"], ["DialogueAgent"])
        if raw.rstrip().endswith("?") or value.startswith(self.QUESTION_STARTERS):
            return RouteDecision("Wissensfrage", "knowledge_agent", "Allgemeine Wissensfrage erkannt; Internet nur bei Bedarf.", ["MemoryAgent", "LocalKnowledge", "WebAgent"], ["MemoryAgent", "LocalKnowledge", "WebAgent"])
        return RouteDecision("Sonstige", "dialogue_agent", "Keine Spezialklasse erkannt.", ["KnowledgeAgent"], ["KnowledgeAgent"])

    def record(self, text: str, decision: RouteDecision, result: str, selected_agent: str | None = None) -> None:
        elapsed_ms = int((time.perf_counter() - decision.started_at) * 1000)
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": text,
            "request_class": decision.request_class,
            "selected_agent": selected_agent or decision.selected_agent,
            "alternatives": decision.alternatives,
            "fallbacks": decision.fallbacks,
            "duration_ms": elapsed_ms,
            "result": result[:500],
            "reason": decision.reason,
            "sources": decision.sources,
        }
        self.last_decision = row
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def format_status(self) -> str:
        row = self.last_decision
        if not row:
            return "Request Router 1.0 Status:\n- Noch keine Routingentscheidung in dieser Sitzung."
        return "\n".join([
            "Request Router 1.0 Status:",
            f"- erkannte Anfrageklasse: {row.get('request_class', '-')}",
            f"- ausgewählter Agent: {row.get('selected_agent', '-')}",
            f"- Begründung: {row.get('reason', '-')}",
            "- verwendete Quellen: " + (", ".join(row.get("sources", [])) if row.get("sources") else "-"),
            "- Fallback-Agenten: " + (", ".join(row.get("fallbacks", [])) if row.get("fallbacks") else "-"),
            f"- Antwortdauer: {row.get('duration_ms', 0)} ms",
            f"- Protokoll: {self.log_path}",
        ])

    def _looks_like_file(self, text: str) -> bool:
        value = normalize(text)
        return bool(self.WINDOWS_PATH.search(text or "") or self.FILE_SUFFIX.search(text or "")) and (
            any(marker in value for marker in self.FILE_MARKERS) or True
        )

    def _looks_like_math(self, text: str) -> bool:
        value = normalize(text)
        if any(marker in value for marker in ("berechne", "rechne", "wieviel ist", "wie viel ist", "wurzel", "sqrt", "√", "prozent")):
            return True
        return bool(self.MATH_EXPRESSION.search(text or ""))

    def _looks_like_change(self, text: str) -> bool:
        value = normalize(text or "")
        return any(marker in value for marker in self.CHANGE_MARKERS) or bool(
            re.search(r"(?i)\bersetze\s+regel\s+\S+\s+durch\b", text or "")
        )

    def _looks_like_identity_config(self, text: str) -> bool:
        value = (text or "").casefold()
        if re.search(r"(?im)^\s*(identity|creator|preferred_address|assistant|role|roles)\s*:", text or ""):
            return True
        return sum(1 for marker in self.IDENTITY_MARKERS if marker in value) >= 3

    def _looks_like_structured_config(self, text: str) -> bool:
        value = (text or "").casefold()
        lines = [line for line in (text or "").splitlines() if line.strip()]
        yaml_like = len(lines) >= 2 and sum(1 for line in lines if ":" in line) >= 2
        json_like = value.strip().startswith("{") and value.strip().endswith("}")
        return (yaml_like or json_like) and any(marker in value for marker in self.CONFIG_MARKERS + self.IDENTITY_MARKERS)

    def _looks_like_vision(self, text: str) -> bool:
        value = normalize(text or "")
        return any(marker in value for marker in self.VISION_MARKERS) or bool(self.IMAGE_SUFFIX.search(text or ""))

    def _chemistry_capability(self, text: str) -> str:
        value = normalize(text or "")
        raw = text or ""
        if not any(marker in value for marker in self.CHEMISTRY_MARKERS) and not re.search(r"\b\d{2,7}-\d{2}-\d\b", raw):
            return ""
        if re.search(r"\b\d{2,7}-\d{2}-\d\b", raw) or "cas" in value:
            return "chemistry.cas"
        if any(marker in value for marker in ("sicherheit", "gefahr", "gefahrstoff", "safety")):
            return "chemistry.safety"
        if "summenformel" in value or re.search(r"\b(?:[A-Z][a-z]?\d*){2,}\b", raw):
            return "chemistry.formula"
        if any(marker in value for marker in ("eigenschaft", "properties", "molare masse", "aggregatzustand")):
            return "chemistry.properties"
        return "chemistry.lookup"

    def _looks_like_git(self, text: str) -> bool:
        value = normalize(text or "")
        return any(marker in value for marker in self.GIT_MARKERS)

    def _looks_like_cgm(self, text: str) -> bool:
        value = normalize(text or "")
        return any(marker in value for marker in self.CGM_MARKERS)

    def _looks_like_code_agent(self, text: str) -> bool:
        value = normalize(text or "")
        return any(marker in value for marker in self.CODE_MARKERS) or (
            bool(self.CODE_SUFFIX.search(text or "")) and any(marker in value for marker in ("code", "projektkarte", "einstiegspunkt", "sprache"))
        )

    @staticmethod
    def _looks_like_code(text: str) -> bool:
        lower = (text or "").casefold()
        return any(marker in lower for marker in ("def ", "class ", "function ", "import ", "console.log", "python:", "code "))
