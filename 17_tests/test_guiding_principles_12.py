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
        records = [
            row for row in system.foundation_memory.canonical_records()
            if row.get("guiding_principle")
        ]
        assert len(records) == 12
        assert [row["guiding_order"] for row in records] == list(range(1, 13))
        assert [row["rule_id"] for row in records] == [
            f"foundation.guiding.{index:02d}" for index in range(1, 13)
        ]
        assert all(row["policy_status"] == "active_provisional" for row in records)
        assert all(row["revocable"] is True for row in records)
        assert all(row["revocation_mode"] == "append_only_superseding_migration" for row in records)
        assert all(row["approval_reference"] == "creator-directive-2026-06-21" for row in records)

        principles = system.ask("Welche Prinzipien gelten?")
        assert "vorläufig und bis auf Widerruf" in principles
        for index in range(1, 13):
            assert f"foundation.guiding.{index:02d}" in principles

        # Append-only migrations retain history, but queries must expose only
        # the newest version of each stable Foundation key.
        with system.storage.connect() as database:
            guiding_rows = database.execute(
                """SELECT content, metadata FROM foundation_memory
                   WHERE kind = 'foundation.memory'
                     AND json_extract(metadata, '$.guiding_principle') = 1
                   ORDER BY id"""
            ).fetchall()
            for row in guiding_rows:
                metadata = json.loads(row["metadata"])
                database.execute(
                    "INSERT INTO foundation_memory(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    ("foundation.memory", row["content"], json.dumps(metadata, ensure_ascii=False), metadata["created_at"]),
                )
            database.commit()

        versioned_principles = system.ask("Welche Prinzipien gelten?")
        for index in range(1, 13):
            assert versioned_principles.count(f"foundation.guiding.{index:02d}") == 1

        classification = system.foundation_memory.classify(
            "Wissen ist nicht automatisch Wahrheit", system.foundation_knowledge_guard
        )
        assert classification["is_foundation"] is True
        assert classification["matched_key"] == "guiding.06_epistemic_distinction"

        decision = system.foundation_decision.begin("Prüfe Wissen und Unsicherheit nachvollziehbar")
        trace = system.foundation_reasoning.decision_trace(int(decision["decision_id"]))
        assert "foundation.guiding.06" in trace["rule_ids"]
        assert "foundation.guiding.08" in trace["rule_ids"]
        system.foundation_decision.complete(int(decision["decision_id"]), "test", "Prüfung abgeschlossen")

        integrity = system.foundation_integrity.verify()
        assert integrity["ok"]
        with system.storage.connect() as database:
            activation = database.execute(
                """SELECT metadata FROM audit_events
                   WHERE kind = 'foundation.change.activated'
                     AND content = 'guiding.principles'"""
            ).fetchone()
        assert activation is not None
        activation_metadata = json.loads(activation["metadata"])
        assert activation_metadata["authorization_basis"] == "explicit_creator_directive"
        assert activation_metadata["approval_reference"] == "creator-directive-2026-06-21"
        assert activation_metadata["principle_count"] == 12
        assert system.foundation_memory.verify()["ok"]
        assert system.foundation_reasoning.verify()["ok"]
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} guiding principles tests passed")
