from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        system.knowledge_platform.integrate("Alpha ist stabil", origin="research", title="Quelle A", locator="https://a.example/x")
        system.knowledge_platform.integrate("Alpha ist stabil", origin="research", title="Quelle B", locator="https://b.example/y")
        system.knowledge_platform.integrate("Alpha ist instabil", origin="notebook", title="Quelle C", locator="C:/Quelle-C.md")
        before_query = system.status()["knowledge_platform"]["integrated_knowledge"]

        trust = system.ask("wie sicher ist Alpha?")
        assert "Vertrauen:" in trust
        assert "Bestätigungen: 1" in trust
        assert "Widersprüche:" in trust

        conflicts = system.ask("Welche Informationen widersprechen sich")
        assert "Alpha" in conflicts
        assert "stabil" in conflicts and "instabil" in conflicts

        learned = system.ask("Was habe ich im letzten Monat gelernt")
        assert "3 Wissenseinheiten" in learned
        topics = system.ask("Welche Themen beschäftigen mich besonders")
        assert "alpha" in topics.casefold()
        growth = system.ask("Welche Wissensgebiete wachsen am stärksten")
        assert "alpha" in growth.casefold()
        self_model = system.ask("wissensselbstmodellstatus")
        assert "Selbstmodell 1.0" in self_model
        assert system.status()["knowledge_platform"]["integrated_knowledge"] == before_query

        with system.storage.connect() as database:
            rows = database.execute(
                "SELECT metadata FROM knowledge_items WHERE kind = 'knowledge.integrated'"
            ).fetchall()
        metadata = [json.loads(row["metadata"]) for row in rows]
        assert all("trust" in item for item in metadata)
        assert all(item["trust"]["last_confirmation"] for item in metadata)
        assert any(item["trust"]["contradictions"] > 0 for item in metadata)
    finally:
        system.close()

print("Kontinuum knowledge intelligence and self-model tests passed")
