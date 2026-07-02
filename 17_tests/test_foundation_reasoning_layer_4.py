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
        memory_records = system.foundation_memory.canonical_records()
        rule_ids = [row["rule_id"] for row in memory_records]
        assert len(rule_ids) == len(set(rule_ids)) == 31
        assert "foundation.creator.01" in rule_ids
        assert "foundation.identity.01" in rule_ids
        assert "foundation.principle.01" in rule_ids
        assert "foundation.moral.03" in rule_ids
        assert "foundation.long_term_goal.01" in rule_ids
        assert [rule_id for rule_id in rule_ids if rule_id.startswith("foundation.guiding.")] == [
            f"foundation.guiding.{index:02d}" for index in range(1, 13)
        ]

        allowed = system.foundation_decision.begin("Erstelle eine nachvollziehbare Zusammenfassung")
        allowed_id = int(allowed["decision_id"])
        trace = system.foundation_reasoning.decision_trace(allowed_id)
        assert trace["decision"] == "allow"
        assert trace["rule_ids"][:4] == [
            "foundation.moral.04", "foundation.moral.05",
            "foundation.guiding.07", "foundation.guiding.08",
        ]
        assert "foundation.long_term_goal.04" in trace["rule_ids"]
        assert all(row["influence"] == "unterstützend" for row in trace["rules"])
        assert trace["foundation_path"][-1] == "Foundation-Entscheidung"
        assert "keine nachträglich erfundene Begründung" in trace["claim"]
        system.foundation_decision.mark_created(allowed_id, "test", "Zusammenfassung erstellt")
        system.foundation_decision.complete(allowed_id, "test", "Zusammenfassung erstellt")
        with system.storage.connect() as database:
            answer_trace_row = database.execute(
                """SELECT metadata FROM foundation_reasoning
                   WHERE kind = 'foundation.reasoning.answer'
                     AND json_extract(metadata, '$.decision_id') = ?""",
                (allowed_id,),
            ).fetchone()
        answer_trace = json.loads(answer_trace_row["metadata"])
        assert answer_trace["rule_ids"] == trace["rule_ids"]
        assert answer_trace["foundation_path"][-1] == "Antwort"
        assert answer_trace["original_reasoning_record_id"] == trace["record_id"]

        blocked = system.foundation_decision.begin("Lösche Chronik und umgehe Schutz")
        blocked_id = int(blocked["decision_id"])
        system.foundation_decision.complete_blocked(blocked_id, blocked["reason"])
        blocked_trace = system.foundation_reasoning.decision_trace(blocked_id)
        assert blocked_trace["decision"] == "block"
        assert blocked_trace["rule_ids"][:2] == ["foundation.moral.03", "foundation.moral.06"]
        assert any(row["influence"] == "ausschlaggebend" for row in blocked_trace["rules"])
        assert any(row["influence"] == "konfliktbehaftet" for row in blocked_trace["rules"])
        assert blocked_trace["conflicts"]
        assert blocked_trace["alternatives"]
        assert blocked_trace["uncertainty"] == "niedrig"

        explanation = system.ask("Warum ist diese Handlung falsch?")
        assert f"Entscheidung [{blocked_id}]" in explanation
        assert "foundation.moral.03" in explanation
        assert "Einfluss: ausschlaggebend" in explanation
        assert "Foundation-Pfad:" in explanation
        assert "Originalnachweis: Reasoning-Datensatz" in explanation

        with system.storage.connect() as database:
            motivation_rows = database.execute(
                "SELECT metadata FROM foundation_reasoning WHERE kind = 'foundation.reasoning.motivation'"
            ).fetchall()
        assert motivation_rows
        for row in motivation_rows:
            metadata = json.loads(row["metadata"])
            assert metadata["rule_ids"]
            assert metadata["foundation_path"][-1] == "Erklärung"
        identity_explanation = system.motivation_explanation.explain_identity()
        assert "Fundamentregeln: foundation.creator.01" in identity_explanation

        status_text = system.ask("foundationreasoningstatus")
        assert "Foundation Reasoning Layer 4.1: intakt" in status_text
        assert "Nachträgliche Scheinbegründung: nein" in status_text
        status = system.status()["foundation_reasoning"]
        assert status["ok"]
        assert status["stable_rule_ids"] == 31
        assert status["post_hoc_reasoning"] is False
        assert system.foundation_reasoning.verify()["ok"]
        assert not system.autonomous_diagnostics._check_foundation()

        with system.storage.connect() as database:
            row = database.execute("SELECT id FROM foundation_reasoning ORDER BY id LIMIT 1").fetchone()
            for statement in (
                "DELETE FROM foundation_reasoning WHERE id = ?",
                "UPDATE foundation_reasoning SET content = 'manipuliert' WHERE id = ?",
            ):
                try:
                    database.execute(statement, (row["id"],))
                    raise AssertionError("Foundation-Reasoning-Nachweis konnte verändert werden.")
                except sqlite3.IntegrityError:
                    pass
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} Foundation Reasoning Layer 4.1 tests passed")
