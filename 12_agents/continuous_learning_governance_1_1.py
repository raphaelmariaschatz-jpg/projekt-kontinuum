from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CLG_VERSION = "1.1"
PROTECTED_ROOTS = ("03_memory", "04_knowledge", "32_data")
LEARNING_ROOT = "33_learning"
QUEUE_FILE = "learning_queue.json"
HISTORY_FILE = "learning_history.json"
EVENT_FILE = "governance_events.json"
VALID_STATUSES = (
    "pending",
    "under_review",
    "approved",
    "knowledge_handoff",
    "memory_handoff",
    "completed",
    "rejected",
    "duplicate",
    "archived",
)
ALLOWED_TRANSITIONS = {
    "pending": {"under_review", "rejected", "duplicate"},
    "under_review": {"approved", "rejected", "duplicate"},
    "approved": {"knowledge_handoff"},
    "knowledge_handoff": {"memory_handoff"},
    "memory_handoff": {"completed"},
    "completed": {"archived"},
    "rejected": {"archived"},
    "duplicate": {"archived"},
    "archived": set(),
}
EVENT_CODES = {
    "under_review": "GLE-002",
    "approved": "GLE-004",
    "knowledge_handoff": "GLE-005",
    "memory_handoff": "GLE-006",
    "completed": "GLE-007",
    "rejected": "GLE-008",
    "archived": "GLE-009",
    "duplicate": "GLE-010",
}
EVENT_NAMES = {
    "under_review": "Review Started",
    "approved": "Approved",
    "knowledge_handoff": "Knowledge Handoff",
    "memory_handoff": "Memory Handoff",
    "completed": "Completed",
    "rejected": "Rejected",
    "archived": "Archived",
    "duplicate": "Duplicate Marked",
}
REQUIRED_PROVENANCE_FIELDS = {
    "proposal_id",
    "source_id",
    "source",
    "origin",
    "timestamp",
    "content_hash",
    "source_quality",
    "risk_level",
    "agent_version",
    "classification",
}


@dataclass(frozen=True)
class GovernanceEvent:
    event_id: str
    event_code: str
    event_name: str
    timestamp: str
    proposal_id: str
    component: str
    description: str
    from_status: str
    to_status: str
    drift_compatible: bool = True
    cam_handoff_only: bool = True
    knowledge_handoff_only: bool = True
    memory_handoff_only: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_code": self.event_code,
            "event_name": self.event_name,
            "timestamp": self.timestamp,
            "proposal_id": self.proposal_id,
            "component": self.component,
            "description": self.description,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "drift_compatible": self.drift_compatible,
            "cam_handoff_only": self.cam_handoff_only,
            "knowledge_handoff_only": self.knowledge_handoff_only,
            "memory_handoff_only": self.memory_handoff_only,
        }


