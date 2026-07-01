from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_SCHEMA_FIELDS = (
    "event_id",
    "event_type",
    "source_component",
    "affected_path",
    "affected_object_id",
    "timestamp",
    "severity",
    "payload",
    "provenance",
    "governance_context",
    "processing_state",
)

DECISION_CLASSES = (
    "ACTIVE",
    "ARCHIVE_CANDIDATE",
    "REVIEW_REQUIRED",
    "CONSOLIDATION_SUGGESTED",
    "BLOCKED",
)

DRIFT_CLASSES = (
    "EXPECTED_DRIFT",
    "LOW_DRIFT",
    "MEDIUM_DRIFT",
    "HIGH_DRIFT",
    "BLOCKING_DRIFT",
)

BLOCKING_DRIFT_CLASSES = {"HIGH_DRIFT", "BLOCKING_DRIFT"}


@dataclass
class CanonicalEvent:
    event_type: str
    source_component: str
    affected_path: str = ""
    affected_object_id: str = ""
    severity: str = "info"
    payload: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    governance_context: dict[str, Any] = field(default_factory=dict)
    processing_state: str = "received"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {field_name: getattr(self, field_name) for field_name in EVENT_SCHEMA_FIELDS}


class CanonicalEventSchema:
    required_fields = EVENT_SCHEMA_FIELDS

    @classmethod
    def validate(cls, event: dict[str, Any]) -> dict[str, Any]:
        missing = [field_name for field_name in cls.required_fields if field_name not in event]
        payload_ok = isinstance(event.get("payload"), dict)
        provenance_ok = isinstance(event.get("provenance"), dict)
        governance_ok = isinstance(event.get("governance_context"), dict)
        return {
            "ok": not missing and payload_ok and provenance_ok and governance_ok,
            "missing": missing,
            "payload_ok": payload_ok,
            "provenance_ok": provenance_ok,
            "governance_context_ok": governance_ok,
        }


