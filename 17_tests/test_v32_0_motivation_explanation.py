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
        status = system.status()["motivation_explanation"]
        assert status["explanations"] > 0
        assert status["evidence"] >= status["explanations"]
        assert status["paths"] > 0
        assert "kein Wille" in status["claim"]
        assert f"Motivation Explanation Core {APP_VERSION}" in system.ask("motivationserklärungsstatus")

        explanation = system.ask("motivationserklärung identität")
        assert "Motivationserklärung" in explanation
        assert "Score" in explanation
        assert "Warum" in explanation
        assert "kein Bewusstsein" in explanation

        influences = system.ask("wichtige einflüsse identität")
        assert "Wichtige Einflüsse" in influences
        assert "Grenze" in influences

        current = system.persistent_self_model.snapshot()
        assert current["self.motivation_explanations"] > 0
        assert current["self.motivation_evidence"] > 0
        assert current["self.motivation_paths"] > 0

        gui_manifest = json.loads((ROOT / "11_gui/archive/32_4/GUI_32_4_MANIFEST.json").read_text(encoding="utf-8"))
        assert gui_manifest["version"] == "32.4"
        assert any("Motivation-Explanation" in feature for feature in gui_manifest["features"])

        with system.storage.connect() as database:
            row = database.execute("SELECT id FROM motivation_explanations LIMIT 1").fetchone()
            assert row is not None
            try:
                database.execute("DELETE FROM motivation_explanations WHERE id = ?", (row["id"],))
                raise AssertionError("motivation_explanations konnte gelöscht werden.")
            except sqlite3.IntegrityError:
                pass
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} motivation explanation tests passed")
