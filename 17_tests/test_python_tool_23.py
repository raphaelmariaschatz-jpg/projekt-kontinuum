from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.tools.python_tools import PythonTools


with tempfile.TemporaryDirectory() as temporary_root:
    tool = PythonTools(temporary_root)
    assert tool.status()["available"]
    assert tool.execute("print(sum(range(11)))")["output"] == "55"
    assert not tool.execute("raise ValueError('Testfehler')")["ok"]
    assert "ValueError" in tool.execute("raise ValueError('Testfehler')")["output"]
    assert not tool.execute("import time; time.sleep(20)")["ok"]

print("Kontinuum Python tool tests passed")
