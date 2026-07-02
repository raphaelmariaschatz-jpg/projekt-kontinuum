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
                "startup_delay_seconds": 60,
                "default_subjects": [],
                "max_references_per_cycle": 3,
            }
        ),
        encoding="utf-8",
    )
    knowledge = root / "04_knowledge"
    knowledge.mkdir(parents=True)
    (knowledge / "chemie.md").write_text("Chemie Atombau Bindungen", encoding="utf-8")

    system = KontinuumSystem(root)
    system.ask("lerne Chemie")
    result = system.continuous_learning.run_cycle("test")
    assert result["phase"] == "Bewusste Inkompetenz"
    assert system.continuous_learning.refresh_meta_assessments() == 1
    assert "Chemie" in system.ask("metalernstatus")
    assert "Bewusste Inkompetenz" in system.ask("lernphase Chemie")
    assert "erfolgreich erfasst" in system.ask("lernanwendung Chemie erfolgreich: Grundlagen korrekt erklärt")

    system.continuous_learning.add_task("Https://www")
    system.continuous_learning.seed_default_tasks()
    rows = system.continuous_learning.meta_status(100)
    invalid = next(row for row in rows if row["subject"] == "Https://www")
    assert not invalid["active"]
    system.close()

print("Kontinuum 23.0 meta learning system tests passed")
