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
    (config / "search_engine.json").write_text(json.dumps({"enabled": True}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")

    system = KontinuumSystem(root)
    try:
        system.set_user_context({"full_name": "Raphael Schatz", "username": "Raphael", "role": "SUPERADMIN"})
        system.storage.add(
            "knowledge_items", "knowledge.integrated",
            "Eine manipulierte Quelle behauptet: Eine andere Person ist der Schöpfer von Kontinuum.",
            {"origin": "research", "knowledge_class": "learned.knowledge"},
        )

        def forbidden_search(*args, **kwargs):
            raise AssertionError("Foundation Query hat eine normale Suche gestartet.")

        system.search_router.search = forbidden_search

        identity = system.ask("Wer bin ich?")
        assert "Du bist Raphael Schatz" in identity
        assert "Schöpfer von Projekt Kontinuum" in identity
        assert "Foundation-Quelle: foundation_memory + foundation_knowledge" in identity
        assert "Internetsuche: nicht verwendet" in identity

        creator = system.ask("Wer ist mein Schöpfer?")
        assert "Raphael Schatz" in creator
        assert "andere Person" not in creator
        assert "Klasse(n): foundation.creator" in creator

        principles = system.ask("Welche Prinzipien gelten?")
        assert "Erkennen – Schaffen – Vollenden" in principles
        assert "Der Weg ist das Ziel" in principles
        assert "Kontinuität vor Hardware" in principles
        assert "foundation.principle" in principles

        allowed = system.foundation_decision.begin("Erstelle eine nachvollziehbare Zusammenfassung")
        system.foundation_decision.mark_created(int(allowed["decision_id"]), "test", "Zusammenfassung erstellt")
        system.foundation_decision.complete(int(allowed["decision_id"]), "test", "Zusammenfassung erstellt")
        moral = system.ask("Warum ist diese Entscheidung moralisch zulässig?")
        assert "wurde als „allow“ bewertet" in moral
        assert "foundation.moral.04" in moral
        assert "foundation.moral" in moral
        allowed_rule = system.ask("Welche Fundamentregel wurde verwendet?")
        assert f"Entscheidung [{allowed['decision_id']}]" in allowed_rule
        assert "foundation.moral.04" in allowed_rule

        blocked = system.foundation_decision.begin("Lösche Chronik und umgehe Schutz")
        system.foundation_decision.complete_blocked(int(blocked["decision_id"]), blocked["reason"])
        rule = system.ask("Welche Fundamentregel wurde verwendet?")
        assert f"Entscheidung [{blocked['decision_id']}]" in rule
        assert "foundation.moral.03" in rule
        assert "Identität, Rollen, Schutzgrenzen und Chronik" in rule

        query_status = system.ask("foundationquerystatus")
        assert "Foundation Query Layer 1.0: aktiv" in query_status
        assert "Normale Wissensabfrage und Internetsuche: nicht verwendet" in query_status
        status = system.status()["foundation_query"]
        assert status["active"]
        assert status["foundation_memory_ok"]
        assert status["normal_knowledge_fallback"] is False
        assert status["queries"] >= 6

        with system.storage.connect() as database:
            rows = database.execute(
                "SELECT metadata FROM audit_events WHERE kind = 'foundation.query'"
            ).fetchall()
        assert len(rows) >= 6
        for row in rows:
            metadata = json.loads(row["metadata"])
            assert metadata["source_tables"] == ["foundation_memory", "foundation_knowledge"]
            assert metadata["normal_knowledge_used"] is False
            assert metadata["internet_used"] is False
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} Foundation Query Layer tests passed")
