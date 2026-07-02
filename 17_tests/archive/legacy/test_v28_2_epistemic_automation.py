from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem

os.environ.pop("KONTINUUM_EPISTEMIC_AUTOMATIC", None)


class SearchStub:
    config = {"enabled": True}

    def search(self, query, limit=None):
        topic = "beta" if "beta" in query.casefold() else "alpha"
        return {
            "ok": True,
            "results": [
                {"title": f"{topic} Studie A", "url": f"https://a.example/{topic}", "snippet": f"{topic} ist stabil und wurde unabhängig wissenschaftlich geprüft.", "provider": "stub"},
                {"title": f"{topic} Studie B", "url": f"https://b.example/{topic}", "snippet": f"{topic} ist stabil und wurde durch eine zweite Untersuchung bestätigt.", "provider": "stub"},
            ],
        }

    def status(self):
        return {"available": True, "enabled": True}


class WebStub:
    def fetch_text(self, url, timeout=6):
        topic = "beta" if "beta" in url else "alpha"
        return {
            "url": url,
            "title": "Peer-reviewed journal DOI: 10.1/test",
            "text": f"Peer-reviewed journal DOI: 10.1/test. {topic} ist stabil und unabhängig bestätigt. " * 8,
        }


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(
        json.dumps({
            "enabled": True,
            "automatic": True,
            "automatic_startup_delay_seconds": 999,
            "automatic_interval_seconds": 999,
            "max_automatic_cycles_per_run": 1,
        }),
        encoding="utf-8",
    )
    system = KontinuumSystem(root)
    try:
        system.epistemic_actions.search_engine = SearchStub()
        system.epistemic_actions.web = WebStub()
        alpha = system.knowledge_platform.integrate("Alpha ist stabil", origin="dialogue")
        beta = system.knowledge_platform.integrate("Beta ist stabil", origin="dialogue")
        system.knowledge_intelligence.refresh()
        with system.storage.connect() as database:
            beta_task = database.execute(
                "SELECT id, metadata FROM learning_tasks WHERE kind='epistemic.review' AND json_extract(metadata, '$.knowledge_id')=?",
                (beta["knowledge_id"],),
            ).fetchone()
            metadata = json.loads(beta_task["metadata"])
            metadata["priority"] = "high"
            database.execute("UPDATE learning_tasks SET metadata=? WHERE id=?", (json.dumps(metadata), beta_task["id"]))
            database.commit()

        result = system.epistemic_actions.run_automatic_cycle()
        assert result["ok"] and result["cycles"] == 1
        assert result["results"][0]["resolved"]
        assert result["results"][0]["sources"] == 2
        with system.storage.connect() as database:
            selected = database.execute(
                "SELECT metadata FROM learning_tasks WHERE id=?", (result["results"][0]["task_id"],)
            ).fetchone()
            assert json.loads(selected["metadata"])["knowledge_id"] == beta["knowledge_id"]
            alpha_task = database.execute(
                "SELECT metadata FROM learning_tasks WHERE kind='epistemic.review' AND json_extract(metadata, '$.knowledge_id')=?",
                (alpha["knowledge_id"],),
            ).fetchone()
            assert json.loads(alpha_task["metadata"]).get("action_attempts", 0) == 0
            assert database.execute("SELECT COUNT(*) FROM events WHERE kind='epistemic.automation.run'").fetchone()[0] == 1
        status = system.epistemic_actions.status()
        assert status["automatic"] and status["running"]
    finally:
        system.close()
        assert not system.epistemic_actions.is_running()

print("Kontinuum 29.0 epistemic automation tests passed")
