from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    root = Path(temporary_directory)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text(
        json.dumps(
            {
                "enabled": True,
                "interval_seconds": 60,
                "startup_delay_seconds": 60,
                "default_subjects": ["Mathematik"],
            }
        ),
        encoding="utf-8",
    )

    first = KontinuumSystem(root)
    assert first.continuous_learning.is_running()
    answer = first.ask("lerne Chemie")
    assert "Lernprojekt angelegt: Chemie" in answer
    status = first.continuous_learning.status()
    assert status["tasks"] == 2
    assert status["policy"] == "references_only"
    first.close()

    second = KontinuumSystem(root)
    assert second.continuous_learning.status()["tasks"] == 2
    assert "Hintergrund läuft: True" in second.ask("autostatus")
    second.close()

print("Kontinuum 23.0 continuous learning system tests passed")
