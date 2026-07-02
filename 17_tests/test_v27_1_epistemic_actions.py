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


class SearchStub:
    config = {"enabled": True}

    def search(self, query, limit=None):
        return {
            "ok": True,
            "query": query,
            "results": [
                {"title": "Alpha Studie A", "url": "https://a.example/alpha", "snippet": "Alpha ist stabil und wurde unabhängig geprüft.", "provider": "stub"},
                {"title": "Alpha Studie B", "url": "https://b.example/alpha", "snippet": "Die Untersuchung bestätigt: Alpha ist stabil.", "provider": "stub"},
                {"title": "Duplikat", "url": "https://a.example/zweite", "snippet": "Alpha ist stabil.", "provider": "stub"},
            ],
        }

    def status(self):
        return {"available": True, "enabled": True}

class WebStub:
    def fetch_text(self, url, timeout=6):
        marker = "Peer-reviewed journal article. DOI: 10.1/alpha"
        return {
            "url": url,
            "title": marker,
            "text": f"{marker}. Alpha ist stabil und wurde mit nachvollziehbarer Methodik geprüft. " * 5,
        }


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        system.epistemic_actions.search_engine = SearchStub()
        system.epistemic_actions.web = WebStub()
        integrated = system.knowledge_platform.integrate("Alpha ist stabil", origin="dialogue", title="Unsichere Aussage")
        system.knowledge_intelligence.refresh()
        before = system.knowledge_intelligence.epistemic_items()
        alpha = next(row for row in before if row["id"] == integrated["knowledge_id"])
        assert alpha["state"] == "uncertain"

        with system.storage.connect() as database:
            task_id = int(database.execute(
                "SELECT id FROM learning_tasks WHERE kind = 'epistemic.review' AND json_extract(metadata, '$.knowledge_id') = ?",
                (integrated["knowledge_id"],),
            ).fetchone()["id"])

        result = system.epistemic_actions.run_cycle(task_id)
        assert result["ok"] and result["sources"] == 2 and result["resolved"]
        after = next(row for row in system.knowledge_intelligence.epistemic_items() if row["id"] == integrated["knowledge_id"])
        assert after["state"] == "knowledge"
        assert after["trust"]["confirming_sources"] == 2
        assert after["trust"]["source_quality_weight"] > 0
        assert after["trust"]["source_classes"]

        protected = system.knowledge_platform.integrate("Mein Passwort ist geheim", origin="dialogue", title="Geschützt")
        system.knowledge_intelligence.refresh()
        with system.storage.connect() as database:
            protected_task = int(database.execute(
                "SELECT id FROM learning_tasks WHERE kind = 'epistemic.review' AND json_extract(metadata, '$.knowledge_id') = ?",
                (protected["knowledge_id"],),
            ).fetchone()["id"])
        blocked = system.epistemic_actions.run_cycle(protected_task)
        assert not blocked["ok"] and "Geschütztes" in blocked["message"]
        system.knowledge_intelligence.refresh()
        with system.storage.connect() as database:
            protected_metadata = json.loads(database.execute(
                "SELECT metadata FROM learning_tasks WHERE id = ?", (protected_task,)
            ).fetchone()["metadata"])
        assert protected_metadata["active"] is False
        assert protected_metadata["terminal"] is True

        status = system.ask("aktionsschichtstatus")
        assert f"Epistemische Aktionsschicht {APP_VERSION}" in status
        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM events WHERE kind = 'epistemic.action.cycle'").fetchone()[0] == 2
            assert database.execute("SELECT COUNT(*) FROM chronicle_entries WHERE kind = 'epistemic.action.cycle'").fetchone()[0] == 2
    finally:
        system.close()

print("Kontinuum 29.0 epistemic action loop tests passed")
