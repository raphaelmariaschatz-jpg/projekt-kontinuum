from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.human_interface import CanonicalHumanInterfaceFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.human_interface_framework
        assert isinstance(framework, CanonicalHumanInterfaceFramework)
        assert system.agent_config["human_interface_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["dimensions"] == 8
        assert status["flow_stages"] == 5
        assert status["quality_criteria"] == 7
        assert status["response_generation"] is False
        assert status["gui_control"] is False
        assert status["automatic_personalization"] is False
        assert status["preference_persistence"] is False
        assert status["decision_authority"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["human_interface_framework"]["active"] is True

        assert [item["id"] for item in framework.list_dimensions()] == [
            f"CHIF-{index:02d}" for index in range(1, 9)
        ]
        assert [item["stage"] for item in framework.list_interaction_flow()] == [
            f"CHIF-FLOW-{index:02d}" for index in range(1, 6)
        ]
        assert [item["id"] for item in framework.list_quality_criteria()] == [
            f"CHIF-QC-{index:02d}" for index in range(1, 8)
        ]

        with system.storage.connect() as database:
            memories_before = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        plan = framework.build_plan(
            goal="Explain an architecture choice",
            detail_level="detailed",
            uncertainty_present=True,
            assumptions=["The caller approved local analysis"],
            sources_required=True,
            accessibility_requirements=["plain_language", "text_alternative"],
            human_decision_required=True,
        )
        duplicate = framework.build_plan(
            goal="Explain an architecture choice",
            detail_level="detailed",
            uncertainty_present=True,
            assumptions=["The caller approved local analysis"],
            sources_required=True,
            accessibility_requirements=["plain_language", "text_alternative"],
            human_decision_required=True,
        )
        assert plan.plan_id == duplicate.plan_id
        assert plan.dimension_ids == [f"CHIF-{index:02d}" for index in range(1, 9)]
        assert plan.disclosures == [
            "state_assumptions",
            "mark_uncertainty",
            "state_missing_sources",
            "preserve_human_decision_authority",
            "do_not_use_persistent_context",
        ]
        assert plan.accessibility_requirements == ["plain_language", "text_alternative"]
        assert plan.response_generated is False
        assert plan.decision_generated is False
        assert plan.preference_persisted is False
        assert plan.direct_memory_write is False

        sourced = framework.build_plan(
            goal="Summarize evidence",
            supplied_sources=["source-a"],
            continuity_allowed=True,
        )
        assert sourced.disclosures == ["cite_supplied_sources"]

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        try:
            framework.build_plan(goal="", detail_level="brief")
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid CHIF plan input was accepted")
    finally:
        system.close()

print("Canonical Human Interface Framework 1.0 tests passed")
