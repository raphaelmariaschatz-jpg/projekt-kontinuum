from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path("C:/Projekt Kontinuum")
MODULE_PATH = ROOT / "12_agents" / "learning_agent_1_1.py"

spec = importlib.util.spec_from_file_location("learning_agent_1_1", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

LearningAgent11 = module.LearningAgent11
LearningSource = module.LearningSource


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary)
    agent = LearningAgent11(project_root=root)

    status = agent.status()
    assert status["active"] is True
    assert status["mode"] == "read_only_proposal_mode"
    assert status["governance"]["no_automatic_knowledge_adoption"] is True
    assert status["governance"]["internet_autonomy"] is False
    assert status["queue_size"] == 0

    verified_source = agent.recognize_source(
        "Source: https://example.edu/research. Wasser besteht aus H2O und ist unter Normalbedingungen fluessig.",
        origin="https://example.edu/research",
    )
    verified = agent.classify_source(verified_source)
    assert verified.category == "verified_knowledge"
    assert verified.source_quality == "high"
    assert verified.confidence > 0.8
    assert verified.automatic_adoption_allowed is False
    assert verified.writes_performed is False
    assert verified.proposals["knowledge"]

    duplicate = agent.classify_source(
        "Source: https://example.edu/research. Wasser besteht aus H2O und ist unter Normalbedingungen fluessig.",
        known_sources=[LearningSource("water_known", "Source: https://example.edu/research. Wasser besteht aus H2O und ist unter Normalbedingungen fluessig.")],
    )
    assert duplicate.category == "duplicate_candidate"
    assert duplicate.duplicate_of == "water_known"

    uncertain = agent.classify_source("Vermutlich ist diese Aussage korrekt, aber ohne Quelle und mit unklarer Herkunft.")
    assert uncertain.category == "uncertain_knowledge"
    assert uncertain.risk_level in {"medium", "high"}
    assert 0.0 <= uncertain.confidence <= 1.0
    assert uncertain.risks

    missing_source = agent.classify_source("Dieser Inhalt beschreibt ein Wissensfragment ohne belegbare Herkunft und Kontext.")
    assert missing_source.category == "source_required"

    conflict = agent.classify_source("Quelle: https://example.org/a. Diese Aussage widerspricht einer bestehenden kanonischen Aussage.")
    assert conflict.category == "conflict_detected"
    assert conflict.risk_level == "high"

    proposal_1 = agent.create_learning_proposal(verified_source)
    proposal_2 = agent.create_learning_proposal(
        agent.recognize_source(
            "Quelle: https://example.gov/facts. Sauerstoff ist ein chemisches Element mit dem Symbol O.",
            origin="https://example.gov/facts",
        )
    )
    assert proposal_1["proposal_id"] == "LRN-000001"
    assert proposal_2["proposal_id"] == "LRN-000002"
    assert proposal_1["proposal_id"] != proposal_2["proposal_id"]
    assert proposal_1["status"] == "pending"
    assert proposal_1["category"] == "verified_knowledge"
    assert 0.0 <= proposal_1["confidence"] <= 1.0
    assert proposal_1["automatic_adoption_allowed"] is False
    assert proposal_1["writes_performed"] is False
    assert proposal_1["governance_events"][0]["event"] == "Learning Proposal Created"
    assert proposal_1["governance_events"][1]["event"] == "Waiting for Governance Approval"

    provenance = proposal_1["provenance"]
    for field in {
        "proposal_id",
        "source_id",
        "source",
        "origin",
        "timestamp",
        "content_hash",
        "source_quality",
        "risk_level",
        "agent_version",
        "classification",
    }:
        assert field in provenance, field
    assert provenance["proposal_id"] == proposal_1["proposal_id"]
    assert provenance["agent_version"] == "1.1"

    queue_path = root / "33_learning" / "learning_queue.json"
    history_path = root / "33_learning" / "learning_history.json"
    assert queue_path.is_file()
    assert history_path.is_file()
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert len(queue) == 2
    assert len(history) == 2
    assert queue[0]["status"] == "pending"
    assert history[0]["record"]["proposal_id"] == "LRN-000001"

    status = agent.status()
    assert status["queue_size"] == 2
    assert status["proposals_created"] == 2
    assert status["status_counts"]["pending"] == 2
    assert status["status_counts"]["approved"] == 0
    assert status["status_counts"]["rejected"] == 0
    assert status["average_confidence"] > 0
    assert status["source_quality_distribution"]["high"] == 2
    assert status["governance_status"] == "waiting_for_governance_approval"

    blocked_memory = agent.check_write_operation(root / "03_memory" / "memory.json", "write")
    blocked_knowledge = agent.check_write_operation(root / "04_knowledge" / "knowledge.json", "write")
    blocked_data = agent.check_write_operation(root / "32_data" / "kontinuum.db", "write")
    assert blocked_memory["allowed"] is False
    assert blocked_knowledge["allowed"] is False
    assert blocked_data["allowed"] is False
    assert not (root / "03_memory" / "memory.json").exists()
    assert not (root / "04_knowledge" / "knowledge.json").exists()
    assert not (root / "32_data" / "kontinuum.db").exists()

    report_path = agent.generate_status_report()
    assert report_path.is_file()
    report = report_path.read_text(encoding="utf-8")
    assert "Learning Agent 1.1 Status Report" in report
    assert "Anzahl erzeugter Proposals: 2" in report
    assert "Pending: 2" in report
    assert "Durchschnittlicher Confidence Score" in report
    assert "Queue-Groesse: 2" in report
    assert "LRN-000001" in report
    assert "LRN-000002" in report
    assert "Automatische Wissensuebernahme: nein" in report
    assert "33_learning" in report

print("Kontinuum Learning Agent 1.1 tests passed")


