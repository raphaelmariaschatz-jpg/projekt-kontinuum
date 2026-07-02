from __future__ import annotations

import json
import os
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
        path = system.ask("bedeutungspfad identität")
        assert "Prinzip" in path
        assert "Ziel" in path
        assert "Chronik" in path
        assert "Identität" in path
        assert "meaning_edge:" not in path
        assert "Wissen aus Dialogantwort" not in path
        assert "Prüfzyklus" not in path

        debug = system.ask("bedeutungspfad identität debug")
        assert "Debug" in debug
        assert "meaning_edge" in debug
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} meaning presentation tests passed")
