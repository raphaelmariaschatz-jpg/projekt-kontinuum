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


assert tuple(map(int, APP_VERSION.split("."))) >= (32, 4)

required_paths = (
    "11_gui/archive/32_4/desktop_gui_32_4.py",
    "11_gui/archive/32_4/GUI_32_4_MANIFEST.json",
    "13_tools/status_check_32_4.py",
    "13_tools/status_check_32_3.py",
    "14_documents/README_GUI_32_4.md",
    "02_versions/projektstrukturen/PROJEKTSTRUKTUR_32_4.md",
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_32_4.md",
    "16_installation/START_GUI_32_4.bat",
    "16_installation/START_KONTINUUM_32_4.bat",
    "16_installation/TEST_KONTINUUM_32_4.bat",
    "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_32_4.md",
    "22_project_chronicle/RELEASE_32_4_VERIFICATION_DOCUMENTATION.md",
)
for relative in required_paths:
    assert (ROOT / relative).is_file(), relative

manifest = json.loads((ROOT / "11_gui/archive/32_4/GUI_32_4_MANIFEST.json").read_text(encoding="utf-8"))
assert manifest["version"] == "32.4"
assert manifest["files"][0] == "11_gui/desktop_gui_32_4.py"

gui = (ROOT / "11_gui/archive/32_4/desktop_gui_32_4.py").read_text(encoding="utf-8")
assert "APP_VERSION" in gui
assert "Sessionstatus" in gui
assert "Fundamentzyklen" in gui

historical_documents = (
    "02_versions/projektstrukturen/PROJEKTSTRUKTUR_32_4.md",
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_32_4.md",
    "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_32_4.md",
)
for relative in historical_documents:
    content = (ROOT / relative).read_text(encoding="utf-8")
    assert "32.4" in content, relative

for relative in (
    "16_installation/START_GUI_23.bat",
    "16_installation/START_GUI_32_3.bat",
    "16_installation/START_KONTINUUM_23.bat",
    "16_installation/START_KONTINUUM_32_3.bat",
    "16_installation/TEST_KONTINUUM_23.bat",
    "16_installation/TEST_KONTINUUM_32_3.bat",
):
    content = (ROOT / relative).read_text(encoding="utf-8")
    assert "34_1" in content or "START_GUI.bat" in content, relative

for relative in (
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_32_0.md",
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_32_2.md",
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_32_3.md",
):
    assert (ROOT / relative).read_text(encoding="utf-8").startswith("# HISTORISCH"), relative

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        long_dialogue = "Ein fachlich geprüftes Ergebnis " + "mit nachvollziehbarer Evidenz " * 20
        result = system.knowledge_platform.integrate(long_dialogue, origin="dialogue", title="Fachdialog")
        with system.storage.connect() as database:
            chronicle = database.execute(
                "SELECT content FROM chronicle_entries WHERE id = ?", (result["chronicle_id"],)
            ).fetchone()["content"]
        assert chronicle == "Geprüftes Dialogwissen integriert: Fachdialog"
        assert long_dialogue not in chronicle
        assert len(chronicle) <= 220
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} full version and path consistency tests passed")
