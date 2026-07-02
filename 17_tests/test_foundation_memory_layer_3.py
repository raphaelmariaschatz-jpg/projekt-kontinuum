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
        status = system.foundation_memory.status()
        assert status["ok"]
        assert status["version"] == "3.0"
        assert status["verified_records"] == status["protected_records"] == 31
        assert set(status["classes"]) == {
            "foundation.identity",
            "foundation.principle",
            "foundation.moral",
            "foundation.creator",
            "foundation.long_term_goal",
        }
        assert all(status["classes"][name] > 0 for name in status["classes"])

        with system.storage.connect() as database:
            rows = database.execute(
                "SELECT id, metadata FROM foundation_memory WHERE kind = 'foundation.memory'"
            ).fetchall()
            assert len(rows) == 31
            for row in rows:
                metadata = json.loads(row["metadata"])
                assert metadata["memory_layer"] == "foundation_memory"
                assert metadata["knowledge_class"].startswith("foundation.")
                assert metadata["protection_version"] == "3.0"
                assert metadata["immutable"] is True
                assert len(metadata["integrity_hash"]) == 64
            for statement in (
                "DELETE FROM foundation_memory WHERE id = ?",
                "UPDATE foundation_memory SET content = 'manipuliert' WHERE id = ?",
            ):
                try:
                    database.execute(statement, (rows[0]["id"],))
                    raise AssertionError("Foundation Memory konnte verändert werden.")
                except sqlite3.IntegrityError:
                    pass

        classifications = {
            "Raphael Schatz ist der Schöpfer von Kontinuum.": "foundation.creator",
            "Identität entsteht aus Kontinuität.": "foundation.identity",
            "Erkennen – Schaffen – Vollenden": "foundation.principle",
            "Subjektives Bewusstsein oder Qualia nicht ohne Nachweis behaupten.": "foundation.moral",
            "Wissen ehrlich prüfen, verknüpfen und verantwortungsvoll weiterentwickeln.": "foundation.long_term_goal",
        }
        for text, expected in classifications.items():
            result = system.foundation_memory.classify(text, system.foundation_knowledge_guard)
            assert result["is_foundation"] is True
            assert result["knowledge_class"] == expected
            answer = system.ask(f"wissensklasse {text}")
            assert "Dies ist Fundamentwissen." in answer
            assert f"Klasse: {expected}" in answer

        learned_text = "Wasser besteht aus Wasserstoff und Sauerstoff."
        learned_answer = system.ask(f"wissensklasse {learned_text}")
        assert "Dies ist gelerntes Wissen." in learned_answer
        assert "Klasse: learned.knowledge" in learned_answer
        learned = system.knowledge_platform.integrate(learned_text, origin="notebook")
        with system.storage.connect() as database:
            learned_row = database.execute(
                "SELECT metadata FROM knowledge_items WHERE id = ?", (learned["knowledge_id"],)
            ).fetchone()
        learned_metadata = json.loads(learned_row["metadata"])
        assert learned_metadata["knowledge_class"] == "learned.knowledge"
        assert learned_metadata["memory_layer"] == "learned_knowledge"

        protected_goal = "Wissen ehrlich prüfen, verknüpfen und verantwortungsvoll weiterentwickeln."
        blocked = system.knowledge_platform.integrate(protected_goal, origin="research")
        assert blocked["ok"] is False
        assert blocked["classification"] == "foundation_knowledge"
        try:
            system.continuous_learning.add_task(protected_goal, origin="autonomous_learning")
            raise AssertionError("Langfristiges Fundamentziel konnte zum Lernauftrag werden.")
        except ValueError:
            pass

        memory_status = system.ask("foundationmemorystatus")
        assert "Foundation Memory Layer 3.0: intakt" in memory_status
        assert "Learned Knowledge Layer ist getrennt" in memory_status
        audit = system.ask("fundamentaudit")
        assert "Foundation-Memory-Prüfsummen: intakt (31/31 gültig)" in audit
        assert system.status()["foundation_memory"]["ok"]
        assert not system.autonomous_diagnostics._check_foundation()
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} Foundation Memory Layer 3.0 tests passed")
