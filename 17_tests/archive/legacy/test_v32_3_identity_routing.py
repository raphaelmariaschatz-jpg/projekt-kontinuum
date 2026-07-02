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
    (config / "search_engine.json").write_text(json.dumps({"enabled": True}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")

    system = KontinuumSystem(root)
    try:
        system.set_user_context({"full_name": "Raphael Schatz", "username": "Raphael", "role": "SUPERADMIN"})
        answer = system.ask("Hallo Kontinuum, weißt du wer ich bin?")
        assert "Raphael Schatz" in answer
        assert "SUPERADMIN" in answer
        assert "lokal" in answer
        assert "Internet" in answer
        assert "arXiv" in answer
        assert "Brave" in answer
        assert system.version == APP_VERSION
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} identity routing tests passed")
