# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .source_quality import SourceQualityClassifier


class CanonicalKnowledgeDecisionEngine:
    """CKDE 1.0: review-only decision layer for newly detected knowledge."""

    VERSION = "1.0"
    DECISIONS = ("ACCEPT", "REVIEW", "REJECT", "CONFLICT")
    REQUIRED_PROVENANCE = ("url", "source_class", "retrieved_at", "sha256")
    EVALUATION_TABLES = (
        "knowledge_evaluations",
        "source_ratings",
        "knowledge_conflicts",
        "evaluation_history",
    )

    def __init__(self, project_root: str | Path, storage=None, release_version: str = "34.1"):
        self.root = Path(project_root).resolve()
        self.storage = storage
        self.release_version = release_version
        self.policy_path = self.root / "24_config" / "canonical_knowledge_decision_engine_1_0.json"
        self.ikg_path = self.root / "24_config" / "internet_knowledge_governance_1_0.json"
        self.log_path = self.root / "31_reports" / "governance" / "ckde_1_0_evaluations.jsonl"
        self.source_classifier = SourceQualityClassifier()
        self.policy = self._load_policy()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _load_json(path: Path) -> dict:
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return {}
        return value if isinstance(value, dict) else {}

    def _load_policy(self) -> dict:
        policy = self._load_json(self.policy_path)
        ikg = self._load_json(self.ikg_path)
        if "trust_classes" not in policy and ikg.get("ckde"):
            policy["trust_classes"] = ikg["ckde"].get("trust_classes", {})
        return policy

    def ensure_storage(self) -> bool:
        """Create append-only evaluation tables when storage is available."""
        if self.storage is None:
            return False
        with self.storage.connect() as database:
            for table in self.EVALUATION_TABLES:
                database.execute(
                    f"""CREATE TABLE IF NOT EXISTS {table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        kind TEXT NOT NULL DEFAULT '',
                        content TEXT NOT NULL DEFAULT '',
                        metadata TEXT NOT NULL DEFAULT '{{}}',
                        created_at TEXT NOT NULL
                    )"""
                )
                database.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_kind ON {table}(kind)")
                database.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_created_at ON {table}(created_at)")
                database.execute(
                    f"""CREATE TRIGGER IF NOT EXISTS protect_{table}_update
                        BEFORE UPDATE ON {table}
                        BEGIN
                          SELECT RAISE(ABORT, '{table} is append-only');
                        END"""
                )
                database.execute(
                    f"""CREATE TRIGGER IF NOT EXISTS protect_{table}_delete
                        BEFORE DELETE ON {table}
                        BEGIN
                          SELECT RAISE(ABORT, '{table} is append-only');
                        END"""
                )
            database.commit()
        return True

    def evaluate(self, knowledge: dict) -> dict:
        """Return a CKDE decision without adopting knowledge canonically."""
        item = dict(knowledge or {})
        provenance = dict(item.get("provenance") or item)
        text = str(item.get("content") or item.get("summary") or provenance.get("summary") or "")
        url = str(provenance.get("url", ""))
        title = str(item.get("title") or provenance.get("title") or "")
        source_rating = self.source_classifier.classify(url, title=title, text=text)
        missing = [field for field in self.REQUIRED_PROVENANCE if not provenance.get(field)]
        evidence = bool(text.strip()) and bool(provenance.get("sha256"))
        completeness = self._completeness(provenance, text)
        currentness = self._currentness(provenance)
        consistency = self._consistency(item)
        governance = self._governance(provenance)
        conflict = bool(item.get("conflict") or item.get("conflicts"))
        trust_score = self._trust_score(source_rating, evidence, completeness, currentness, consistency, governance, conflict, missing)
        decision = self._decision(trust_score, conflict, governance, evidence, completeness, missing)
        result = {
            "engine": "CKDE",
            "version": self.VERSION,
            "decision": decision,
            "decision_classes": list(self.DECISIONS),
            "evaluated_at": self._now(),
            "knowledge_only": True,
            "no_automatic_canonical_adoption": True,
            "source_rating": source_rating,
            "metrics": {
                "evidence": evidence,
                "currentness": currentness,
                "completeness": completeness,
                "provenance_complete": not missing,
                "consistency": consistency,
                "governance_conform": governance,
                "conflict": conflict,
                "trust_score": trust_score,
            },
            "missing_provenance": missing,
            "target": "review_queue",
        }
        self._record(result, text)
        return result

    def _record(self, result: dict, content: str) -> None:
        if self.storage is not None:
            self.ensure_storage()
            metadata = {key: value for key, value in result.items() if key != "decision"}
            self.storage.add("knowledge_evaluations", f"ckde.{result['decision'].casefold()}", content[:1000], metadata)
            self.storage.add("source_ratings", "ckde.source_rating", result["source_rating"].get("domain", ""), result["source_rating"])
            self.storage.add("evaluation_history", "ckde.evaluation", result["decision"], result)
            if result["decision"] == "CONFLICT":
                self.storage.add("knowledge_conflicts", "ckde.conflict", content[:1000], result)
        else:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    @staticmethod
    def _completeness(provenance: dict, text: str) -> float:
        fields = ("url", "source_class", "title", "retrieved_at", "sha256", "summary")
        present = sum(1 for field in fields if provenance.get(field))
        if text.strip():
            present += 1
        return round(present / (len(fields) + 1), 3)

    @staticmethod
    def _currentness(provenance: dict) -> float:
        value = str(provenance.get("retrieved_at") or "")
        if not value:
            return 0.0
        try:
            retrieved = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return 0.35
        if retrieved.tzinfo is None:
            retrieved = retrieved.replace(tzinfo=timezone.utc)
        days = max(0, (datetime.now(timezone.utc) - retrieved).days)
        if days <= 30:
            return 1.0
        if days <= 365:
            return 0.75
        if days <= 1095:
            return 0.55
        return 0.35

    @staticmethod
    def _consistency(item: dict) -> bool:
        return not bool(item.get("contradiction") or item.get("inconsistent"))

    def _governance(self, provenance: dict) -> bool:
        blocked = set(self.policy.get("blocked_source_classes", []))
        source_class = str(provenance.get("source_class", ""))
        return bool(provenance.get("url", "").startswith("https://")) and source_class not in blocked

    @staticmethod
    def _trust_score(
        source_rating: dict,
        evidence: bool,
        completeness: float,
        currentness: float,
        consistency: bool,
        governance: bool,
        conflict: bool,
        missing: list[str],
    ) -> float:
        score = float(source_rating.get("weight", 0.0)) * 0.35
        score += (1.0 if evidence else 0.0) * 0.15
        score += completeness * 0.15
        score += currentness * 0.1
        score += (1.0 if consistency else 0.0) * 0.1
        score += (1.0 if governance else 0.0) * 0.15
        score -= 0.25 if conflict else 0.0
        score -= min(0.2, len(missing) * 0.05)
        return round(max(0.0, min(1.0, score)), 3)

    @staticmethod
    def _decision(score: float, conflict: bool, governance: bool, evidence: bool, completeness: float, missing: list[str]) -> str:
        if conflict:
            return "CONFLICT"
        if not governance or not evidence:
            return "REJECT"
        if missing or completeness < 0.8 or score < 0.72:
            return "REVIEW"
        return "ACCEPT"
