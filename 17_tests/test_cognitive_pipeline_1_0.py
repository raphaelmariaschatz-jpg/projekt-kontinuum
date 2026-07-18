from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.cognitive_pipeline import CanonicalCognitivePipeline
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        pipeline = system.cognitive_pipeline
        assert isinstance(pipeline, CanonicalCognitivePipeline)
        assert system.agent_config["cognitive_pipeline"] is pipeline
        status = pipeline.status()
        assert status["active"] is True
        assert status["mode"] == "explicit_audit_trace_only"
        assert status["stages"] == 9
        assert status["automatic_processing"] is False
        assert status["response_logic_change"] is False
        assert status["execution"] is False
        assert status["direct_memory_write"] is False
        assert status["registry_write"] is False
        assert system.status()["cognitive_pipeline"]["active"] is True

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'ccp_cognitive.trace'"
            ).fetchone()[0]

        trace = pipeline.build_trace(
            touched_stage_ids=["CCP-01", "CCP-02", "CCP-08"],
            correlation_id="request-001",
        )
        duplicate = pipeline.build_trace(
            touched_stage_ids=["CCP-01", "CCP-02", "CCP-08"],
            correlation_id="request-001",
        )
        assert trace.trace_id == duplicate.trace_id
        assert trace.touched_stage_ids == ["CCP-01", "CCP-02", "CCP-08"]
        assert len(trace.stages) == 9
        assert [stage.stage_id for stage in trace.stages] == [
            f"CCP-{index:02d}" for index in range(1, 10)
        ]
        assert trace.stages[0].status == "touched"
        assert trace.stages[2].status == "not_touched"
        assert trace.output_boundary == "audit_only"
        assert trace.execution_performed is False
        assert trace.memory_write_performed is False
        assert trace.registry_write_performed is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'ccp_cognitive.trace'"
            ).fetchone()[0] == events_before

        recorded = pipeline.record_trace(
            touched_stage_ids=["CCP-01", "CCP-09"],
            correlation_id="request-002",
        )
        assert recorded.touched_stage_ids == ["CCP-01", "CCP-09"]

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'ccp_cognitive.trace'"
            ).fetchone()[0] == events_before + 1

        try:
            pipeline.build_trace(touched_stage_ids=["CCP-10"])
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown CCP stage was accepted")
    finally:
        system.close()

print("Canonical Cognitive Pipeline 1.0 tests passed")
