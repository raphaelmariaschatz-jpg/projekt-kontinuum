from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .canonical_knowledge_decision import CanonicalKnowledgeDecisionEngine
from .source_quality import SourceQualityClassifier


@dataclass(frozen=True)
class EvaluationReport:
    """Structured KEE report wrapper around the canonical CKDE decision."""

    status: str
    engine: str
    canonical_engine: str
    decision: str
    source_path: str
    evaluated_at: str
    read_only: bool
    no_automatic_memory_write: bool
    result: dict

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "engine": self.engine,
            "canonical_engine": self.canonical_engine,
            "decision": self.decision,
            "source_path": self.source_path,
            "evaluated_at": self.evaluated_at,
            "read_only": self.read_only,
            "no_automatic_memory_write": self.no_automatic_memory_write,
            "result": self.result,
        }


class SourceEvaluator:
    """KEE source evaluator backed by the canonical source quality classifier."""

    def __init__(self):
        self.classifier = SourceQualityClassifier()

    def evaluate(self, provenance: dict, content: str = "") -> dict:
        provenance = dict(provenance or {})
        return self.classifier.classify(
            str(provenance.get("url", "")),
            title=str(provenance.get("title", "")),
            text=content or str(provenance.get("summary", "")),
        )


class EvidenceEvaluator:
    """Evaluate minimal evidence and provenance completeness for KEE."""

    REQUIRED_PROVENANCE = CanonicalKnowledgeDecisionEngine.REQUIRED_PROVENANCE

    def evaluate(self, knowledge: dict) -> dict:
        item = dict(knowledge or {})
        provenance = dict(item.get("provenance") or item)
        content = str(item.get("content") or item.get("summary") or provenance.get("summary") or "")
        missing = [field for field in self.REQUIRED_PROVENANCE if not provenance.get(field)]
        return {
            "evidence_present": bool(content.strip()) and bool(provenance.get("sha256")),
            "provenance_complete": not missing,
            "missing_provenance": missing,
        }


class ConflictEvaluator:
    """Detect explicit unresolved conflicts without resolving them automatically."""

    def evaluate(self, knowledge: dict) -> dict:
        item = dict(knowledge or {})
        conflict = bool(item.get("conflict") or item.get("conflicts") or item.get("contradiction"))
        return {
            "conflict_detected": conflict,
            "automatic_resolution_allowed": False,
            "required_action": "governance_review" if conflict else "none",
        }


class GovernanceEvaluator:
    """Check the governance constraints that gate canonical knowledge adoption."""

    def __init__(self, project_root: str | Path):
        self.engine = CanonicalKnowledgeDecisionEngine(project_root)

    def evaluate(self, knowledge: dict) -> dict:
        item = dict(knowledge or {})
        provenance = dict(item.get("provenance") or item)
        governance_conform = self.engine._governance(provenance)
        return {
            "governance_conform": governance_conform,
            "no_direct_memory_write": True,
            "no_automatic_canonical_knowledge_adoption": True,
            "review_queue_required": True,
        }


class KnowledgeEvaluationEngine:
    """KEE 1.0 facade that delegates canonical decisions to CKDE 1.0.

    KEE remains a review-only quality layer. It never writes directly to canonical
    memory and never supersedes the CanonicalKnowledgeDecisionEngine.
    """

    VERSION = "KEE 1.0"
    CANONICAL_ENGINE = "CKDE 1.0"

    def __init__(self, project_root: str | Path, storage=None, release_version: str = "34.1"):
        self.root = Path(project_root).resolve()
        self.storage = storage
        self.release_version = release_version
        self.ckde = CanonicalKnowledgeDecisionEngine(self.root, storage=storage, release_version=release_version)
        self.source_evaluator = SourceEvaluator()
        self.evidence_evaluator = EvidenceEvaluator()
        self.conflict_evaluator = ConflictEvaluator()
        self.governance_evaluator = GovernanceEvaluator(self.root)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def evaluate(self, knowledge: dict) -> dict:
        return self.evaluate_knowledge(knowledge).to_dict()

    def evaluate_knowledge(self, knowledge: dict) -> EvaluationReport:
        item = dict(knowledge or {})
        provenance = dict(item.get("provenance") or item)
        content = str(item.get("content") or item.get("summary") or provenance.get("summary") or "")
        ckde_result = self.ckde.evaluate(item)
        kee_result = {
            "kee_version": self.VERSION,
            "canonical_engine": self.CANONICAL_ENGINE,
            "used_canonical_decision_engine": True,
            "source_evaluation": self.source_evaluator.evaluate(provenance, content),
            "evidence_evaluation": self.evidence_evaluator.evaluate(item),
            "conflict_evaluation": self.conflict_evaluator.evaluate(item),
            "governance_evaluation": self.governance_evaluator.evaluate(item),
            "ckde_result": ckde_result,
        }
        return EvaluationReport(
            status="evaluated",
            engine=self.VERSION,
            canonical_engine=self.CANONICAL_ENGINE,
            decision=str(ckde_result.get("decision", "REVIEW")),
            source_path=str(provenance.get("url") or provenance.get("source_path") or ""),
            evaluated_at=self._now(),
            read_only=True,
            no_automatic_memory_write=True,
            result=kee_result,
        )
