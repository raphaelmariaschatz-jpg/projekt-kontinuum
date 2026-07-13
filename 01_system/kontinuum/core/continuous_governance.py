# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .canonical_architecture import CanonicalArchitectureManager
from .canonical_artifacts import CanonicalArtifactManager
from .release_integrity import ReleaseIntegrityFramework


@dataclass(frozen=True)
class GovernanceDecision:
    path: str
    classification: str
    reason: str
    context: str
    verification_status: str
    timestamp_utc: str

    def as_dict(self) -> dict:
        return {
            "timestamp_utc": self.timestamp_utc,
            "path": self.path,
            "classification": self.classification,
            "reason": self.reason,
            "context": self.context,
            "verification_status": self.verification_status,
        }


@dataclass(frozen=True)
class GovernanceEvent:
    event_type: str
    severity: str
    message: str
    payload: dict
    timestamp_utc: str

    def as_dict(self) -> dict:
        return {
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "payload": self.payload,
        }


class GovernanceEventLogger:
    """Append-only audit logger for Phase-3 governance events."""

    VERSION = "1.0"

    def __init__(self, project_root: str | Path, log_path: str | Path):
        self.root = Path(project_root).resolve()
        self.log_path = self.root / log_path

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_event(self, event_type: str, severity: str, message: str, payload: dict | None = None) -> dict:
        event = GovernanceEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            payload=payload or {},
            timestamp_utc=self._now(),
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        record = event.as_dict()
        self.log_path.open("a", encoding="utf-8").write(
            json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        )
        return record

    def status(self) -> dict:
        return {
            "component": "GEL",
            "name": "Governance Event Logger",
            "active": True,
            "ok": self.log_path.parent.exists() or (self.root / "31_reports" / "governance").exists(),
            "log": self.log_path.relative_to(self.root).as_posix(),
            "mode": "append_only_jsonl",
        }


class CanonicalGovernanceBaselineReference:
    """Immutable read-only reference to canonical_governance_baseline_34_1.json."""

    VERSION = "1.0"

    def __init__(self, project_root: str | Path, release_version: str = "34.1"):
        self.root = Path(project_root).resolve()
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.path = self.root / "24_config" / f"canonical_governance_baseline_{token}.json"
        self.acceptance_path = self.root / "24_config" / f"canonical_governance_baseline_{token}_ACCEPTED.json"
        self.document = self._load_json(self.path)
        self.acceptance = self._load_json(self.acceptance_path) if self.acceptance_path.is_file() else {}

    @staticmethod
    def _load_json(path: Path) -> dict:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Canonical Governance Baseline fehlt oder ist ungueltig: {path}") from exc

    @staticmethod
    def _file_hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def status(self) -> dict:
        digest = self._file_hash(self.path)
        accepted_hash = self.acceptance.get("sha256", "")
        immutable = (
            self.document.get("kind") == "kontinuum.canonical_governance_baseline"
            and self.document.get("version") == self.release_version
            and self.document.get("status") == "VERIFIZIERT"
            and self.document.get("freigabe") == "JA"
            and (not accepted_hash or accepted_hash == digest)
        )
        return {
            "component": "Baseline Layer",
            "active": True,
            "ok": immutable,
            "path": self.path.relative_to(self.root).as_posix(),
            "sha256": digest,
            "accepted_sha256": accepted_hash,
            "status": "IMMUTABLE_READ_ONLY_REFERENCE" if immutable else "BASELINE_MISMATCH",
            "replacement_policy": self.acceptance.get(
                "replacement_policy",
                "Nur durch offiziell freigegebene Governance-Versionen ersetzbar.",
            ),
        }

    def artifact_hashes(self) -> dict:
        return self.document.get("artifact_hashes", {})

    def required_roots(self) -> list[str]:
        return [Path(item).as_posix() for item in self.document.get("active_main_folders", [])]


