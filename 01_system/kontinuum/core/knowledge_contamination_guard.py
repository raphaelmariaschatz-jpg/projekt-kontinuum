from __future__ import annotations

from .conversation import normalize


class KnowledgeContaminationGuard:
    """Prevents status/report output from becoming domain knowledge."""

    MARKERS = (
        "systemstatus",
        "motivationsprioritaten",
        "motivationsprioritäten",
        "motivationserklarung",
        "motivationserklarung",
        "motivationserklärung",
        "wichtige einflusse",
        "wichtige einflüsse",
        "bedeutungspfad",
        "bedeutungsstatus",
        "relevanzstatus",
        "temporal relevance core",
        "foundation decision layer",
        "score-grund des motivation core",
        "grenze erklarbare bewertungsherkunft",
        "kein wille kein bewusstsein",
        "zirkularitatsverletzungen",
        "bedeutungsinflationsprufung",
        "kontinuitats-snapshots",
        "chronikschutz",
        "wissenslucken und prufauftrage",
        "priorisierte wissenslucken",
        "teilantwort zeitbudget",
        "teilantwort zu",
        "quellenseiten konnten nicht rechtzeitig abgerufen werden",
        "automatische zusammenfassung war nicht verfugbar",
        "bibtex formatted citation",
        "lernprojekt existiert bereits",
        "vorhandenes lernprojekt aktualisiert",
        "lernprojekt angelegt",
        "lernsystem aktiv",
        "mein name ist kontinuum",
        "ich bin projekt kontinuum",
        "du bist raphael",
        "dialogantwort",
    )
    REPORT_PREFIXES = (
        "Motivationsprioritäten:",
        "Motivationserklärung",
        "Wichtige Einflüsse",
        "Bedeutungspfad:",
        "Meaning Core",
        "Motivation Core",
        "Motivation Explanation Core",
        "Temporal Relevance Core",
        "Foundation Decision Layer",
        "Continuity Core",
        "Persistent Self Model Core",
        "Bedeutungsinflationsprüfung:",
        "Priorisierte Wissenslücken:",
        "Wissenslücken und Prüfaufträge",
        "Teilantwort",
        "Lernprojekt angelegt",
        "Lernprojekt Programmieren existiert bereits",
        "Mein Name ist Kontinuum. Ich bin Projekt Kontinuum",
        "Du bist Raphael",
    )

    def classify(self, text: str, origin: str = "", title: str = "") -> str:
        if origin in {"report", "status", "audit", "diagnostic"}:
            return "report"
        stripped = (text or "").strip()
        if any(stripped.startswith(prefix) for prefix in self.REPORT_PREFIXES):
            return "report"
        value = normalize(f"{title} {text}")
        compact = value.replace(":", " ")
        if any(marker in compact for marker in self.MARKERS):
            return "report"
        return "knowledge"

    def should_integrate(self, text: str, origin: str = "", title: str = "") -> bool:
        return self.classify(text, origin, title) == "knowledge"
