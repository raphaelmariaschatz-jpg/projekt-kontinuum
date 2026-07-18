from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.media_learning import CanonicalMediaLearningFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.media_learning_framework
        assert isinstance(framework, CanonicalMediaLearningFramework)
        assert system.agent_config["media_learning_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["media_types"] == 7
        assert status["automatic_media_generation"] is False
        assert status["preference_persistence"] is False
        assert status["learner_profile"] is False
        assert status["decision_authority"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["media_learning_framework"]["active"] is True

        media = framework.list_media_types()
        assert [item["id"] for item in media] == [
            f"CMLF-M{index:02d}" for index in range(1, 8)
        ]

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        recommendation = framework.recommend(
            learning_goal="understand",
            topic_structure="relationship",
            complexity="medium",
            user_preference="CMLF-M03",
            evidence_need=True,
        )
        duplicate = framework.recommend(
            learning_goal="understand",
            topic_structure="relationship",
            complexity="medium",
            user_preference="CMLF-M03",
            evidence_need=True,
        )
        assert recommendation.recommendation_id == duplicate.recommendation_id
        assert recommendation.media_type_ids == ["CMLF-M02", "CMLF-M03"]
        assert recommendation.media_generated is False
        assert recommendation.preference_persisted is False
        assert recommendation.decision_authority is False

        reduced = framework.recommend(
            learning_goal="apply",
            topic_structure="action",
            complexity="high",
            user_preference="CMLF-M05",
            overload_risk=True,
            practical_prerequisites_met=True,
        )
        assert reduced.media_type_ids == ["CMLF-M06"]
        assert reduced.overload_reduced is True

        accessible = framework.recommend(
            learning_goal="understand",
            topic_structure="concept",
            complexity="low",
            accessibility_media="CMLF-M04",
        )
        assert accessible.media_type_ids == ["CMLF-M04"]

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        try:
            framework.recommend(
                learning_goal="score_user",
                topic_structure="concept",
                complexity="low",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Unsupported learning goal was accepted")
    finally:
        system.close()

print("Canonical Media Learning Framework 1.0 tests passed")
