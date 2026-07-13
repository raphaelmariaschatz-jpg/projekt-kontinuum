# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ResponsePolicyResult:
    answer: str
    changed: bool = False
    violations: list[str] = field(default_factory=list)


class ResponsePolicyManager:
    VERSION = "1.0"
    FOUNDATION_RULE = (
        "Kontinuum darf niemals Antworten erzeugen, die den Fähigkeiten oder dem aktuellen Zustand seiner "
        "eigenen Architektur widersprechen. Ist eine Aufgabe nicht ausführbar, muss die tatsächliche Ursache "
        "benannt werden, z. B. fehlende Berechtigung, nicht geladene Datei, Routerfehler oder Agent nicht verfügbar."
    )

    MEMORY_PATTERNS = (
        r"\bich habe keine erinnerungen\b",
        r"\bich verf[üu]ge über keine erinnerungen\b",
        r"\bich kann mich an nichts erinnern\b",
    )
    FILE_PATTERNS = (
        r"\bich kann keine dateien lesen\b",
        r"\bich kann keine dateien öffnen\b",
        r"\bich habe keinen zugriff auf dateien\b",
        r"\bdateien kann ich nicht lesen\b",
    )
    WEB_PATTERNS = (
        r"\bich habe keinen internetzugang\b",
        r"\bich kann nicht ins internet\b",
        r"\bich kann keine webseiten abrufen\b",
        r"\bich habe keinen zugriff auf das internet\b",
    )
    KNOWLEDGE_PATTERNS = (
        r"\bich weiß nichts darüber\b",
        r"\bich weiss nichts darüber\b",
        r"\bdazu weiß ich nichts\b",
        r"\bdazu weiss ich nichts\b",
    )

    def __init__(self, system):
        self.system = system
        self.last_result = ResponsePolicyResult("")

    def apply(self, answer: str, agent: str = "", intent=None) -> ResponsePolicyResult:
        text = answer or ""
        result = ResponsePolicyResult(text)
        result = self._guard_capability_claims(result)
        result = self._guard_router_echo(result)
        self.last_result = result
        return result

    def _guard_capability_claims(self, result: ResponsePolicyResult) -> ResponsePolicyResult:
        replacements: list[tuple[bool, tuple[str, ...], str, str]] = [
            (
                self._foundation_memory_exists(),
                self.MEMORY_PATTERNS,
                "foundation_memory_contradiction",
                "Ich habe Foundation Memory und kann Erinnerungs-/Foundation-Kontext prüfen; falls nichts gefunden wurde, liegt es an fehlenden passenden Treffern oder Berechtigungen.",
            ),
            (
                self._agent_active("file_agent"),
                self.FILE_PATTERNS,
                "file_agent_contradiction",
                "Ich habe einen FileAgent und kann freigegebene Dateien lesen; falls eine Datei nicht gelesen wurde, liegt es an Pfad, Freigabe, Existenz, Format oder Extraktion.",
            ),
            (
                self._agent_active("web_agent"),
                self.WEB_PATTERNS,
                "web_agent_contradiction",
                "Ich habe einen aktiven WebAgent und kann Webquellen abrufen; falls kein Abruf erfolgte, liegt es an Auftrag, Netzwerk, robots.txt, Berechtigung oder Connector-Fehler.",
            ),
            (
                self._knowledge_agent_exists(),
                self.KNOWLEDGE_PATTERNS,
                "knowledge_agent_contradiction",
                "Ich habe einen KnowledgeAgent; wenn lokal keine belastbare Antwort vorliegt, muss ich das als fehlende Quelle oder nötige Recherche benennen.",
            ),
        ]
        text = result.answer
        for active, patterns, violation, replacement in replacements:
            if not active:
                continue
            for pattern in patterns:
                text, count = re.subn(pattern, replacement, text, flags=re.I)
                if count:
                    result.changed = True
                    result.violations.append(violation)
        result.answer = text
        return result

    def _guard_router_echo(self, result: ResponsePolicyResult) -> ResponsePolicyResult:
        router = getattr(self.system, "request_router", None)
        last = getattr(router, "last_decision", {}) if router else {}
        user_input = str(last.get("input") or self._last_user_input()).strip()
        if not user_input or not result.answer:
            return result
        normalized_answer = self._normalize(result.answer)
        normalized_input = self._normalize(user_input)
        if normalized_answer == normalized_input:
            result.answer = (
                "Der Router hat den Auftrag erkannt, aber es wurde keine ausführende Agentenantwort erzeugt. "
                "Tatsächliche Ursache: Router-/Agentenübergabe unvollständig oder Agent nicht verfügbar."
            )
            result.changed = True
            result.violations.append("router_echo_without_execution")
        return result

    def _foundation_memory_exists(self) -> bool:
        memory = getattr(self.system, "foundation_memory", None)
        if not memory:
            return False
        try:
            status = memory.status()
            return bool(status.get("ok", True))
        except Exception:
            return True

    def _agent_active(self, name: str) -> bool:
        agent = getattr(self.system, name, None)
        if not agent:
            return False
        try:
            status = agent.status()
            return bool(status.get("active", True))
        except Exception:
            return True

    def _knowledge_agent_exists(self) -> bool:
        return any(getattr(agent, "name", "") == "knowledge" for agent in getattr(self.system, "agents", []))

    def _last_user_input(self) -> str:
        conversation = getattr(self.system, "conversation", None)
        if not conversation:
            return ""
        try:
            for turn in reversed(conversation.recent_context(limit=6)):
                if turn.get("role") == "user":
                    return str(turn.get("content", ""))
        except Exception:
            return ""
        return ""

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join((value or "").split()).casefold().strip(" .!?")
