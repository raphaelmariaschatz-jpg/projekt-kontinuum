from __future__ import annotations

"""Historical live-root integration test, excluded from active release suites.

This legacy scenario intentionally targets the real project root and may rebuild
the complete historical meaning graph or mutate runtime data.  Its filename
therefore does not match ``test_*.py``.  Run it only manually against a prepared
copy of the historical runtime.
"""

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.structure import validate_structure
from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION
from kontinuum.core.auth import AuthManager


system = KontinuumSystem(ROOT)
auth_status = AuthManager(ROOT).status()
assert auth_status["configured"]
assert auth_status["consistent"]
assert auth_status["is_superadmin"]
status = system.status()
assert status["version"] == APP_VERSION
assert status["backend"] == f"KontinuumSystem {APP_VERSION}"
assert status["language_model"]["model"] == "qwen2.5:3b"
assert status["python"]["available"]
assert status["winget"]["enabled"] is False
assert status["search_engine"]["available"]
assert validate_structure(system.path_tools)["ok"]
assert "Kontinuum" in system.ask("Wie ist dein Name?")
assert "Raphael Schatz" in system.ask("Wer ist dein Schoepfer?")
assert "Hallo Raphael" in system.ask("Hallo Kontinuum, ich bin Raphael, dein Schöpfer")
assert "Erkennen" in system.ask("Welche Prinzipien gelten fuer dich?")
assert "48" in system.ask("wieviel ist 6 x 8?")
assert "Hookesche" in system.ask("Was ist das Hooksche Gesetz?")
assert "Aktive Agenten" in system.ask("agentenstatus")
assert "codex" in system.modules.list_active()
assert "python" in system.modules.list_active()
assert "winget" in system.modules.list_active()
assert f"Version {APP_VERSION} aktiv" in system.ask("versionen")
assert "Programmieren" in system.ask("ab sofort kannst du aktiv sein und lernen. Lerne zuerst zu programmieren")
assert "Python" in system.ask("welche Programmiersprache lernst du zuerst?")
assert "Programmieren" in system.ask("lernstatus")
assert system.ask("modellstatus")
assert "Python" in system.ask("pythonstatus")
assert system.ask("python: print(6 * 8)").strip() == "48"
assert "winget" in system.ask("wingetstatus")
assert system.tools["winget_tools"].status()["enabled"] is False
assert "regelbasiert" in system.ask("warum antwortest du nicht auf meine Fragen?")
search = system.search_router.search("Mathematik", limit=5)
assert search["hits"]
assert search["hits"][0]["area"] != "02_versions"
source_id = system.storage.add_source("https://example.org/reference", {"title": "Reference only"})
assert source_id > 0
try:
    system.storage.add_memory("research.web", "This full research text must not be stored.", {})
    raise AssertionError("Research content storage guard did not reject full text.")
except ValueError:
    pass
print("Kontinuum 29.0 core tests passed")
