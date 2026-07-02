from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
required = (
    "01_system/kontinuum/core/autonomous_diagnostics.py",
    "01_system/kontinuum/core/error_classification.py",
    "01_system/kontinuum/core/solution_proposal.py",
    "01_system/kontinuum/agents/internal_diagnostic_agent.py",
    "11_gui/archive/34_0/desktop_gui_34_0.py",
    "11_gui/archive/34_0/GUI_34_0_MANIFEST.json",
    "13_tools/status_check_34_0.py",
    "02_versions/projektstrukturen/PROJEKTSTRUKTUR_34_0.md",
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_34_0.md",
    "16_installation/START_GUI_34_0.bat",
    "16_installation/START_KONTINUUM_34_0.bat",
    "16_installation/TEST_KONTINUUM_34_0.bat",
    "22_project_chronicle/RELEASE_34_0_FOUNDATION_REASONING_4_1.md",
    "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_34_0.md",
)
for relative in required:
    assert (ROOT / relative).is_file(), relative

version_text = (ROOT / "01_system/kontinuum/version.py").read_text(encoding="utf-8")
active = version_text.split('APP_VERSION = "', 1)[1].split('"', 1)[0]
assert tuple(map(int, active.split("."))) >= (34, 0)
manifest = json.loads((ROOT / "11_gui/archive/34_0/GUI_34_0_MANIFEST.json").read_text(encoding="utf-8"))
assert manifest["version"] == "34.0"
gui = (ROOT / "11_gui/archive/34_0/desktop_gui_34_0.py").read_text(encoding="utf-8")
assert "diagnostikstatus" in gui
assert "diagnostic_report" in gui
assert "START_GUI.bat" in (ROOT / "16_installation/START_GUI_34_0.bat").read_text(encoding="utf-8")

assert 'VERSION = "4.1"' in (ROOT / "01_system/kontinuum/core/foundation_reasoning.py").read_text(encoding="utf-8")
print("Kontinuum 34.0 version consistency tests passed")
