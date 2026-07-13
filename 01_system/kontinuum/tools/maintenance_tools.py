# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path


class MaintenanceTools:
    DEFAULT_CONFIG = {
        "enabled": True,
        "execution_enabled": True,
        "cache_directory_names": ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage_cache", "htmlcov"],
        "cache_file_suffixes": [".pyc", ".pyo"],
        "obsolete_test_copy_names": ["Projekt_Kontinuum_Test", "Projekt_Kontinuum_Backup_Vor_Patch"],
        "obsolete_test_copies_keep": 0,
        "structure_report_names": ["dateiliste.txt", "dateiliste_versions.txt", "ordnerstruktur.txt", "projektstruktur.txt", "Projekt_Kontinuum_Struktur_2026.txt"],
        "structure_report_archive_after_days": 30,
        "protected_roots": ["02_versions", "03_memory", "04_knowledge", "07_models", "09_backups", "10_security", "22_project_chronicle", "32_data"],
        "valuable_artifact_categories": [
            "temporary_test_projects", "test_fixtures", "cam_test_manifests",
            "generated_verification_reports", "release_integrity_reports",
            "verification_logs", "migration_logs", "migration_reports",
            "architecture_reports", "audit_logs",
        ],
        "release_archive_requirements": [
            "tests_green", "status_green", "release_gate_green",
            "documentation_updated", "codex_release_confirmed",
        ],
        "valuable_artifact_action_before_release": "retain",
        "valuable_artifact_action_after_release": "archive",
        "valuable_artifact_deletion": "manual_only_after_explicit_review",
        "migration_artifact_archive_root": "02_versions/migration_artifacts",
        "migration_report_backup_root": "09_backups/migration_reports",
        "permanent_backup_patterns": ["*.zip", "auth_*", "security_*", "self_extension_*"],
        "functional_backup_review_after_days": 180,
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()
        self.config_path = self.project_root / "24_config" / "retention_policy.json"
        self.config = self._load_config()
        self.audit_path = self.project_root / "27_logs" / "maintenance_cleanup_audit.log"
        self.archive_root = self.project_root / "31_reports" / "archive"

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    def inspect(self) -> dict:
        candidates = []
        protected = set(self.config["protected_roots"])
        cache_names = set(self.config["cache_directory_names"])
        obsolete_names = set(self.config["obsolete_test_copy_names"])
        obsolete_paths = []
        for directory, directories, files in os.walk(self.project_root):
            current = Path(directory)
            relative = current.relative_to(self.project_root)
            if relative.parts and relative.parts[0] in protected:
                directories[:] = []
                continue
            kept_directories = []
            for name in directories:
                path = current / name
                child_relative = path.relative_to(self.project_root)
                if child_relative.parts and child_relative.parts[0] in protected:
                    continue
                if name in cache_names:
                    candidates.append(self._candidate(path, "delete", "cache", "Regenerierbares Cacheverzeichnis."))
                    continue
                if name in obsolete_names and child_relative.parts[:1] == ("17_tests",):
                    obsolete_paths.append(path)
                    continue
                kept_directories.append(name)
            directories[:] = kept_directories
            for name in files:
                path = current / name
                if path.suffix.casefold() in self.config["cache_file_suffixes"]:
                    candidates.append(self._candidate(path, "delete", "cache", "Regenerierbarer Python-Bytecode."))
                elif name in self.config["structure_report_names"]:
                    age = self._age_days(path)
                    if age >= int(self.config["structure_report_archive_after_days"]):
                        candidates.append(self._candidate(path, "archive", "structure_report", f"Strukturbericht ist {age} Tage alt."))

        keep_count = max(0, int(self.config.get("obsolete_test_copies_keep", 0)))
        obsolete_paths.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        for path in obsolete_paths[keep_count:]:
            candidates.append(
                self._candidate(
                    path,
                    "delete",
                    "obsolete_test_copy",
                    f"Nicht aktive eingebettete Testvollkopie; Aufbewahrungslimit: {keep_count}.",
                )
            )

        reviews = self._backup_reviews()
        executable = [row for row in candidates if not self._is_protected(Path(row["path"]))]
        bytes_total = sum(int(row["bytes"]) for row in executable)
        return {
            "ok": True,
            "mode": "inspection",
            "candidates": executable,
            "review_only": reviews,
            "candidate_count": len(executable),
            "candidate_bytes": bytes_total,
            "protected_roots": list(self.config["protected_roots"]),
            "message": f"Bereinigungsprüfung: {len(executable)} ausführbare Kandidaten, {len(reviews)} manuelle Backup-Hinweise.",
        }

    def execute(self) -> dict:
        if not self.config.get("execution_enabled", False):
            return {"ok": False, "message": "Bereinigungsausführung ist in der Aufbewahrungspolicy deaktiviert."}
        inspection = self.inspect()
        completed = []
        errors = []
        for candidate in sorted(inspection["candidates"], key=lambda row: len(row["path"]), reverse=True):
            path = Path(candidate["path"]).resolve()
            if not self._inside_root(path) or self._is_protected(path):
                errors.append({"path": str(path), "error": "Pfad ist geschützt oder außerhalb der Projektwurzel."})
                continue
            try:
                if candidate["action"] == "delete":
                    if path.is_dir():
                        shutil.rmtree(path)
                    elif path.exists():
                        path.unlink()
                elif candidate["action"] == "archive":
                    self.archive_root.mkdir(parents=True, exist_ok=True)
                    destination = self.archive_root / path.name
                    if destination.exists():
                        destination = self.archive_root / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
                    shutil.move(str(path), str(destination))
                completed.append(candidate)
            except OSError as exc:
                errors.append({"path": str(path), "error": str(exc)})
        result = {
            "ok": not errors,
            "mode": "execution",
            "completed": completed,
            "errors": errors,
            "completed_count": len(completed),
            "review_only": inspection["review_only"],
            "message": f"Bereinigung ausgeführt: {len(completed)} Aktionen, {len(errors)} Fehler. Backups wurden nicht automatisch gelöscht.",
        }
        self._audit(result)
        return result

    def status(self) -> dict:
        return {
            "enabled": bool(self.config.get("enabled")),
            "execution_enabled": bool(self.config.get("execution_enabled")),
            "policy": str(self.config_path),
            "valuable_artifacts": {
                "before_release": self.config["valuable_artifact_action_before_release"],
                "after_release": self.config["valuable_artifact_action_after_release"],
                "deletion": self.config["valuable_artifact_deletion"],
                "release_requirements": list(self.config["release_archive_requirements"]),
            },
            "message": (
                "Sicherer Wartungsmodus aktiv: wertvolle Entwicklungs-, Migrations-, "
                "Release-, Architektur- und Audit-Artefakte werden nie automatisch gelöscht. "
                "Nur reproduzierbare Caches/Testkopien sind löschbar; Berichte werden archiviert."
            ),
        }

    def _backup_reviews(self) -> list[dict]:
        reviews = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(self.config["functional_backup_review_after_days"]))
        backup_root = self.project_root / "09_backups"
        if not backup_root.is_dir():
            return reviews
        for path in backup_root.iterdir():
            if path.suffix.casefold() == ".zip" or any(path.match(pattern) for pattern in self.config["permanent_backup_patterns"]):
                continue
            modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            if modified < cutoff:
                reviews.append(self._candidate(path, "review_only", "functional_backup", "Altes Funktionsbackup; nur manuell entscheiden."))
        return reviews

    def _candidate(self, path: Path, action: str, category: str, reason: str) -> dict:
        return {
            "path": str(path.resolve()),
            "relative_path": str(path.resolve().relative_to(self.project_root)),
            "action": action,
            "category": category,
            "reason": reason,
            "bytes": self._size(path),
        }

    def _is_protected(self, path: Path) -> bool:
        relative = path.resolve().relative_to(self.project_root)
        return bool(relative.parts and relative.parts[0] in set(self.config["protected_roots"]))

    def _inside_root(self, path: Path) -> bool:
        return path == self.project_root or self.project_root in path.parents

    @staticmethod
    def _size(path: Path) -> int:
        if path.is_file():
            return path.stat().st_size
        return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())

    @staticmethod
    def _age_days(path: Path) -> int:
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        return max(0, (datetime.now(timezone.utc) - modified).days)

    def _audit(self, result: dict) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"created_at": datetime.now(timezone.utc).isoformat(), **result}
        with self.audit_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
