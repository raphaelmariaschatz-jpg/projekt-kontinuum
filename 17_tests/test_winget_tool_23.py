from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.tools.winget_tools import WingetTools


tool = WingetTools(ROOT)
status = tool.status()
assert status["enabled"] is False
assert tool.change("installieren", "Ollama.Ollama")["ok"] is False
print("Kontinuum winget tool tests passed")
