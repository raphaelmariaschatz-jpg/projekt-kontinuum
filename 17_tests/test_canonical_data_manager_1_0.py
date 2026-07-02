from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_data_manager import CanonicalDataManager, SafetyBlock


manager = CanonicalDataManager(ROOT)
registry = manager.load_registry()

assert registry["version"] == "1.0"
assert registry["mutation_policy"] == "read_only_no_migration_no_move_no_delete"
assert registry["data_objects"]

core_memory = manager.resolve("runtime.core_memory")
assert core_memory == ROOT / "32_data/core_memory.json"
assert manager.exists("runtime.core_memory")

assert manager.classify("32_data/02_versions/version_03/projekt_kontinuum_3_0/projekt_kontinuum_3_0/data/goals.json") == "historical_version_data"
assert manager.classify("32_data/kontinuum.db") == "runtime_data"
assert manager.classify("32_data/unknown_future_file.json") == "unclear_review_required"

validation = manager.validate_registry()
assert validation["ok"], validation
assert validation["object_count"] >= 17434
assert not validation["write_or_migration_enabled"]

status = manager.generate_status_report()
assert status["read_only"]
assert not status["migration_performed"]
assert status["object_count"] == validation["object_count"]
assert status["historical_count"] >= 17311
assert status["runtime_count"] >= 18
assert status["unclear_count"] >= 36
assert "Canonical Data Manager 1.0" in manager.format_status_report()

assert manager.list_active_data()
assert manager.list_historical_data()
assert manager.list_runtime_data()
assert manager.list_unclear_data()

for method in (manager.migrate, manager.move, manager.delete, manager.rewrite_reference):
    try:
        method("runtime.core_memory")
    except SafetyBlock:
        pass
    else:
        raise AssertionError(f"{method.__name__} must be blocked in CDM 1.0")

print("Kontinuum CDM 1.0 tests passed")
