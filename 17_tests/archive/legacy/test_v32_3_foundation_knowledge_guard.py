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
        content = "Raphael Schatz ist der Schöpfer von Kontinuum. Der Weg ist das Ziel."
        result = system.knowledge_platform.integrate(content, {"origin": "notebook"})
        assert result["ok"] is False
        assert result["classification"] == "foundation_knowledge"

        system.knowledge_intelligence.refresh()
        assert all(content not in gap["subject"] for gap in system.knowledge_intelligence.knowledge_gaps())
        assert system.knowledge_intelligence._is_foundation_knowledge("Wissen 5 überprüfen: Mein Schöpfer ist Raphael Schatz.")
        assert system.knowledge_intelligence._is_foundation_knowledge("Wissen 7 überprüfen: Erkennen - Schaffen - Vollenden.")
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} foundation knowledge guard tests passed")
