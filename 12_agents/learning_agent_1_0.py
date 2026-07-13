from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEARNING_AGENT_VERSION = "1.0"
LEARNING_CATEGORIES = (
    "verified_knowledge",
    "uncertain_knowledge",
    "duplicate_candidate",
    "conflict_detected",
    "source_required",
    "manual_review_required",
)
PROTECTED_ROOTS = ("03_memory", "04_knowledge", "32_data")
WRITE_VERBS = (
    "write",
    "save",
    "store",
    "persist",
    "delete",
    "update",
    "insert",
    "replace",
    "remember",
    "add_memory",
    "add_knowledge",
)
UNCERTAIN_MARKERS = (
    "maybe",
    "possibly",
    "probably",
    "unverified",
    "unknown source",
    "no source",
    "i think",
    "could be",
    "might be",
    "vermutlich",
    "vielleicht",
    "wahrscheinlich",
    "unklar",
    "unbelegt",
    "ohne quelle",
)
CONFLICT_MARKERS = (
    "conflicts with",
    "contradicts",
    "opposes",
    "widerspricht",
    "konflikt",
    "gegenteilig",
    "nicht vereinbar",
)
SOURCE_MARKERS = ("source:", "quelle:", "doi:", "isbn:", "http://", "https://")
HIGH_QUALITY_SOURCE_MARKERS = ("doi:", ".edu", ".gov", "university", "universität", "peer-reviewed", "official", "offiziell")
LOW_QUALITY_SOURCE_MARKERS = ("forum", "reddit", "blog", "unknown", "unbekannt", "hearsay", "hörensagen")


@dataclass(frozen=True)
class LearningSource:
    source_id: str
    content: str
    origin: str = "manual"
    source_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningAssessment:
    source_id: str
    category: str
    content_hash: str
    source_quality: str
    risk_level: str
    risks: tuple[str, ...]
    duplicate_of: str | None
    proposals: dict[str, list[str]]
    automatic_adoption_allowed: bool
    writes_performed: bool
    governance: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "category": self.category,
            "content_hash": self.content_hash,
            "source_quality": self.source_quality,
            "risk_level": self.risk_level,
            "risks": list(self.risks),
            "duplicate_of": self.duplicate_of,
            "proposals": self.proposals,
            "automatic_adoption_allowed": self.automatic_adoption_allowed,
            "writes_performed": self.writes_performed,
            "governance": self.governance,
        }