class DriftDetectionEngine:
    """Compares the current project state against the immutable 34.1 baseline."""

    VERSION = "1.0"

    def __init__(self, project_root: str | Path, config: dict, baseline: CanonicalGovernanceBaselineReference):
        self.root = Path(project_root).resolve()
        self.config = config
        self.baseline = baseline

    @staticmethod
    def _severity(high: int, medium: int, low: int) -> str:
        if high:
            return "HIGH"
        if medium:
            return "MEDIUM"
        if low:
            return "LOW"
        return "NONE"

    @staticmethod
    def _file_hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def analyze(self) -> dict:
        findings: list[dict] = []
        for relative in self.baseline.required_roots():
            if not (self.root / relative).exists():
                findings.append({
                    "type": "missing_baseline_root",
                    "severity": "HIGH",
                    "path": relative,
                    "message": "Baseline-Hauptordner fehlt.",
                })
        for relative, expected in self.baseline.artifact_hashes().items():
            path = self.root / relative
            if not path.is_file():
                findings.append({
                    "type": "missing_baseline_artifact",
                    "severity": "HIGH",
                    "path": relative,
                    "message": "Baseline-Artefakt fehlt.",
                })
                continue
            current_hash = self._file_hash(path)
            if current_hash != expected.get("sha256"):
                findings.append({
                    "type": "artifact_hash_drift",
                    "severity": "MEDIUM",
                    "path": relative,
                    "expected_sha256": expected.get("sha256"),
                    "actual_sha256": current_hash,
                    "message": "Artefakt weicht vom Baseline-Hash ab.",
                })
        for relative in self.config.get("single_active_patterns", []):
            matches = sorted((self.root.glob(relative)), key=lambda path: path.as_posix().casefold())
            if len(matches) != 1:
                findings.append({
                    "type": "single_active_pattern_drift",
                    "severity": "MEDIUM",
                    "pattern": relative,
                    "count": len(matches),
                    "expected": 1,
                    "matches": [path.relative_to(self.root).as_posix() for path in matches],
                })
        unmanaged = []
        for relative in self.config.get("watch_roots", []):
            root = self.root / relative
            if not root.exists():
                continue
            allowed = self.config.get("allowed_top_level_entries", {}).get(relative, [])
            for path in root.iterdir():
                if path.name == "archive":
                    continue
                candidate = path.relative_to(self.root).as_posix()
                if candidate not in allowed and path.is_dir():
                    unmanaged.append(candidate)
                    findings.append({
                        "type": "unmanaged_top_level_entry",
                        "severity": "LOW",
                        "path": candidate,
                        "message": "Ueberwachter Bereich enthaelt nicht registrierten Top-Level-Eintrag.",
                    })
        high = sum(1 for item in findings if item.get("severity") == "HIGH")
        medium = sum(1 for item in findings if item.get("severity") == "MEDIUM")
        low = sum(1 for item in findings if item.get("severity") == "LOW")
        return {
            "component": "DDE",
            "name": "Drift Detection Engine",
            "active": True,
            "ok": not findings,
            "classification": self._severity(high, medium, low),
            "counts": {"HIGH": high, "MEDIUM": medium, "LOW": low},
            "findings": findings,
            "unmanaged_top_level_entries": unmanaged,
        }


class CanonicalIntegrityChecker:
    """Read-only validator for new or changed artifacts."""

    VERSION = "1.0"

    def __init__(self, project_root: str | Path, config: dict, baseline: CanonicalGovernanceBaselineReference):
        self.root = Path(project_root).resolve()
        self.config = config
        self.baseline = baseline

    def validate_artifact(self, path: str | Path, classification: GovernanceDecision | None = None) -> dict:
        relative = Path(path)
        if relative.is_absolute():
            relative = relative.resolve().relative_to(self.root)
        normalized = relative.as_posix()
        decision = classification
        issues: list[str] = []
        baseline_hashes = self.baseline.artifact_hashes()
        if normalized == self.baseline.path.relative_to(self.root).as_posix():
            issues.append("baseline_is_immutable_read_only_reference")
        if normalized in baseline_hashes:
            path_obj = self.root / normalized
            if not path_obj.is_file():
                issues.append("registered_baseline_artifact_missing")
        allowed_names = tuple(self.config.get("canonical_name_markers", ["34_1", "34.1", "canonical", "governance"]))
        if normalized.startswith(("24_config/", "31_reports/governance/", "14_documents/")):
            if not any(marker in Path(normalized).name for marker in allowed_names):
                if decision is None or decision.classification != "active":
                    issues.append("canonical_naming_or_registry_review_required")
        classification_name = decision.classification if decision else "unclassified"
        return {
            "component": "CIC",
            "name": "Canonical Integrity Checker",
            "active": True,
            "path": normalized,
            "classification": classification_name,
            "ok": not issues,
            "action": "allow" if not issues else "flag",
            "enforcement": "read_only_flagging_no_mutation",
            "issues": issues,
        }

    def status(self) -> dict:
        checks = []
        for relative in self.config.get("active_paths", []):
            decision = GovernanceDecision(
                path=relative,
                classification="active",
                reason="configured_active_path",
                context="integrity_status",
                verification_status="VERIFIZIERT",
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
            )
            checks.append(self.validate_artifact(relative, classification=decision))
        return {
            "component": "CIC",
            "name": "Canonical Integrity Checker",
            "active": True,
            "ok": all(item["ok"] for item in checks),
            "checked": len(checks),
            "issues": [item for item in checks if not item["ok"]],
            "enforcement": "read_only_flagging_no_mutation",
        }


