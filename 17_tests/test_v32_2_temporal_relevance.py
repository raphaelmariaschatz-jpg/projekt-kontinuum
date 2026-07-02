from __future__ import annotations

import json
import os
import sqlite3
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
        assert system.version == APP_VERSION
        system.storage.add(
            "chronicle_entries",
            "release.test",
            f"Version {APP_VERSION} testet Temporal Relevance Core, Bedeutungsinflation, Identität und Chronikprägung.",
            {"test": True},
        )
        system.temporal_relevance.assess("test.chronicle_entry")
        status = system.status()["temporal_relevance"]
        assert status["assessments"] > 0
        assert status["reports"] >= 1
        assert status["by_kind"]["meaning_edge.relevance"] > 0
        assert status["by_kind"]["chronicle.importance"] > 0
        assert status["by_kind"]["knowledge_gap.priority"] > 0
        assert "active" in status["edge_status_counts"]
        assert status["circularity_violations"] == 0

        relevance = system.ask("relevanzstatus")
        assert f"Temporal Relevance Core {APP_VERSION}" in relevance
        assert "Kantenstatus" in relevance
        assert "Zirkularitätsverletzungen: 0" in relevance

        inflation = system.ask("bedeutungsinflation")
        assert "Bedeutungsinflationsprüfung" in inflation
        assert "Obsoleszenz-Kandidaten" in inflation

        chronicle = system.ask("chronikprägung")
        assert "Prägende Chronikereignisse" in chronicle

        gaps = system.ask("wissenslückenpriorität")
        assert "Priorisierte Wissenslücken" in gaps

        current = system.persistent_self_model.snapshot()
        assert current["self.relevance_assessments"] > 0
        assert current["self.relevance_reports"] >= 1
        assert current["self.circularity_violations"] == 0

        explanation = system.ask("motivationserklärung identität")
        assert "nicht durch ihren Motivation-Score begründet" in explanation

        with system.storage.connect() as database:
            row = database.execute("SELECT id FROM relevance_assessments LIMIT 1").fetchone()
            assert row is not None
            try:
                database.execute("DELETE FROM relevance_assessments WHERE id = ?", (row["id"],))
                raise AssertionError("relevance_assessments konnte gelöscht werden.")
            except sqlite3.IntegrityError:
                pass
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} temporal relevance tests passed")
