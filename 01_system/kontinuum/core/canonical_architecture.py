# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import ast
import json
import sqlite3
from pathlib import Path

from .canonical_database import CanonicalDatabaseManager


class CanonicalArchitectureManager:
    """Read-only verifier for Kontinuum's canonical architecture."""

    VERSION = "1.2"
    LAYERS = ("foundation", "canonical", "operational", "learning")

    def __init__(
        self,
        project_root: str | Path,
        storage=None,
        release_version: str = "34.1",
        strict_config: bool = True,
    ):
        self.root = Path(project_root).resolve()
        self.storage = storage
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.config_path = self.root / "24_config" / f"canonical_architecture_{token}.json"
        self.strict_config = strict_config
        self.config = self._load_config()

    def _load_config(self) -> dict:
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            if not self.strict_config:
                return {"version": self.release_version, "configured": False}
            raise RuntimeError(f"CAM-Konfiguration fehlt oder ist ungueltig: {self.config_path}") from exc
        if value.get("version") != self.release_version:
            raise RuntimeError("CAM-Konfiguration gehoert nicht zur aktiven Version.")
        return value

    def _database_path(self) -> Path:
        if self.storage is not None:
            return Path(self.storage.database)
        return self.root / self.config.get("database", "32_data/kontinuum.db")

    def project_structure_check(self) -> dict:
        documents = self.root / "14_documents"
        active = sorted(path.name for path in documents.glob("PROJEKTSTRUKTUR_*.md") if path.is_file())
        expected = self.config["canonical_project_structure"]
        duplicates = [name for name in active if name != Path(expected).name]
        return {
            "ok": active == [Path(expected).name] and (self.root / expected).is_file(),
            "expected": expected,
            "active": active,
            "active_count": len(active),
            "duplicates": duplicates,
            "warning": "Mehrere aktive Projektstrukturen erkannt." if len(active) > 1 else "",
        }

    def archive_check(self) -> dict:
        archive = self.root / self.config["project_structure_archive"]
        expected = sorted(self.config.get("historical_project_structures", []))
        present = sorted(path.name for path in archive.glob("PROJEKTSTRUKTUR_*.md")) if archive.is_dir() else []
        missing = [name for name in expected if name not in present]
        return {
            "ok": archive.is_dir() and not missing,
            "path": self.config["project_structure_archive"],
            "expected": len(expected),
            "present": len(present),
            "missing": missing,
        }

    def path_check(self, key: str) -> dict:
        configured = self.config.get(key, [])
        missing = [relative for relative in configured if not (self.root / relative).exists()]
        return {"ok": not missing, "checked": len(configured), "missing": missing}

    def main_archive_roots_check(self) -> dict:
        configured = self.config.get("active_main_archive_roots", [])
        missing = [relative for relative in configured if not (self.root / relative).is_dir()]
        invalid = [relative for relative in configured if Path(relative).name != "archive"]
        return {
            "ok": not missing and not invalid,
            "checked": len(configured),
            "missing": missing,
            "invalid": invalid,
            "policy": "each_active_main_folder_has_archive_subfolder",
        }

    def api_check(self) -> dict:
        missing: list[dict] = []
        checked = 0
        discovered: set[str] = set()
        for specification in self.config.get("apis", []):
            relative = specification["path"]
            path = self.root / relative
            if not path.is_file():
                missing.append({"path": relative, "symbols": specification.get("symbols", [])})
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            except (OSError, SyntaxError) as exc:
                missing.append({"path": relative, "error": str(exc)})
                continue
            symbols = {
                node.name
                for node in tree.body
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            }
            required = specification.get("symbols", [])
            discovered.update(symbol for symbol in required if symbol in symbols)
            absent = [symbol for symbol in required if symbol not in symbols]
            checked += len(required)
            if absent:
                missing.append({"path": relative, "symbols": absent})
        registry = self.config.get("api_registry", [])
        unregistered = [symbol for symbol in registry if symbol not in discovered]
        return {
            "ok": not missing and not unregistered,
            "checked_symbols": checked,
            "registry": registry,
            "unregistered": unregistered,
            "missing": missing,
        }

    def database_schema_check(self) -> dict:
        try:
            return CanonicalDatabaseManager(
                self.root,
                storage=self.storage,
                release_version=self.release_version,
                strict_config=self.strict_config,
            ).status()
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}

    def artifact_lifecycle_check(self) -> dict:
        policy = self.config.get("artifact_lifecycle", {})
        required_values = {
            "valuable_artifacts": "retain_until_release_then_archive",
            "audit_and_migration_records": "never_auto_delete",
        }
        required_paths = {
            "policy": policy.get("policy", ""),
            "documentation": policy.get("documentation", ""),
            "migration_archive": policy.get("migration_archive", ""),
            "migration_report_backup": policy.get("migration_report_backup", ""),
        }
        missing = [
            relative
            for relative in required_paths.values()
            if not relative or not (self.root / relative).exists()
        ]
        invalid_values = {
            key: {"expected": expected, "actual": policy.get(key)}
            for key, expected in required_values.items()
            if policy.get(key) != expected
        }
        evidence_root = self.root / policy.get("signed_evidence_archive", "")
        required_evidence = policy.get(
            "required_signed_evidence",
            ["baseline.json", "audit_snapshot.json", "release_gate.json"],
        )
        evidence_missing = []
        evidence_unsigned = []
        for name in required_evidence:
            path = evidence_root / name
            if not path.is_file():
                evidence_missing.append(name)
                continue
            try:
                document = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError):
                evidence_unsigned.append(name)
                continue
            if not document.get("proof_hash"):
                evidence_unsigned.append(name)
        return {
            "ok": not missing and not invalid_values and not evidence_missing and not evidence_unsigned,
            "policy_version": policy.get("version", ""),
            "paths": required_paths,
            "missing": missing,
            "invalid_values": invalid_values,
            "signed_evidence_archive": policy.get("signed_evidence_archive", ""),
            "evidence_missing": evidence_missing,
            "evidence_unsigned": evidence_unsigned,
            "automatic_deletion": False,
            "archive_instead_of_delete": True,
            "release_requirements": policy.get("release_requirements", []),
        }

    def canonical_active_directory_check(self) -> dict:
        policy = self.config.get("canonical_active_directory_policy", {})
        required_values = {
            "foundation_rule": "FND-ID-049",
            "active_area_policy": "canonical_only",
            "historical_artifact_policy": "archive_only",
            "replacement_action": "move_previous_version_to_archive",
            "post_move_audit": "required",
            "monitoring_authority": "CAM_OR_ORCHESTRATOR_CORE",
        }
        invalid_values = {
            key: {"expected": expected, "actual": policy.get(key)}
            for key, expected in required_values.items()
            if policy.get(key) != expected
        }
        archive_roots = policy.get("required_archive_roots", [])
        missing_archives = [
            relative
            for relative in archive_roots
            if not (self.root / relative).is_dir()
        ]
        required_reference_scopes = {
            "documentation",
            "canonical_manifests",
            "cam_registrations",
            "architecture_models",
            "handbooks",
            "project_chronicle",
            "release_files",
            "configuration",
            "required_paths",
            "registry_entries",
            "scripts",
            "internal_references",
        }
        reference_scopes = set(policy.get("reference_check_scopes", []))
        missing_reference_scopes = sorted(required_reference_scopes - reference_scopes)
        required_audit_checks = {
            "no_outdated_files_in_active_area",
            "all_references_valid",
            "no_duplicate_active_versions",
            "no_orphan_paths",
            "manifest_filesystem_consistency",
        }
        audit_checks = set(policy.get("audit_checks", []))
        missing_audit_checks = sorted(required_audit_checks - audit_checks)
        return {
            "ok": (
                not invalid_values
                and not missing_archives
                and not missing_reference_scopes
                and not missing_audit_checks
            ),
            "policy_version": policy.get("version", ""),
            "foundation_rule": policy.get("foundation_rule", ""),
            "invalid_values": invalid_values,
            "required_archive_roots": len(archive_roots),
            "missing_archives": missing_archives,
            "missing_reference_scopes": missing_reference_scopes,
            "missing_audit_checks": missing_audit_checks,
            "active_area_policy": policy.get("active_area_policy", ""),
            "historical_artifact_policy": policy.get("historical_artifact_policy", ""),
            "monitoring_authority": policy.get("monitoring_authority", ""),
        }

    def canonical_change_policy_check(self) -> dict:
        policy = self.config.get("canonical_change_policy", {})
        required_values = {
            "foundation_rule": "FND-ID-050",
            "controlled_update": "required_after_pre_audit_and_governance_review",
            "cadp_link": "required_when_file_replaced",
            "documentation_sync": "required",
            "release_integrity_gate": "required_or_documented",
            "canonical_acceptance": "all_checks_completed_or_justified",
            "monitoring_authority": "CAM_OR_ORCHESTRATOR_CORE",
        }
        invalid_values = {
            key: {"expected": expected, "actual": policy.get(key)}
            for key, expected in required_values.items()
            if policy.get(key) != expected
        }
        required_flow = [
            "Change Proposal",
            "Pre-Audit",
            "Governance Review",
            "Controlled Canonical Update",
            "CADP Archive / Path Sync",
            "Documentation Sync",
            "Release Integrity Gate",
            "Canonical Acceptance",
        ]
        flow = policy.get("change_flow", [])
        flow_ok = flow == required_flow
        required_proposal_fields = {
            "affected_file",
            "reason",
            "goal",
            "architecture_component",
            "expected_impact",
            "required_follow_up_checks",
        }
        proposal_fields = set(policy.get("proposal_required_fields", []))
        missing_proposal_fields = sorted(required_proposal_fields - proposal_fields)
        required_pre_audit_checks = {
            "no_invalid_paths",
            "no_conflicting_architecture_terms",
            "no_duplicate_active_canonical_files",
            "no_open_legacy_references",
            "cadp_1_0_not_violated",
            "foundation_rules_not_violated",
        }
        pre_audit_checks = set(policy.get("pre_audit_checks", []))
        missing_pre_audit_checks = sorted(required_pre_audit_checks - pre_audit_checks)
        required_governance_checks = {
            "foundation_compatible",
            "canonical_architecture_compatible",
            "no_policy_violation",
            "no_uncontrolled_drift",
            "documentation_and_manifest_impact_checked",
        }
        governance_checks = set(policy.get("governance_review_checks", []))
        missing_governance_checks = sorted(required_governance_checks - governance_checks)
        return {
            "ok": (
                not invalid_values
                and flow_ok
                and not missing_proposal_fields
                and not missing_pre_audit_checks
                and not missing_governance_checks
            ),
            "policy_version": policy.get("version", ""),
            "foundation_rule": policy.get("foundation_rule", ""),
            "invalid_values": invalid_values,
            "flow_ok": flow_ok,
            "missing_proposal_fields": missing_proposal_fields,
            "missing_pre_audit_checks": missing_pre_audit_checks,
            "missing_governance_checks": missing_governance_checks,
            "controlled_update": policy.get("controlled_update", ""),
            "cadp_link": policy.get("cadp_link", ""),
            "release_integrity_gate": policy.get("release_integrity_gate", ""),
            "monitoring_authority": policy.get("monitoring_authority", ""),
        }
    def layer_status(self) -> dict:
        result = {}
        configured = self.config.get("layers", {})
        for layer in self.LAYERS:
            components = configured.get(layer, [])
            missing = [
                component["path"]
                for component in components
                if component.get("path") and not (self.root / component["path"]).exists()
            ]
            result[layer] = {
                "ok": not missing and bool(components),
                "components": len(components),
                "missing": missing,
                "change_policy": self.config.get("change_policies", {}).get(layer, ""),
            }
        return result

    def status(self) -> dict:
        if not self.config.get("configured", True):
            return {
                "version": self.VERSION,
                "architecture_version": self.release_version,
                "active": False,
                "ok": False,
                "configured": False,
                "checks": {},
                "mutation_policy": "read_only_verification; controlled_migration_only",
            }
        project_structure = self.project_structure_check()
        archive = self.archive_check()
        folders = self.path_check("required_folders")
        main_archives = self.main_archive_roots_check()
        entrypoints = self.path_check("entrypoints")
        registry = self.path_check("registries")
        apis = self.api_check()
        database = self.database_schema_check()
        artifact_lifecycle = self.artifact_lifecycle_check()
        canonical_active_directory = self.canonical_active_directory_check()
        canonical_change_policy = self.canonical_change_policy_check()
        layers = self.layer_status()
        checks = {
            "project_structure": project_structure["ok"],
            "historical_archive": archive["ok"],
            "folders": folders["ok"],
            "main_archives": main_archives["ok"],
            "entrypoints": entrypoints["ok"],
            "registries": registry["ok"],
            "apis": apis["ok"],
            "database_schema": database["ok"],
            "artifact_lifecycle": artifact_lifecycle["ok"],
            "canonical_active_directory": canonical_active_directory["ok"],
            "canonical_change_policy": canonical_change_policy["ok"],
            "layers": all(item["ok"] for item in layers.values()),
        }
        return {
            "version": self.VERSION,
            "architecture_version": self.release_version,
            "active": True,
            "ok": all(checks.values()),
            "checks": checks,
            "project_structure": project_structure,
            "archive": archive,
            "folders": folders,
            "main_archives": main_archives,
            "entrypoints": entrypoints,
            "registries": registry,
            "apis": apis,
            "database_schema": database,
            "artifact_lifecycle": artifact_lifecycle,
            "canonical_active_directory": canonical_active_directory,
            "canonical_change_policy": canonical_change_policy,
            "layers": layers,
            "mutation_policy": "read_only_verification; controlled_migration_only",
        }

    def format_status(self) -> str:
        status = self.status()
        structure = status["project_structure"]
        layers = status["layers"]
        return (
            f"Canonical Architecture Manager {self.VERSION}: "
            f"{'VERIFIZIERT' if status['ok'] else 'NICHT VERIFIZIERT'}.\n"
            f"- Kanonische Projektstruktur: {structure['active_count']} aktiv; "
            f"erwartet {structure['expected']}.\n"
            f"- Ebenen: Foundation={layers['foundation']['ok']}, Canonical={layers['canonical']['ok']}, "
            f"Operational={layers['operational']['ok']}, Learning={layers['learning']['ok']}.\n"
            f"- APIs={status['apis']['ok']}, Startpunkte={status['entrypoints']['ok']}, "
            f"Ordner={status['folders']['ok']}, Archive={status['main_archives']['ok']}, Canonical Database Manager="
            f"{status['database_schema']['ok']}.\n"
            f"- Artifact Lifecycle Policy={status['artifact_lifecycle']['ok']}; "
            "wertvolle Artefakte werden archiviert und nie automatisch geloescht.\n"
            f"- CADP={status['canonical_active_directory']['ok']}; aktive Ordner enthalten nur kanonische Dateien, "
            "historische Artefakte gehoeren in archive-Strukturen.\n"
            f"- CCP={status['canonical_change_policy']['ok']}; kanonische Aenderungen folgen Proposal, "
            "Pre-Audit, Governance Review und Release Integrity Gate.\n"
            "- Aenderungen erfolgen ausschliesslich ueber kontrollierte Migrationen."
        )
