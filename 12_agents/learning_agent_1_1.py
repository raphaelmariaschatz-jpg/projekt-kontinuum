from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEARNING_AGENT_VERSION = "1.1"
LEARNING_CATEGORIES = (
    "verified_knowledge",
    "uncertain_knowledge",
    "duplicate_candidate",
    "conflict_detected",
    "source_required",
    "manual_review_required",
)
PROPOSAL_STATUSES = ("pending", "approved", "rejected", "duplicate", "superseded", "archived")
PROTECTED_ROOTS = ("03_memory", "04_knowledge", "32_data")
ALLOWED_LEARNING_ROOT = "33_learning"
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
    confidence: float
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
            "confidence": self.confidence,
            "risks": list(self.risks),
            "duplicate_of": self.duplicate_of,
            "proposals": self.proposals,
            "automatic_adoption_allowed": self.automatic_adoption_allowed,
            "writes_performed": self.writes_performed,
            "governance": self.governance,
        }


class LearningAgent11:
    """Read-only proposal governance agent for controlled knowledge intake.

    Version 1.1 keeps all Learning Agent 1.0 classification behavior and adds a
    canonical proposal queue plus append-only proposal history. It never writes to
    Memory, Knowledge, 32_data or external networks, and it never approves or adopts
    knowledge automatically.
    """

    name = "learning_agent_1_1"
    version = LEARNING_AGENT_VERSION
    categories = LEARNING_CATEGORIES
    proposal_statuses = PROPOSAL_STATUSES

    def __init__(self, project_root: str | Path | None = None, known_sources: list[dict[str, Any]] | None = None):
        self.project_root = Path(project_root or "C:/Projekt Kontinuum")
        self.learning_root = self.project_root / ALLOWED_LEARNING_ROOT
        self.queue_path = self.learning_root / "learning_queue.json"
        self.history_path = self.learning_root / "learning_history.json"
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

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

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
            confidence=self.calculate_confidence(source_quality, risk_level, category, has_source, duplicate_of),
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

    @staticmethod
    def calculate_confidence(source_quality: str, risk_level: str, category: str, has_source: bool, duplicate_of: str | None) -> float:
        score = 0.5
        score += {"high": 0.3, "medium": 0.1, "low": -0.2}.get(source_quality, 0.0)
        score += {"low": 0.15, "medium": -0.05, "high": -0.25}.get(risk_level, 0.0)
        if category == "verified_knowledge":
            score += 0.08
        if category == "conflict_detected":
            score -= 0.2
        if category == "source_required":
            score -= 0.15
        if category == "uncertain_knowledge":
            score -= 0.12
        if duplicate_of:
            score -= 0.08
        if has_source:
            score += 0.05
        return round(max(0.0, min(1.0, score)), 2)

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
        allowed_learning_queue = (
            f"\\{ALLOWED_LEARNING_ROOT.casefold()}\\" in f"\\{path_text}\\"
            and Path(target_path).name in {"learning_queue.json", "learning_history.json"}
            and operation_text in {"append_queue", "append_history", "initialize_queue", "write_report"}
        )
        allowed = allowed_learning_queue or not (protected and write_intent)
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
            "foundation_layer_compatible": True,
            "governance_layer_compatible": True,
            "drift_layer_compatible": True,
            "cam_compatible": True,
            "knowledge_agent_handoff_only": True,
            "memory_agent_handoff_only": True,
            "no_automatic_knowledge_adoption": True,
            "no_direct_memory_write": True,
            "no_direct_knowledge_write": True,
            "no_32_data_write": True,
            "internet_autonomy": False,
            "requires_explicit_approval_for_adoption": True,
        }

    def _read_records(self, path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return []
        return value if isinstance(value, list) else []

    def _write_records(self, path: Path, records: list[dict[str, Any]], operation: str) -> None:
        guard = self.check_write_operation(path, operation)
        if not guard["allowed"]:
            raise PermissionError(guard["reason"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def ensure_learning_queue(self) -> dict[str, Path]:
        self._write_records(self.queue_path, self._read_records(self.queue_path), "initialize_queue")
        self._write_records(self.history_path, self._read_records(self.history_path), "initialize_queue")
        return {"queue": self.queue_path, "history": self.history_path}

    def _next_proposal_id(self) -> str:
        records = self._read_records(self.queue_path) + self._read_records(self.history_path)
        max_id = 0
        for record in records:
            raw = str(record.get("proposal_id", ""))
            match = re.fullmatch(r"LRN-(\d{6})", raw)
            if match:
                max_id = max(max_id, int(match.group(1)))
        return f"LRN-{max_id + 1:06d}"

    def create_learning_proposal(self, source: LearningSource | str, known_sources: list[LearningSource | dict[str, Any] | str] | None = None) -> dict[str, Any]:
        if isinstance(source, str):
            source = self.recognize_source(source)
        self.ensure_learning_queue()
        assessment = self.classify_source(source, known_sources=known_sources)
        proposal_id = self._next_proposal_id()
        timestamp = self._now()
        provenance = {
            "proposal_id": proposal_id,
            "source_id": source.source_id,
            "source": source.metadata.get("source", source.origin),
            "origin": source.origin,
            "source_type": source.source_type,
            "timestamp": timestamp,
            "content_hash": assessment.content_hash,
            "source_quality": assessment.source_quality,
            "risk_level": assessment.risk_level,
            "agent_version": self.version,
            "classification": assessment.category,
            "duplicate_of": assessment.duplicate_of,
        }
        record = {
            "proposal_id": proposal_id,
            "status": "pending",
            "category": assessment.category,
            "source_hash": assessment.content_hash,
            "timestamp": timestamp,
            "confidence": assessment.confidence,
            "source_quality": assessment.source_quality,
            "risk_level": assessment.risk_level,
            "risks": list(assessment.risks),
            "proposals": assessment.proposals,
            "provenance": provenance,
            "governance_events": [
                {"event": "Learning Proposal Created", "timestamp": timestamp, "agent": self.name},
                {"event": "Waiting for Governance Approval", "timestamp": timestamp, "next": "Knowledge Agent / Memory Agent via Governance Layer"},
            ],
            "automatic_adoption_allowed": False,
            "writes_performed": False,
        }
        queue = self._read_records(self.queue_path)
        queue.append(record)
        self._write_records(self.queue_path, queue, "append_queue")
        history = self._read_records(self.history_path)
        history.append({"history_event": "proposal_created", "record": record})
        self._write_records(self.history_path, history, "append_history")
        return record

    def status(self) -> dict[str, Any]:
        queue = self._read_records(self.queue_path)
        status_counts = {status: 0 for status in self.proposal_statuses}
        quality_counts: dict[str, int] = {}
        confidence_values: list[float] = []
        for record in queue:
            status = str(record.get("status", "pending"))
            if status in status_counts:
                status_counts[status] += 1
            quality = str(record.get("source_quality", "unknown"))
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            try:
                confidence_values.append(float(record.get("confidence", 0.0)))
            except (TypeError, ValueError):
                pass
        average_confidence = round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else 0.0
        return {
            "agent": self.name,
            "version": self.version,
            "active": True,
            "mode": "read_only_proposal_mode",
            "categories": list(self.categories),
            "proposal_statuses": list(self.proposal_statuses),
            "queue_path": str(self.queue_path),
            "history_path": str(self.history_path),
            "queue_size": len(queue),
            "proposals_created": len(queue),
            "status_counts": status_counts,
            "average_confidence": average_confidence,
            "source_quality_distribution": quality_counts,
            "governance_status": "waiting_for_governance_approval" if status_counts.get("pending", 0) else "no_pending_proposals",
            "governance": self.governance_context(),
        }

    def format_status(self) -> str:
        status = self.status()
        counts = status["status_counts"]
        return (
            "Learning Agent 1.1 Status\n"
            f"Agent: {status['agent']}\n"
            f"Modus: {status['mode']}\n"
            f"Proposals erzeugt: {status['proposals_created']}\n"
            f"Pending: {counts['pending']} | Approved: {counts['approved']} | Rejected: {counts['rejected']} | Duplicate: {counts['duplicate']}\n"
            f"Durchschnittlicher Confidence Score: {status['average_confidence']}\n"
            f"Queue-Groesse: {status['queue_size']}\n"
            "Automatische Wissensuebernahme: nein\n"
            "Internet-Autonomie: nein\n"
            "Geschuetzte Datenwurzeln: 03_memory, 04_knowledge, 32_data\n"
        )

    def generate_status_report(self, output_path: str | Path | None = None) -> Path:
        target = Path(output_path or self.project_root / "31_reports" / "learning_agent" / "learning_agent_1_1_status_report.md")
        guard = self.check_write_operation(target, "write_report")
        if not guard["allowed"]:
            raise PermissionError(guard["reason"])
        target.parent.mkdir(parents=True, exist_ok=True)
        status = self.status()
        counts = status["status_counts"]
        quality_lines = "".join(f"- {key}: {value}\n" for key, value in sorted(status["source_quality_distribution"].items())) or "- keine\n"
        proposal_lines = "".join(
            f"- {record.get('proposal_id', '<missing>')}: {record.get('status', 'unknown')} | {record.get('category', 'unknown')} | confidence={record.get('confidence', 0.0)}\n"
            for record in self._read_records(self.queue_path)
        ) or "- keine\n"
        target.write_text(
            "# Learning Agent 1.1 Status Report\n\n"
            f"Stand: {self._now()}\n\n"
            "## Status\n"
            "- Agent: learning_agent_1_1\n"
            "- Version: 1.1\n"
            "- Modus: read-only + Proposal Governance\n"
            "- Automatische Wissensuebernahme: nein\n"
            "- Internet-Autonomie: nein\n\n"
            "## Proposal Governance\n"
            f"- Anzahl erzeugter Proposals: {status['proposals_created']}\n"
            f"- Pending: {counts['pending']}\n"
            f"- Approved: {counts['approved']}\n"
            f"- Rejected: {counts['rejected']}\n"
            f"- Duplicate: {counts['duplicate']}\n"
            f"- Superseded: {counts['superseded']}\n"
            f"- Archived: {counts['archived']}\n"
            f"- Durchschnittlicher Confidence Score: {status['average_confidence']}\n"
            f"- Governance-Status: {status['governance_status']}\n"
            f"- Queue-Groesse: {status['queue_size']}\n\n"
            "## Quellenqualitaetsverteilung\n"
            f"{quality_lines}\n"
            "## Aktuelle Proposals\n"
            f"{proposal_lines}\n"
            "## Kategorien\n"
            + "".join(f"- {category}\n" for category in self.categories)
            + "\n## Queue und Historie\n"
            f"- Queue: {self.queue_path}\n"
            f"- History: {self.history_path}\n"
            "- Proposal-IDs folgen dem kanonischen Format LRN-000001.\n"
            "- Der Learning Agent erzeugt ausschliesslich pending-Eintraege.\n"
            "- Freigabe, Ablehnung, Duplikat-Markierung, Superseding und Archivierung bleiben Governance-Komponenten vorbehalten.\n\n"
            "## Governance Hook\n"
            "Learning Proposal Created -> Waiting for Governance Approval -> Knowledge Agent -> Memory Agent. "
            "Learning Agent 1.1 fuehrt keine produktive Uebernahme aus.\n\n"
            "## Ergebnis\n"
            "Learning Agent 1.1 erweitert Version 1.0 um kanonische Proposal-IDs, Learning Queue, append-only History, Provenance und Confidence Scores. "
            "Keine Datenmigration und keine automatische Wissensaenderung wurden vorgenommen.\n",
            encoding="utf-8",
        )
        return target


LearningAgent = LearningAgent11


