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
    source = root / "alpha.md"
    source.write_text(
        "Alpha ist ein nachvollziehbarer Testbegriff für die vollständig integrierte Knowledge Platform.",
        encoding="utf-8",
    )
    system = KontinuumSystem(root)
    try:
        answer = system.ask(f'notizbuch import "{source}"')
        assert "Quelle -> Notebook -> Memory-Core -> Wissensgraph -> Projektchronik" in answer

        status = system.status()["knowledge_platform"]
        assert status["version"] == APP_VERSION
        assert status["integrated_knowledge"] == 1
        assert status["graph_edges"] == 5
        assert status["chronicle_entries"] == 1

        explanation = system.ask("wissensweg Alpha")
        assert "alpha.md" in explanation
        assert str(source) in explanation
        assert f"Eingeführt mit Version: {APP_VERSION}" in explanation
        assert "Verbundene Erinnerung:" in explanation

        with system.storage.connect() as database:
            assert database.execute(
                "SELECT COUNT(*) FROM graph_nodes WHERE kind IN ('source', 'notebook', 'knowledge', 'memory', 'version', 'chronicle')"
            ).fetchone()[0] >= 6
            assert database.execute(
                "SELECT COUNT(*) FROM memories WHERE json_extract(metadata, '$.provenance.introduced_version') = ?",
                (APP_VERSION,),
            ).fetchone()[0] >= 1

        assert "Lernprojekt angelegt" in system.ask("lerne Quanten-Testwissen")
        assert "Erinnerung store" in system.ask("merke Integrationswissen verbindet alle Säulen")
        assert "Hookesche Gesetz" in system.ask("Was ist das Hookesche Gesetz?")

        origins = system.status()["knowledge_platform"]["origins"]
        assert origins["notebook"] == 1
        assert origins["learning"] == 1
        assert origins["memory"] == 1
        rejected = system.knowledge_platform.integrate(
            "Systemstatus 32.3: Projektwurzel C:\\Projekt Kontinuum.",
            origin="dialogue",
            title="Dialogantwort (system)",
        )
        assert rejected["ok"] is False
        assert rejected["classification"] == "report"
        assert system.knowledge_contamination_guard.should_integrate(
            "Das Hookesche Gesetz beschreibt im elastischen Bereich F = -k · x.",
            origin="dialogue",
            title="Fachdialog",
        )

        common_answer = system.ask("Was weißt du über Integrationswissen?")
        assert "Wissensweg für" in common_answer
        assert "Ursprung: memory" in common_answer

        first_backfill = system.knowledge_platform.backfill()
        second_backfill = system.knowledge_platform.backfill()
        assert first_backfill["total"] > 0
        assert second_backfill["total"] == 0
    finally:
        system.close()

print("Kontinuum 29.0 knowledge platform regression tests passed")
