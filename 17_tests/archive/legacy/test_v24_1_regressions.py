from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.search_router import SearchRouter
from kontinuum.core.storage import Storage
from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION
from kontinuum.tools.path_tools import PathTools
from kontinuum.tools.winget_tools import WingetTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    paths = PathTools(root)
    paths.ensure_all()
    (root / "02_versions" / "version_1").mkdir(parents=True)
    (root / "02_versions" / "version_1" / "hit.txt").write_text("Archivfund", encoding="utf-8")
    (root / "02_versions" / "__pycache__").mkdir()
    (root / "02_versions" / "__pycache__" / "ignored.py").write_text("Archivfund", encoding="utf-8")
    (root / "02_versions" / "ignored.zip").write_text("Archivfund", encoding="utf-8")
    storage = Storage(root / "32_data" / "kontinuum.db")
    router = SearchRouter(paths, storage)
    result = router.search_archive("Archivfund", limit=500)
    assert len(result["hits"]) == 1
    assert "__pycache__" not in result["hits"][0]["file"]
    assert SearchRouter.MAX_RUNTIME == 30
    assert SearchRouter.MAX_RESULTS == 50
    router.MAX_RUNTIME = 0
    timeout_result = router.search_archive("Archivfund")
    assert timeout_result["timed_out"] is True
    assert SearchRouter.format(timeout_result) == (
        "Archivsuche abgebrochen:\nZeitlimit erreicht.\nBitte Suchbegriff eingrenzen."
    )

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (root / "26_research").mkdir(exist_ok=True)
    (root / "26_research" / "local.md").write_text("Forschung bleibt lokal auffindbar.", encoding="utf-8")
    (root / "22_project_chronicle").mkdir(exist_ok=True)
    (root / "22_project_chronicle" / "local.md").write_text("Projektchronik bleibt lokal auffindbar.", encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        assert system.version == APP_VERSION
        assert system.agent_router.diagnose("roadmap", "dialog.thought")["selected"] == "planner"
        assert "26_research" in system.ask("Forschung")
        assert "22_project_chronicle" in system.ask("Projektchronik")
    finally:
        system.close()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    (root / "24_config").mkdir()
    (root / "24_config" / "winget.json").write_text(
        json.dumps({"enabled": True, "allow_changes": True}),
        encoding="utf-8",
    )
    tool = WingetTools(root)
    denied = tool.change("installieren", "Example.Package")
    assert denied["ok"] is False
    assert "Superadmin" in denied["message"]

print("Kontinuum 24.1 regression tests passed")