class LearningAgent10:
    """Read-only learning review agent for controlled knowledge intake.

    Learning Agent 1.0 classifies sources and creates review proposals only. It never
    writes to Memory, Knowledge, 32_data or external networks, and it never adopts
    knowledge automatically.
    """

    name = "learning_agent_1_0"
    version = LEARNING_AGENT_VERSION
    categories = LEARNING_CATEGORIES

    def __init__(self, project_root: str | Path | None = None, known_sources: list[dict[str, Any]] | None = None):
        self.project_root = Path(project_root or "C:/Projekt Kontinuum")
        self.known_hashes: dict[str, str] = {}
        for item in known_sources or []:
            content = str(item.get("content", ""))
            source_id = str(item.get("source_id") or item.get("id") or "known_source")
            if content:
                self.known_hashes[self._hash(content)] = source_id

    @staticmethod
    def _normalize(content: str) -> str:
        return re.sub(r"\s+", " ", (content or "").strip().casefold())

    @classmethod
    def _hash(cls, content: str) -> str:
        return hashlib.sha256(cls._normalize(content).encode("utf-8")).hexdigest()

    @staticmethod
    def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
        return any(marker in text for marker in markers)

    def recognize_source(self, content: str, origin: str = "manual", source_type: str = "text", **metadata: Any) -> LearningSource:
        source_id = metadata.pop("source_id", None) or self._hash(content)[:16]
        return LearningSource(source_id=str(source_id), content=content or "", origin=origin, source_type=source_type, metadata=metadata)

    def classify_source(self, source: LearningSource | str, known_sources: list[LearningSource | dict[str, Any] | str] | None = None) -> LearningAssessment:
        if isinstance(source, str):
            source = self.recognize_source(source)
        known_hashes = dict(self.known_hashes)
        for item in known_sources or []:
            if isinstance(item, LearningSource):
                known_hashes[self._hash(item.content)] = item.source_id
            elif isinstance(item, dict):
                content = str(item.get("content", ""))
                source_id = str(item.get("source_id") or item.get("id") or "known_source")
                if content:
                    known_hashes[self._hash(content)] = source_id
            else:
                known_hashes[self._hash(str(item))] = "known_source"

        text = self._normalize(source.content)
        content_hash = self._hash(source.content)
        duplicate_of = known_hashes.get(content_hash)
        risks: list[str] = []

        has_source = self._contains_any(text, SOURCE_MARKERS)
        uncertain = self._contains_any(text, UNCERTAIN_MARKERS)
        conflict = self._contains_any(text, CONFLICT_MARKERS)
        empty_or_too_short = len(text) < 40

        if duplicate_of:
            category = "duplicate_candidate"
            risks.append("Inhalt entspricht einer bekannten Quelle.")
        elif conflict:
            category = "conflict_detected"
            risks.append("Quelle markiert einen möglichen Wissenskonflikt.")
        elif uncertain:
            category = "uncertain_knowledge"
            risks.append("Quelle enthält Unsicherheitsmarker oder unklare Aussagen.")
        elif not has_source:
            category = "source_required"
            risks.append("Nachvollziehbare Quelle fehlt.")
        elif empty_or_too_short:
            category = "manual_review_required"
            risks.append("Inhalt ist zu kurz für belastbare Einordnung.")
        else:
            category = "verified_knowledge"

        source_quality = self.evaluate_source_quality(source)
        if source_quality == "low":
            risks.append("Quellenqualität niedrig oder nicht belastbar.")
        if source.metadata.get("requires_manual_review"):
            category = "manual_review_required"
            risks.append("Manuelle Prüfung wurde durch Metadaten angefordert.")

        risk_level = "low"
        if category in {"uncertain_knowledge", "source_required", "duplicate_candidate"} or source_quality == "medium":
            risk_level = "medium"
        if category in {"conflict_detected", "manual_review_required"} or source_quality == "low":
            risk_level = "high"

        assessment = LearningAssessment(
            source_id=source.source_id,
            category=category,
            content_hash=content_hash,
            source_quality=source_quality,
            risk_level=risk_level,
            risks=tuple(dict.fromkeys(risks)),
            duplicate_of=duplicate_of,
            proposals=self.create_proposals(source, category),
            automatic_adoption_allowed=False,
            writes_performed=False,
            governance=self.governance_context(),
        )
        return assessment

    def evaluate_source_quality(self, source: LearningSource) -> str:
        text = self._normalize(" ".join([source.content, source.origin, str(source.metadata)]))
        if self._contains_any(text, HIGH_QUALITY_SOURCE_MARKERS):
            return "high"
        if self._contains_any(text, LOW_QUALITY_SOURCE_MARKERS) or not self._contains_any(text, SOURCE_MARKERS):
            return "low"
        return "medium"

    def create_proposals(self, source: LearningSource, category: str) -> dict[str, list[str]]:
        summary = self._summarize(source.content)
        proposals = {"knowledge": [], "memory": [], "research": []}
        if category == "verified_knowledge":
            proposals["knowledge"].append(f"Review candidate for Knowledge: {summary}")
        elif category == "duplicate_candidate":
            proposals["research"].append(f"Compare duplicate candidate before consolidation: {summary}")
        elif category == "conflict_detected":
            proposals["research"].append(f"Open conflict review with canonical references: {summary}")
        elif category == "source_required":
            proposals["research"].append(f"Request verifiable source before adoption: {summary}")
        else:
            proposals["research"].append(f"Manual epistemic review required: {summary}")
        proposals["memory"].append("No direct memory write. Store only after explicit human approval.")
        return proposals

    @staticmethod
    def _summarize(content: str, limit: int = 180) -> str:
        cleaned = re.sub(r"\s+", " ", (content or "").strip())
        if len(cleaned) <= limit:
            return cleaned or "<empty source>"
        return cleaned[: limit - 3].rstrip() + "..."

    def check_write_operation(self, target_path: str | Path, operation: str = "write") -> dict[str, Any]:
        path_text = str(target_path).replace("/", "\\").casefold()
        operation_text = operation.casefold()
        protected = any(f"\\{root.casefold()}\\" in f"\\{path_text}\\" or path_text.endswith(f"\\{root.casefold()}") for root in PROTECTED_ROOTS)
        write_intent = any(verb in operation_text for verb in WRITE_VERBS)
        allowed = not (protected and write_intent)
        return {
            "allowed": allowed,
            "mode": "read_only_proposal_mode",
            "target_path": str(target_path),
            "operation": operation,
            "reason": "Protected Kontinuum data roots require explicit approval." if not allowed else "No protected write detected.",
        }

    def assert_no_write_operation(self, target_path: str | Path, operation: str = "write") -> bool:
        return not self.check_write_operation(target_path, operation)["allowed"]

    def governance_context(self) -> dict[str, Any]:
        return {
            "mode": "read_only_proposal_mode",
            "canonical_alignment": "diagnostic_report_only",
            "no_automatic_knowledge_adoption": True,
            "no_direct_memory_write": True,
            "no_direct_knowledge_write": True,
            "no_32_data_write": True,
            "internet_autonomy": False,
            "requires_explicit_approval_for_adoption": True,
        }

    def status(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "version": self.version,
            "active": True,
            "mode": "read_only_proposal_mode",
            "categories": list(self.categories),
            "governance": self.governance_context(),
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            "Learning Agent 1.0 Status\n"
            f"Agent: {status['agent']}\n"
            f"Modus: {status['mode']}\n"
            "Automatische Wissensuebernahme: nein\n"
            "Internet-Autonomie: nein\n"
            "Geschuetzte Datenwurzeln: 03_memory, 04_knowledge, 32_data\n"
        )

    def generate_status_report(self, output_path: str | Path | None = None) -> Path:
        target = Path(output_path or self.project_root / "31_reports" / "learning_agent" / "learning_agent_1_0_status_report.md")
        guard = self.check_write_operation(target, "write_report")
        if not guard["allowed"]:
            raise PermissionError(guard["reason"])
        target.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        target.write_text(
            "# Learning Agent 1.0 Status Report\n\n"
            f"Stand: {now}\n\n"
            "## Status\n"
            "- Agent: learning_agent_1_0\n"
            "- Version: 1.0\n"
            "- Modus: read-only + Vorschlagsmodus\n"
            "- Automatische Wissensuebernahme: nein\n"
            "- Internet-Autonomie: nein\n\n"
            "## Kategorien\n"
            + "".join(f"- {category}\n" for category in self.categories)
            + "\n## Governance\n"
            "Learning Agent 1.0 schreibt nicht direkt in Memory, Knowledge oder 32_data. "
            "Jede spaetere automatische Uebernahme braucht ausdrueckliche Freigabe. "
            "Die Einordnung ist kompatibel mit der bestehenden Canonical-/Governance-Architektur im diagnostic_report_only-Sinn.\n\n"
            "## Ergebnis\n"
            "Learning Agent 1.0 ist als kontrollierte Lern- und Bewertungsinstanz verfuegbar. "
            "Er erzeugt Klassifikationen, Risiko- und Qualitaetsbewertungen sowie Vorschlaege fuer Knowledge/Memory/Research, ohne produktive Daten zu migrieren oder Wissen automatisch zu uebernehmen.\n",
            encoding="utf-8",
        )
        return target


LearningAgent = LearningAgent10