class ContinuousCanonicalEngine:
    VERSION = "1.0"
    RELEASE_VERSION = "34.1"
    CONFIG_RELATIVE = "24_config/continuous_canonical_engine_34_1.json"

    def __init__(
        self,
        project_root: str | Path | None = None,
        path_tools: Any | None = None,
        storage: Any | None = None,
        release_version: str = RELEASE_VERSION,
        strict_config: bool = False,
    ):
        self.path_tools = path_tools
        self.storage = storage
        self.release_version = release_version
        self.root = self._resolve_root(project_root, path_tools)
        self.config_path = self.root / self.CONFIG_RELATIVE
        self.config = self._load_config(strict_config)
        logs = self.config.get("logs", {})
        self.event_log = self.root / logs.get("canonical_events", "31_reports/events/canonical_events.jsonl")
        self.processing_log = self.root / logs.get("event_processing", "31_reports/events/event_processing_log.jsonl")
        self.drift_log = self.root / logs.get("drift_events", "31_reports/drift/drift_events.jsonl")
        self.hook_log = self.root / logs.get("governance_hooks", "31_reports/governance/governance_hooks.jsonl")
        self._ensure_log_files()

    @staticmethod
    def _resolve_root(project_root: str | Path | None, path_tools: Any | None) -> Path:
        if project_root:
            return Path(project_root).resolve()
        if path_tools and hasattr(path_tools, "project_root"):
            return Path(path_tools.project_root()).resolve()
        return Path.cwd().resolve()

    def _load_config(self, strict: bool) -> dict[str, Any]:
        try:
            config = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            if strict:
                raise RuntimeError(f"Continuous-Canonical-Engine-Konfiguration fehlt oder ist ungueltig: {self.config_path}")
            return self._default_config()
        if config.get("version") != self.release_version:
            if strict:
                raise RuntimeError("Continuous-Canonical-Engine-Konfiguration gehoert nicht zur aktiven Version.")
        return config

    @staticmethod
    def _default_config() -> dict[str, Any]:
        return {
            "version": ContinuousCanonicalEngine.RELEASE_VERSION,
            "engine_version": ContinuousCanonicalEngine.VERSION,
            "active": True,
            "mode": "diagnostic_report_only",
            "logs": {
                "canonical_events": "31_reports/events/canonical_events.jsonl",
                "event_processing": "31_reports/events/event_processing_log.jsonl",
                "drift_events": "31_reports/drift/drift_events.jsonl",
                "governance_hooks": "31_reports/governance/governance_hooks.jsonl",
            },
            "event_schema": list(EVENT_SCHEMA_FIELDS),
            "decision_classes": list(DECISION_CLASSES),
            "drift_classes": list(DRIFT_CLASSES),
            "release_gate": {"blocking_drift_classes": sorted(BLOCKING_DRIFT_CLASSES)},
        }

    def _ensure_log_files(self) -> None:
        for path in (self.event_log, self.processing_log, self.drift_log, self.hook_log):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)

    @staticmethod
    def _hash(value: dict[str, Any]) -> str:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    @staticmethod
    def _read_jsonl(path: Path, limit: int = 20) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        rows = []
        try:
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                if not line.strip():
                    continue
                rows.append(json.loads(line))
        except (OSError, ValueError):
            return []
        return rows[-limit:]

    def create_event(
        self,
        event_type: str,
        source_component: str,
        affected_path: str = "",
        affected_object_id: str = "",
        severity: str = "info",
        payload: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
        governance_context: dict[str, Any] | None = None,
        processing_state: str = "received",
    ) -> dict[str, Any]:
        return CanonicalEvent(
            event_type=event_type,
            source_component=source_component,
            affected_path=affected_path,
            affected_object_id=affected_object_id,
            severity=severity,
            payload=payload or {},
            provenance=provenance or {},
            governance_context=governance_context or {},
            processing_state=processing_state,
        ).as_dict()

    def append_event(self, event: dict[str, Any]) -> dict[str, Any]:
        validation = CanonicalEventSchema.validate(event)
        envelope = {
            "kind": "continuous_canonical.event",
            "recorded_at": self._now(),
            "event_hash": self._hash(event),
            "schema_valid": validation["ok"],
            "event": event,
        }
        self._append_jsonl(self.event_log, envelope)
        return {"ok": validation["ok"], "validation": validation, "event_hash": envelope["event_hash"]}

    def decide(self, event: dict[str, Any]) -> dict[str, Any]:
        severity = str(event.get("severity", "info")).casefold()
        event_type = str(event.get("event_type", "")).casefold()
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        affected_path = str(event.get("affected_path", "")).casefold()
        governance = event.get("governance_context") if isinstance(event.get("governance_context"), dict) else {}

        decision_class = "ACTIVE"
        reasons: list[str] = []
        if severity in {"critical", "blocking"} or payload.get("policy_violation"):
            decision_class = "BLOCKED"
            reasons.append("blocking_severity_or_policy_violation")
        elif payload.get("requires_review") or not event.get("provenance") or governance.get("requires_review"):
            decision_class = "REVIEW_REQUIRED"
            reasons.append("review_required_or_missing_provenance")
        elif "archive" in event_type or "archive" in affected_path:
            decision_class = "ARCHIVE_CANDIDATE"
            reasons.append("archive_signal")
        elif payload.get("duplicate") or payload.get("consolidation_candidate"):
            decision_class = "CONSOLIDATION_SUGGESTED"
            reasons.append("consolidation_signal")
        else:
            reasons.append("active_without_blocking_signal")

        return {
            "decision_class": decision_class,
            "reasons": reasons,
            "decided_at": self._now(),
            "engine": "CDE 2.0",
        }

    def classify_drift(self, event: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
        severity = str(event.get("severity", "info")).casefold()
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        governance = event.get("governance_context") if isinstance(event.get("governance_context"), dict) else {}
        event_type = str(event.get("event_type", "")).casefold()

        drift_class = "LOW_DRIFT"
        action = "log"
        reasons: list[str] = []
        if decision.get("decision_class") == "BLOCKED" or severity in {"critical", "blocking"}:
            drift_class = "BLOCKING_DRIFT"
            action = "stop_gate"
            reasons.append("blocked_decision_or_blocking_severity")
        elif severity == "high" or payload.get("code_doc_conflict") or governance.get("release_relevant"):
            drift_class = "HIGH_DRIFT"
            action = "block_release"
            reasons.append("high_severity_release_relevant_or_code_doc_conflict")
        elif payload.get("requires_review") or decision.get("decision_class") == "REVIEW_REQUIRED":
            drift_class = "MEDIUM_DRIFT"
            action = "review"
            reasons.append("review_required")
        elif "documentation" in event_type and payload.get("expected_change"):
            drift_class = "EXPECTED_DRIFT"
            action = "document_only"
            reasons.append("expected_documentation_change")
        else:
            reasons.append("low_drift_log_only")

        return {
            "drift_class": drift_class,
            "action": action,
            "reasons": reasons,
            "classified_at": self._now(),
        }

    def evaluate_hooks(self, event: dict[str, Any], decision: dict[str, Any], drift: dict[str, Any]) -> list[dict[str, Any]]:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        governance = event.get("governance_context") if isinstance(event.get("governance_context"), dict) else {}
        hooks: list[dict[str, Any]] = []

        def add(hook_type: str, severity: str, reason: str) -> None:
            hooks.append({
                "hook_id": str(uuid.uuid4()),
                "event_id": event.get("event_id", ""),
                "hook_type": hook_type,
                "severity": severity,
                "reason": reason,
                "state": "open",
                "created_at": self._now(),
            })

        if drift.get("drift_class") in BLOCKING_DRIFT_CLASSES:
            add("drift_gate", "high", f"{drift.get('drift_class')} requires release gate attention")
        if not event.get("provenance"):
            add("missing_provenance", "medium", "Canonical event has no provenance.")
        if payload.get("policy_violation"):
            add("policy_violation", "high", "Payload reports a policy violation.")
        if payload.get("unregistered_artifact"):
            add("unregistered_artifact", "medium", "Artifact is not registered canonically.")
        if payload.get("unclear_canonicity"):
            add("unclear_canonicity", "medium", "Canonical status is unclear.")
        if payload.get("code_doc_conflict"):
            add("code_doc_conflict", "high", "Code and documentation conflict.")
        if payload.get("internet_learning") and not payload.get("reviewed"):
            add("internet_learning_without_review", "medium", "Internet learning requires review before adoption.")
        if governance.get("release_gate") and governance.get("open_review"):
            add("release_gate_open_review", "high", "Release gate has open review items.")
        if decision.get("decision_class") == "BLOCKED":
            add("blocked_decision", "high", "CDE 2.0 returned BLOCKED.")
        return hooks

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        append = self.append_event(event)
        decision = self.decide(event)
        drift = self.classify_drift(event, decision)
        hooks = self.evaluate_hooks(event, decision, drift)
        processing = {
            "kind": "continuous_canonical.processing",
            "processed_at": self._now(),
            "event_id": event.get("event_id", ""),
            "schema_valid": append["ok"],
            "decision": decision,
            "drift": drift,
            "hook_count": len(hooks),
            "processing_state": "processed" if append["ok"] else "review_required",
        }
        self._append_jsonl(self.processing_log, processing)
        self._append_jsonl(self.drift_log, {
            "kind": "continuous_canonical.drift",
            "event_id": event.get("event_id", ""),
            "recorded_at": self._now(),
            **drift,
        })
        for hook in hooks:
            self._append_jsonl(self.hook_log, {"kind": "continuous_canonical.governance_hook", **hook})
        return {"ok": append["ok"], "event": event, "decision": decision, "drift": drift, "hooks": hooks}

    def ingest(
        self,
        event_type: str,
        source_component: str,
        affected_path: str = "",
        affected_object_id: str = "",
        severity: str = "info",
        payload: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
        governance_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = self.create_event(
            event_type=event_type,
            source_component=source_component,
            affected_path=affected_path,
            affected_object_id=affected_object_id,
            severity=severity,
            payload=payload,
            provenance=provenance,
            governance_context=governance_context,
        )
        return self.process_event(event)

    def open_hooks(self, limit: int = 50) -> list[dict[str, Any]]:
        hooks = self._read_jsonl(self.hook_log, limit=limit)
        return [hook for hook in hooks if hook.get("state") == "open"]

    def blocking_findings(self) -> list[dict[str, Any]]:
        findings = []
        for drift in self._read_jsonl(self.drift_log, limit=200):
            if drift.get("drift_class") in BLOCKING_DRIFT_CLASSES:
                findings.append(drift)
        for hook in self.open_hooks(limit=200):
            if hook.get("severity") == "high":
                findings.append(hook)
        return findings

    def gate_status(self) -> dict[str, Any]:
        schema_ok = self.config.get("event_schema") == list(EVENT_SCHEMA_FIELDS)
        decisions_ok = set(self.config.get("decision_classes", [])) >= set(DECISION_CLASSES)
        drift_ok = set(self.config.get("drift_classes", [])) >= set(DRIFT_CLASSES)
        log_files_ok = all(path.is_file() for path in (self.event_log, self.processing_log, self.drift_log, self.hook_log))
        blocking = self.blocking_findings()
        ok = bool(self.config.get("active", True)) and schema_ok and decisions_ok and drift_ok and log_files_ok and not blocking
        return {
            "ok": ok,
            "active": bool(self.config.get("active", True)),
            "mode": self.config.get("mode", "diagnostic_report_only"),
            "schema_ok": schema_ok,
            "decision_classes_ok": decisions_ok,
            "drift_classes_ok": drift_ok,
            "append_only_logs_present": log_files_ok,
            "blocking_findings": blocking,
            "last_gate_decision": "PASS" if ok else "BLOCKED",
        }

    def status(self) -> dict[str, Any]:
        events = self._read_jsonl(self.event_log, limit=5)
        processing = self._read_jsonl(self.processing_log, limit=5)
        drift = self._read_jsonl(self.drift_log, limit=5)
        hooks = self.open_hooks(limit=20)
        last_event = events[-1] if events else {}
        gate = self.gate_status()
        return {
            "version": self.VERSION,
            "release_version": self.release_version,
            "active": bool(self.config.get("active", True)),
            "mode": self.config.get("mode", "diagnostic_report_only"),
            "event_bus": {
                "status": "active" if self.event_log.is_file() else "missing",
                "log": str(self.event_log),
                "recent_count": len(events),
            },
            "last_event": last_event,
            "last_processing": processing[-1] if processing else {},
            "last_drift": drift[-1] if drift else {},
            "open_hooks": hooks,
            "blocking_findings": gate["blocking_findings"],
            "cde_status": "active",
            "drift_status": "active",
            "last_gate_decision": gate["last_gate_decision"],
            "gate": gate,
        }

    def format_status(self) -> str:
        status = self.status()
        last_event = status.get("last_event", {}).get("event", {})
        last_drift = status.get("last_drift", {})
        lines = [
            "Continuous Canonical Engine 1.0 Status:",
            f"- Web-/lokaler Event Bus aktiv: {'ja' if status['active'] else 'nein'}",
            f"- Modus: {status['mode']}",
            f"- Event Bus Status: {status['event_bus']['status']}",
            f"- Letztes Event: {last_event.get('event_type', '-')}",
            f"- Letzte Quelle: {last_event.get('source_component', '-')}",
            f"- Drift Status: {status['drift_status']} ({last_drift.get('drift_class', '-')})",
            f"- CDE Status: {status['cde_status']}",
            f"- Offene Governance-Hooks: {len(status['open_hooks'])}",
            f"- Blockierende Befunde: {len(status['blocking_findings'])}",
            f"- Letzte Gate-Entscheidung: {status['last_gate_decision']}",
        ]
        return "\n".join(lines)
