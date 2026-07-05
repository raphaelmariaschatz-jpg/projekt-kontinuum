from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .foundation_2_2 import FOUNDATION_2_2_RULES, FoundationMigrationManager, ImprovementFoundation
from .canonical_architecture import CanonicalArchitectureManager
from .canonical_database import CanonicalDatabaseManager
from .canonical_api_registry import CanonicalAPIRegistryManager
from .canonical_artifacts import CanonicalArtifactManager
from .continuous_canonical_engine import ContinuousCanonicalEngine


class ReleaseIntegrityFramework:
    """Creates and verifies the complete evidence chain for a release."""

    VERSION = "1.0"

    def __init__(self, project_root: str | Path, release_version: str = "34.1"):
        self.root = Path(project_root).resolve()
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.config_path = self.root / "24_config" / f"release_integrity_{token}.json"
        self.config = self._load_config()
        self.report_root = self.root / "31_reports" / "release_integrity" / release_version
        self.backup_root = self.root / "09_backups" / "release_integrity"
        self.database = self.root / "32_data" / "kontinuum.db"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _digest_bytes(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    @classmethod
    def _digest_json(cls, value: dict | list) -> str:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return cls._digest_bytes(raw.encode("utf-8"))

    @classmethod
    def verify_signed_document(cls, document: dict) -> bool:
        payload = {key: value for key, value in document.items() if key != "proof_hash"}
        return bool(document.get("proof_hash")) and document["proof_hash"] == cls._digest_json(payload)

    def _load_config(self) -> dict:
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Release-Integrity-Konfiguration fehlt oder ist ungültig: {self.config_path}") from exc
        if value.get("version") != self.release_version:
            raise RuntimeError("Release-Integrity-Konfiguration gehört nicht zur aktiven Version.")
        return value

    def _write_signed(self, path: Path, payload: dict) -> dict:
        document = {**payload, "proof_hash": self._digest_json(payload)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return document

    def _relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def _file_hash(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def active_files(self) -> list[Path]:
        files: set[Path] = set()
        for relative in self.config.get("active_roots", []):
            root = self.root / relative
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.casefold() in {".py", ".json", ".bat", ".md"}:
                    if "__pycache__" not in path.parts:
                        files.add(path.resolve())
        for pattern in self.config.get("active_test_patterns", ["17_tests/test_*.py"]):
            files.update(path.resolve() for path in self.root.glob(pattern) if path.is_file())
        for relative in self.config.get("required_paths", []):
            path = self.root / relative
            if path.is_file():
                files.add(path.resolve())
        return sorted(files, key=lambda path: self._relative(path).casefold())

    def required_paths_check(self) -> dict:
        missing = [relative for relative in self.config.get("required_paths", []) if not (self.root / relative).is_file()]
        return {"ok": not missing, "missing": missing, "checked": len(self.config.get("required_paths", []))}

    def foundation_core_check(self) -> dict:
        rules = {rule.rule_id: rule for rule in FOUNDATION_2_2_RULES}
        rule = rules.get("FND-ID-048")
        cadp_rule = rules.get("FND-ID-049")
        ccp_rule = rules.get("FND-ID-050")
        required_paths = self.config.get("foundation_required_paths", [])
        missing = [relative for relative in required_paths if not (self.root / relative).is_file()]
        required_foundation_rules = set(self.config.get("required_foundation_rules", ["FND-ID-048"]))
        missing_foundation_rules = sorted(rule_id for rule_id in required_foundation_rules if rule_id not in rules)
        checks = {
            "rule_present": bool(rule),
            "rule_class": bool(rule and rule.foundation_class == "improvement"),
            "rule_text": bool(rule and rule.content == "Versuche es beim naechsten Mal immer besser zu machen."),
            "highest_protection": bool(rule and rule.protection_level == "highest"),
            "cadp_rule_present": bool(cadp_rule),
            "cadp_rule_class": bool(cadp_rule and cadp_rule.foundation_class == "canonical_active_directory"),
            "cadp_highest_protection": bool(cadp_rule and cadp_rule.protection_level == "highest"),
            "ccp_rule_present": bool(ccp_rule),
            "ccp_rule_class": bool(ccp_rule and ccp_rule.foundation_class == "canonical_change_policy"),
            "ccp_highest_protection": bool(ccp_rule and ccp_rule.protection_level == "highest"),
            "required_foundation_rules": not missing_foundation_rules,
            "improvement_class": ImprovementFoundation.RULE_ID == "FND-ID-048",
            "foundation_version": ImprovementFoundation.VERSION == "2.2",
            "migration_manager": FoundationMigrationManager.MIGRATION_ID == "foundation-2.2-fnd-id-048",
            "compatibility_path": (
                FoundationMigrationManager.COMPATIBILITY_MIGRATION_ID == "foundation-2.1-fnd-id-048"
            ),
            "required_paths": not missing,
        }
        return {
            "ok": all(checks.values()),
            "rule_id": "FND-ID-048",
            "cadp_rule_id": "FND-ID-049",
            "ccp_rule_id": "FND-ID-050",
            "checks": checks,
            "missing": missing,
            "missing_foundation_rules": missing_foundation_rules,
        }

    def canonical_architecture_check(self) -> dict:
        try:
            status = CanonicalArchitectureManager(
                self.root,
                release_version=self.release_version,
                strict_config=True,
            ).status()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}
        return status

    def canonical_database_check(self) -> dict:
        try:
            return CanonicalDatabaseManager(
                self.root,
                release_version=self.release_version,
                strict_config=True,
            ).status()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

    def canonical_api_registry_check(self) -> dict:
        try:
            return CanonicalAPIRegistryManager(
                self.root,
                release_version=self.release_version,
                strict_config=True,
            ).status()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

    def canonical_artifacts_check(self) -> dict:
        try:
            return CanonicalArtifactManager(
                self.root,
                release_version=self.release_version,
                strict_config=True,
            ).status()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

    def continuous_canonical_engine_check(self) -> dict:
        try:
            engine = ContinuousCanonicalEngine(
                self.root,
                release_version=self.release_version,
                strict_config=True,
            )
            status = engine.status()
            gate = status.get("gate", {})
            return {
                "ok": gate.get("ok", False),
                "active": status.get("active", False),
                "mode": status.get("mode", ""),
                "event_bus": status.get("event_bus", {}),
                "open_hooks": len(status.get("open_hooks", [])),
                "blocking_findings": status.get("blocking_findings", []),
                "last_gate_decision": status.get("last_gate_decision", "BLOCKED"),
                "gate": gate,
            }
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

    def create_baseline(self) -> dict:
        files = {
            self._relative(path): {"sha256": self._file_hash(path), "bytes": path.stat().st_size}
            for path in self.active_files()
        }
        payload = {
            "kind": "release.integrity.baseline",
            "framework_version": self.VERSION,
            "release_version": self.release_version,
            "created_at": self._now(),
            "files": files,
            "file_count": len(files),
        }
        return self._write_signed(self.report_root / "baseline.json", payload)

    def _database_audit(self, database: Path | None = None) -> dict:
        target = database or self.database
        if not target.is_file():
            return {"ok": False, "path": str(target), "error": "Datenbank fehlt."}
        uri = f"file:{target.resolve().as_posix()}?mode=ro"
        try:
            with sqlite3.connect(uri, uri=True) as connection:
                integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
                tables = [row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )]
                counts = {table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]) for table in tables}
                triggers = int(connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'"
                ).fetchone()[0])
        except sqlite3.Error as exc:
            return {"ok": False, "path": str(target), "error": str(exc)}
        return {
            "ok": integrity == "ok",
            "path": str(target),
            "integrity_check": integrity,
            "tables": counts,
            "trigger_count": triggers,
            "bytes": target.stat().st_size,
            "sha256": self._file_hash(target),
        }

    def create_audit_snapshot(self, baseline: dict) -> dict:
        required = self.required_paths_check()
        database = self._database_audit()
        payload = {
            "kind": "release.integrity.audit_snapshot",
            "framework_version": self.VERSION,
            "release_version": self.release_version,
            "created_at": self._now(),
            "baseline_hash": baseline.get("proof_hash", ""),
            "baseline_valid": self.verify_signed_document(baseline),
            "required_paths": required,
            "database": database,
            "ok": self.verify_signed_document(baseline) and required["ok"] and database["ok"],
        }
        return self._write_signed(self.report_root / "audit_snapshot.json", payload)

    def create_backup(self, baseline: dict, audit: dict) -> dict:
        self.backup_root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.backup_root / f"Kontinuum_{self.release_version.replace('.', '_')}_{stamp}.zip"
        files = {relative: data["sha256"] for relative, data in baseline.get("files", {}).items()}
        manifest = {
            "kind": "release.integrity.backup_manifest",
            "release_version": self.release_version,
            "created_at": self._now(),
            "baseline_hash": baseline.get("proof_hash", ""),
            "audit_hash": audit.get("proof_hash", ""),
            "files": files,
        }
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
            database_copy = Path(temporary) / "kontinuum.db"
            if self.database.is_file():
                with sqlite3.connect(self.database) as source, sqlite3.connect(database_copy) as destination:
                    source.backup(destination)
                manifest["database"] = {
                    "archive_path": "database/kontinuum.db",
                    "sha256": self._file_hash(database_copy),
                }
            manifest["manifest_hash"] = self._digest_json(manifest)
            with zipfile.ZipFile(backup, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                for relative in files:
                    archive.write(self.root / relative, f"project/{relative}")
                if database_copy.is_file():
                    archive.write(database_copy, "database/kontinuum.db")
                archive.writestr("release_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        return {
            "ok": backup.is_file(),
            "path": str(backup),
            "sha256": self._file_hash(backup),
            "bytes": backup.stat().st_size,
            "manifest_hash": manifest["manifest_hash"],
        }

    def verify_backup(self, backup_result: dict) -> dict:
        path = Path(backup_result.get("path", ""))
        issues = []
        if not path.is_file():
            return {"ok": False, "issues": ["Backup-Datei fehlt."]}
        try:
            with zipfile.ZipFile(path, "r") as archive:
                bad = archive.testzip()
                if bad:
                    issues.append(f"Beschädigter ZIP-Eintrag: {bad}")
                manifest = json.loads(archive.read("release_manifest.json"))
                expected_hash = manifest.pop("manifest_hash", "")
                if expected_hash != self._digest_json(manifest):
                    issues.append("Backup-Manifest-Hash ist ungültig.")
                for relative, expected in manifest.get("files", {}).items():
                    actual = self._digest_bytes(archive.read(f"project/{relative}"))
                    if actual != expected:
                        issues.append(f"Datei-Hash im Backup verletzt: {relative}")
                database = manifest.get("database") or {}
                if database:
                    actual = self._digest_bytes(archive.read(database["archive_path"]))
                    if actual != database.get("sha256"):
                        issues.append("Datenbank-Hash im Backup verletzt.")
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            issues.append(str(exc))
        return {"ok": not issues, "issues": issues, "path": str(path)}

    def rollback_probe(self, backup_result: dict) -> dict:
        path = Path(backup_result.get("path", ""))
        issues = []
        checked_files = 0
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
                target = Path(temporary)
                with zipfile.ZipFile(path, "r") as archive:
                    archive.extractall(target)
                manifest = json.loads((target / "release_manifest.json").read_text(encoding="utf-8"))
                for relative, expected in manifest.get("files", {}).items():
                    restored = target / "project" / relative
                    if not restored.is_file() or self._file_hash(restored) != expected:
                        issues.append(f"Wiederherstellung fehlgeschlagen: {relative}")
                    checked_files += 1
                database = manifest.get("database") or {}
                database_audit = self._database_audit(target / database.get("archive_path", "missing"))
                if database and not database_audit["ok"]:
                    issues.append("Wiederhergestellte Datenbank ist nicht integer.")
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            database_audit = {"ok": False, "error": str(exc)}
            issues.append(str(exc))
        return {
            "ok": not issues,
            "issues": issues,
            "checked_files": checked_files,
            "database": database_audit,
            "mode": "temporary_restore_no_production_write",
        }

    def legacy_scan(self) -> dict:
        forbidden = tuple(self.config.get("forbidden_active_versions", []))
        allowed = set(self.config.get("allowed_legacy_paths", []))
        historical_roots = tuple(
            str(Path(relative).as_posix()).rstrip("/") + "/"
            for relative in self.config.get("historical_artifact_roots", [])
        )
        findings = []
        scanned = 0
        for path in self.active_files():
            relative = self._relative(path)
            if relative in allowed or relative.startswith(historical_roots):
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError):
                continue
            scanned += 1
            for version in forbidden:
                for line_number, line in enumerate(text.splitlines(), 1):
                    if version in line or version.replace(".", "_") in line:
                        findings.append({"path": relative, "line": line_number, "version": version, "text": line.strip()[:240]})
        return {
            "ok": not findings,
            "scanned_files": scanned,
            "findings": findings,
            "forbidden_versions": list(forbidden),
            "historical_artifact_roots": list(self.config.get("historical_artifact_roots", [])),
        }

    def path_consistency(self) -> dict:
        required = self.required_paths_check()
        version_file = self.root / "01_system" / "kontinuum" / "version.py"
        version_ok = f'APP_VERSION = "{self.release_version}"' in version_file.read_text(encoding="utf-8")
        active_entry = self.root / "22_project_chronicle" / "EINSTIEGSPUNKTE_NAECHSTE_SITZUNG.md"
        entry_ok = active_entry.is_file() and self.release_version in active_entry.read_text(encoding="utf-8-sig")
        chronicle_paths = self.config.get("chronicle_paths", [])
        chronicle_ok = all((self.root / relative).is_file() for relative in chronicle_paths)
        starter_paths = self.config.get("starter_paths", [])
        starters_ok = all((self.root / relative).is_file() for relative in starter_paths)
        gui_paths = self.config.get("gui_paths", [])
        gui_ok = all((self.root / relative).is_file() for relative in gui_paths)
        canonical_start = self._canonical_start_check()
        return {
            "ok": (
                required["ok"]
                and version_ok
                and entry_ok
                and chronicle_ok
                and starters_ok
                and gui_ok
                and canonical_start["ok"]
            ),
            "required_paths": required,
            "version_ok": version_ok,
            "entrypoint_ok": entry_ok,
            "starters_ok": starters_ok,
            "canonical_start": canonical_start,
            "gui_ok": gui_ok,
            "chronicle_migration_ok": chronicle_ok,
        }

    def _canonical_start_check(self) -> dict:
        configured = set(self.config.get("starter_paths", [])) | set(self.config.get("required_paths", []))
        if "START_KONTINUUM.bat" not in configured:
            return {"ok": True, "configured": False}
        path = self.root / "START_KONTINUUM.bat"
        if not path.is_file():
            return {"ok": False, "configured": True, "error": "START_KONTINUUM.bat fehlt."}
        text = path.read_text(encoding="utf-8-sig")
        checks = {
            "sets_pythonpath_to_01_system": 'set "PYTHONPATH=%KONTINUUM_ROOT%\\01_system"' in text,
            "starts_package_module": "-m kontinuum" in text,
            "does_not_start_main_py": "main.py" not in text,
            "does_not_start_01_system_module": "-m 01_system.kontinuum" not in text,
        }
        return {"ok": all(checks.values()), "configured": True, "path": "START_KONTINUUM.bat", "checks": checks}

    def run_tests(self) -> dict:
        pattern = self.config.get("test_pattern", "17_tests/test_*.py")
        tests = sorted((path for path in self.root.glob(pattern) if path.is_file()), key=lambda path: path.name.casefold())
        timeout = int(self.config.get("test_timeout_seconds", 420))
        environment = os.environ.copy()
        environment.update({
            "KONTINUUM_ROOT": str(self.root),
            "PYTHONPATH": str(self.root / "01_system"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
        })
        suite_started_at = self._now()
        results = []
        for path in tests:
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    [sys.executable, "-u", str(path)],
                    cwd=self.root,
                    env=environment,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                    check=False,
                )
                ok = completed.returncode == 0
                output = (completed.stdout + completed.stderr).strip()
                result = {"name": path.name, "ok": ok, "returncode": completed.returncode, "output": output[-4000:]}
            except subprocess.TimeoutExpired as exc:
                output = ((exc.stdout or "") + (exc.stderr or "")) if isinstance(exc.stdout, str) else ""
                result = {"name": path.name, "ok": False, "timeout": True, "returncode": 124, "output": output[-4000:]}
            result["duration_seconds"] = round(time.monotonic() - started, 3)
            results.append(result)
        failed = [result["name"] for result in results if not result["ok"]]
        return {
            "ok": not failed and bool(results),
            "count": len(results),
            "failed": failed,
            "tests": results,
            "timeout_seconds": timeout,
            "started_at": suite_started_at,
            "completed_at": self._now(),
        }

    def run(self, include_tests: bool = True) -> dict:
        self.report_root.mkdir(parents=True, exist_ok=True)
        baseline = self.create_baseline()
        audit = self.create_audit_snapshot(baseline)
        backup = self.create_backup(baseline, audit)
        backup_verification = self.verify_backup(backup)
        rollback = self.rollback_probe(backup)
        legacy = self.legacy_scan()
        paths = self.path_consistency()
        foundation_core = self.foundation_core_check()
        canonical_architecture = self.canonical_architecture_check()
        canonical_database = self.canonical_database_check()
        canonical_api_registry = self.canonical_api_registry_check()
        canonical_artifacts = self.canonical_artifacts_check()
        continuous_canonical_engine = self.continuous_canonical_engine_check()
        artifact_lifecycle = canonical_architecture.get("artifact_lifecycle", {})
        tests = self.run_tests() if include_tests else {
            "ok": False,
            "skipped": True,
            "reason": "Eine Release-Freigabe ist ohne vollständige Testsuite unzulässig.",
        }
        gates = {
            "baseline": self.verify_signed_document(baseline),
            "backup": backup.get("ok", False) and backup_verification.get("ok", False),
            "audit_snapshot": audit.get("ok", False) and self.verify_signed_document(audit),
            "rollback_test": rollback.get("ok", False),
            "legacy_scan": legacy.get("ok", False),
            "test_suite": tests.get("ok", False),
            "version_consistency": paths.get("version_ok", False) and paths.get("required_paths", {}).get("ok", False),
            "chronicle_migration": paths.get("chronicle_migration_ok", False),
            "entrypoints": (
                paths.get("entrypoint_ok", False)
                and paths.get("starters_ok", False)
                and paths.get("canonical_start", {}).get("ok", False)
                and paths.get("gui_ok", False)
            ),
            "foundation_core": foundation_core.get("ok", False),
            "canonical_architecture": canonical_architecture.get("ok", False),
            "canonical_database": canonical_database.get("ok", False),
            "canonical_api_registry": canonical_api_registry.get("ok", False),
            "canonical_artifacts": canonical_artifacts.get("ok", False),
            "continuous_canonical_engine": continuous_canonical_engine.get("ok", False),
            "artifact_lifecycle": artifact_lifecycle.get("ok", False),
        }
        verified = all(gates.values())
        payload = {
            "kind": "release.integrity.gate",
            "framework_version": self.VERSION,
            "release_version": self.release_version,
            "created_at": self._now(),
            "status": "VERIFIZIERT" if verified else "NICHT VERIFIZIERT",
            "release_approved": verified,
            "freigabe": "JA" if verified else "NEIN",
            "gates": gates,
            "evidence": {
                "baseline_hash": baseline.get("proof_hash", ""),
                "audit_hash": audit.get("proof_hash", ""),
                "backup": backup,
                "backup_verification": backup_verification,
                "rollback": rollback,
                "legacy_scan": legacy,
                "tests": tests,
                "path_consistency": paths,
                "foundation_core": foundation_core,
                "canonical_architecture": canonical_architecture,
                "canonical_database": canonical_database,
                "canonical_api_registry": canonical_api_registry,
                "canonical_artifacts": canonical_artifacts,
                "continuous_canonical_engine": continuous_canonical_engine,
                "artifact_lifecycle": artifact_lifecycle,
            },
        }
        return self._write_signed(self.report_root / "release_gate.json", payload)

    def status(self) -> dict:
        path = self.report_root / "release_gate.json"
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"version": self.VERSION, "status": "NICHT VERIFIZIERT", "release_approved": False, "report": str(path)}
        valid = self.verify_signed_document(report)
        approved = bool(valid and report.get("release_version") == self.release_version and report.get("release_approved"))
        return {
            "version": self.VERSION,
            "status": "VERIFIZIERT" if approved else "NICHT VERIFIZIERT",
            "release_approved": approved,
            "freigabe": "JA" if approved else "NEIN",
            "proof_valid": valid,
            "gates": report.get("gates", {}),
            "report": str(path),
        }
