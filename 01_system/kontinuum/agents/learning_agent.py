# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import re
import unicodedata

from kontinuum.version import APP_VERSION
from .base_agent import AgentResult, BaseAgent


class LearningAgent(BaseAgent):
    name = "learning"
    FIRST_PROGRAMMING_LANGUAGE = "Python"

    SUBJECTS = {
        "mathematik": ["Arithmetik", "Algebra", "Geometrie", "Analysis", "Statistik"],
        "physik": ["Mechanik", "Thermodynamik", "Elektromagnetismus", "Optik", "Quantenphysik"],
        "chemie": ["Atombau", "Periodensystem", "Bindungen", "Reaktionen", "Organische Chemie"],
        "biologie": ["Zellbiologie", "Genetik", "Evolution", "Oekologie"],
        "informatik": ["Algorithmen", "Datenstrukturen", "Datenbanken", "KI", "IT-Sicherheit"],
        "bewusstsein": ["Selbstmodell", "Gedaechtnis", "Qualia", "Intentionalitaet", "KI-Bewusstsein"],
        "programmieren": ["Python-Grundlagen", "Datentypen", "Kontrollfluss", "Funktionen", "Tests", "Projekte"],
    }

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return (
            "lernstatus" in lower
            or lower in {
                "lernprojekte",
                "zeige alle lernprojekte",
                "zeige mir alle lernprojekte",
                "zeige aktive lernprojekte",
            }
            or "metalernstatus" in lower
            or lower.startswith(("lernphase ", "lernanwendung "))
            or "programmiersprache" in lower
            or bool(re.search(r"\b(?:lerne|studiere|trainiere)\b", lower))
        )

    def handle(self, prompt: str) -> AgentResult:
        lower = prompt.casefold().strip()
        if "metalernstatus" in lower:
            return AgentResult(self.name, True, self._meta_learning_status())
        if lower.startswith("lernphase "):
            subject = prompt.split(" ", 1)[1].strip()
            return AgentResult(self.name, True, self._subject_phase(subject))
        if lower.startswith("lernanwendung "):
            return AgentResult(self.name, True, self._record_application(prompt))
        if "lernstatus" in lower:
            return AgentResult(self.name, True, self._learning_status())
        if lower in {
            "lernprojekte",
            "zeige alle lernprojekte",
            "zeige mir alle lernprojekte",
            "zeige aktive lernprojekte",
        }:
            return AgentResult(self.name, True, self._list_projects())

        if "programmiersprache" in lower:
            answer = (
                f"Ich lerne zuerst {self.FIRST_PROGRAMMING_LANGUAGE}. "
                "Python eignet sich gut fuer den Einstieg und wird bereits im Kontinuum-Kern verwendet."
            )
            return AgentResult(self.name, True, answer)

        subjects = self._extract_subjects(prompt)
        if not subjects:
            return AgentResult(
                self.name,
                True,
                "Kein klar abgegrenztes Lernziel erkannt. Format: lerne <Thema>.",
            )
        answers = [self._create_project(subject) for subject in subjects]
        return AgentResult(self.name, True, "\n\n".join(answers))

    def _create_project(self, subject: str) -> str:
        canonical, subject_key = self._canonical_subject(subject)
        if not self._is_valid_subject(canonical):
            return f"Lernziel abgelehnt: {canonical}. Bitte nenne ein klar abgegrenztes Fach- oder Sachthema."
        existing = self._existing_project(canonical)
        if existing:
            continuous_learning = self.config.get("continuous_learning")
            if continuous_learning:
                continuous_learning.add_task(canonical, existing.get("topics", []), origin="learning_agent")
            return (
                f"Lernprojekt {canonical} existiert bereits.\n"
                "Vorhandenes Lernprojekt aktualisiert, nicht neu angelegt.\n"
                f"Status: {'aktiv' if existing.get('active', True) else 'inaktiv'}."
            )
        topics = self.SUBJECTS.get(
            subject_key,
            ["Grundlagen", "Begriffe", "Kernkonzepte", "Methoden", "Anwendungen"],
        )
        metadata = {"subject": canonical, "topics": topics, "version": APP_VERSION}
        if subject_key == "programmieren":
            metadata["first_language"] = self.FIRST_PROGRAMMING_LANGUAGE

        memory_id = self.remember("learning.project", f"Lernprojekt: {canonical}", metadata)
        continuous_learning = self.config.get("continuous_learning")
        if continuous_learning:
            continuous_learning.add_task(canonical, topics, origin="learning_agent")
        for topic in topics:
            self.add_edge(f"Lernprojekt: {canonical}", "enthaelt Lerngebiet", topic)
        platform = self.config.get("knowledge_platform")
        if platform:
            platform.integrate(
                f"Lernprojekt {canonical}: {', '.join(topics)}",
                origin="learning",
                title=f"Lernprojekt {canonical}",
                existing_memory_id=memory_id,
                extra={"subject": canonical, "topics": topics},
            )

        answer = f"Lernprojekt angelegt: {canonical}\nTeilgebiete: {', '.join(topics)}."
        if subject_key == "programmieren":
            answer += f"\nErste Programmiersprache: {self.FIRST_PROGRAMMING_LANGUAGE}."
        return answer

    @classmethod
    def _extract_subjects(cls, prompt: str) -> list[str]:
        matches = re.findall(
            r"\b(?:lerne|studiere|trainiere)(?:\s+zuerst)?\s+(?:zu\s+)?([^.!?]+)",
            prompt,
            flags=re.I,
        )
        if not matches:
            return []
        subjects: list[str] = []
        for match in matches:
            for subject in re.split(r"\s*[,;]\s*", match):
                clean = " ".join(subject.split()).strip(" .!?")
                if clean and clean.casefold() not in {item.casefold() for item in subjects}:
                    subjects.append(clean)
        return subjects

    @classmethod
    def _canonical_subject(cls, subject: str) -> tuple[str, str]:
        key = cls._normalize(subject).strip(" .!?")
        aliases = {
            "bewusstsein": "Bewusstsein",
            "geogrphie": "Geographie",
            "geographie": "Geographie",
            "python": "Python",
            "google suchmaschiene": "Google Suchmaschine",
            "google suchmaschine": "Google Suchmaschine",
        }
        if key in {"programmieren", "programmierung", "programming"}:
            return "Programmieren", "programmieren"
        canonical = aliases.get(key, subject[:1].upper() + subject[1:] if subject else "Allgemeines Wissen")
        return canonical, cls._normalize(canonical)

    @staticmethod
    def _normalize(text: str) -> str:
        decomposed = unicodedata.normalize("NFKD", (text or "").casefold().replace("ß", "ss"))
        return "".join(character for character in decomposed if not unicodedata.combining(character))

    @staticmethod
    def _is_valid_subject(subject: str) -> bool:
        value = " ".join((subject or "").split())
        lower = value.casefold()
        instruction_phrases = ("benutze ", "verwende ", "für das lernen", "fuer das lernen", "auch die google suche")
        return (
            bool(value)
            and len(value) <= 120
            and "\n" not in subject
            and "http://" not in lower
            and "https://" not in lower
            and lower not in {"http", "https", "www"}
            and not any(phrase in lower for phrase in instruction_phrases)
        )

    def _learning_status(self) -> str:
        projects = self.storage.list_learning_tasks(active_only=True) if self.storage else []

        if not projects:
            return f"Lernsystem {APP_VERSION} aktiv. Noch keine Lernprojekte angelegt."
        continuous_learning = self.config.get("continuous_learning")
        continuous_status = continuous_learning.status() if continuous_learning else {}
        return (
            f"Lernsystem {APP_VERSION} aktiv. Aktive Lernprojekte: {len(projects)}. Auswahl: "
            + ", ".join(project["subject"] for project in projects[:10])
            + (". Nutze 'zeige alle Lernprojekte' für die vollständige Liste" if len(projects) > 10 else "")
            + ". Kontinuierlicher Lerndienst: "
            + ("läuft." if continuous_status.get("running") else "nicht aktiv.")
        )

    def _list_projects(self) -> str:
        projects = self.storage.list_learning_tasks(active_only=True) if self.storage else []
        if not projects:
            return "Noch keine aktiven Lernprojekte angelegt."
        lines = [f"Aktive Lernprojekte ({len(projects)}):"]
        for index, project in enumerate(projects, start=1):
            integrated = self._integrated_units(project["subject"])
            base = "ja" if integrated > 0 else "nein"
            lines.append(
                f"{index}. {project['subject']} | Status: aktiv | Integrierte Wissenseinheiten: {integrated} | Abrufbare Basisantworten: {base}"
            )
        return "\n".join(lines)

    def _existing_project(self, canonical: str) -> dict | None:
        key = self._normalize(canonical)
        if self.storage:
            for task in self.storage.all_learning_tasks():
                if self._normalize(task["subject"]) == key:
                    return {**task, "active": task["metadata"].get("active", True)}
            for project in self.storage.existing_learning_projects():
                if self._normalize(project["subject"]) == key:
                    return {**project, "active": True}
        return None

    def _integrated_units(self, subject: str) -> int:
        if not self.storage:
            return 0
        pattern = f"%{subject}%"
        with self.storage.connect() as db:
            return int(db.execute(
                """SELECT COUNT(*) FROM knowledge_items
                   WHERE kind = 'knowledge.integrated'
                     AND (content LIKE ? OR metadata LIKE ?)""",
                (pattern, pattern),
            ).fetchone()[0])

    def _meta_learning_status(self) -> str:
        service = self.config.get("continuous_learning")
        if not service:
            return "Meta-Lernen ist nicht angebunden."
        rows = service.meta_status()
        if not rows:
            return "Noch keine Meta-Lernbewertungen vorhanden."
        lines = ["Meta-Lernstatus:"]
        for row in rows:
            state = row["phase"] if row["active"] else "deaktiviertes Lernziel"
            lines.append(f"- {row['subject']}: {state} | nächste Strategie: {row['strategy']}")
        return "\n".join(lines)

    def _subject_phase(self, subject: str) -> str:
        service = self.config.get("continuous_learning")
        if not service:
            return "Meta-Lernen ist nicht angebunden."
        row = next((item for item in service.meta_status(100) if item["subject"].casefold() == subject.casefold()), None)
        if not row:
            return f"Kein Lernauftrag für {subject} gefunden."
        gaps = ", ".join(row["open_gaps"]) if row["open_gaps"] else "keine ausdrücklich offenen Lücken"
        return f"{row['subject']}: {row['phase']}. Nächste Strategie: {row['strategy']} Offene Lücken: {gaps}."

    def _record_application(self, prompt: str) -> str:
        service = self.config.get("continuous_learning")
        if not service:
            return "Meta-Lernen ist nicht angebunden."
        match = re.match(r"lernanwendung\s+(.+?)\s+(erfolgreich|fehlgeschlagen)(?:\s*:\s*(.*))?$", prompt, flags=re.I)
        if not match:
            return "Format: lernanwendung <Thema> erfolgreich|fehlgeschlagen: <kurze Evidenz>"
        subject, outcome, detail = match.groups()
        successful = outcome.casefold() == "erfolgreich"
        if not service.record_application(subject.strip(), successful, detail or ""):
            return f"Kein Lernauftrag für {subject.strip()} gefunden."
        return f"Anwendungsevidenz für {subject.strip()} wurde als {outcome.casefold()} erfasst."
