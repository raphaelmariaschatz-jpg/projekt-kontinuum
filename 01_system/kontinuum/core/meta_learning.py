# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import dataclass


PHASES = {
    1: "Unbewusste Inkompetenz",
    2: "Bewusste Inkompetenz",
    3: "Bewusste Kompetenz",
    4: "Unbewusste Kompetenz",
}


@dataclass(frozen=True)
class LearningAssessment:
    phase: int
    phase_name: str
    strategy: str
    open_gaps: list[str]
    evidence: dict

    def as_dict(self) -> dict:
        return {
            "phase": self.phase,
            "phase_name": self.phase_name,
            "strategy": self.strategy,
            "open_gaps": self.open_gaps,
            "evidence": self.evidence,
        }


class MetaLearningEngine:
    """Evaluates learning progress from evidence instead of claiming knowledge."""

    def assess(self, task: dict, references: list[dict]) -> LearningAssessment:
        metadata = task.get("metadata", {})
        topics = [str(topic) for topic in task.get("topics", []) if str(topic).strip()]
        cycles = int(metadata.get("cycles", 0))
        applications = int(metadata.get("successful_applications", 0))
        last_application_successful = metadata.get("last_application_successful")
        source_areas = sorted(
            {
                str(reference.get("metadata", {}).get("area", ""))
                for reference in references
                if reference.get("metadata", {}).get("area")
            }
        )
        referenced_topics = {
            str(topic)
            for reference in references
            for topic in reference.get("metadata", {}).get("topics", [])
            if str(topic).strip()
        }
        open_gaps = [topic for topic in topics if topic not in referenced_topics]
        learning_form = self.learning_form_for(task.get("subject", ""))
        if not topics:
            open_gaps = ["Lerngebiet in konkrete Teilgebiete gliedern"]

        if cycles == 0:
            phase = 2
            strategy = "Lernlücke bewusst beschreiben, Teilgebiete bilden und erste belastbare Fundstellen finden."
        elif last_application_successful is False:
            phase = 2
            strategy = "Fehlgeschlagene Anwendung analysieren, erkannte Lücke bearbeiten und erneut bewusst prüfen."
        elif len(references) < 3 or len(source_areas) < 2 or open_gaps:
            phase = 2
            strategy = "Offene Lücken schließen und Fundstellen aus unterschiedlichen Bereichen vergleichen."
        elif applications < 3:
            phase = 3
            strategy = "Wissen bewusst anwenden, erklären, prüfen und Fehler als neue Lernlücken erfassen."
        else:
            phase = 4
            strategy = "Kompetenz regelmäßig stichprobenartig prüfen und bei Fehlern wieder bewusst bearbeiten."

        return LearningAssessment(
            phase=phase,
            phase_name=PHASES[phase],
            strategy=strategy,
            open_gaps=open_gaps[:12],
            evidence={
                "cycles": cycles,
                "references": len(references),
                "source_areas": source_areas,
                "successful_applications": applications,
                "failed_applications": int(metadata.get("failed_applications", 0)),
                "learning_form": learning_form,
            },
        )

    @staticmethod
    def is_valid_subject(subject: str) -> bool:
        value = " ".join((subject or "").split())
        lower = value.casefold()
        instruction_phrases = (
            "benutze ",
            "verwende ",
            "für das lernen",
            "fuer das lernen",
            "auch die google suche",
        )
        return (
            bool(value)
            and len(value) <= 120
            and "\n" not in subject
            and "http://" not in lower
            and "https://" not in lower
            and lower not in {"http", "https", "www"}
            and not any(phrase in lower for phrase in instruction_phrases)
        )

    @staticmethod
    def learning_form_for(subject: str) -> str:
        lower = (subject or "").casefold()
        if any(term in lower for term in ("programm", "python", "werkzeug", "tool", "software")):
            return "kognitiv-prozedural"
        return "kognitiv"
