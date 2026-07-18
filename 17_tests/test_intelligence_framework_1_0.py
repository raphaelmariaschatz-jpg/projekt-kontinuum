from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.intelligence_framework import CanonicalIntelligenceFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.intelligence_framework
        assert isinstance(framework, CanonicalIntelligenceFramework)
        assert system.agent_config["intelligence_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["mode"] == "explicit_audit_mapping_only"
        assert status["dimensions"] == 8
        assert status["metrics"] is False
        assert status["scoring"] is False
        assert status["decision_authority"] is False
        assert status["execution"] is False
        assert status["self_modification"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["intelligence_framework"]["active"] is True

        dimensions = framework.list_dimensions()
        assert [item["id"] for item in dimensions] == [
            f"CIF-{index:02d}" for index in range(1, 9)
        ]

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'cif.dimension_mapping'"
            ).fetchone()[0]

        mapping = framework.build_mapping(
            touched_dimension_ids=["CIF-01", "CIF-03", "CIF-07"],
            correlation_id="request-001",
        )
        duplicate = framework.build_mapping(
            touched_dimension_ids=["CIF-01", "CIF-03", "CIF-07"],
            correlation_id="request-001",
        )
        assert mapping.mapping_id == duplicate.mapping_id
        assert mapping.touched_dimension_ids == ["CIF-01", "CIF-03", "CIF-07"]
        assert [item["id"] for item in mapping.dimensions] == mapping.touched_dimension_ids
        assert mapping.output_boundary == "audit_only"
        assert mapping.score_generated is False
        assert mapping.decision_generated is False
        assert mapping.execution_performed is False
        assert mapping.self_modification_performed is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'cif.dimension_mapping'"
            ).fetchone()[0] == events_before

        framework.record_mapping(
            touched_dimension_ids=["CIF-02", "CIF-04"],
            correlation_id="request-002",
        )
        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'cif.dimension_mapping'"
            ).fetchone()[0] == events_before + 1

        try:
            framework.build_mapping(touched_dimension_ids=["CIF-09"])
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown CIF dimension was accepted")
    finally:
        system.close()

print("Canonical Intelligence Framework 1.0 tests passed")
