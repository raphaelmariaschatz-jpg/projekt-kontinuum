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
        report = "Motivation Core: Score 0.97. Kein Wille, kein Bewusstsein."
        partial = "Teilantwort (Zeitbudget erreicht): Belegte Kernaussagen waren nicht verfügbar."
        self_description = "Mein Name ist Kontinuum. Ich bin Projekt Kontinuum 32.3."
        decision = system.knowledge_contamination_guard.classify(report, origin="dialogue")
        assert decision == "report"
        assert system.knowledge_contamination_guard.should_integrate(report, origin="dialogue") is False
        assert system.knowledge_contamination_guard.should_integrate(partial, origin="dialogue") is False
        assert system.knowledge_contamination_guard.should_integrate(self_description, origin="dialogue") is False

        integrated = system.knowledge_platform.integrate(
            report,
            {"origin": "dialogue", "title": "Motivationserklärung"},
        )
        assert integrated["ok"] is False
        assert integrated["classification"] == "report"

        item_id = system.storage.add("knowledge_items", "knowledge.integrated", report, {"origin": "legacy"})
        system.knowledge_intelligence.refresh()
        with system.storage.connect() as database:
            row = database.execute(
                "SELECT metadata FROM knowledge_items WHERE id = ?",
                (item_id,),
            ).fetchone()
            metadata = json.loads(row["metadata"])
            task = database.execute(
                "SELECT metadata FROM learning_tasks WHERE kind = 'epistemic.review' AND json_extract(metadata, '$.knowledge_id') = ?",
                (item_id,),
            ).fetchone()
        assert metadata["epistemic"]["state"] == "report_output"
        assert task is None or json.loads(task["metadata"]).get("active") is False
        assert all(gap.get("knowledge_id") != item_id for gap in system.knowledge_intelligence.knowledge_gaps())

        system.storage.add(
            "motivation_scores",
            "strategic_knowledge_gap",
            "Wissen 99 überprüfen: Teilantwort (Zeitbudget erreicht): nicht verfügbar",
            {
                "motivation_core": True,
                "label": "Wissen 99 überprüfen: Teilantwort (Zeitbudget erreicht): nicht verfügbar",
                "score": 1.0,
                "reason": "test",
            },
        )
        assert "Teilantwort" not in system.motivation_core.format_priorities()
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} knowledge contamination guard tests passed")
