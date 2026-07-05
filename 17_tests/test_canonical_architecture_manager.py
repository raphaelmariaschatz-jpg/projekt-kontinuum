from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_architecture import CanonicalArchitectureManager


manager = CanonicalArchitectureManager(ROOT, release_version="34.1")
status = manager.status()
assert status["ok"], status
assert status["project_structure"]["active_count"] == 1
assert status["project_structure"]["active"] == ["PROJEKTSTRUKTUR_34_1.md"]
assert status["archive"]["present"] >= 19
assert all(status["checks"].values())
assert tuple(status["layers"]) == manager.LAYERS
foundation_names = [item["name"] for item in manager.config["layers"]["foundation"]]
canonical_names = [item["name"] for item in manager.config["layers"]["canonical"]]
operational_names = [item["name"] for item in manager.config["layers"]["operational"]]
learning_names = [item["name"] for item in manager.config["layers"]["learning"]]
assert {"Foundation Rules", "Creator Knowledge", "Moral Core", "Identity Core"} <= set(foundation_names)
assert {"Projektstruktur", "CAM", "Canonical Database Manager", "Agent Registry", "API Registry"} <= set(canonical_names)
assert {"Artefakt-Lifecycle-Policy", "Migration Artifacts"} <= set(canonical_names)
assert {"Capability Resolution Engine", "Capability Registry"} <= set(canonical_names)
assert {"Execution Planner", "Execution Plan Schema"} <= set(canonical_names)
assert {"Orchestrator Core", "Orchestrator Runtime Schema"} <= set(canonical_names)
assert {"Agenten", "GUI", "Connectoren", "Modelle", "Suchsystem"} <= set(operational_names)
assert {"Wissen", "Forschung", "Chronik", "Lernprojekte", "Wissensgraph"} <= set(learning_names)
assert status["apis"]["registry"] == manager.config["api_registry"]
assert "CapabilityResolutionEngine" in manager.config["api_registry"]
assert "ExecutionPlanner" in manager.config["api_registry"]
assert "OrchestratorCore" in manager.config["api_registry"]
assert "ExecutionTask" in manager.config["api_registry"]
assert "ExecutionResult" in manager.config["api_registry"]
assert "OrchestratorError" in manager.config["api_registry"]
assert "24_config/capability_registry_34_1.json" in manager.config["registries"]
assert "24_config/execution_plan_schema_34_1.json" in manager.config["registries"]
assert "24_config/orchestrator_runtime_schema_34_1.json" in manager.config["registries"]
assert not status["apis"]["unregistered"]
assert manager.config["artifact_lifecycle"]["valuable_artifacts"] == "retain_until_release_then_archive"
assert manager.config["artifact_lifecycle"]["audit_and_migration_records"] == "never_auto_delete"
assert status["artifact_lifecycle"]["ok"]
assert status["artifact_lifecycle"]["policy_version"] == "CAM 1.1"
assert len(status["artifact_lifecycle"]["release_requirements"]) == 5
assert not status["artifact_lifecycle"]["evidence_missing"]
assert not status["artifact_lifecycle"]["evidence_unsigned"]
assert status["canonical_active_directory"]["ok"]
assert status["canonical_active_directory"]["foundation_rule"] == "FND-ID-049"
assert status["canonical_active_directory"]["active_area_policy"] == "canonical_only"
assert status["canonical_active_directory"]["historical_artifact_policy"] == "archive_only"
assert not status["canonical_active_directory"]["missing_reference_scopes"]
assert not status["canonical_active_directory"]["missing_audit_checks"]
assert status["canonical_change_policy"]["ok"]
assert status["canonical_change_policy"]["foundation_rule"] == "FND-ID-050"
assert status["canonical_change_policy"]["flow_ok"]
assert not status["canonical_change_policy"]["missing_proposal_fields"]
assert not status["canonical_change_policy"]["missing_pre_audit_checks"]
assert not status["canonical_change_policy"]["missing_governance_checks"]
assert status["mutation_policy"] == "read_only_verification; controlled_migration_only"
assert status["database_schema"]["version"] == "1.2"
assert status["database_schema"]["checks"]["fts"]
assert "Canonical Architecture Manager 1.2: VERIFIZIERT" in manager.format_status()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    project = Path(temporary)
    shutil.copytree(ROOT / "24_config", project / "24_config")
    shutil.copytree(ROOT / "14_documents", project / "14_documents")
    shutil.copytree(ROOT / "02_versions/projektstrukturen", project / "02_versions/projektstrukturen")
    shutil.copytree(ROOT / "02_versions/migration_artifacts", project / "02_versions/migration_artifacts")
    (project / "09_backups/migration_reports").mkdir(parents=True)
    for relative in manager.config["required_folders"]:
        (project / relative).mkdir(parents=True, exist_ok=True)
    for relative in manager.config["entrypoints"] + manager.config["registries"]:
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text("", encoding="utf-8")
    for specification in manager.config["apis"]:
        source = ROOT / specification["path"]
        target = project / specification["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    shutil.copy2(ROOT / "32_data/kontinuum.db", project / "32_data/kontinuum.db")
    duplicate = project / "14_documents/PROJEKTSTRUKTUR_34_0.md"
    duplicate.write_text("# duplicate", encoding="utf-8")
    duplicate_status = CanonicalArchitectureManager(project, release_version="34.1").status()
    assert not duplicate_status["ok"]
    assert duplicate_status["project_structure"]["warning"] == "Mehrere aktive Projektstrukturen erkannt."
    assert duplicate_status["project_structure"]["duplicates"] == ["PROJEKTSTRUKTUR_34_0.md"]

print("Kontinuum 34.1 Canonical Architecture Manager tests passed")
