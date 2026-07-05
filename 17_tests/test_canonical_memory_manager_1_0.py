from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem
from kontinuum.core.storage import Storage
from kontinuum.foundation.canonical_memory_manager import CanonicalMemoryManager, MemoryValidationError
from kontinuum.tools.path_tools import PathTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    storage = Storage(root / "32_data" / "kontinuum.db")
    manager = CanonicalMemoryManager(PathTools(root), storage)

    assert manager.load_memory()["schema_version"] == "1.0"
    saved = manager.save_memory(
        {"class": "project", "title": "CMM Test", "content": "Projekt Kontinuum CMM 1.0 ist im Test.", "source": "test"},
        actor="test",
    )
    assert saved["ok"] is True
    first_id = saved["memory_id"]
    first = manager.find_memory(first_id)
    assert first and first["hash"] == manager.entry_hash(first)
    assert manager.classify_memory("Raphael bevorzugt lokale Systeme") == "user_preferences"

    updated = manager.update_memory(first_id, {"importance": "high"}, actor="test")
    assert updated["ok"] is True
    assert manager.find_memory(first_id)["version"] == 2

    second = manager.save_memory("Projekt Kontinuum CMM Merge-Ziel", memory_class="project", actor="test")
    merged = manager.merge_memory(second["memory_id"], first_id, actor="test")
    assert merged["ok"] is True
    assert manager.find_memory(second["memory_id"])["status"] == "merged"
    assert manager.search_memory("Merge-Ziel")
    assert manager.list_memory(memory_class="project")

    stats = manager.get_statistics()
    assert stats["active"] >= 1
    assert stats["merged"] == 1
    assert stats["integrity"] == "ok"
    assert "Canonical Memory Manager 1.0 Status" in manager.format_status()
    assert "Canonical Memory Manager 1.0 Statistik" in manager.format_statistics()

    bad = manager._copy_data()
    bad["entries"][0]["hash"] = "broken"
    try:
        manager.validate_memory(bad)
        raise AssertionError("Ungueltiger Hash wurde akzeptiert")
    except MemoryValidationError:
        pass

    backups = list((root / "24_config" / "history" / "canonical_memory_history").glob("canonical_memory_*.json"))
    assert backups
    with storage.connect() as database:
        governance = database.execute("SELECT COUNT(*) FROM audit_events WHERE kind = 'canonical_memory.change'").fetchone()[0]
    assert governance >= 3

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text("{\"enabled\": false}", encoding="utf-8")
    (config / "search_engine.json").write_text("{\"enabled\": false}", encoding="utf-8")
    (config / "language_model.json").write_text("{\"enabled\": false}", encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        status = system.ask("memory status")
        statistics = system.ask("memory statistics")
        assert "Canonical Memory Manager 1.0 Status" in status
        assert "Anzahl Erinnerungen" in status
        assert "Canonical Memory Manager 1.0 Statistik" in statistics
    finally:
        system.close()

print("Canonical Memory Manager 1.0 tests passed")
