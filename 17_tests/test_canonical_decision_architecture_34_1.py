from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_knowledge_decision import CanonicalKnowledgeDecisionEngine
from kontinuum.core.knowledge_evaluation_engine import (
    ConflictEvaluator,
    EvaluationReport,
    EvidenceEvaluator,
    GovernanceEvaluator,
    KnowledgeEvaluationEngine,
    SourceEvaluator,
)
from kontinuum.core.source_quality import SourceQualityClassifier
from kontinuum.core.storage import Storage


cde = json.loads((ROOT / "24_config" / "canonical_decision_engine_2_0.json").read_text(encoding="utf-8"))
ckde_policy = json.loads((ROOT / "24_config" / "canonical_knowledge_decision_engine_1_0.json").read_text(encoding="utf-8"))
ikg = json.loads((ROOT / "24_config" / "internet_knowledge_governance_1_0.json").read_text(encoding="utf-8"))

assert cde["version"] == "CDE 2.0"
assert "files" in cde["scope"]["responsible_for"]
assert "knowledge_objects" in cde["scope"]["not_responsible_for"]
assert cde["safety_rules"]["no_automatic_delete"] is True
assert cde["safety_rules"]["no_automatic_consolidation"] is True

assert ckde_policy["version"] == "CKDE 1.0"
assert "KEE 1.0" in ckde_policy["compatibility_aliases"]
assert ckde_policy["canonical_facade_classes"] == [
    "KnowledgeEvaluationEngine",
    "SourceEvaluator",
    "EvidenceEvaluator",
    "ConflictEvaluator",
    "GovernanceEvaluator",
    "EvaluationReport",
]
assert ckde_policy["decision_classes"] == ["ACCEPT", "REVIEW", "REJECT", "CONFLICT"]
assert "files" in ckde_policy["scope"]["not_responsible_for"]
assert "knowledge_objects" in ckde_policy["scope"]["responsible_for"]
assert ckde_policy["governance_rules"]["no_automatic_canonical_knowledge_adoption"] is True
assert list(ckde_policy["trust_classes"]) == ["A", "B", "C", "D", "E"]

assert ikg["ckde"]["policy"] == "24_config/canonical_knowledge_decision_engine_1_0.json"
assert ikg["ckde"]["decision_classes"] == ["ACCEPT", "REVIEW", "REJECT", "CONFLICT"]
assert "knowledge_evaluations" in ikg["ckde"]["append_only_storage"]

classifier = SourceQualityClassifier()
assert classifier.classify("https://mit.edu/research", "MIT", "University research")["trust_class"] == "A"
assert classifier.classify("https://publisher.example/book", "Book", "ISBN publisher")["trust_class"] == "B"
assert classifier.classify("https://reuters.com/story", "News", "News report")["trust_class"] == "C"
assert classifier.classify("https://reddit.com/r/test", "Forum", "Community")["trust_class"] == "D"
assert classifier.classify("https://example.org/page", "Page", "General")["trust_class"] == "E"

assert SourceEvaluator().evaluate({"url": "https://mit.edu/research", "title": "MIT"})["trust_class"] == "A"
assert EvidenceEvaluator().evaluate({"content": "Text", "provenance": {"sha256": "abc"}})["evidence_present"] is True
assert ConflictEvaluator().evaluate({"conflict": True})["conflict_detected"] is True
assert GovernanceEvaluator(ROOT).evaluate({"provenance": {"url": "https://example.org", "source_class": "public_documentation"}})[
    "no_automatic_canonical_knowledge_adoption"
] is True

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    storage = Storage(Path(temporary) / "kontinuum.db")
    engine = CanonicalKnowledgeDecisionEngine(ROOT, storage=storage)
    result = engine.evaluate(
        {
            "content": "Peer-reviewed journal article with stable evidence.",
            "provenance": {
                "url": "https://journal.example/paper",
                "source_class": "scientific_publication",
                "title": "Article",
                "retrieved_at": "2026-06-30T00:00:00+00:00",
                "sha256": "abc123",
                "summary": "Peer-reviewed journal article. DOI: 10.1/test",
            },
        }
    )
    assert result["decision"] in {"ACCEPT", "REVIEW"}
    assert result["no_automatic_canonical_adoption"] is True
    assert result["source_rating"]["trust_class"] == "A"

    kee = KnowledgeEvaluationEngine(ROOT, storage=storage)
    kee_report = kee.evaluate_knowledge(
        {
            "content": "Peer-reviewed journal article with stable evidence.",
            "provenance": {
                "url": "https://journal.example/paper",
                "source_class": "scientific_publication",
                "title": "Article",
                "retrieved_at": "2026-06-30T00:00:00+00:00",
                "sha256": "ghi789",
                "summary": "Peer-reviewed journal article. DOI: 10.1/test",
            },
        }
    )
    assert isinstance(kee_report, EvaluationReport)
    kee_dict = kee_report.to_dict()
    assert kee_dict["engine"] == "KEE 1.0"
    assert kee_dict["canonical_engine"] == "CKDE 1.0"
    assert kee_dict["read_only"] is True
    assert kee_dict["no_automatic_memory_write"] is True
    assert kee_dict["decision"] in {"ACCEPT", "REVIEW"}
    assert kee_dict["result"]["used_canonical_decision_engine"] is True

    conflict = engine.evaluate(
        {
            "content": "Conflicting claim.",
            "conflict": True,
            "provenance": {
                "url": "https://agency.gov/report",
                "source_class": "government",
                "title": "Report",
                "retrieved_at": "2026-06-30T00:00:00+00:00",
                "sha256": "def456",
                "summary": "Official report",
            },
        }
    )
    assert conflict["decision"] == "CONFLICT"

    with sqlite3.connect(Path(temporary) / "kontinuum.db") as database:
        tables = {
            row[0]
            for row in database.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        triggers = {
            row[0]
            for row in database.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        assert {"knowledge_evaluations", "source_ratings", "knowledge_conflicts", "evaluation_history"} <= tables
        assert "protect_knowledge_evaluations_update" in triggers
        assert database.execute("SELECT COUNT(*) FROM knowledge_evaluations").fetchone()[0] == 3
        assert database.execute("SELECT COUNT(*) FROM knowledge_conflicts").fetchone()[0] == 1
        assert database.execute("SELECT COUNT(*) FROM knowledge_items").fetchone()[0] == 0

print("Kontinuum 34.1 CDE/CKDE architecture tests passed")
