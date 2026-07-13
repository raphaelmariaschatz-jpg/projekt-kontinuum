from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path("C:/Projekt Kontinuum")
MODULE_PATH = ROOT / "12_agents" / "continuous_learning_governance_1_0.py"

spec = importlib.util.spec_from_file_location("continuous_learning_governance_1_0", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

ContinuousLearningGovernance10 = module.ContinuousLearningGovernance10


def proposal(proposal_id: str, status: str = "pending", confidence: float = 0.9) -> dict:
    return {
        "proposal_id": proposal_id,
        "status": status,
        "category": "verified_knowledge",
        "source_hash": "abc123",
        "timestamp": "2026-07-02T00:00:00+00:00",
        "confidence": confidence,
        "source_quality": "high",
        "risk_level": "low",
        "provenance": {
            "proposal_id": proposal_id,
            "source_id": "source-1",
            "source": "https://example.edu/source",
            "origin": "https://example.edu/source",
            "source_type": "text",
            "timestamp": "2026-07-02T00:00:00+00:00",
            "content_hash": "abc123",
            "source_quality": "high",
            "risk_level": "low",
            "agent_version": "1.2",
            "classification": "verified_knowledge",
        },
        "governance_events": [
            {"event": "Learning Proposal Created", "timestamp": "2026-07-02T00:00:00+00:00", "agent": "learning_agent_1_2"}
        ],
        "automatic_adoption_allowed": False,
        "writes_performed": False,
    }


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary)
    learning = root / "33_learning"
    learning.mkdir(parents=True, exist_ok=True)
    queue_path = learning / "learning_queue.json"
    history_path = learning / "learning_history.json"
    events_path = learning / "governance_events.json"
    queue_path.write_text(json.dumps([proposal("LRN-000001"), proposal("LRN-000002")]), encoding="utf-8")
    history_seed = [
        {"history_event": "proposal_created", "record": proposal("LRN-000001")},
        {"history_event": "proposal_created", "record": proposal("LRN-000002")},
    ]
    history_path.write_text(json.dumps(history_seed), encoding="utf-8")
    events_path.write_text("[]", encoding="utf-8")

    clg = ContinuousLearningGovernance10(root)
    assert clg.version == "1.0"
    assert clg.validate_transition("pending", "under_review")["ok"]
    assert clg.validate_transition("under_review", "approved")["ok"]
    assert clg.validate_transition("approved", "knowledge_handoff")["ok"]
    assert clg.validate_transition("knowledge_handoff", "memory_handoff")["ok"]
    assert clg.validate_transition("memory_handoff", "completed")["ok"]
    assert not clg.validate_transition("pending", "completed")["ok"]

    invalid = clg.transition_proposal("LRN-000001", "completed")
    assert not invalid["ok"]
    assert json.loads(history_path.read_text(encoding="utf-8")) == history_seed
    assert json.loads(events_path.read_text(encoding="utf-8")) == []

    assert clg.start_review("LRN-000001")["ok"]
    assert clg.approve("LRN-000001")["ok"]
    knowledge = clg.prepare_knowledge_handoff("LRN-000001")
    assert knowledge["ok"], knowledge
    memory = clg.prepare_memory_handoff("LRN-000001")
    assert memory["ok"], memory
    assert clg.complete("LRN-000001")["ok"]

    assert clg.start_review("LRN-000002")["ok"]
    rejected = clg.reject("LRN-000002")
    assert rejected["ok"], rejected
    assert clg.archive("LRN-000002")["ok"]

    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert queue[0]["status"] == "completed"
    assert queue[1]["status"] == "archived"
    assert json.loads(history_path.read_text(encoding="utf-8")) == history_seed

    events = json.loads(events_path.read_text(encoding="utf-8"))
    assert len(events) == 8
    assert len({event["event_id"] for event in events}) == len(events)
    assert all(event["timestamp"] for event in events)
    assert all(event["proposal_id"].startswith("LRN-") for event in events)
    assert all(event["component"] for event in events)
    assert all(event["description"] for event in events)
    assert {"GLE-002", "GLE-004", "GLE-005", "GLE-006", "GLE-007", "GLE-008", "GLE-009"}.issubset(
        {event["event_code"] for event in events}
    )
    assert knowledge["event"]["component"] == "Knowledge Agent"
    assert knowledge["event"]["knowledge_handoff_only"] is True
    assert memory["event"]["component"] == "Memory Agent"
    assert memory["event"]["memory_handoff_only"] is True
    assert all(event["drift_compatible"] for event in events)

    compliance = clg.check_canonical_compliance()
    assert compliance["ok"], compliance
    assert compliance["proposal_id_valid"]
    assert compliance["queue_consistent"]
    assert compliance["history_consistent"]
    assert compliance["provenance_complete"]
    assert compliance["confidence_present"]
    assert compliance["governance_events_present"]

    status = clg.status()
    assert status["governance_status"] == "compliant"
    assert status["metrics"]["completed_proposals"] == 1
    assert status["metrics"]["archivings"] == 1
    assert status["metrics"]["event_count"] == 8
    assert status["metrics"]["average_confidence"] == 0.9
    assert status["compatibility"]["cam"] == "handoff_only"
    assert status["compatibility"]["knowledge_agent"] == "handoff_only"
    assert status["compatibility"]["memory_agent"] == "handoff_only"

    assert clg.check_write_operation(root / "03_memory" / "memory.json", "write")["allowed"] is False
    assert clg.check_write_operation(root / "04_knowledge" / "knowledge.json", "write")["allowed"] is False
    assert clg.check_write_operation(root / "32_data" / "kontinuum.db", "write")["allowed"] is False
    assert not (root / "03_memory" / "memory.json").exists()
    assert not (root / "04_knowledge" / "knowledge.json").exists()
    assert not (root / "32_data" / "kontinuum.db").exists()

    before_events = json.loads(events_path.read_text(encoding="utf-8"))
    missing = clg.transition_proposal("LRN-999999", "under_review")
    assert not missing["ok"]
    after_events = json.loads(events_path.read_text(encoding="utf-8"))
    assert after_events == before_events

    report_path = clg.generate_status_report()
    assert report_path.is_file()
    report = report_path.read_text(encoding="utf-8")
    assert "Continuous Learning Governance 1.0 Status Report" in report
    assert "Governance Status" in report
    assert "Queue Status" in report
    assert "Proposal Lifecycle" in report
    assert "Anzahl Events: 8" in report
    assert "Compliance Score: 100" in report
    assert "Drift-Kompatibilitaet" in report
    assert "CAM-Kompatibilitaet" in report
    assert "Foundation-Kompatibilitaet" in report
    assert "Aktive Proposals" in report
    assert "Abgeschlossene Proposals: 1" in report
    assert "Wissensuebernahme: keine automatische Uebernahme" in report

print("Kontinuum Continuous Learning Governance 1.0 tests passed")