class CanonicalGovernanceMonitor:
    """Orchestrates CGM, DDE, CIC and GEL for exportable Phase-3 reports."""

    VERSION = "1.0"

    def __init__(
        self,
        project_root: str | Path,
        release_version: str,
        config: dict,
        baseline: CanonicalGovernanceBaselineReference,
        drift_engine: DriftDetectionEngine,
        integrity_checker: CanonicalIntegrityChecker,
        event_logger: GovernanceEventLogger,
    ):
        self.root = Path(project_root).resolve()
        self.release_version = release_version
        self.config = config
        self.baseline = baseline
        self.drift_engine = drift_engine
        self.integrity_checker = integrity_checker
        self.event_logger = event_logger
        self.report_root = self.root / "31_reports" / "governance" / "phase3"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def compliance_score(drift: dict, integrity: dict, baseline: dict) -> int:
        score = 100
        counts = drift.get("counts", {})
        score -= counts.get("HIGH", 0) * 35
        score -= counts.get("MEDIUM", 0) * 15
        score -= counts.get("LOW", 0) * 5
        if not integrity.get("ok", False):
            score -= 20
        if not baseline.get("ok", False):
            score -= 40
        return max(0, min(100, score))

    def run_full_analysis(self, write_reports: bool = True) -> dict:
        baseline_status = self.baseline.status()
        drift = self.drift_engine.analyze()
        integrity = self.integrity_checker.status()
        score = self.compliance_score(drift, integrity, baseline_status)
        status = {
            "kind": "kontinuum.phase3.governance_status",
            "version": self.release_version,
            "created_at": self._now(),
            "component": "CGM",
            "name": "Canonical Governance Monitor",
            "active": True,
            "ok": baseline_status["ok"] and drift["active"] and integrity["active"],
            "drift_free": drift["ok"],
            "baseline": baseline_status,
            "drift": drift,
            "integrity": integrity,
            "baseline_compliance_score": score,
            "reports": {
                "governance_status": "31_reports/governance/phase3/governance_status_report.json",
                "drift": "31_reports/governance/phase3/drift_report.json",
                "integrity": "31_reports/governance/phase3/integrity_report.json",
                "compliance": "31_reports/governance/phase3/baseline_compliance_score.json",
            },
        }
        severity = "INFO" if status["ok"] else drift.get("classification", "MEDIUM")
        self.event_logger.log_event(
            "baseline_comparison_completed",
            severity,
            "Phase-3-Governanceanalyse gegen Baseline 34.1 durchgefuehrt.",
            {
                "ok": status["ok"],
                "drift_classification": drift.get("classification"),
                "baseline_compliance_score": score,
            },
        )
        if write_reports:
            self.export_reports(status)
        return status

    def export_reports(self, status: dict) -> dict:
        self.report_root.mkdir(parents=True, exist_ok=True)
        reports = {
            "governance_status_report.json": status,
            "drift_report.json": status["drift"],
            "integrity_report.json": status["integrity"],
            "baseline_compliance_score.json": {
                "version": self.release_version,
                "created_at": status["created_at"],
                "score": status["baseline_compliance_score"],
                "baseline": status["baseline"],
                "drift_classification": status["drift"].get("classification"),
            },
        }
        written = {}
        for name, payload in reports.items():
            path = self.report_root / name
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            written[name] = path.relative_to(self.root).as_posix()
        return written


