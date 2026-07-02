from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.continuous_canonical_engine import (  # noqa: E402
    DECISION_CLASSES,
    DRIFT_CLASSES,
    EVENT_SCHEMA_FIELDS,
    CanonicalEventSchema,
    ContinuousCanonicalEngine,
)
from kontinuum.version import APP_VERSION  # noqa: E402


def write_config(project: Path) -> None:
    (project / "24_config").mkdir(parents=True, exist_ok=True)
    config = {
        "version": "34.1",
        "engine_version": "1.0",
        "active": True,
        "mode": "diagnostic_report_only",
        "logs": {
            "canonical_events": "31_reports/events/canonical_events.jsonl",
            "event_processing": "31_reports/events/event_processing_log.jsonl",
            "drift_events": "31_reports/drift/drift_events.jsonl",
            "governance_hooks": "31_reports/governance/governance_hooks.jsonl",
        },
        "event_schema": list(EVENT_SCHEMA_FIELDS),
        "decision_classes": list(DECISION_CLASSES),
        "drift_classes": list(DRIFT_CLASSES),
        "release_gate": {"blocking_drift_classes": ["HIGH_DRIFT", "BLOCKING_DRIFT"]},
    }
    (project / "24_config/continuous_canonical_engine_34_1.json").write_text(
        json.dumps(config), encoding="utf-8"
    )


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    project = Path(temporary)
    write_config(project)
    engine = ContinuousCanonicalEngine(project, release_version="34.1", strict_config=True)

    event = engine.create_event(
        event_type="documentation.update",
        source_component="test",
        affected_path="14_documents/example.md",
        severity="info",
        payload={"expected_change": True},
        provenance={"actor": "test"},
    )
    assert set(EVENT_SCHEMA_FIELDS) == set(event)
    assert CanonicalEventSchema.validate(event)["ok"]

    appended = engine.append_event(event)
    assert appended["ok"]
    event_log = project / "31_reports/events/canonical_events.jsonl"
    first_size = event_log.stat().st_size
    engine.append_event(event)
    assert event_log.stat().st_size > first_size

    decision = engine.decide(event)
    assert decision["decision_class"] == "ACTIVE"
    drift = engine.classify_drift(event, decision)
    assert drift["drift_class"] == "EXPECTED_DRIFT"
    assert not engine.evaluate_hooks(event, decision, drift)

    missing_provenance = engine.create_event(
        event_type="artifact.change",
        source_component="test",
        affected_path="01_system/kontinuum/core/example.py",
        severity="medium",
        payload={"requires_review": True},
        provenance={},
    )
    result = engine.process_event(missing_provenance)
    assert result["decision"]["decision_class"] == "REVIEW_REQUIRED"
    assert result["drift"]["drift_class"] == "MEDIUM_DRIFT"
    assert any(hook["hook_type"] == "missing_provenance" for hook in result["hooks"])

    high = engine.create_event(
        event_type="release.gate",
        source_component="release_integrity",
        affected_path="01_system/kontinuum/core/release_integrity.py",
        severity="high",
        payload={"code_doc_conflict": True},
        provenance={"actor": "test"},
        governance_context={"release_relevant": True},
    )
    high_result = engine.process_event(high)
    assert high_result["drift"]["drift_class"] == "HIGH_DRIFT"
    assert not engine.gate_status()["ok"]
    assert engine.gate_status()["blocking_findings"]

    clean_project = Path(temporary) / "clean"
    write_config(clean_project)
    clean_engine = ContinuousCanonicalEngine(clean_project, release_version="34.1", strict_config=True)
    clean_result = clean_engine.process_event(event)
    assert clean_result["drift"]["drift_class"] == "EXPECTED_DRIFT"
    assert clean_engine.gate_status()["ok"]
    assert "Continuous Canonical Engine 1.0 Status" in clean_engine.format_status()

print(f"Kontinuum {APP_VERSION} Continuous Canonical Engine 34.1 tests passed")
