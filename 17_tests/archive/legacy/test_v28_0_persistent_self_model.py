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
    system = KontinuumSystem(root)
    try:
        status = system.ask("selbstmodellstatus")
        assert f"Persistent Self Model Core {APP_VERSION}" in status
        assert "epistemische Automatik: deaktiviert" in status
        assert "geschützte Grenzen: 5 von 5" in status

        before = system.persistent_self_model.current()["system.integrated_knowledge"]
        system.knowledge_platform.integrate("Alpha ist stabil", origin="dialogue", title="Selbstmodelltest")
        system.persistent_self_model.observe("Testwissen integriert.", "test")
        after = system.persistent_self_model.current()["system.integrated_knowledge"]
        assert after == before + 1

        changes = system.ask("was hat sich geändert")
        assert "system.integrated_knowledge" in changes
        assert "Testwissen integriert" in changes
        assert "Grund:" in system.ask("warum hat sich das geändert")
        assert "Keine offenen inneren Konflikte" in system.ask("zeige offene innere konflikte")

        with system.storage.connect() as database:
            for table in (
                "self_state",
                "self_state_events",
                "self_explanations",
                "self_boundaries",
                "self_change_log",
            ):
                assert database.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] > 0
            classes = {
                row[0]
                for row in database.execute("SELECT DISTINCT kind FROM self_state").fetchall()
            }
            assert "self_knowledge" in classes
            assert "identity_knowledge" in classes
            assert "security_knowledge" in classes
            assert "moral_knowledge" in classes
            protected = database.execute(
                "SELECT COUNT(*) FROM self_boundaries WHERE json_extract(metadata, '$.protected') = 1"
            ).fetchone()[0]
            assert protected == 5
    finally:
        system.close()

print("Kontinuum 29.0 persistent self model tests passed")
