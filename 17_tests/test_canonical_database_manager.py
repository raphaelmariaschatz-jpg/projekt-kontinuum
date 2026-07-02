from __future__ import annotations

import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_database import CanonicalDatabaseManager


manager = CanonicalDatabaseManager(ROOT, release_version="34.1")
status = manager.status()
assert status["ok"], status
assert status["version"] == "1.2"
assert all(status["checks"].values())
assert status["integrity_check"] == "ok"
assert status["object_counts"]["tables"] >= 39
assert status["object_counts"]["indexes"] >= 8
assert status["object_counts"]["triggers"] >= 12
assert status["fts"]["file_search_fts"]["fts5"]
assert status["data_domains"]["foundation"]["ok"]
assert status["data_domains"]["memory"]["ok"]
assert status["mutation_policy"] == "read_only_verification; controlled_migration_only"
assert "Canonical Database Manager 1.2: VERIFIZIERT" in manager.format_status()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    project = Path(temporary)
    (project / "24_config").mkdir()
    shutil.copy2(
        ROOT / "24_config/canonical_database_34_1.json",
        project / "24_config/canonical_database_34_1.json",
    )
    shutil.copy2(ROOT / "32_data/kontinuum.db", project / "kontinuum.db")
    config_path = project / "24_config/canonical_database_34_1.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["database"] = "kontinuum.db"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with sqlite3.connect(project / "kontinuum.db") as connection:
        connection.execute("DROP INDEX idx_foundation_memory_kind")
    broken = CanonicalDatabaseManager(project, release_version="34.1").status()
    assert not broken["ok"]
    assert "idx_foundation_memory_kind" in broken["missing_indexes"]

print("Kontinuum 34.1 Canonical Database Manager tests passed")
