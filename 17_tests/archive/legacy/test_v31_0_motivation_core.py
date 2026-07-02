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
        status = system.status()["motivation_core"]
        assert status["scores"] > 0
        assert status["reports"] == 1
        assert "goal_support" in status["score_kinds"]
        assert "central_meaning_relation" in status["score_kinds"]
        assert f"Motivation Core {APP_VERSION}" in system.ask("motivationsstatus")
        priorities = system.ask("motivationsprioritäten")
        assert "Motivationsprioritäten" in priorities
        assert "nicht Wille" in system.ask("motivationsstatus")
        current = system.persistent_self_model.snapshot()
        assert current["self.motivation_scores"] > 0
        assert current["self.motivation_reports"] == 1
        gui_manifest = json.loads((ROOT / "11_gui/archive/32_4/GUI_32_4_MANIFEST.json").read_text(encoding="utf-8"))
        assert gui_manifest["version"] == "32.4"
        assert any("Motivation-Core" in feature for feature in gui_manifest["features"])
        with system.storage.connect() as database:
            row = database.execute("SELECT id FROM motivation_scores LIMIT 1").fetchone()
            assert row is not None
            try:
                database.execute("DELETE FROM motivation_scores WHERE id = ?", (row["id"],))
                raise AssertionError("motivation_scores konnte gelöscht werden.")
            except sqlite3.IntegrityError:
                pass
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} motivation core tests passed")
