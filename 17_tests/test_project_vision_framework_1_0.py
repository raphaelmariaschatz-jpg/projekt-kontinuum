from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.project_vision import CanonicalProjectVisionFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.project_vision_framework
        assert isinstance(framework, CanonicalProjectVisionFramework)
        assert system.agent_config["project_vision_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["abbreviation"] == "CPVF"
        assert status["cvf_reserved_for_visual_perception"] is True
        assert status["principles"] == 9
        assert status["goal_areas"] == 4
        assert status["decision_authority"] is False
        assert status["automatic_change"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["project_vision_framework"]["active"] is True

        catalog = framework.catalog()
        assert [item["id"] for item in catalog["principles"]] == [
            f"CPVF-P{index:02d}" for index in range(1, 10)
        ]
        assert len(catalog["long_term_goals"]) == 4

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'cpvf.alignment_review'"
            ).fetchone()[0]

        review = framework.assess_alignment(
            target_reference="framework-test",
            principle_checks={"CPVF-P01": True, "CPVF-P07": False},
        )
        duplicate = framework.assess_alignment(
            target_reference="framework-test",
            principle_checks={"CPVF-P01": True, "CPVF-P07": False},
        )
        assert review.review_id == duplicate.review_id
        assert review.status == "gaps_found"
        assert review.aligned_principle_ids == ["CPVF-P01"]
        assert review.gap_principle_ids == ["CPVF-P07"]
        assert len(review.unchecked_principle_ids) == 7
        assert review.governance_review_required is True
        assert review.decision_authority is False
        assert review.automatic_change_allowed is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'cpvf.alignment_review'"
            ).fetchone()[0] == events_before

        framework.record_alignment(
            target_reference="framework-record",
            principle_checks={item["id"]: True for item in catalog["principles"]},
        )
        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'cpvf.alignment_review'"
            ).fetchone()[0] == events_before + 1

        try:
            framework.assess_alignment(
                target_reference="invalid",
                principle_checks={"CVF-P01": True},
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Colliding CVF principle id was accepted")
    finally:
        system.close()

print("Canonical Project Vision Framework 1.0 tests passed")
