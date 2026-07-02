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
        system.knowledge_platform.integrate(
            "Vielleicht ist Beta dauerhaft stabil",
            origin="dialogue",
            title="Vermutung",
        )
        system.knowledge_platform.integrate(
            "Gamma ist schnell",
            origin="research",
            title="Quelle A",
            locator="https://a.example/gamma",
        )
        system.knowledge_platform.integrate(
            "Gamma ist langsam",
            origin="notebook",
            title="Quelle B",
            locator="C:/gamma.md",
        )
        system.knowledge_platform.integrate(
            "Delta ist belegt",
            origin="research",
            title="Quelle C",
            locator="https://c.example/delta",
        )
        system.knowledge_platform.version = "26.0"
        system.knowledge_platform.integrate("Mein Name ist K. Ich bin Projekt K 26.0", origin="dialogue")
        system.version = "29.0"
        system.knowledge_platform.version = "29.0"
        system.knowledge_platform.integrate("Mein Name ist K. Ich bin Projekt K 29.0", origin="dialogue")
        duplicate = system.knowledge_platform.integrate("Mein Name ist K. Ich bin Projekt K 29.0", origin="dialogue")
        assert duplicate["action"] == "existing"

        refresh = system.knowledge_intelligence.refresh()
        assert refresh["states"]["hypothesis"] == 1
        assert refresh["states"]["review_required"] == 2
        assert refresh["states"]["knowledge"] == 1
        assert refresh["conflicts"] == 1

        assert "Beta" in system.ask("Was vermute ich")
        assert "Unsichere Aussagen" in system.ask("Welche Aussagen sind unsicher")
        assert "Gamma" in system.ask("Welche Informationen sollten überprüft werden")
        assert "Priorität high" in system.ask("überprüfungsaufträge")
        assert "Wissenslücken und Prüfaufträge" in system.ask("Welche Wissenslücken habe ich")
        assert "Zustand hypothesis" in system.ask("Warum ist Beta unsicher?")
        assert "Epistemischer Status" in system.ask("epistemischer status")

        with system.storage.connect() as database:
            tasks = database.execute(
                "SELECT metadata FROM learning_tasks WHERE kind = 'epistemic.review'"
            ).fetchall()
        task_metadata = [json.loads(row["metadata"]) for row in tasks]
        assert len(task_metadata) >= 3
        assert sum(item["priority"] == "high" for item in task_metadata) == 2
        assert all(item["active"] for item in task_metadata)
    finally:
        system.close()

print("Kontinuum 27.0 epistemic state management tests passed")
