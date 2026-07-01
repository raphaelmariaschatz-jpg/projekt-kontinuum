from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CanonicalGitManager:
    VERSION = "2.0"
    MODE = "diagnostic_read_only"
    COMMAND_MARKERS = (
        "commit bereitschaft prüfen",
        "commit bereitschaft prufen",
        "commit bereitschaft pruefen",
        "release bereitschaft prüfen",
        "release bereitschaft prufen",
        "release bereitschaft pruefen",
        "cgm report",
        "cgm release prüfen",
        "cgm release prufen",
        "cgm release pruefen",
        "cgm chronik vorbereiten",
        "cgm cam abgleich",
        "cgm cde abgleich",
        "cgmstatus",
    )
    CANONICAL_PREFIXES = (
        "01_system/",
        "11_gui/",
        "13_tools/",
        "14_documents/",
        "17_tests/",
        "22_project_chronicle/",
        "24_config/",
        "31_reports/",
    )

    def __init__(
        self,
        path_tools,
        git_agent,
        storage: Any | None = None,
        canonical_engine: Any | None = None,
        canonical_architecture: Any | None = None,
        canonical_artifacts: Any | None = None,
        continuous_governance: Any | None = None,
    ):
        self.path_tools = path_tools
        self.git_agent = git_agent
        self.storage = storage
        self.canonical_engine = canonical_engine
        self.canonical_architecture = canonical_architecture
        self.canonical_artifacts = canonical_artifacts
        self.continuous_governance = continuous_governance
        self.root = path_tools.project_root().resolve()
        self.report_dir = path_tools.paths()["reports"] / "git"
        self.log_path = path_tools.paths()["logs"] / "canonical_git_manager_2_0.jsonl"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.touch(exist_ok=True)
        self._last_report: dict[str, Any] = {}

    @classmethod
    def looks_like_cgm_command(cls, text: str) -> bool:
        lower = (text or "").casefold().strip()
        return any(marker in lower for marker in cls.COMMAND_MARKERS)

    def handle_command(self, text: str) -> dict[str, Any]:
        lower = (text or "").casefold().strip(" .!?")
        path = self._extract_path(text)
        if lower == "cgmstatus":
            return {"ok": True, "message": self.format_status(), "result": self.status()}
        if lower.startswith("commit bereitschaft"):
            result = self.evaluate_commit_readiness(path)
            return {"ok": True, "message": self.format_commit_readiness(result), "result": result}
        if lower.startswith("release bereitschaft") or lower.startswith("cgm release"):
            result = self.evaluate_release_readiness(path)
            return {"ok": True, "message": self.format_release_readiness(result), "result": result}
        if lower.startswith("cgm cam"):
            result = self.compare_git_with_cam(path)
            return {"ok": True, "message": self.format_compare("CAM-Abgleich", result), "result": result}
        if lower.startswith("cgm cde"):
            result = self.compare_git_with_cde(path)
            return {"ok": True, "message": self.format_compare("CDE-Abgleich", result), "result": result}
        if lower.startswith("cgm chronik"):
            result = self.prepare_chronicle_entry(path, "CGM 2.0 vorbereiteter Chronik-Eintrag")
            return {"ok": True, "message": self.format_chronicle_entry(result), "result": result}
        result = self.create_cgm_report(path)
        return {"ok": True, "message": self.format_cgm_report(result), "result": result}

    def status(self) -> dict[str, Any]:
        return {
            "active": True,
            "version": self.VERSION,
            "mode": self.MODE,
            "read_only": True,
            "last_report_status": self._last_report.get("status", ""),
            "last_repo_path": self._last_report.get("repo_path", ""),
            "last_report_path": self._last_report.get("report_path", ""),
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Canonical Git Manager 2.0 Status:",
            "- CGM aktiv: ja",
            f"- Modus: {status['mode']}",
            "- read-only: ja",
            f"- letztes Repository: {status['last_repo_path'] or '-'}",
            f"- letzter Reportstatus: {status['last_report_status'] or '-'}",
            f"- letzter Report: {status['last_report_path'] or '-'}",
        ])

    def evaluate_commit_readiness(self, path: str = "") -> dict[str, Any]:
        git_status = self.git_agent.get_status(path)
        findings: list[str] = []
        warnings: list[str] = []
        actions: list[str] = []
        if git_status.get("status") == "error":
            findings.extend(git_status.get("errors", []))
        if not git_status.get("is_git_repo"):
            findings.append("Kein Git-Repository erkannt.")
        changed = git_status.get("changed_files", [])
        untracked = git_status.get("untracked_files", [])
        deleted = git_status.get("deleted_files", [])
        if not (changed or untracked or deleted):
            warnings.append("Keine uncommitted changes vorhanden; ein Commit ist aktuell nicht nötig.")
        if untracked:
            warnings.append("Neue Dateien vorhanden; kanonische Relevanz vor Commit prüfen.")
        if deleted:
            findings.append("Gelöschte Dateien vorhanden; Löschungen vor Commit governance-seitig prüfen.")
        canonical_changed = self._canonical_changes(git_status)
        if canonical_changed:
            warnings.append("Kanonische Artefakte/Module sind betroffen.")
            actions.append("CAM/CDE-Abgleich vor Commit prüfen.")
        if changed or untracked or deleted:
            actions.append("Tests ausführen und Abschlussreport/Chronikbedarf prüfen.")
            actions.append("Commit erst nach ausdrücklicher Freigabe erstellen.")
        return self._finish({
            "status": "ok",
            "kind": "commit_readiness",
            "repo_path": git_status.get("repo_path", path or str(self.root)),
            "commit_ready": bool(git_status.get("is_git_repo")) and bool(changed or untracked or deleted) and not findings,
            "git_status": git_status,
            "canonical_changed_files": canonical_changed,
            "blocking_findings": findings,
            "warnings": warnings,
            "recommended_next_actions": actions,
            "read_only": True,
            "timestamp": self._now(),
        }, "CGM_COMMIT_READINESS_EVALUATED")

    def evaluate_release_readiness(self, path: str = "") -> dict[str, Any]:
        git_status = self.git_agent.get_status(path)
        cam = self.compare_git_with_cam(path)
        cde = self.compare_git_with_cde(path)
        findings: list[str] = []
        warnings: list[str] = []
        actions: list[str] = []
        if not git_status.get("is_git_repo"):
            findings.append("Kein Git-Repository erkannt.")
        if not git_status.get("clean_worktree"):
            findings.append("Arbeitsbaum ist nicht sauber.")
        if not cam.get("cam_ok", False):
            warnings.append("CAM-Status ist nicht vollständig verifiziert oder nicht verfügbar.")
        if not cde.get("cde_ok", False):
            warnings.append("CDE/Event-Bus-Status ist nicht vollständig verifiziert oder nicht verfügbar.")
        if not self._has_recent_report():
            warnings.append("Kein aktueller Abschluss-/Umsetzungsreport im Dokumentenbereich erkannt.")
        suggested_tag = self._suggest_tag(git_status)
        actions.extend([
            "Release-Tests vollständig ausführen.",
            "Projektchronik-Eintrag vorbereiten und nach Freigabe schreiben.",
            f"Release-Tag nur nach Freigabe erzeugen: {suggested_tag}",
        ])
        return self._finish({
            "status": "ok",
            "kind": "release_readiness",
            "repo_path": git_status.get("repo_path", path or str(self.root)),
            "release_ready": bool(git_status.get("is_git_repo")) and bool(git_status.get("clean_worktree")) and not findings,
            "blocking_findings": findings,
            "warnings": warnings,
            "recommended_next_actions": actions,
            "suggested_tag": suggested_tag,
            "git_status": git_status,
            "cam": cam,
            "cde": cde,
            "read_only": True,
            "timestamp": self._now(),
        }, "CGM_RELEASE_READINESS_EVALUATED")

    def compare_git_with_cam(self, path: str = "") -> dict[str, Any]:
        git_status = self.git_agent.get_status(path)
        cam_status = self._safe_status(self.canonical_artifacts)
        architecture_status = self._safe_status(self.canonical_architecture)
        relevant = self._canonical_changes(git_status)
        untracked_canonical = [item for item in git_status.get("untracked_files", []) if self._is_canonical_path(item)]
        return self._finish({
            "status": "ok",
            "kind": "cam_compare",
            "repo_path": git_status.get("repo_path", path or str(self.root)),
            "cam_ok": bool(cam_status.get("ok") or cam_status.get("configured") or architecture_status.get("ok")),
            "cam_status": cam_status,
            "canonical_architecture_status": architecture_status,
            "canonical_changed_files": relevant,
            "untracked_canonical_files": untracked_canonical,
            "artifact_drift": bool(untracked_canonical),
            "write_performed": False,
            "read_only": True,
            "timestamp": self._now(),
        }, "CGM_CAM_COMPARE_REPORTED")

    def compare_git_with_cde(self, path: str = "") -> dict[str, Any]:
        git_status = self.git_agent.get_status(path)
        cde_status = self._safe_status(self.canonical_engine)
        last_commit = self._last_commit(path)
        return self._finish({
            "status": "ok",
            "kind": "cde_compare",
            "repo_path": git_status.get("repo_path", path or str(self.root)),
            "cde_ok": bool(cde_status.get("ok") or cde_status.get("active") or cde_status.get("event_bus")),
            "event_bus": cde_status.get("event_bus", {}),
            "last_event": cde_status.get("last_event", {}),
            "git_commit_hash": last_commit.get("hash", ""),
            "git_commit_short_hash": last_commit.get("short_hash", ""),
            "drift_findings": self._cde_drift_findings(git_status, cde_status),
            "write_performed": False,
            "read_only": True,
            "timestamp": self._now(),
        }, "CGM_CDE_COMPARE_REPORTED")

    def prepare_release_tag(self, path: str = "", version: str = "") -> dict[str, Any]:
        git_status = self.git_agent.get_status(path)
        tag = version.strip() if version else self._suggest_tag(git_status)
        return {
            "status": "prepared",
            "repo_path": git_status.get("repo_path", path or str(self.root)),
            "suggested_tag": tag,
            "command_preview": f"git tag {tag}",
            "execute_automatically": False,
            "requires_explicit_approval": True,
            "read_only": True,
            "timestamp": self._now(),
        }

    def prepare_chronicle_entry(self, path: str = "", summary: str = "") -> dict[str, Any]:
        git_status = self.git_agent.get_status(path)
        cam = self.compare_git_with_cam(path)
        cde = self.compare_git_with_cde(path)
        last_commit = self._last_commit(path)
        entry = {
            "date": self._now(),
            "version_or_tag": self._suggest_tag(git_status),
            "commit_hash": last_commit.get("hash", ""),
            "summary": summary or "CGM 2.0 Git-/Governance-Status vorbereitet.",
            "affected_modules": self._affected_modules(git_status),
            "governance_status": "pending_review" if not git_status.get("clean_worktree") else "ready_for_review",
            "cam_status": "ok" if cam.get("cam_ok") else "review_needed",
            "cde_status": "ok" if cde.get("cde_ok") else "review_needed",
            "open_points": self.evaluate_commit_readiness(path).get("warnings", []),
            "next_step": "Chronik nach Freigabe schreiben; keine automatische Änderung durch CGM 2.0.",
            "write_performed": False,
            "read_only": True,
        }
        return self._finish({
            "status": "prepared",
            "kind": "chronicle_entry",
            "repo_path": git_status.get("repo_path", path or str(self.root)),
            "chronicle_entry": entry,
            "read_only": True,
            "timestamp": self._now(),
        }, "CGM_CHRONICLE_ENTRY_PREPARED")

    def create_cgm_report(self, path: str = "") -> dict[str, Any]:
        commit = self.evaluate_commit_readiness(path)
        release = self.evaluate_release_readiness(path)
        cam = self.compare_git_with_cam(path)
        cde = self.compare_git_with_cde(path)
        chronicle = self.prepare_chronicle_entry(path, "CGM 2.0 Report")
        report = {
            "status": "ok",
            "kind": "cgm_report",
            "repo_path": commit.get("repo_path", path or str(self.root)),
            "commit_readiness": commit,
            "release_readiness": release,
            "cam_compare": cam,
            "cde_compare": cde,
            "chronicle_preparation": chronicle,
            "safety": {
                "automatic_commits": False,
                "automatic_tags": False,
                "automatic_branches": False,
                "automatic_merges": False,
                "automatic_rollbacks": False,
                "remote_push": False,
                "delete_actions": False,
            },
            "read_only": True,
            "timestamp": self._now(),
        }
        path_out = self.report_dir / f"cgm_2_0_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path_out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path_out)
        return self._finish(report, "CGM_REPORT_CREATED")

    def _finish(self, result: dict[str, Any], event_type: str) -> dict[str, Any]:
        self._last_report = result
        if event_type == "CGM_REPORT_CREATED":
            self._log(result)
            self._emit_event(event_type, result)
        return result

    def _safe_status(self, component: Any | None) -> dict[str, Any]:
        if not component:
            return {"available": False}
        try:
            if hasattr(component, "status"):
                value = component.status()
                return value if isinstance(value, dict) else {"status": str(value)}
        except Exception as exc:
            return {"available": True, "error": str(exc)}
        return {"available": True}

    def _last_commit(self, path: str = "") -> dict[str, Any]:
        history = self.git_agent.list_recent_commits(path, 1)
        commits = history.get("recent_commits", [])
        return commits[0] if commits else {}

    def _canonical_changes(self, git_status: dict[str, Any]) -> list[str]:
        files = git_status.get("changed_files", []) + git_status.get("untracked_files", []) + git_status.get("deleted_files", [])
        return [item for item in files if self._is_canonical_path(item)]

    def _is_canonical_path(self, value: str) -> bool:
        normalized = (value or "").replace("\\", "/")
        return normalized.startswith(self.CANONICAL_PREFIXES)

    def _cde_drift_findings(self, git_status: dict[str, Any], cde_status: dict[str, Any]) -> list[str]:
        findings = []
        if not cde_status.get("event_bus"):
            findings.append("CDE Event Bus Status nicht verfügbar.")
        if self._canonical_changes(git_status):
            findings.append("Git meldet Änderungen an kanonischen Pfaden; CDE/CAM Review empfohlen.")
        return findings

    def _has_recent_report(self) -> bool:
        docs = self.path_tools.paths()["documents"]
        return any(docs.glob("*umsetzung*.md")) or any(docs.glob("*abschluss*.md"))

    def _suggest_tag(self, git_status: dict[str, Any]) -> str:
        branch = (git_status.get("current_branch") or "main").replace("/", "-")
        return f"v{datetime.now().strftime('%Y.%m.%d')}-{branch}"

    @staticmethod
    def _affected_modules(git_status: dict[str, Any]) -> list[str]:
        files = git_status.get("changed_files", []) + git_status.get("untracked_files", []) + git_status.get("deleted_files", [])
        modules = sorted({item.replace("\\", "/").split("/", 1)[0] for item in files if item})
        return modules

    @staticmethod
    def _extract_path(text: str) -> str:
        quoted = re.search(r'"([^"]+)"|\'([^\']+)\'', text or "")
        if quoted:
            return quoted.group(1) or quoted.group(2)
        windows_path = re.search(r"(?i)\b[a-z]:[\\/][^\s\"']+", text or "")
        if windows_path:
            return windows_path.group(0).rstrip(".,;:!?)]}")
        return ""

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _log(self, result: dict[str, Any]) -> None:
        row = {
            "timestamp": self._now(),
            "kind": result.get("kind", ""),
            "status": result.get("status"),
            "repo_path": result.get("repo_path"),
            "read_only": result.get("read_only", True),
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def _emit_event(self, event_type: str, result: dict[str, Any]) -> None:
        engine = self.canonical_engine
        if not engine:
            return
        try:
            engine.ingest(
                event_type=event_type,
                source_component="canonical_git_manager",
                affected_path=result.get("repo_path", str(self.root)),
                affected_object_id=result.get("kind", ""),
                severity="info",
                payload={
                    "kind": result.get("kind", ""),
                    "read_only": True,
                    "blocking_findings": result.get("blocking_findings", []),
                    "warnings": result.get("warnings", []),
                },
                provenance={"agent": "CanonicalGitManager", "version": self.VERSION},
                governance_context={"git": True, "canonical_git_manager": True, "requires_review": False, "read_only": True},
            )
        except Exception:
            pass

    @staticmethod
    def format_commit_readiness(result: dict[str, Any]) -> str:
        return "\n".join([
            "CGM 2.0 Commit-Bereitschaft:",
            f"- Repository: {result.get('repo_path')}",
            f"- commit_ready: {'ja' if result.get('commit_ready') else 'nein'}",
            "- blockierende Befunde: " + ("; ".join(result.get("blocking_findings", [])) if result.get("blocking_findings") else "-"),
            "- Warnungen: " + ("; ".join(result.get("warnings", [])) if result.get("warnings") else "-"),
            "- nächste Schritte: " + ("; ".join(result.get("recommended_next_actions", [])) if result.get("recommended_next_actions") else "-"),
            "- automatische Commits: nein",
        ])

    @staticmethod
    def format_release_readiness(result: dict[str, Any]) -> str:
        return "\n".join([
            "CGM 2.0 Release-Bereitschaft:",
            f"- Repository: {result.get('repo_path')}",
            f"- release_ready: {'ja' if result.get('release_ready') else 'nein'}",
            f"- vorgeschlagener Tag: {result.get('suggested_tag')}",
            "- blockierende Befunde: " + ("; ".join(result.get("blocking_findings", [])) if result.get("blocking_findings") else "-"),
            "- Warnungen: " + ("; ".join(result.get("warnings", [])) if result.get("warnings") else "-"),
            "- automatische Tags: nein",
        ])

    @staticmethod
    def format_compare(title: str, result: dict[str, Any]) -> str:
        drift = result.get("artifact_drift", bool(result.get("drift_findings")))
        return "\n".join([
            f"CGM 2.0 {title}:",
            f"- Repository: {result.get('repo_path')}",
            f"- Status: {result.get('status')}",
            f"- Drift erkannt: {'ja' if drift else 'nein'}",
            f"- Schreibzugriff ausgeführt: {'ja' if result.get('write_performed') else 'nein'}",
            "- read-only: ja",
        ])

    @staticmethod
    def format_chronicle_entry(result: dict[str, Any]) -> str:
        entry = result.get("chronicle_entry", {})
        return "\n".join([
            "CGM 2.0 Chronik-Eintrag vorbereitet:",
            f"- Datum: {entry.get('date', '-')}",
            f"- Tag/Version: {entry.get('version_or_tag', '-')}",
            f"- Commit: {entry.get('commit_hash', '-') or '-'}",
            f"- Zusammenfassung: {entry.get('summary', '-')}",
            f"- Governance-Status: {entry.get('governance_status', '-')}",
            "- automatisch geschrieben: nein",
        ])

    @staticmethod
    def format_cgm_report(result: dict[str, Any]) -> str:
        release = result.get("release_readiness", {})
        commit = result.get("commit_readiness", {})
        return "\n".join([
            "Canonical Git Manager 2.0 Report:",
            f"- Repository: {result.get('repo_path')}",
            f"- Commit bereit: {'ja' if commit.get('commit_ready') else 'nein'}",
            f"- Release bereit: {'ja' if release.get('release_ready') else 'nein'}",
            f"- Report: {result.get('report_path', '-')}",
            "- automatische Git-Aktionen: nein",
            "- Chronik nur vorbereitet: ja",
        ])
