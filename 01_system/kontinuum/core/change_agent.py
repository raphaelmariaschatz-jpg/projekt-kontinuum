# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .conversation import normalize


@dataclass
class ChangeRequest:
    timestamp: str
    original_input: str
    change_type: str
    old_value: str
    new_value: str
    affected_area: str
    risk: str
    status: str
    hash: str
    event_id: str
    governance_status: str
    blocking_findings: list[str]


class ChangeAgentService:
    VERSION = "1.0"
    MODE = "diagnostic_read_only"
    TRIGGERS = (
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
    PROTECTED_AREAS = {
        "Foundation-Regel",
        "Foundation / Creator Command Policy",
        "Creator-/Schöpfer-Regel",
        "Governance-Regel",
        "Sicherheitsregel",
    }

    def __init__(self, path_tools, canonical_engine: Any | None = None, storage: Any | None = None):
        self.path_tools = path_tools
        self.canonical_engine = canonical_engine
        self.storage = storage
        self.root = Path(path_tools.project_root())
        self.directory = self.root / "14_documents" / "change_agent"
        self.requests_path = self.directory / "change_requests.jsonl"
        self.status_path = self.directory / "change_agent_status.json"
        self.pending_path = self.directory / "pending_governance_changes.json"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.requests_path.touch(exist_ok=True)
        if not self.pending_path.exists():
            self._write_json(self.pending_path, [])
        self._update_status(None)

    def is_change_request(self, text: str) -> bool:
        value = normalize(text or "")
        if not value:
            return False
        return any(trigger in value for trigger in self.TRIGGERS) or bool(
            re.search(r"(?i)\bersetze\s+regel\s+\S+\s+durch\b", text or "")
        )

    def process(self, text: str) -> ChangeRequest:
        detected_event_id = self._emit_event("CHANGE_DETECTED", text, {"original_input": text}, "info", False)
        change_type = self._classify_type(text)
        old_value, new_value = self._extract_values(text)
        affected_area = self._classify_area(text, old_value, new_value)
        risk = self._classify_risk(text, affected_area)
        blocking_findings = self._blocking_findings(text, affected_area)
        if blocking_findings:
            status = "blocked"
            governance_status = "blocked"
        elif affected_area in self.PROTECTED_AREAS:
            status = "pending_review"
            governance_status = "pending Governance Review"
        else:
            status = "diagnostic_recorded"
            governance_status = "diagnostisch protokolliert"

        payload = {
            "change_type": change_type,
            "old_value": old_value,
            "new_value": new_value,
            "affected_area": affected_area,
            "risk": risk,
            "status": status,
            "blocking_findings": blocking_findings,
        }
        self._emit_event("CHANGE_CLASSIFIED", text, payload, "medium" if affected_area in self.PROTECTED_AREAS else "info", status == "blocked")
        final_event = "CHANGE_BLOCKED" if status == "blocked" else ("CHANGE_PENDING_REVIEW" if status == "pending_review" else "CHANGE_APPLIED")
        event_id = self._emit_event(
            final_event,
            text,
            payload | {"requires_review": status == "pending_review", "policy_violation": status == "blocked"},
            "blocking" if status == "blocked" else ("medium" if status == "pending_review" else "info"),
            status in {"pending_review", "blocked"},
        ) or detected_event_id

        row_without_hash = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_input": text,
            "change_type": change_type,
            "old_value": old_value,
            "new_value": new_value,
            "affected_area": affected_area,
            "risk": risk,
            "status": status,
            "event_id": event_id,
            "governance_status": governance_status,
            "blocking_findings": blocking_findings,
        }
        row_hash = self._hash(row_without_hash)
        request = ChangeRequest(hash=row_hash, **row_without_hash)
        self._append_jsonl(self.requests_path, asdict(request))
        if status == "pending_review":
            self._append_pending(asdict(request))
        self._update_status(request)
        if self.storage:
            self.storage.add("audit_events", "change_agent.request", text[:500], asdict(request))
        return request

    def format_response(self, request: ChangeRequest) -> str:
        lines = [
            "Änderungsauftrag erkannt.",
            f"Bereich: {request.affected_area}.",
            f"Änderungsart: {request.change_type}.",
        ]
        if request.old_value:
            lines.append(f"Alte Regel erkannt: „{request.old_value}“")
        if request.new_value:
            lines.append("Neue Regel vorgeschlagen:")
            lines.append(f"„{request.new_value}“")
        lines.append(f"Risiko: {request.risk}.")
        if request.status == "blocked":
            lines.append("Status: blockiert.")
            lines.append("Blockierende Befunde: " + "; ".join(request.blocking_findings))
        elif request.status == "pending_review":
            lines.append("Status: zur Governance-Prüfung vorgemerkt.")
        else:
            lines.append("Status: diagnostisch protokolliert; keine aktive Regelübernahme.")
        return "\n".join(lines)

    def format_status(self) -> str:
        status = self._read_json(self.status_path, {})
        last = status.get("last_change") or {}
        return "\n".join([
            "ChangeAgent 1.0 Status:",
            f"- ChangeAgent aktiv: {'ja' if status.get('active') else 'nein'}",
            f"- Modus: {status.get('mode', self.MODE)}",
            f"- erkannte Änderungsaufträge: {status.get('recognized_change_requests', 0)}",
            f"- offene Änderungen: {status.get('open_changes', 0)}",
            f"- letzte Änderung: {last.get('timestamp', '-')}",
            f"- betroffener Bereich: {last.get('affected_area', '-')}",
            f"- Governance-Status: {last.get('governance_status', '-')}",
            "- blockierende Befunde: " + ("; ".join(last.get("blocking_findings", [])) if last.get("blocking_findings") else "-"),
            f"- letzte Übernahme: {status.get('last_applied', '-')}",
            f"- Protokoll: {self.requests_path}",
        ])

    def _classify_type(self, text: str) -> str:
        value = normalize(text)
        if "korrektur" in value or "korrigiere" in value:
            return "Regelkorrektur"
        if "ersetze" in value:
            return "Regelersetzung"
        if "lösche" in value or "losche" in value or "loesche" in value or "streiche" in value:
            return "Regellöschung"
        if "verankere" in value or "speichere als regel" in value or "übernimm als neue regel" in value:
            return "Regelverankerung"
        if "aktualisiere" in value or "ändere" in value or "aendere" in value or "setze" in value:
            return "Regeländerung"
        return "Änderungsauftrag"

    def _classify_area(self, text: str, old_value: str, new_value: str) -> str:
        value = normalize(" ".join([text, old_value, new_value]))
        if "sicherheitsregel" in value or "sicherheitsregeln" in value:
            return "Sicherheitsregel"
        if "schöpfer" in value or "schopfer" in value or "schoepfer" in value or "creator" in value:
            return "Foundation / Creator Command Policy"
        if "sicherheit" in value or "schutz" in value:
            return "Sicherheitsregel"
        if "governance" in value:
            return "Governance-Regel"
        if "foundation" in value or "fundament" in value:
            return "Foundation-Regel"
        if "motivation" in value:
            return "Motivationsregel"
        if "gui" in value or "aktivitätsfenster" in value or "aktivitaetsfenster" in value:
            return "GUI-Einstellung"
        if "konfiguration" in value or "konfig" in value:
            return "Konfiguration"
        if "lernregel" in value or "lernen" in value:
            return "Lernregel"
        if "chronik" in value or "projektchronik" in value:
            return "Projektchronik-Eintrag"
        if "memory" in value or "gedächtnis" in value or "gedaechtnis" in value or "erinnerung" in value:
            return "Memory-Änderung"
        return "Konfiguration"

    def _classify_risk(self, text: str, affected_area: str) -> str:
        if self._blocking_findings(text, affected_area):
            return "Sicherheits-/Governance-Verstoß"
        if affected_area in self.PROTECTED_AREAS:
            return "Governance-relevant"
        return "niedrig"

    def _extract_values(self, text: str) -> tuple[str, str]:
        raw = " ".join((text or "").split())
        match = re.search(r"(?is)\bersetze\s+(?:regel\s+\S+\s+)?(.+?)\s+durch\s+(.+)$", raw)
        if match:
            return self._strip_quotes(match.group(1)), self._strip_quotes(match.group(2))
        match = re.search(r"(?is)^(.+?)\s+zu\s*:\s*(.+)$", raw)
        if match:
            prefix, new_value = match.group(1), match.group(2)
            old_value = prefix.split(":", 1)[1] if ":" in prefix else prefix
            return self._strip_quotes(old_value), self._strip_quotes(new_value)
        match = re.search(r"(?is):\s*(.+)$", raw)
        if match:
            return "", self._strip_quotes(match.group(1))
        return "", ""

    def _blocking_findings(self, text: str, affected_area: str) -> list[str]:
        value = normalize(text)
        findings = []
        destructive = any(marker in value for marker in ("lösche", "losche", "loesche", "streiche", "entferne"))
        if destructive and affected_area in {"Sicherheitsregel", "Governance-Regel", "Foundation-Regel"}:
            findings.append("Schutz-, Foundation- oder Governance-Regeln dürfen nicht gelöscht werden.")
        if "alle befehle" in value and not any(marker in value for marker in ("sofern", "nicht mit", "sicherheit", "governance", "foundation")):
            findings.append("Unbegrenzte Befehlsausführung würde Schutzgrenzen umgehen.")
        return findings

    def _emit_event(
        self,
        event_type: str,
        text: str,
        payload: dict[str, Any],
        severity: str,
        requires_review: bool,
    ) -> str:
        engine = self.canonical_engine
        if not engine:
            return ""
        event = engine.create_event(
            event_type=event_type,
            source_component="change_agent",
            affected_path="14_documents/change_agent",
            affected_object_id=payload.get("hash", ""),
            severity=severity,
            payload=payload,
            provenance={"actor": "user", "input_hash": self._hash({"input": text})},
            governance_context={"requires_review": requires_review, "change_agent": True},
            processing_state="received",
        )
        engine.process_event(event)
        return str(event.get("event_id", ""))

    def _append_pending(self, row: dict[str, Any]) -> None:
        pending = self._read_json(self.pending_path, [])
        pending.append(row)
        self._write_json(self.pending_path, pending)

    def _update_status(self, last: ChangeRequest | None) -> None:
        requests = self._read_jsonl(self.requests_path)
        pending = self._read_json(self.pending_path, [])
        previous = self._read_json(self.status_path, {})
        last_row = asdict(last) if last else previous.get("last_change")
        status = {
            "active": True,
            "version": self.VERSION,
            "mode": self.MODE,
            "recognized_change_requests": len(requests),
            "open_changes": len(pending),
            "last_change": last_row,
            "last_applied": previous.get("last_applied", "-"),
        }
        self._write_json(self.status_path, status)

    @staticmethod
    def _strip_quotes(value: str) -> str:
        return (value or "").strip().strip("„“\"'` .")

    @staticmethod
    def _hash(value: dict[str, Any]) -> str:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    @staticmethod
    def _read_json(path: Path, default: Any) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return default

    @staticmethod
    def _write_json(path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
