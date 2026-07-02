from __future__ import annotations

import json
import hashlib
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.release_integrity import ReleaseIntegrityFramework
from kontinuum.version import APP_VERSION


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    project = Path(temporary)
    for relative in (
        "01_system/kontinuum",
        "02_versions/projektstrukturen",
        "02_versions/migration_artifacts/release_evidence",
        "09_backups/migration_reports",
        "14_documents",
        "17_tests",
        "22_project_chronicle",
        "24_config",
        "32_data",
    ):
        (project / relative).mkdir(parents=True, exist_ok=True)
    (project / "01_system/kontinuum/version.py").write_text('APP_VERSION = "34.1"\n', encoding="utf-8")
    (project / "START_KONTINUUM.bat").write_text(
        '@echo off\nset "KONTINUUM_ROOT=%~dp0"\nset "PYTHONPATH=%KONTINUUM_ROOT%\\01_system"\npython -m kontinuum %*\n',
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/core").mkdir()
    (project / "01_system/kontinuum/core/foundation_2_2.py").write_text(
        "# Foundation 2.2 fixture for required-path verification\n",
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/core/foundation_2_1.py").write_text(
        "# Foundation 2.1 compatibility fixture\n",
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/core/canonical_database.py").write_text(
        "class CanonicalDatabaseManager: pass\n",
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/core/canonical_api_registry.py").write_text(
        "class CanonicalAPIRegistryManager: pass\n",
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/core/canonical_artifacts.py").write_text(
        "class CanonicalArtifactManager: pass\n",
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/core/continuous_canonical_engine.py").write_text(
        "class ContinuousCanonicalEngine: pass\n",
        encoding="utf-8",
    )
    (project / "01_system/kontinuum/probe.py").write_text(
        "VALUE = 341\n\nclass FixtureAPI:\n    def status(self):\n        return {'ok': True}\n",
        encoding="utf-8",
    )
    (project / "17_tests/test_probe.py").write_text("assert 34 + 1 == 35\n", encoding="utf-8")
    (project / "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG.md").write_text(
        "Kontinuum 34.1", encoding="utf-8"
    )
    (project / "22_project_chronicle/RELEASE_34_1.md").write_text("Release 34.1", encoding="utf-8")
    (project / "14_documents/PROJEKTSTRUKTUR_34_1.md").write_text(
        "# Projektstruktur 34.1", encoding="utf-8"
    )
    (project / "14_documents/ARBEITSREGEL_ARTEFAKT_LIFECYCLE_34_1.md").write_text(
        "# Artifact Lifecycle Policy", encoding="utf-8"
    )
    (project / "24_config/retention_policy.json").write_text("{}", encoding="utf-8")
    for evidence_name in ("baseline.json", "audit_snapshot.json", "release_gate.json"):
        (project / "02_versions/migration_artifacts/release_evidence" / evidence_name).write_text(
            json.dumps({"proof_hash": "fixture-proof"}),
            encoding="utf-8",
        )
    canonical_config = {
        "version": "34.1",
        "canonical_project_structure": "14_documents/PROJEKTSTRUKTUR_34_1.md",
        "project_structure_archive": "02_versions/projektstrukturen",
        "historical_project_structures": [],
        "required_folders": ["01_system/kontinuum", "14_documents", "32_data"],
        "entrypoints": [],
        "registries": [],
        "apis": [],
        "database": "32_data/kontinuum.db",
        "required_tables": ["evidence"],
        "artifact_lifecycle": {
            "version": "CAM 1.1",
            "policy": "24_config/retention_policy.json",
            "documentation": "14_documents/ARBEITSREGEL_ARTEFAKT_LIFECYCLE_34_1.md",
            "migration_archive": "02_versions/migration_artifacts",
            "migration_report_backup": "09_backups/migration_reports",
            "signed_evidence_archive": "02_versions/migration_artifacts/release_evidence",
            "required_signed_evidence": ["baseline.json", "audit_snapshot.json", "release_gate.json"],
            "release_requirements": [
                "tests_green",
                "status_green",
                "release_gate_green",
                "documentation_updated",
                "codex_release_confirmed"
            ],
            "valuable_artifacts": "retain_until_release_then_archive",
            "audit_and_migration_records": "never_auto_delete"
        },
        "change_policies": {
            "foundation": "protected_migration_only",
            "canonical": "release_controlled_migration",
            "operational": "replaceable_with_contract_checks",
            "learning": "dynamic_with_provenance_and_audit"
        },
        "layers": {
            "foundation": [{"name": "Foundation", "path": "01_system/kontinuum/core/foundation_2_2.py"}],
            "canonical": [{"name": "Structure", "path": "14_documents/PROJEKTSTRUKTUR_34_1.md"}],
            "operational": [{"name": "Runtime", "path": "01_system/kontinuum/probe.py"}],
            "learning": [{"name": "Data", "path": "32_data"}]
        }
    }
    (project / "24_config/canonical_architecture_34_1.json").write_text(
        json.dumps(canonical_config), encoding="utf-8"
    )
    database_config = {
        "version": "34.1",
        "database": "32_data/kontinuum.db",
        "required_tables": ["evidence"],
        "table_contracts": {
            "evidence": {
                "id": {"type": "INTEGER", "primary_key": True},
                "value": {"type": "TEXT"}
            }
        },
        "required_indexes": [],
        "required_triggers": [],
        "required_fts": [],
        "data_domains": {"release": ["evidence"]}
    }
    (project / "24_config/canonical_database_34_1.json").write_text(
        json.dumps(database_config), encoding="utf-8"
    )
    api_registry_config = {
        "version": "34.1",
        "scope": "fixture_release_api",
        "apis": [
            {
                "api_uid": "KAPI-FIXTURE-000001",
                "api_id": "KAPI-FIXTURE",
                "canonical_name": "FixtureAPI",
                "symbol": "FixtureAPI",
                "introduced_in": "34.1",
                "deprecated_in": None,
                "supersedes": None,
                "creator": "Release Fixture",
                "canonical_hash": "",
                "contract_version": "1.0",
                "owner": "release_fixture",
                "responsibility": "Release-Integrity-Fixture-API.",
                "path": "01_system/kontinuum/probe.py",
                "kind": "class",
                "version": "34.1",
                "stability": "release_stable",
                "inputs": [],
                "outputs": {"type": "class_contract", "required_keys": []},
                "required_methods": ["status"],
                "dependencies": [],
                "foundation_relevance": "low",
                "security_class": "release_protected",
                "mutation_policy": "read_only",
                "test_coverage": ["17_tests/test_probe.py"],
                "change_policy": "release_controlled_migration"
            }
        ]
    }
    fixture_api = api_registry_config["apis"][0]
    fixture_payload = {key: value for key, value in fixture_api.items() if key != "canonical_hash"}
    fixture_api["canonical_hash"] = hashlib.sha256(
        json.dumps(fixture_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    (project / "24_config/canonical_api_registry_34_1.json").write_text(
        json.dumps(api_registry_config), encoding="utf-8"
    )
    artifact_config = {
        "version": "34.1",
        "scope": "fixture_artifacts",
        "lifecycle_policy": "24_config/retention_policy.json",
        "allowed_lifecycle_policies": ["release_controlled", "never_auto_delete"],
        "required_lifecycle_values": {
            "valuable_artifact_action_before_release": "retain",
            "valuable_artifact_action_after_release": "archive",
            "valuable_artifact_deletion": "manual_only_after_explicit_review",
            "migration_artifact_archive_root": "02_versions/migration_artifacts",
            "migration_report_backup_root": "09_backups/migration_reports"
        },
        "required_lifecycle_roots": ["02_versions/migration_artifacts", "09_backups/migration_reports"],
        "generated_cache_names": ["__pycache__"],
        "generated_cache_suffixes": [".pyc"],
        "cache_scan_roots": ["01_system"],
        "protected_cache_roots": [],
        "artifacts": [
            {
                "artifact_id": "ART-FIXTURE-001",
                "artifact_class": "release-critical",
                "path": "01_system/kontinuum/probe.py",
                "required": True,
                "expected_root": "01_system/kontinuum",
                "signed": False,
                "lifecycle_policy": "release_controlled"
            }
        ],
        "artifact_patterns": []
    }
    (project / "24_config/canonical_artifacts_34_1.json").write_text(
        json.dumps(artifact_config), encoding="utf-8"
    )
    cce_config = {
        "version": "34.1",
        "engine_version": "1.0",
        "active": True,
        "mode": "diagnostic_report_only",
        "logs": {
            "canonical_events": "31_reports/events/canonical_events.jsonl",
            "event_processing": "31_reports/events/event_processing_log.jsonl",
            "drift_events": "31_reports/drift/drift_events.jsonl",
            "governance_hooks": "31_reports/governance/governance_hooks.jsonl"
        },
        "event_schema": [
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
            "processing_state"
        ],
        "decision_classes": [
            "ACTIVE",
            "ARCHIVE_CANDIDATE",
            "REVIEW_REQUIRED",
            "CONSOLIDATION_SUGGESTED",
            "BLOCKED"
        ],
        "drift_classes": [
            "EXPECTED_DRIFT",
            "LOW_DRIFT",
            "MEDIUM_DRIFT",
            "HIGH_DRIFT",
            "BLOCKING_DRIFT"
        ],
        "release_gate": {"blocking_drift_classes": ["HIGH_DRIFT", "BLOCKING_DRIFT"]}
    }
    (project / "24_config/continuous_canonical_engine_34_1.json").write_text(
        json.dumps(cce_config), encoding="utf-8"
    )
    (project / "24_config/retention_policy.json").write_text(json.dumps({
        "valuable_artifact_action_before_release": "retain",
        "valuable_artifact_action_after_release": "archive",
        "valuable_artifact_deletion": "manual_only_after_explicit_review",
        "migration_artifact_archive_root": "02_versions/migration_artifacts",
        "migration_report_backup_root": "09_backups/migration_reports"
    }), encoding="utf-8")
    config = {
        "version": "34.1",
        "active_roots": ["01_system/kontinuum"],
        "active_test_patterns": ["17_tests/test_*.py"],
        "test_pattern": "17_tests/test_*.py",
        "test_timeout_seconds": 30,
        "forbidden_active_versions": ["34.0"],
        "allowed_legacy_paths": [],
        "historical_artifact_roots": ["02_versions/projektstrukturen"],
        "required_paths": [
            "START_KONTINUUM.bat",
            "01_system/kontinuum/core/canonical_database.py",
            "01_system/kontinuum/core/canonical_api_registry.py",
            "01_system/kontinuum/core/canonical_artifacts.py",
            "01_system/kontinuum/core/continuous_canonical_engine.py",
            "01_system/kontinuum/version.py",
            "24_config/canonical_api_registry_34_1.json",
            "24_config/canonical_artifacts_34_1.json",
            "24_config/continuous_canonical_engine_34_1.json",
            "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG.md",
            "22_project_chronicle/RELEASE_34_1.md"
        ],
        "foundation_required_paths": [
            "01_system/kontinuum/core/foundation_2_2.py",
            "01_system/kontinuum/core/foundation_2_1.py",
            "17_tests/test_probe.py"
        ],
        "chronicle_paths": [
            "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG.md",
            "22_project_chronicle/RELEASE_34_1.md"
        ],
        "starter_paths": ["START_KONTINUUM.bat"]
    }
    (project / "24_config/release_integrity_34_1.json").write_text(
        json.dumps(config), encoding="utf-8"
    )
    with sqlite3.connect(project / "32_data/kontinuum.db") as database:
        database.execute("CREATE TABLE evidence(id INTEGER PRIMARY KEY, value TEXT)")
        database.execute("INSERT INTO evidence(value) VALUES ('release-integrity')")

    framework = ReleaseIntegrityFramework(project, "34.1")
    report = framework.run(include_tests=True)
    assert report["release_approved"], report["gates"]
    assert report["status"] == "VERIFIZIERT"
    assert report["freigabe"] == "JA"
    assert all(report["gates"].values())
    assert report["gates"]["foundation_core"]
    assert report["gates"]["canonical_architecture"]
    assert report["gates"]["canonical_database"]
    assert report["gates"]["canonical_api_registry"]
    assert report["gates"]["canonical_artifacts"]
    assert report["gates"]["continuous_canonical_engine"]
    assert report["gates"]["artifact_lifecycle"]
    assert report["evidence"]["foundation_core"]["rule_id"] == "FND-ID-048"
    assert report["evidence"]["canonical_architecture"]["project_structure"]["active_count"] == 1
    assert report["evidence"]["canonical_api_registry"]["api_count"] == 1
    assert report["evidence"]["canonical_artifacts"]["artifact_count"] == 1
    assert report["evidence"]["continuous_canonical_engine"]["last_gate_decision"] == "PASS"
    assert report["evidence"]["path_consistency"]["canonical_start"]["ok"]
    assert framework.verify_signed_document(report)
    assert framework.status()["release_approved"]
    assert Path(report["evidence"]["backup"]["path"]).is_file()
    assert report["evidence"]["rollback"]["database"]["integrity_check"] == "ok"

    source = project / "01_system/kontinuum/probe.py"
    source.write_text('LEGACY = "34.0"\n', encoding="utf-8")
    assert not framework.legacy_scan()["ok"]
    source.write_text("VALUE = 341\n\nclass FixtureAPI:\n    def status(self):\n        return {'ok': True}\n", encoding="utf-8")

    unsigned = dict(report)
    unsigned["freigabe"] = "NEIN"
    assert not framework.verify_signed_document(unsigned)

print(f"Kontinuum {APP_VERSION} Release Integrity Framework tests passed")
