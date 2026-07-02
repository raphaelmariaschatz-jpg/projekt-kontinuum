from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        assert system.version == APP_VERSION
        status = system.status()["meaning_core"]
        assert status["path"] == ["principle", "goal", "action", "memory", "chronicle", "identity"]
        assert status["nodes"] >= 8
        assert status["edges"] >= 7
        assert status["paths"] == 1
        assert f"Meaning Core {APP_VERSION}" in system.ask("bedeutungsstatus")
        path = system.ask("bedeutungspfad identität")
        assert "Bedeutungspfad" in path
        assert "Identität" in path or "identity" in path
        current = system.persistent_self_model.snapshot()
        assert current["self.meaning_nodes"] >= 8
        assert current["self.meaning_edges"] >= 7
        assert current["self.meaning_paths"] == 1
        first_paths = system.meaning_core.status()["paths"]
        system.meaning_core.rebuild()
        assert system.meaning_core.status()["paths"] == first_paths
        with system.storage.connect() as database:
            edge = database.execute("SELECT id FROM meaning_edges LIMIT 1").fetchone()
            assert edge is not None
            try:
                database.execute("DELETE FROM meaning_edges WHERE id = ?", (edge["id"],))
                raise AssertionError("meaning_edges konnte gelöscht werden.")
            except sqlite3.IntegrityError:
                pass
    finally:
        system.close()

print("Kontinuum 30.0 meaning core tests passed")
