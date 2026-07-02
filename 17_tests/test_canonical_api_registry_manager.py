from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_api_registry import CanonicalAPIRegistryManager


manager = CanonicalAPIRegistryManager(ROOT, release_version="34.1")
status = manager.status()
assert status["ok"], status
assert status["version"] == "1.3"
assert status["api_count"] == 7
assert all(status["checks"].values())
assert status["checks"]["unique_api_uids"]
assert status["checks"]["unique_canonical_names"]
assert status["checks"]["canonical_hashes"]
assert status["scope"] == "release_relevant_core_apis"
assert {item["api_uid"] for item in status["apis"]} == {
    "KAPI-000001",
    "KAPI-000002",
    "KAPI-000003",
    "KAPI-000004",
    "KAPI-000005",
    "KAPI-000006",
    "KAPI-000007",
}
assert {item["symbol"] for item in status["apis"]} == {
    "FoundationRegistry",
    "FoundationAPI",
    "FoundationStatusCenter",
    "CanonicalArchitectureManager",
    "CanonicalDatabaseManager",
    "ReleaseIntegrityFramework",
    "CanonicalArtifactManager",
}
assert status["mutation_policy"] == "read_only_verification; controlled_migration_only"
assert "Canonical API Registry Manager 1.3: VERIFIZIERT" in manager.format_status()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    project = Path(temporary)
    shutil.copytree(ROOT / "24_config", project / "24_config")
    for relative in {
        "01_system/kontinuum/core/foundation_2_2.py",
        "01_system/kontinuum/core/canonical_architecture.py",
        "01_system/kontinuum/core/canonical_database.py",
        "01_system/kontinuum/core/release_integrity.py",
        "17_tests/test_foundation_2_2_active.py",
        "17_tests/test_canonical_architecture_manager.py",
        "17_tests/test_canonical_database_manager.py",
        "17_tests/test_release_integrity_framework_34_1.py",
    }:
        source = ROOT / relative
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    config_path = project / "24_config/canonical_api_registry_34_1.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["apis"][0]["symbol"] = "MissingFoundationRegistry"
    config["apis"][1].pop("security_class")
    config["apis"][2]["canonical_hash"] = "invalid"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    broken = CanonicalAPIRegistryManager(project, release_version="34.1").status()
    assert not broken["ok"]
    assert "symbol" in broken["apis"][0]["issues"]
    assert "security_class" in broken["apis"][1]["missing_fields"]
    assert "canonical_hash" in broken["apis"][2]["issues"]

print("Kontinuum 34.1 Canonical API Registry Manager tests passed")
