from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_artifacts import CanonicalArtifactManager


manager = CanonicalArtifactManager(ROOT, release_version="34.1")
status = manager.status()
assert status["ok"], status
assert status["version"] == "1.4"
assert status["artifact_count"] >= 14
assert status["pattern_count"] >= 4
assert all(status["checks"].values())
assert status["checks"]["required_artifacts"]
assert status["checks"]["signatures"]
assert status["checks"]["lifecycle"]
assert status["class_counts"]["audit-evidence"] >= 3
assert status["class_counts"]["migration-artifact"] >= 3
assert status["mutation_policy"] == "read_only_verification; no_move_no_delete_no_autofix"
assert "Canonical Artifact Manager 1.4: VERIFIZIERT" in manager.format_status()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    project = Path(temporary)
    for relative in (
        "24_config",
        "01_system/kontinuum/core",
        "14_documents",
        "31_reports/release_integrity/34.1",
        "02_versions/migration_artifacts/34_1_Foundation_2_2_CAM_1_1/release_evidence",
        "02_versions/projektstrukturen",
        "09_backups/release_integrity",
        "09_backups/migration_reports",
    ):
        (project / relative).mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "24_config/canonical_artifacts_34_1.json", project / "24_config/canonical_artifacts_34_1.json")
    shutil.copy2(ROOT / "24_config/retention_policy.json", project / "24_config/retention_policy.json")
    for relative in manager.config["artifacts"]:
        source = ROOT / relative["path"]
        target = project / relative["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_file():
            shutil.copy2(source, target)
    for source in (ROOT / "02_versions/projektstrukturen").glob("PROJEKTSTRUKTUR_*.md"):
        shutil.copy2(source, project / "02_versions/projektstrukturen" / source.name)
    for source in (ROOT / "09_backups/release_integrity").glob("Kontinuum_34_1_*.zip"):
        shutil.copy2(source, project / "09_backups/release_integrity" / source.name)
        break

    config_path = project / "24_config/canonical_artifacts_34_1.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["artifacts"][0]["path"] = "01_system/kontinuum/core/missing_release_integrity.py"
    config["artifacts"][1]["artifact_class"] = "wrong-class"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    broken = CanonicalArtifactManager(project, release_version="34.1").status()
    assert not broken["ok"]
    assert "missing" in broken["artifacts"][0]["issues"]
    assert "artifact_class" in broken["artifacts"][1]["issues"]

print("Kontinuum 34.1 Canonical Artifact Manager tests passed")