class ContinuousGovernanceSystem:
    """Read-only continuous governance layer for canonical project stability."""

    VERSION = "1.0"
    CLASSIFICATIONS = ("active", "archive_candidate", "review", "consolidate_suggest")

    def __init__(self, project_root: str | Path, release_version: str = "34.1", strict_config: bool = True):
        self.root = Path(project_root).resolve()
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.config_path = self.root / "24_config" / f"continuous_governance_{token}.json"
        self.strict_config = strict_config
        self.config = self._load_config()
        self.log_path = self.root / self.config.get(
            "governance_log",
            "31_reports/governance/phase3_continuous_governance_log.jsonl",
        )
        self.baseline = CanonicalGovernanceBaselineReference(self.root, self.release_version)
        self.event_logger = GovernanceEventLogger(self.root, self.log_path.relative_to(self.root))
        self.drift_engine = DriftDetectionEngine(self.root, self.config, self.baseline)
        self.integrity_checker = CanonicalIntegrityChecker(self.root, self.config, self.baseline)
        self.monitor = CanonicalGovernanceMonitor(
            self.root,
            self.release_version,
            self.config,
            self.baseline,
            self.drift_engine,
            self.integrity_checker,
            self.event_logger,
        )

    def _load_config(self) -> dict:
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            if not self.strict_config:
                return {"version": self.release_version, "configured": False}
            raise RuntimeError(f"Continuous-Governance-Konfiguration fehlt oder ist ungueltig: {self.config_path}") from exc
        if value.get("version") != self.release_version:
            raise RuntimeError("Continuous-Governance-Konfiguration gehoert nicht zur aktiven Version.")
        return value

    def _relative(self, path: str | Path) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate.resolve().relative_to(self.root).as_posix()
        return candidate.as_posix()

    @staticmethod
    def _inside(relative: str, root: str) -> bool:
        root = root.rstrip("/")
        return relative == root or relative.startswith(root + "/")

    def _known_active_paths(self) -> set[str]:
        paths: set[str] = set()
        for key in ("active_paths", "canonical_paths", "entrypoint_paths", "registry_paths"):
            paths.update(Path(item).as_posix() for item in self.config.get(key, []))
        return paths

    def classify_artifact(self, path: str | Path, context: str = "event") -> GovernanceDecision:
        relative = self._relative(path)
        active_paths = self._known_active_paths()
        archive_roots = [Path(item).as_posix() for item in self.config.get("archive_roots", [])]
        review_roots = [Path(item).as_posix() for item in self.config.get("review_roots", [])]
        consolidation_roots = [Path(item).as_posix() for item in self.config.get("consolidation_roots", [])]
        archive_markers = tuple(self.config.get("archive_candidate_markers", []))

        if any(self._inside(relative, root) for root in archive_roots):
            classification = "active"
            reason = "already_inside_governed_archive_root"
        elif relative in active_paths or any(self._inside(relative, root) for root in active_paths if root.endswith("/")):
            classification = "active"
            reason = "canonical_or_required_active_artifact"
        elif any(self._inside(relative, root) for root in review_roots):
            classification = "review"
            reason = "created_or_changed_inside_review_root"
        elif any(self._inside(relative, root) for root in consolidation_roots):
            classification = "consolidate_suggest"
            reason = "potential_redundancy_or_consolidation_root"
        elif archive_markers and any(marker in Path(relative).name for marker in archive_markers):
            classification = "archive_candidate"
            reason = "historical_marker_detected"
        else:
            classification = "review"
            reason = "unknown_noncanonical_artifact_requires_review"

        return GovernanceDecision(
            path=relative,
            classification=classification,
            reason=reason,
            context=context,
            verification_status=self.verification_status(),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )

    def log_decision(self, decision: GovernanceDecision) -> dict:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = decision.as_dict()
        self.event_logger.log_event(
            "artifact_validated",
            "INFO" if decision.classification == "active" else "LOW",
            "Artefakt wurde durch Phase-3-Governance klassifiziert.",
            payload,
        )
        self.log_path.open("a", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return payload

    def classify_and_log(self, path: str | Path, context: str = "event") -> dict:
        return self.log_decision(self.classify_artifact(path, context=context))

    def stability_check(self) -> dict:
        required_roots = self.config.get("required_roots", [])
        archive_roots = self.config.get("archive_roots", [])
        missing_required = [relative for relative in required_roots if not (self.root / relative).exists()]
        missing_archives = [relative for relative in archive_roots if not (self.root / relative).is_dir()]
        free_roots = [relative for relative in self.config.get("forbidden_free_roots", []) if (self.root / relative).exists()]
        return {
            "ok": not missing_required and not missing_archives and not free_roots,
            "missing_required_roots": missing_required,
            "missing_archive_roots": missing_archives,
            "free_roots": free_roots,
            "mode": "read_only_no_mutation",
        }

    def drift_detection(self) -> dict:
        analysis = self.drift_engine.analyze()
        pattern_findings = [
            item for item in analysis["findings"] if item.get("type") == "single_active_pattern_drift"
        ]
        return {
            "ok": analysis["active"],
            "drift_free": analysis["ok"],
            "classification": analysis["classification"],
            "counts": analysis["counts"],
            "pattern_findings": pattern_findings,
            "findings": analysis["findings"],
            "unmanaged_top_level_entries": analysis["unmanaged_top_level_entries"],
        }

    def enforcement_check(self) -> dict:
        policies = self.config.get("enforcement", {})
        checks = {
            "no_auto_delete": policies.get("auto_delete") is False,
            "no_auto_move": policies.get("auto_move") is False,
            "verification_required": policies.get("verification_required") is True,
            "log_required": policies.get("log_required") is True,
            "phase2_batch_migration_closed": policies.get("phase2_batch_migration") == "closed",
        }
        return {"ok": all(checks.values()), "checks": checks}

    def verification_status(self) -> str:
        release = ReleaseIntegrityFramework(self.root, self.release_version).status()
        return "VERIFIZIERT" if release.get("release_approved") else "NICHT VERIFIZIERT"

    def verification_loop(self) -> dict:
        architecture = CanonicalArchitectureManager(self.root, release_version=self.release_version).status()
        artifacts = CanonicalArtifactManager(self.root, release_version=self.release_version).status()
        release = ReleaseIntegrityFramework(self.root, self.release_version).status()
        checks = {
            "canonical_architecture": architecture.get("ok", False),
            "canonical_artifacts": artifacts.get("ok", False),
            "release_integrity_report_present": bool(release.get("report")),
        }
        return {
            "ok": all(checks.values()),
            "checks": checks,
            "release_status": release.get("status", ""),
            "release_approved": release.get("release_approved", False),
            "freigabe": release.get("freigabe", ""),
        }

    def status(self) -> dict:
        if not self.config.get("configured", True):
            return {"version": self.VERSION, "active": False, "ok": False, "configured": False}
        stability = self.stability_check()
        drift = self.drift_detection()
        enforcement = self.enforcement_check()
        verification = self.verification_loop()
        monitor_status = self.monitor.run_full_analysis(write_reports=True)
        logger_status = self.event_logger.status()
        checks = {
            "stability": stability["ok"],
            "cgm": monitor_status["active"],
            "dde": drift["ok"],
            "cic": monitor_status["integrity"]["active"],
            "gel": logger_status["active"],
            "drift_detection": drift["ok"],
            "enforcement": enforcement["ok"],
            "verification_loop": verification["ok"],
            "logging": self.log_path.parent.exists() or (self.root / "31_reports" / "governance").exists(),
            "baseline_reference": monitor_status["baseline"]["ok"],
            "reports_generable": all(monitor_status.get("reports", {}).values()),
        }
        return {
            "version": self.VERSION,
            "governance_version": self.release_version,
            "active": True,
            "configured": True,
            "ok": all(checks.values()),
            "checks": checks,
            "stability": stability,
            "drift_detection": drift,
            "drift_free": drift["drift_free"],
            "drift_classification": drift["classification"],
            "enforcement": enforcement,
            "verification_loop": verification,
            "components": {
                "CGM": {"active": monitor_status["active"], "ok": monitor_status["ok"]},
                "DDE": {"active": drift["ok"], "classification": drift["classification"]},
                "CIC": monitor_status["integrity"],
                "GEL": logger_status,
            },
            "baseline": monitor_status["baseline"],
            "baseline_compliance_score": monitor_status["baseline_compliance_score"],
            "reports": monitor_status["reports"],
            "governance_log": self.log_path.relative_to(self.root).as_posix(),
            "mutation_policy": "read_only_classification; no_delete_no_auto_move; verified_change_only",
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            f"Continuous Governance System {self.VERSION}: "
            f"{'VERIFIZIERT' if status.get('ok') else 'NICHT VERIFIZIERT'}.\n"
            f"- Stabilitaet={status.get('checks', {}).get('stability', False)}, "
            f"Drift={status.get('checks', {}).get('drift_detection', False)}, "
            f"Enforcement={status.get('checks', {}).get('enforcement', False)}.\n"
            f"- Verification Loop={status.get('checks', {}).get('verification_loop', False)}, "
            f"Log={status.get('governance_log', '')}.\n"
            "- Phase 3 klassifiziert kontinuierlich und protokolliert; keine automatische Loeschung oder Migration."
        )
