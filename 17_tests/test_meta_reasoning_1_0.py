from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.meta_reasoning import MetaReasoningEngine
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        engine = system.meta_reasoning
        assert isinstance(engine, MetaReasoningEngine)
        assert system.agent_config["meta_reasoning"] is engine
        assert system.status()["meta_reasoning"]["active"] is True
        assert engine.status()["automatic_live_review"] is False
        assert engine.status()["direct_memory_write"] is False

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'meta_reasoning.review'"
            ).fetchone()[0]

        assessment = engine.assess(
            target_type="plan",
            target_reference="plan-001",
            reasoning_summary="Use the existing manager pattern.",
            assumptions=["The manager contract remains stable."],
            uncertainties=["Integration timing is not verified."],
            alternatives_reviewed=["Create a parallel service."],
            preferred_path_rationale="The existing pattern avoids duplication.",
            governance_checks={"foundation": True, "release_integrity": True},
        )
        duplicate = engine.assess(
            target_type="plan",
            target_reference="plan-001",
            reasoning_summary="Use the existing manager pattern.",
            assumptions=["The manager contract remains stable."],
            uncertainties=["Integration timing is not verified."],
            alternatives_reviewed=["Create a parallel service."],
            preferred_path_rationale="The existing pattern avoids duplication.",
            governance_checks={"foundation": True, "release_integrity": True},
        )
        assert assessment.review_id == duplicate.review_id
        assert assessment.confidence == "medium"
        assert assessment.governance_alignment["status"] == "aligned"
        assert assessment.revision_trigger["required"] is True
        assert assessment.output_boundary == "review_only"

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'meta_reasoning.review'"
            ).fetchone()[0] == events_before

        recorded = engine.review(
            target_type="decision",
            target_reference="decision-001",
            reasoning_summary="Proceed only after the required check.",
            governance_checks={"foundation": True, "release_integrity": False},
        )
        assert recorded.confidence == "low"
        assert recorded.governance_alignment["status"] == "blocked"
        assert recorded.governance_alignment["decision_authority"] is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'meta_reasoning.review'"
            ).fetchone()[0] == events_before + 1

        try:
            engine.assess(
                target_type="unknown",
                target_reference="invalid",
                reasoning_summary="Invalid target type.",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown target type was accepted")
    finally:
        system.close()

print("Meta-Reasoning 1.0 tests passed")
