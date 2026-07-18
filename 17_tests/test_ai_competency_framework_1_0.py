from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.ai_competency_framework import (
    CanonicalAICompetencyFramework,
)
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.ai_competency_framework
        assert isinstance(framework, CanonicalAICompetencyFramework)
        assert system.agent_config["ai_competency_framework"] is framework

        status = framework.status()
        assert status["active"] is True
        assert status["mode"] == "read_only_competency_catalog"
        assert status["competency_areas"] == 4
        assert status["automatic_assessment"] is False
        assert status["learner_profile_persistence"] is False
        assert status["memory_handoff"] is False
        assert system.status()["ai_competency_framework"]["active"] is True

        areas = framework.list_areas()
        assert [area["id"] for area in areas] == [
            "CAICF-ENGAGE",
            "CAICF-CREATE",
            "CAICF-MANAGE",
            "CAICF-DESIGN",
        ]

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()[0]

        focus = framework.plan_focus(
            area_id="CAICF-ENGAGE",
            dimension="skills",
        )
        duplicate = framework.plan_focus(
            area_id="CAICF-ENGAGE",
            dimension="skills",
        )
        assert focus.focus_id == duplicate.focus_id
        assert focus.area_name == "Engage with AI"
        assert focus.dimension == "skills"
        assert focus.progression_basis == "individual_knowledge_state"
        assert focus.evidence_required is True
        assert focus.review_required is True
        assert focus.automatic_assessment is False
        assert focus.persistence_allowed is False
        assert focus.learning_targets

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        try:
            framework.plan_focus(area_id="CAICF-UNKNOWN", dimension="skills")
        except KeyError:
            pass
        else:
            raise AssertionError("Unknown CAICF area was accepted")

        try:
            framework.plan_focus(area_id="CAICF-ENGAGE", dimension="age")
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown CAICF dimension was accepted")
    finally:
        system.close()

print("Canonical AI Competency Framework 1.0 tests passed")
