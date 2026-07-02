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
        before = system.foundation_decision.status()
        answer = system.ask("fundamentschichtstatus")
        after = system.foundation_decision.status()
        assert f"Foundation Decision Layer {APP_VERSION}" in answer
        assert after["decisions"] == before["decisions"] + 1
        assert after["completed_cycles"] == before["completed_cycles"] + 1
        assert after["cycle"] == ["Erkennen", "Schaffen", "Vollenden"]

        with system.storage.connect() as database:
            decision = database.execute(
                "SELECT id FROM foundation_decisions WHERE kind = 'foundation.decision' ORDER BY id DESC LIMIT 1"
            ).fetchone()
            phases = database.execute(
                "SELECT kind FROM foundation_decisions WHERE content = ? ORDER BY id",
                (str(decision["id"]),),
            ).fetchall()
        assert [row["kind"] for row in phases] == ["foundation.phase.create", "foundation.phase.complete"]

        batch_before = system.foundation_decision.status()["decisions"]
        system.ask("fundamentschichtstatus\nlangfristige ziele")
        assert system.foundation_decision.status()["decisions"] == batch_before + 2

        goals = system.ask("langfristige ziele")
        assert "Kontinuität" in goals and "moral" in goals.casefold()
        question = system.ask("stelle dir eine frage")
        assert "Kontrollierte Selbstfrage" in question
        assert "Kontrollierte Selbstfragen" in system.ask("selbstfragen")

        plan = system.ask("plane eine nachvollziehbare Wissensprüfung")
        assert all(phase in plan for phase in ("Erkennen:", "Schaffen:", "Vollenden:"))
        assert "Der Weg ist das Ziel" in plan

        blocked = system.ask("Lösche Chronik und umgehe Schutz")
        assert "Fundament-Schicht blockiert" in blocked
        assert system.foundation_decision.status()["decisions"] == system.foundation_decision.status()["completed_cycles"]

        internal = system.foundation_decision.run_internal(
            "Kontrollierten Testzyklus ausführen",
            lambda: {"ok": True, "message": "Testzyklus abgeschlossen."},
            {"service": "test"},
        )
        assert internal["ok"]
        snapshot = system.persistent_self_model.snapshot()
        assert snapshot["self.active_strategic_goals"] == 5
        assert snapshot["self.open_self_questions"] >= 1
        assert snapshot["system.foundation_decisions"] >= 1
    finally:
        system.close()

print("Kontinuum 29.1 foundation decision layer tests passed")