class ContinuousLearningGovernance11:
    """Governance-only orchestrator for the Continuous Learning workflow."""

    name = "continuous_learning_governance_1_1"
    version = CLG_VERSION
    valid_statuses = VALID_STATUSES
    allowed_transitions = ALLOWED_TRANSITIONS

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or "C:/Projekt Kontinuum")
        self.learning_root = self.project_root / LEARNING_ROOT
        self.queue_path = self.learning_root / QUEUE_FILE
        self.history_path = self.learning_root / HISTORY_FILE
        self.events_path = self.learning_root / EVENT_FILE
        self.report_path = self.project_root / "31_reports" / "clg_1_1_status_report.md"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _read_records(path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return []
        return value if isinstance(value, list) else []

    @staticmethod
    def _write_records(path: Path, records: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def check_write_operation(self, target_path: str | Path, operation: str = "write") -> dict[str, Any]:
        path_text = str(target_path).replace("/", "\\").casefold()
        operation_text = operation.casefold()
        protected = any(f"\\{root.casefold()}\\" in f"\\{path_text}\\" or path_text.endswith(f"\\{root.casefold()}") for root in PROTECTED_ROOTS)
        allowed_learning_write = (
            f"\\{LEARNING_ROOT.casefold()}\\" in f"\\{path_text}\\"
            and Path(target_path).name in {QUEUE_FILE, EVENT_FILE}
            and operation_text in {"update_queue_status", "append_governance_event", "initialize_audit_log"}
        )
        allowed_report = "\\31_reports\\" in f"\\{path_text}\\" and operation_text == "write_report"
        write_intent = operation_text in {"write", "update", "insert", "delete", "store", "persist"}
        allowed = allowed_learning_write or allowed_report or not (protected and write_intent)
        return {
            "allowed": allowed,
            "mode": "governance_orchestration_only",
            "target_path": str(target_path),
            "operation": operation,
            "reason": "CLG must not write to productive knowledge, memory, or 32_data roots." if not allowed else "No protected CLG write detected.",
        }

    def ensure_audit_log(self) -> Path:
        guard = self.check_write_operation(self.events_path, "initialize_audit_log")
        if not guard["allowed"]:
            raise PermissionError(guard["reason"])
        if not self.events_path.exists():
            self._write_records(self.events_path, [])
        return self.events_path

    def load_queue(self) -> list[dict[str, Any]]:
        return self._read_records(self.queue_path)

    def load_history(self) -> list[dict[str, Any]]:
        return self._read_records(self.history_path)

    def load_events(self) -> list[dict[str, Any]]:
        return self._read_records(self.events_path)

    @staticmethod
    def is_valid_proposal_id(proposal_id: str) -> bool:
        return bool(re.fullmatch(r"LRN-\d{6}", proposal_id or ""))

    def validate_transition(self, from_status: str, to_status: str) -> dict[str, Any]:
        if from_status not in self.valid_statuses:
            return {"ok": False, "reason": f"Invalid source status: {from_status}"}
        if to_status not in self.valid_statuses:
            return {"ok": False, "reason": f"Invalid target status: {to_status}"}
        if to_status not in self.allowed_transitions[from_status]:
            return {"ok": False, "reason": f"Invalid transition: {from_status} -> {to_status}"}
        return {"ok": True, "reason": "Transition allowed."}

    def _next_event_id(self) -> str:
        max_id = 0
        for event in self.load_events():
            match = re.fullmatch(r"GLE-(\d{6})", str(event.get("event_id", "")))
            if match:
                max_id = max(max_id, int(match.group(1)))
        return f"GLE-{max_id + 1:06d}"

    def append_event(self, event: GovernanceEvent) -> dict[str, Any]:
        guard = self.check_write_operation(self.events_path, "append_governance_event")
        if not guard["allowed"]:
            raise PermissionError(guard["reason"])
        self.ensure_audit_log()
        events = self.load_events()
        events.append(event.as_dict())
        self._write_records(self.events_path, events)
        return event.as_dict()

    def transition_proposal(self, proposal_id: str, to_status: str, component: str = "CLG", description: str = "") -> dict[str, Any]:
        queue = self.load_queue()
        for index, proposal in enumerate(queue):
            if proposal.get("proposal_id") != proposal_id:
                continue
            from_status = str(proposal.get("status", ""))
            validation = self.validate_transition(from_status, to_status)
            if not validation["ok"]:
                return {"ok": False, "error": validation["reason"], "proposal_id": proposal_id, "from_status": from_status, "to_status": to_status}
            guard = self.check_write_operation(self.queue_path, "update_queue_status")
            if not guard["allowed"]:
                raise PermissionError(guard["reason"])
            updated = dict(proposal)
            updated["status"] = to_status
            updated["governance_status"] = to_status
            updated["updated_at"] = self._now()
            updated["clg_version"] = self.version
            queue[index] = updated
            self._write_records(self.queue_path, queue)
            event = GovernanceEvent(
                event_id=self._next_event_id(),
                event_code=EVENT_CODES.get(to_status, "GLE-003"),
                event_name=EVENT_NAMES.get(to_status, "Governance Transition"),
                timestamp=self._now(),
                proposal_id=proposal_id,
                component=component,
                description=description or f"Transition {from_status} -> {to_status}",
                from_status=from_status,
                to_status=to_status,
            )
            return {"ok": True, "proposal": updated, "event": self.append_event(event)}
        return {"ok": False, "error": "Proposal not found.", "proposal_id": proposal_id, "to_status": to_status}

    def start_review(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "under_review", "Governance Review", "Review started for learning proposal.")

    def approve(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "approved", "Governance Review", "Proposal approved for handoff only.")

    def reject(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "rejected", "Governance Review", "Proposal rejected by governance review.")

    def mark_duplicate(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "duplicate", "Governance Review", "Proposal marked as duplicate.")

    def prepare_knowledge_handoff(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "knowledge_handoff", "Knowledge Agent", "Handoff prepared; no knowledge adoption performed by CLG.")

    def prepare_memory_handoff(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "memory_handoff", "Memory Agent", "Handoff prepared; no memory write performed by CLG.")

    def complete(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "completed", "CLG", "Governance workflow completed.")

    def archive(self, proposal_id: str) -> dict[str, Any]:
        return self.transition_proposal(proposal_id, "archived", "CLG", "Governance proposal archived.")

    def check_canonical_compliance(self) -> dict[str, Any]:
        queue = self.load_queue()
        history = self.load_history()
        events = self.load_events()
        errors: list[str] = []
        event_ids = [str(event.get("event_id", "")) for event in events]
        event_proposals = {str(event.get("proposal_id", "")) for event in events}
        history_ids = set()
        for row in history:
            record = row.get("record") if isinstance(row.get("record"), dict) else row
            if isinstance(record, dict):
                history_ids.add(str(record.get("proposal_id", "")))
        for proposal in queue:
            proposal_id = str(proposal.get("proposal_id", ""))
            status = str(proposal.get("status", ""))
            provenance = proposal.get("provenance") if isinstance(proposal.get("provenance"), dict) else {}
            if not self.is_valid_proposal_id(proposal_id):
                errors.append(f"Invalid Proposal-ID: {proposal_id}")
            if status not in self.valid_statuses:
                errors.append(f"Invalid status for {proposal_id}: {status}")
            if proposal_id not in history_ids:
                errors.append(f"History missing proposal {proposal_id}")
            missing_provenance = sorted(REQUIRED_PROVENANCE_FIELDS - set(provenance))
            if missing_provenance:
                errors.append(f"Provenance incomplete for {proposal_id}: {', '.join(missing_provenance)}")
            if "confidence" not in proposal:
                errors.append(f"Confidence missing for {proposal_id}")
            if status != "pending" and proposal_id not in event_proposals:
                errors.append(f"Governance event missing for active transition {proposal_id}")
        if len(event_ids) != len(set(event_ids)):
            errors.append("Governance event IDs are not unique.")
        compliance_score = 100 if not errors else max(0, 100 - 10 * len(errors))
        return {
            "ok": not errors,
            "errors": errors,
            "compliance_score": compliance_score,
            "proposal_id_valid": all(self.is_valid_proposal_id(str(item.get("proposal_id", ""))) for item in queue),
            "queue_consistent": not any("Invalid status" in error or "Invalid Proposal-ID" in error for error in errors),
            "history_consistent": not any("History missing" in error for error in errors),
            "provenance_complete": not any("Provenance incomplete" in error for error in errors),
            "confidence_present": not any("Confidence missing" in error for error in errors),
            "governance_events_present": not any("Governance event missing" in error for error in errors),
        }

    def metrics(self) -> dict[str, Any]:
        queue = self.load_queue()
        events = self.load_events()
        counts = {status: 0 for status in self.valid_statuses}
        quality_distribution: dict[str, int] = {}
        confidence_values: list[float] = []
        for proposal in queue:
            status = str(proposal.get("status", ""))
            if status in counts:
                counts[status] += 1
            quality = str(proposal.get("source_quality", "unknown"))
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
            try:
                confidence_values.append(float(proposal.get("confidence", 0.0)))
            except (TypeError, ValueError):
                pass
        compliance = self.check_canonical_compliance()
        return {
            "counts": counts,
            "active_proposals": counts["pending"] + counts["under_review"] + counts["approved"] + counts["knowledge_handoff"] + counts["memory_handoff"],
            "completed_proposals": counts["completed"],
            "handoffs": counts["knowledge_handoff"] + counts["memory_handoff"],
            "rejections": counts["rejected"],
            "archivings": counts["archived"],
            "average_processing_seconds": 0.0,
            "average_confidence": round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else 0.0,
            "source_quality_distribution": quality_distribution,
            "event_count": len(events),
            "compliance": compliance,
        }

    def status(self) -> dict[str, Any]:
        metrics = self.metrics()
        return {
            "agent": self.name,
            "version": self.version,
            "mode": "governance_orchestration_only",
            "governance_status": "compliant" if metrics["compliance"]["ok"] else "review_required",
            "queue_status": "available" if self.queue_path.is_file() else "missing",
            "audit_log": str(self.events_path),
            "report": str(self.report_path),
            "metrics": metrics,
            "compatibility": {
                "foundation_layer": "compatible",
                "canonical_layer": "compatible",
                "governance_layer": "compatible",
                "operational_layer": "compatible",
                "learning_layer": "compatible",
                "drift_layer": "drift-compatible logging only",
                "cam": "handoff_only",
                "knowledge_agent": "handoff_only",
                "memory_agent": "handoff_only",
            },
            "productive_write_policy": {
                "03_memory": "blocked",
                "04_knowledge": "blocked",
                "32_data": "blocked",
                "33_learning": "append_or_queue_status_only",
            },
        }

    def generate_status_report(self, output_path: str | Path | None = None) -> Path:
        target = Path(output_path or self.report_path)
        guard = self.check_write_operation(target, "write_report")
        if not guard["allowed"]:
            raise PermissionError(guard["reason"])
        target.parent.mkdir(parents=True, exist_ok=True)
        status = self.status()
        metrics = status["metrics"]
        counts = metrics["counts"]
        compliance = metrics["compliance"]
        quality_lines = "".join(f"- {key}: {value}\n" for key, value in sorted(metrics["source_quality_distribution"].items())) or "- keine\n"
        error_lines = "".join(f"- {error}\n" for error in compliance["errors"]) or "- keine\n"
        target.write_text(
            "# Continuous Learning Governance 1.1 Status Report\n\n"
            f"Stand: {self._now()}\n\n"
            "## Governance Status\n"
            f"- CLG: {status['governance_status']}\n"
            f"- Queue Status: {status['queue_status']}\n"
            f"- Anzahl Events: {metrics['event_count']}\n"
            f"- Compliance Score: {compliance['compliance_score']}\n"
            "- Drift-Kompatibilitaet: ja, audit-only\n"
            "- CAM-Kompatibilitaet: Handoff only\n"
            "- Foundation-Kompatibilitaet: kompatibel\n\n"
            "## Governance Environment\n"
            f"Queue:\n{self.queue_path}\n\n"
            f"History:\n{self.history_path}\n\n"
            f"Audit:\n{self.events_path}\n\n"
            f"Version:\nCLG {self.version}\n\n"
            "## Proposal Lifecycle\n"
            "pending -> under_review -> approved -> knowledge_handoff -> memory_handoff -> completed\n\n"
            "pending -> rejected\n\n"
            "pending -> duplicate -> archived\n\n"
            "## Queue Metrics\n"
            f"- Pending: {counts['pending']}\n"
            f"- Under Review: {counts['under_review']}\n"
            f"- Approved: {counts['approved']}\n"
            f"- Knowledge Handoff: {counts['knowledge_handoff']}\n"
            f"- Memory Handoff: {counts['memory_handoff']}\n"
            f"- Completed: {counts['completed']}\n"
            f"- Rejected: {counts['rejected']}\n"
            f"- Duplicate: {counts['duplicate']}\n"
            f"- Archived: {counts['archived']}\n"
            f"- Aktive Proposals: {metrics['active_proposals']}\n"
            f"- Abgeschlossene Proposals: {metrics['completed_proposals']}\n"
            f"- Handoffs: {metrics['handoffs']}\n"
            f"- Rejections: {metrics['rejections']}\n"
            f"- Archivierungen: {metrics['archivings']}\n"
            f"- Durchschnittliche Bearbeitungszeit Sekunden: {metrics['average_processing_seconds']}\n"
            f"- Durchschnittlicher Confidence Score: {metrics['average_confidence']}\n\n"
            "## Quellenqualitaetsverteilung\n"
            f"{quality_lines}\n"
            "## Canonical Compliance\n"
            f"- Proposal-ID gueltig: {compliance['proposal_id_valid']}\n"
            f"- Queue konsistent: {compliance['queue_consistent']}\n"
            f"- History konsistent: {compliance['history_consistent']}\n"
            f"- Provenance vollstaendig: {compliance['provenance_complete']}\n"
            f"- Confidence vorhanden: {compliance['confidence_present']}\n"
            f"- Governance Events vorhanden: {compliance['governance_events_present']}\n\n"
            "## Compliance Meldungen\n"
            f"{error_lines}\n"
            "## Kompatibilitaet\n"
            "- Foundation Layer: kompatibel\n"
            "- Canonical Layer: kompatibel\n"
            "- Governance Layer: kompatibel\n"
            "- Operational Layer: kompatibel\n"
            "- Learning Layer: kompatibel\n"
            "- Drift Layer: kompatibel protokolliert\n"
            "- CAM: Handoff\n"
            "- Knowledge Agent: Handoff\n"
            "- Memory Agent: Handoff\n\n"
            "## Schreibschutz\n"
            "- 03_memory: blockiert\n"
            "- 04_knowledge: blockiert\n"
            "- 32_data: blockiert\n"
            "- Wissensuebernahme: keine automatische Uebernahme\n",
            encoding="utf-8",
        )
        return target


ContinuousLearningGovernance = ContinuousLearningGovernance11

