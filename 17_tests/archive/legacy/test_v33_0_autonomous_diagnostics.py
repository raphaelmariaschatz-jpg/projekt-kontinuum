from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.error_classification import DiagnosticFinding, ErrorClassificationEngine, Severity
from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION


assert tuple(map(int, APP_VERSION.split("."))) >= (33, 0)

classifier = ErrorClassificationEngine()
assert classifier.classify(DiagnosticFinding("a", "database", "x", "x", "x", tags=("data_loss",))) == Severity.CRITICAL
assert classifier.classify(DiagnosticFinding("b", "routing", "x", "x", "x", tags=("routing_error",))) == Severity.HIGH
assert classifier.classify(DiagnosticFinding("c", "database", "x", "x", "x", tags=("performance",))) == Severity.MEDIUM
assert classifier.classify(DiagnosticFinding("d", "version", "x", "x", "x", tags=("documentation",))) == Severity.LOW

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        startup = system.diagnostic_report
        assert startup["trigger"] == "automatic.startup"
        assert len(startup["checked_areas"]) == 8
        assert Path(startup["report_path"]).is_file()
        assert "[DIAGNOSTIK]" in startup["message"]

        clean_runtime_areas = {item["area"] for item in startup["findings"]}
        assert not clean_runtime_areas.intersection({"routing", "identity", "database", "chronicle", "memory", "foundation", "agent_communication"})

        with system.storage.connect() as database:
            database.execute(
                "INSERT INTO foundation_decisions(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                ("foundation.decision", "stale test cycle", "{}", "2020-01-01T00:00:00+00:00"),
            )
            database.commit()
        system.storage.add("graph_edges", "invalid", "broken", {"source": "only-source"})
        result = system.autonomous_diagnostics.run("test.graph")
        graph = next(item for item in result["findings"] if item["code"] == "knowledge_graph.malformed_edges")
        foundation = next(item for item in result["findings"] if item["code"] == "foundation.open_cycles")
        assert graph["severity"] == "HOCH"
        assert foundation["severity"] == "KRITISCH"
        assert graph["solution"]
        assert graph["status"] == "OFFEN"

        text = Path(result["report_path"]).read_text(encoding="utf-8")
        for heading in ("Fehler:", "Prioritaet:", "Wahrscheinliche Ursache:", "Loesung:", "Status:"):
            assert heading in text

        response = system.ask("diagnostikstatus")
        assert "[DIAGNOSTIK]" in response
        assert "interne_fehler_und_loesungen" in response
        with system.storage.connect() as database:
            audit_count = database.execute(
                "SELECT COUNT(*) FROM audit_events WHERE kind = 'diagnostics.run'"
            ).fetchone()[0]
        assert audit_count >= 2
    finally:
        system.close()

print("Kontinuum 33.0 autonomous diagnostics tests passed")
