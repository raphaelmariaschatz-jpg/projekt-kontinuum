# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from kontinuum.version import APP_VERSION

from .error_classification import DiagnosticFinding, ErrorClassificationEngine, Severity
from .solution_proposal import SolutionProposalEngine


class AutonomousDiagnosticsCore:
    AREAS = (
        "routing",
        "knowledge_graph",
        "database",
        "chronicle",
        "memory",
        "foundation",
        "agent_communication",
        "version",
    )

    def __init__(self, system):
        self.system = system
        self.classifier = ErrorClassificationEngine()
        self.solutions = SolutionProposalEngine()
        self.last_report: dict = {}

    def run(self, trigger: str = "automatic.startup") -> dict:
        findings: list[DiagnosticFinding] = []
        checks = (
            self._check_routing,
            self._check_knowledge_graph,
            self._check_database,
            self._check_chronicle,
            self._check_memory,
            self._check_foundation,
            self._check_agent_communication,
            self._check_version,
        )
        for check in checks:
            try:
                findings.extend(check())
            except Exception as exc:
                area = check.__name__.removeprefix("_check_")
                findings.append(self._finding(
                    f"diagnostic.{area}.failed", area, "Diagnosepruefung fehlgeschlagen",
                    "Der Bereich konnte nicht vollstaendig bewertet werden.", str(exc),
                    tags=("routing_error",), evidence=type(exc).__name__,
                ))
        completed = [self.solutions.apply(self.classifier.apply(item)) for item in findings]
        completed.sort(key=lambda item: (-int(item.severity or Severity.LOW), item.area, item.code))
        path = self._write_report(completed, trigger)
        highest = max((item.severity for item in completed), default=None)
        result = {
            "ok": not completed,
            "trigger": trigger,
            "checked_areas": list(self.AREAS),
            "findings": [self._serialize(item) for item in completed],
            "count": len(completed),
            "highest_severity": highest.label if highest else "KEINE",
            "report_path": str(path),
            "message": self._message(len(completed), highest, path),
        }
        self.last_report = result
        self.system.storage.add("audit_events", "diagnostics.run", result["message"], {
            "trigger": trigger,
            "count": result["count"],
            "highest_severity": result["highest_severity"],
            "report_path": result["report_path"],
            "findings": result["findings"],
        })
        return result

    def status(self) -> dict:
        return dict(self.last_report) if self.last_report else {
            "ok": True, "count": 0, "highest_severity": "KEINE", "message": "Diagnostik wurde noch nicht ausgefuehrt."
        }

    def _check_routing(self) -> list[DiagnosticFinding]:
        findings = []
        identity = self.system.identity_router.answer("Wer bin ich?")
        if not identity or self.system.session_context.current().get("display_name") not in identity:
            findings.append(self._finding(
                "routing.identity_context", "identity", "Identity Routing Fehler",
                "Identitaetsfragen koennen falsch beantwortet werden.",
                "Session Context wird nicht vor dem Identity Router ausgewertet.",
                tags=("identity_violation", "wrong_answer", "routing_error"), evidence=str(identity),
            ))
        diagnosis = self.system.agent_router.diagnose("pythonstatus", "command")
        if diagnosis.get("selected") != "python":
            findings.append(self._finding(
                "routing.pythonstatus", "routing", "Explizites Kommando wird falsch geroutet",
                "Ein Statuskommando kann vom falschen Agenten beantwortet werden.",
                "Prioritaet oder can_handle-Regel im Agentenregister ist inkonsistent.",
                tags=("wrong_answer", "routing_error"), evidence=json.dumps(diagnosis, ensure_ascii=False),
            ))
        return findings

    def _check_knowledge_graph(self) -> list[DiagnosticFinding]:
        malformed = 0
        with self.system.storage.connect() as db:
            for row in db.execute("SELECT metadata FROM graph_edges").fetchall():
                try:
                    data = json.loads(row["metadata"])
                    malformed += int(not all(data.get(key) for key in ("source", "relation", "target")))
                except (TypeError, ValueError):
                    malformed += 1
        if malformed:
            return [self._finding(
                "knowledge_graph.malformed_edges", "knowledge_graph", "Wissensgraph enthaelt unvollstaendige Kanten",
                "Graphabfragen koennen Beziehungen auslassen oder falsch deuten.",
                "Kantenmetadaten wurden unvollstaendig oder ungueltig gespeichert.",
                evidence=f"Betroffene Kanten: {malformed}", tags=("wrong_answer",),
            )]
        return []

    def _check_database(self) -> list[DiagnosticFinding]:
        with self.system.storage.connect() as db:
            result = str(db.execute("PRAGMA integrity_check").fetchone()[0])
        if result.casefold() != "ok":
            return [self._finding(
                "database.integrity", "database", "Datenbankintegritaet verletzt",
                "Gespeicherte Informationen koennen verloren oder unlesbar sein.",
                "SQLite meldet strukturelle Inkonsistenzen.", evidence=result, tags=("data_loss",),
            )]
        return []

    def _check_chronicle(self) -> list[DiagnosticFinding]:
        result = self.system.storage.verify_chronicle_integrity()
        if not result["ok"]:
            return [self._finding(
                "chronicle.integrity", "chronicle", "Chronik-Integritaet verletzt",
                "Historische Eintraege oder ihre Reihenfolge sind nicht mehr verlaesslich.",
                "Signatur fehlt oder Hash-Kette/Inhalt wurde veraendert.",
                evidence=json.dumps(result["issues"][:10], ensure_ascii=False), tags=("data_loss", "identity_violation"),
            )]
        return []

    def _check_memory(self) -> list[DiagnosticFinding]:
        invalid = 0
        with self.system.storage.connect() as db:
            for row in db.execute("SELECT metadata FROM memories").fetchall():
                try:
                    json.loads(row["metadata"])
                except (TypeError, ValueError):
                    invalid += 1
        if invalid:
            return [self._finding(
                "memory.invalid_metadata", "memory", "Memory-Metadaten sind ungueltig",
                "Erinnerungen koennen nicht korrekt eingeordnet werden.",
                "Nicht valides JSON wurde in Memory gespeichert.", evidence=f"Betroffene Eintraege: {invalid}", tags=("wrong_answer",),
            )]
        return []

    def _check_foundation(self) -> list[DiagnosticFinding]:
        findings = []
        integrity = self.system.foundation_integrity.run_audit("autonomous_diagnostics")
        memory_integrity = integrity.get("foundation_memory", self.system.foundation_memory.verify())
        reasoning_integrity = self.system.foundation_reasoning.verify()
        if not integrity["ok"] or not reasoning_integrity["ok"]:
            findings.append(self._finding(
                "foundation.integrity", "foundation", "Foundation Knowledge Protection verletzt",
                "Fundamentwissen könnte fehlen, verändert oder als Lern-/Wissenslücke kontaminiert sein.",
                "Integrität, Herkunft, Version oder Trennung der Schutzklasse weicht vom kanonischen Bestand ab.",
                evidence=json.dumps({
                    "issues": integrity["issues"][:10],
                    "contamination": integrity["contamination"][:10],
                    "foundation_memory_issues": memory_integrity["issues"][:10],
                    "foundation_reasoning_issues": reasoning_integrity["issues"][:10],
                }, ensure_ascii=False), tags=("identity_violation", "data_loss"),
            ))
        candidates = self.system.foundation_cycle_recovery.open_cycles()
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=30)
        open_ids = []
        if candidates:
            placeholders = ",".join("?" for _ in candidates)
            with self.system.storage.connect() as db:
                rows = db.execute(
                    f"SELECT id, created_at FROM foundation_decisions WHERE id IN ({placeholders})",
                    candidates,
                ).fetchall()
            for row in rows:
                try:
                    created = datetime.fromisoformat(row["created_at"])
                except (TypeError, ValueError):
                    created = datetime.min.replace(tzinfo=timezone.utc)
                if created <= cutoff:
                    open_ids.append(int(row["id"]))
        if open_ids:
            findings.append(self._finding(
                "foundation.open_cycles", "foundation", "Offene Foundation-Zyklen erkannt",
                "Entscheidungen besitzen keinen dokumentierten Abschluss.",
                "Eine fruehere Verarbeitung wurde vor der Complete-Phase beendet.",
                evidence=f"IDs: {open_ids[:20]}", tags=("identity_violation",),
            ))
        return findings

    def _check_agent_communication(self) -> list[DiagnosticFinding]:
        names = [agent.name for agent in self.system.agents]
        broken = [agent.name for agent in self.system.agents if agent.storage is not self.system.storage or agent.config is not self.system.agent_config]
        if len(names) != len(set(names)) or broken:
            return [self._finding(
                "agents.communication", "agent_communication", "Agentenkommunikation inkonsistent",
                "Agenten koennen mit abweichendem Zustand arbeiten.",
                "Doppelte Namen oder getrennte Storage-/Config-Bindings.",
                evidence=f"Doppelte Namen: {len(names) != len(set(names))}; fehlerhafte Bindings: {broken}", tags=("routing_error",),
            )]
        return []

    def _check_version(self) -> list[DiagnosticFinding]:
        root = self.system.path_tools.project_root()
        suffix = APP_VERSION.replace(".", "_")
        required = (
            root / "11_gui" / "desktop_gui.py",
            root / "11_gui" / f"desktop_gui_{suffix}.py",
            root / "11_gui" / "gui_manifest.json",
            root / "11_gui" / "README_GUI.md",
            root / "16_installation" / "START_GUI.bat",
            root / "13_tools" / f"status_check_{suffix}.py",
            root / "16_installation" / f"START_GUI_{suffix}.bat",
            root / "16_installation" / f"START_KONTINUUM_{suffix}.bat",
            root / "16_installation" / f"TEST_KONTINUUM_{suffix}.bat",
            root / "14_documents" / f"PROJEKTSTRUKTUR_{suffix}.md",
            root / "14_documents" / "projektstatus" / f"PROJEKTSTATUS_AKTUELL_{suffix}.md",
            root / "22_project_chronicle" / f"EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_{suffix}.md",
        )
        missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
        stale = []
        for path in (
            root / "README.md",
            root / "14_documents" / "projektstatus" / "README_PROJEKTSTATUS.md",
            root / "22_project_chronicle" / "EINSTIEGSPUNKTE_NAECHSTE_SITZUNG.md",
        ):
            try:
                if APP_VERSION not in path.read_text(encoding="utf-8"):
                    stale.append(str(path.relative_to(root)))
            except OSError:
                stale.append(str(path.relative_to(root)))
        if missing or stale:
            return [self._finding(
                "version.active_paths", "version", "Versionskonsistenz verletzt",
                "Aktive Start- oder Pruefpfade passen nicht zur Kernversion.",
                "Versionstraeger wurden nicht vollstaendig migriert.",
                evidence="; ".join(filter(None, (
                    "Fehlend: " + ", ".join(missing) if missing else "",
                    "Ohne aktive Version: " + ", ".join(stale) if stale else "",
                ))), tags=("documentation",),
            )]
        return []

    def _finding(self, code: str, area: str, error: str, impact: str, cause: str, *, evidence: str = "", tags=()) -> DiagnosticFinding:
        return DiagnosticFinding(code, area, error, impact, cause, evidence=evidence, tags=tuple(tags))

    def _write_report(self, findings: list[DiagnosticFinding], trigger: str) -> Path:
        directory = self.system.path_tools.paths()["documents"] / "interne_fehler_und_loesungen"
        directory.mkdir(parents=True, exist_ok=True)
        now = datetime.now().astimezone()
        path = directory / f"{now:%Y_%m_%d}_error_report.md"
        lines = [
            f"# Interner Fehler- und Loesungsbericht {now:%d.%m.%Y}", "",
            f"- Version: {APP_VERSION}", f"- Diagnosezeit: {now.isoformat(timespec='seconds')}",
            f"- Ausloeser: {trigger}", f"- Befunde: {len(findings)}", "",
        ]
        if not findings:
            lines += ["## Ergebnis", "", "Keine moeglichen Probleme erkannt.", "", "Status: GEPRUEFT", ""]
        for index, item in enumerate(findings, 1):
            lines += [
                f"## {index}. {item.error}", "", f"- Fehler: {item.error}",
                f"- Prioritaet: {item.severity.label if item.severity else 'NIEDRIG'}",
                f"- Bereich: {item.area}", f"- Auswirkung: {item.impact}",
                f"- Wahrscheinliche Ursache: {item.probable_cause}", f"- Loesung: {item.solution}",
                f"- Status: {item.status}", f"- Evidenz: {item.evidence or 'keine Zusatzangabe'}", "",
            ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _message(self, count: int, highest: Severity | None, path: Path) -> str:
        importance = highest.label if highest else "KEINE"
        return (
            "[DIAGNOSTIK]\n\n"
            f"Wichtigkeit: {importance}\n\n"
            f"{count} moegliche Probleme erkannt.\n\n"
            "Details wurden gespeichert:\n"
            "14_documents/interne_fehler_und_loesungen/"
        )

    @staticmethod
    def _serialize(item: DiagnosticFinding) -> dict:
        data = asdict(item)
        data["severity"] = item.severity.label if item.severity else "NIEDRIG"
        data["tags"] = list(item.tags)
        return data
