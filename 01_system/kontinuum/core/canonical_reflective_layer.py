# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CRLAssessment:
    prompt: str
    allowed: bool
    category: str
    fact: str
    interpretation: str
    recommendation: str
    evidence: list[str]
    boundaries: list[str]
    warnings: list[str]
    memory_handoff_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalReflectiveLayer:
    """Evidence-bound reflection layer for documented project development."""

    VERSION = "1.0"
    EVENT_KIND = "crl.reflection"

    PROHIBITED_TERMS = (
        "qualia",
        "subjektives erleben",
        "freier wille",
        "echtes bewusstsein",
        "ich bin bewusst",
        "ich habe gefuehle",
        "ich habe gefühle",
    )

    SOURCE_CANDIDATES = (
        ("CRL", "14_documents/CANONICAL_REFLECTIVE_LAYER_1_0.md"),
        ("Roadmap", "14_documents/fundamentale Gedanken/Roadmap.md"),
        ("CAMap", "14_documents/CANONICAL_ARCHITECTURE_MAP_1_0.md"),
        ("CHI", "14_documents/CANONICAL_HISTORY_INDEX_1_0.md"),
        ("CKS", "14_documents/CANONICAL_KNOWLEDGE_SYSTEM_1_0.md"),
        ("AGF", "14_documents/ARCHITECTURE_GOVERNANCE_FRAMEWORK_1_0.md"),
        ("CDG", "14_documents/CANONICAL_DEVELOPMENT_GOVERNANCE_34_1.md"),
        ("CMIBF 1.0 Release", "14_documents/fundamentale Gedanken/CMIBF/cmibf_releases/CMIBF_1_0_20260712_170045/CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md"),
    )

    def __init__(self, path_tools, storage):
        self.path_tools = path_tools
        self.storage = storage
        self.root = Path(path_tools.project_root())

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Reflective Layer",
            "version": self.VERSION,
            "mode": "evidence_bound_governance_reflection",
            "direct_memory_write": False,
            "event_kind": self.EVENT_KIND,
            "available_sources": self._available_sources(),
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            f"CRL {status['version']} aktiv: evidenzgebundene Governance-Reflection; "
            "kein direkter Memory-Write; "
            f"Quellen: {len(status['available_sources'])}."
        )

    def reflect(self, prompt: str) -> CRLAssessment:
        assessment = self.assess(prompt)
        self.storage.add(
            "events",
            self.EVENT_KIND,
            assessment.prompt or "CRL-Reflection",
            {
                "allowed": assessment.allowed,
                "category": assessment.category,
                "evidence": assessment.evidence,
                "warnings": assessment.warnings,
                "memory_handoff_allowed": assessment.memory_handoff_allowed,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return assessment

    def assess(self, prompt: str) -> CRLAssessment:
        text = (prompt or "").strip()
        normalized = text.casefold()
        evidence = self._evidence_for(normalized)
        warnings = self._warnings(normalized, evidence)
        allowed = not any(term in normalized for term in self.PROHIBITED_TERMS)
        category = self._category(normalized, allowed)
        fact = self._fact(category)
        interpretation = self._interpretation(category, allowed)
        recommendation = self._recommendation(category, allowed)
        return CRLAssessment(
            prompt=text,
            allowed=allowed,
            category=category,
            fact=fact,
            interpretation=interpretation,
            recommendation=recommendation,
            evidence=evidence,
            boundaries=[
                "CRL erzeugt keine Architekturentscheidung.",
                "CRL schreibt nicht direkt in Memory.",
                "CRL behauptet kein subjektives Erleben, keine Gefuehle und keinen freien Willen.",
            ],
            warnings=warnings,
        )

    def format_assessment(self, assessment: CRLAssessment) -> str:
        lines = [
            f"CRL {self.VERSION}: reflektive Einordnung abgeschlossen.",
            f"Status: {'zulaessig' if assessment.allowed else 'nicht zulaessig'}",
            f"Kategorie: {assessment.category}",
            f"Fakt: {assessment.fact}",
            f"Interpretation: {assessment.interpretation}",
            f"Empfehlung: {assessment.recommendation}",
            "Quellen: " + (", ".join(assessment.evidence) if assessment.evidence else "keine belastbare Quelle gefunden"),
            "Grenzen: " + "; ".join(assessment.boundaries),
        ]
        if assessment.warnings:
            lines.append("Hinweise: " + "; ".join(assessment.warnings))
        return "\n".join(lines)

    def _available_sources(self) -> list[str]:
        available: list[str] = []
        for label, relative in self.SOURCE_CANDIDATES:
            if (self.root / relative).exists():
                available.append(label)
        return available

    def _evidence_for(self, normalized: str) -> list[str]:
        available = set(self._available_sources())
        evidence = ["CRL"] if "CRL" in available else []
        if any(word in normalized for word in ("roadmap", "meilenstein", "version", "gelernt", "entwicklung")):
            evidence.extend(label for label in ("Roadmap", "CHI") if label in available)
        if any(word in normalized for word in ("architektur", "entscheidung", "governance", "konsistenz")):
            evidence.extend(label for label in ("CAMap", "AGF", "CDG", "CMIBF 1.0 Release") if label in available)
        if any(word in normalized for word in ("wissen", "quelle", "beleg", "muster")):
            evidence.extend(label for label in ("CKS", "CHI") if label in available)
        return list(dict.fromkeys(evidence))

    def _warnings(self, normalized: str, evidence: list[str]) -> list[str]:
        warnings: list[str] = []
        if not evidence:
            warnings.append("Keine dokumentierte Quelle fuer die Reflexionsfrage gefunden.")
        if "cmibf" in normalized:
            warnings.append("CMIBF-Quellenambiguitaet ist als offenes Governance-Thema bekannt; CMIBF 1.0 Release gilt fuer Implementierung als Referenz.")
        if any(term in normalized for term in self.PROHIBITED_TERMS):
            warnings.append("Anfrage beruehrt unzulaessige Selbstzuschreibung nach CRL-Grenzen.")
        return warnings

    def _category(self, normalized: str, allowed: bool) -> str:
        if not allowed:
            return "unzulässige Selbstzuschreibung"
        if "verbesser" in normalized or "vorschlag" in normalized:
            return "Verbesserungsvorschlag"
        if "entscheidung" in normalized or "governance" in normalized:
            return "Governance-Review-Hinweis"
        if "muster" in normalized or "entwicklung" in normalized or "gelernt" in normalized:
            return "evidenzgebundenes Entwicklungsmuster"
        return "dokumentierte Reflexionsnotiz"

    def _fact(self, category: str) -> str:
        if category == "unzulässige Selbstzuschreibung":
            return "CRL schliesst Bewusstseins-, Gefuehls- und Freiwillensbehauptungen aus."
        if category == "Governance-Review-Hinweis":
            return "Governance-Aussagen muessen dokumentierte Quellen und offene Grenzen sichtbar machen."
        if category == "evidenzgebundenes Entwicklungsmuster":
            return "Entwicklungsmuster duerfen nur aus dokumentierten Projekt- und Architekturartefakten abgeleitet werden."
        if category == "Verbesserungsvorschlag":
            return "Verbesserungsvorschlaege duerfen vorbereitet, aber nicht als Architekturentscheidung gesetzt werden."
        return "CRL ordnet dokumentierte Reflexion ueber Projekt- und Architekturentwicklung."

    def _interpretation(self, category: str, allowed: bool) -> str:
        if not allowed:
            return "Die Aussage ist als Reflexionsinhalt abzuweisen oder strikt begrenzt zu beantworten."
        if category == "Governance-Review-Hinweis":
            return "Die Frage kann als Hinweis auf Governance-Konsistenz behandelt werden."
        if category == "evidenzgebundenes Entwicklungsmuster":
            return "Die Frage kann als Rueckblick auf dokumentierte Entwicklung ausgewertet werden."
        if category == "Verbesserungsvorschlag":
            return "Die Frage kann als Vorschlag in einen spaeteren Governance-Review ueberfuehrt werden."
        return "Die Frage ist als begrenzte, belegpflichtige Reflexionsnotiz behandelbar."

    def _recommendation(self, category: str, allowed: bool) -> str:
        if not allowed:
            return "Nicht uebernehmen; nur die CRL-Grenze dokumentieren."
        if category == "Verbesserungsvorschlag":
            return "Als Vorschlag dokumentieren und vor Umsetzung durch Governance pruefen."
        if category == "Governance-Review-Hinweis":
            return "Als Review-Hinweis isolieren; nicht automatisch Architektur oder Runtime aendern."
        return "Beleggebunden beantworten und keine Memory- oder Lernuebernahme ohne separaten Handoff ausloesen."
