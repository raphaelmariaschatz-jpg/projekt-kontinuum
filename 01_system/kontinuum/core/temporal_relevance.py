from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone

from kontinuum.version import APP_VERSION


class TemporalRelevanceCore:
    """Tracks relevance over time without rewriting historical records."""

    VERSION = "1.0"
    CLAIM = "Relevanz über Zeit; keine Löschung historischer Bedeutung, keine zirkuläre Motivationsbegründung."

    RELATION_WEIGHT = {
        "principle_to_identity": 1.0,
        "principle_to_goal": 0.95,
        "goal_to_action": 0.75,
        "action_to_memory": 0.6,
        "memory_to_chronicle": 0.7,
        "chronicle_to_identity": 0.9,
    }
    PROTECTED_RELATIONS = {"principle_to_identity", "principle_to_goal", "chronicle_to_identity"}
    MARKERS = ("identität", "kontinuit", "moral", "schöpfer", "schoepfer", "meaning", "bedeutung", "bewusstsein", "selbst")

    def __init__(self, storage, meaning_core, motivation_core, knowledge_intelligence):
        self.storage = storage
        self.meaning_core = meaning_core
        self.motivation_core = motivation_core
        self.knowledge_intelligence = knowledge_intelligence
        self.assess("system.startup")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).date().isoformat()

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value or "{}")
        except (TypeError, ValueError):
            return {}

    def assess(self, reason: str = "manual") -> dict:
        now = self._now()
        today = self._today()
        with self.storage.connect() as db:
            existing = {
                (row["kind"], row["content"])
                for row in db.execute("SELECT kind, content FROM relevance_assessments").fetchall()
            }
            edge_rows = db.execute(
                """SELECT id, kind, content, metadata, created_at FROM meaning_edges
                   WHERE json_extract(metadata, '$.meaning_core') = 1"""
            ).fetchall()
            chronicle_rows = db.execute(
                "SELECT id, kind, content, metadata, created_at FROM chronicle_entries ORDER BY id DESC LIMIT 250"
            ).fetchall()

            degree: dict[str, int] = {}
            parsed_edges = []
            for row in edge_rows:
                metadata = self._metadata(row["metadata"])
                source = metadata.get("source", "")
                target = metadata.get("target", "")
                degree[source] = degree.get(source, 0) + 1
                degree[target] = degree.get(target, 0) + 1
                parsed_edges.append((row, metadata, source, target))

            rows = []
            edge_status_counts = {"active": 0, "aging": 0, "obsolete_candidate": 0}
            for row, metadata, source, target in parsed_edges:
                content = f"meaning_edge:{row['id']}:{today}"
                if ("meaning_edge.relevance", content) in existing:
                    continue
                label = f"{metadata.get('source_label', source)} -> {metadata.get('target_label', target)}"
                centrality = degree.get(source, 0) + degree.get(target, 0)
                strength = self._edge_strength(row["kind"], row["created_at"], centrality, label)
                status = self._status_for(row["kind"], strength)
                edge_status_counts[status] += 1
                rows.append((
                    "meaning_edge.relevance",
                    content,
                    json.dumps(
                        {
                            "temporal_relevance_core": True,
                            "version": self.VERSION,
                            "meaning_edge_id": int(row["id"]),
                            "edge_kind": row["kind"],
                            "edge_content": row["content"],
                            "label": label,
                            "strength": strength,
                            "status": status,
                            "centrality": centrality,
                            "age_days": self._age_days(row["created_at"]),
                            "protected_relation": row["kind"] in self.PROTECTED_RELATIONS,
                            "reason": reason,
                            "claim": self.CLAIM,
                        },
                        ensure_ascii=False,
                    ),
                    now,
                ))

            chronicle_scores = []
            for row in chronicle_rows:
                content = f"chronicle:{row['id']}:{today}"
                if ("chronicle.importance", content) in existing:
                    continue
                importance = self._chronicle_importance(row["content"], row["kind"], row["created_at"])
                chronicle_scores.append(importance)
                rows.append((
                    "chronicle.importance",
                    content,
                    json.dumps(
                        {
                            "temporal_relevance_core": True,
                            "version": self.VERSION,
                            "chronicle_id": int(row["id"]),
                            "label": row["content"][:220],
                            "importance": importance,
                            "status": "formative" if importance >= 0.7 else "context" if importance >= 0.4 else "background",
                            "age_days": self._age_days(row["created_at"]),
                            "reason": "Chronikereignis nach Prägungsmarkern, Version/Milestone-Hinweisen und Zeitnähe bewertet.",
                            "claim": self.CLAIM,
                        },
                        ensure_ascii=False,
                    ),
                    now,
                ))

            gaps = self.knowledge_intelligence.knowledge_gaps()[:100]
            for index, gap in enumerate(gaps, start=1):
                subject = str(gap.get("subject", "Wissenslücke"))
                digest = hashlib.sha256(subject.encode("utf-8")).hexdigest()[:16]
                content = f"knowledge_gap:{digest}:{today}"
                if ("knowledge_gap.priority", content) in existing:
                    continue
                priority = self._gap_priority(subject, index)
                rows.append((
                    "knowledge_gap.priority",
                    content,
                    json.dumps(
                        {
                            "temporal_relevance_core": True,
                            "version": self.VERSION,
                            "subject": subject,
                            "priority": priority,
                            "rank": index,
                            "strategy": "Identität, Kontinuität, Moral, Quellen und Selbstmodell vor allgemeinen Lücken.",
                            "claim": self.CLAIM,
                        },
                        ensure_ascii=False,
                    ),
                    now,
                ))

            circularity = self._circularity_audit()
            content = f"circularity.guard:{today}"
            if ("circularity.guard", content) not in existing:
                rows.append((
                    "circularity.guard",
                    content,
                    json.dumps(
                        {
                            "temporal_relevance_core": True,
                            "version": self.VERSION,
                            "violations": circularity["violations"],
                            "checked": circularity["checked"],
                            "rule": "Meaning-Kanten und Motivation-Scores dürfen sich nicht gegenseitig als alleinige Begründung verwenden.",
                            "claim": self.CLAIM,
                        },
                        ensure_ascii=False,
                    ),
                    now,
                ))

            if rows:
                db.executemany(
                    "INSERT INTO relevance_assessments(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    rows,
                )
            report_content = f"temporal_relevance_report:{today}"
            report_exists = db.execute(
                "SELECT id FROM relevance_reports WHERE kind = 'relevance.report' AND content = ? LIMIT 1",
                (report_content,),
            ).fetchone()
            if not report_exists:
                db.execute(
                    "INSERT INTO relevance_reports(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    (
                        "relevance.report",
                        report_content,
                        json.dumps(
                            {
                                "temporal_relevance_core": True,
                                "version": self.VERSION,
                                "reason": reason,
                                "edge_status_counts": edge_status_counts,
                                "chronicle_assessed": len(chronicle_rows),
                                "knowledge_gaps_assessed": len(gaps),
                                "circularity": circularity,
                                "claim": self.CLAIM,
                            },
                            ensure_ascii=False,
                        ),
                        now,
                    ),
                )
            db.commit()
        return self.status()

    def status(self) -> dict:
        with self.storage.connect() as db:
            total = int(db.execute(
                "SELECT COUNT(*) FROM relevance_assessments WHERE json_extract(metadata, '$.temporal_relevance_core') = 1"
            ).fetchone()[0])
            by_kind = {
                row["kind"]: int(row["count"])
                for row in db.execute(
                    """SELECT kind, COUNT(*) AS count FROM relevance_assessments
                       WHERE json_extract(metadata, '$.temporal_relevance_core') = 1 GROUP BY kind"""
                ).fetchall()
            }
            latest_edges = db.execute(
                """SELECT metadata FROM relevance_assessments WHERE kind = 'meaning_edge.relevance'
                   ORDER BY id DESC LIMIT 10000"""
            ).fetchall()
            reports = int(db.execute("SELECT COUNT(*) FROM relevance_reports").fetchone()[0])
        latest_by_edge = {}
        for row in latest_edges:
            metadata = self._metadata(row["metadata"])
            latest_by_edge.setdefault(metadata.get("meaning_edge_id"), metadata)
        status_counts = {"active": 0, "aging": 0, "obsolete_candidate": 0}
        for metadata in latest_by_edge.values():
            status_counts[metadata.get("status", "active")] = status_counts.get(metadata.get("status", "active"), 0) + 1
        return {
            "version": self.VERSION,
            "assessments": total,
            "reports": reports,
            "by_kind": by_kind,
            "edge_status_counts": status_counts,
            "circularity_violations": self._latest_circularity_violations(),
            "claim": self.CLAIM,
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            f"Temporal Relevance Core {APP_VERSION}:\n"
            f"- Relevanzbewertungen: {status['assessments']}\n"
            f"- Berichte: {status['reports']}\n"
            f"- Kantenstatus: {status['edge_status_counts']}\n"
            f"- Kategorien: {status['by_kind']}\n"
            f"- Zirkularitätsverletzungen: {status['circularity_violations']}\n"
            "- Bedeutungskanten bleiben append-only; Relevanz wird zeitlich neu bewertet."
        )

    def format_chronicle_importance(self, limit: int = 10) -> str:
        rows = self._top("chronicle.importance", "$.importance", limit)
        if not rows:
            return "Noch keine Chronik-Relevanzbewertung vorhanden."
        lines = ["Prägende Chronikereignisse:"]
        for metadata in rows:
            lines.append(f"- {metadata.get('importance', 0):.2f} | {metadata.get('status')} | {metadata.get('label')}")
        return "\n".join(lines)

    def format_gap_priorities(self, limit: int = 10) -> str:
        rows = self._top("knowledge_gap.priority", "$.priority", limit)
        if not rows:
            return "Noch keine Wissenslücken-Priorisierung vorhanden."
        lines = ["Priorisierte Wissenslücken:"]
        for metadata in rows:
            lines.append(f"- {metadata.get('priority', 0):.2f} | Rang {metadata.get('rank')} | {metadata.get('subject')}")
        return "\n".join(lines)

    def format_inflation_risk(self) -> str:
        status = self.status()
        counts = status["edge_status_counts"]
        total = max(1, sum(counts.values()))
        aging_ratio = (counts.get("aging", 0) + counts.get("obsolete_candidate", 0)) / total
        return (
            "Bedeutungsinflationsprüfung:\n"
            f"- aktive Kanten: {counts.get('active', 0)}\n"
            f"- alternde Kanten: {counts.get('aging', 0)}\n"
            f"- Obsoleszenz-Kandidaten: {counts.get('obsolete_candidate', 0)}\n"
            f"- Alterungsquote: {aging_ratio:.2%}\n"
            "- Gegenmaßnahme: historische Kanten bleiben erhalten, aktuelle Relevanz wird getrennt und zeitlich bewertet."
        )

    def _top(self, kind: str, json_path: str, limit: int) -> list[dict]:
        with self.storage.connect() as db:
            rows = db.execute(
                f"""SELECT metadata FROM relevance_assessments WHERE kind = ?
                    ORDER BY CAST(json_extract(metadata, '{json_path}') AS REAL) DESC, id DESC LIMIT ?""",
                (kind, max(1, limit)),
            ).fetchall()
        return [self._metadata(row["metadata"]) for row in rows]

    def _edge_strength(self, kind: str, created_at: str, centrality: int, label: str) -> float:
        age_days = self._age_days(created_at)
        base = self.RELATION_WEIGHT.get(kind, 0.5)
        centrality_factor = min(1.0, 0.45 + math.log1p(max(0, centrality)) / 6.0)
        marker_bonus = 0.12 if any(marker in label.casefold() for marker in self.MARKERS) else 0.0
        if kind in self.PROTECTED_RELATIONS:
            decay = max(0.86, 1.0 - age_days / 3650.0)
        else:
            decay = max(0.35, 1.0 - age_days / 900.0)
        return round(max(0.01, min(1.0, (base * centrality_factor + marker_bonus) * decay)), 4)

    def _status_for(self, kind: str, strength: float) -> str:
        if kind in self.PROTECTED_RELATIONS:
            return "active"
        if strength < 0.25:
            return "obsolete_candidate"
        if strength < 0.45:
            return "aging"
        return "active"

    def _chronicle_importance(self, content: str, kind: str, created_at: str) -> float:
        text = f"{kind} {content}".casefold()
        marker_bonus = sum(0.08 for marker in self.MARKERS if marker in text)
        milestone_bonus = 0.2 if any(marker in text for marker in ("version", "release", "core", "schutz", "chronik", "testsuite")) else 0
        recency = max(0.05, 1.0 - self._age_days(created_at) / 1200.0)
        return round(max(0.01, min(1.0, 0.25 + marker_bonus + milestone_bonus + recency * 0.25)), 4)

    def _gap_priority(self, subject: str, index: int) -> float:
        marker_bonus = sum(0.06 for marker in self.MARKERS if marker in subject.casefold())
        rank_factor = max(0.05, 1.0 - (index - 1) / 120.0)
        return round(max(0.01, min(1.0, 0.35 + marker_bonus + rank_factor * 0.45)), 4)

    def _circularity_audit(self) -> dict:
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT metadata FROM motivation_explanations
                   WHERE json_extract(metadata, '$.motivation_explanation_core') = 1
                   ORDER BY id DESC LIMIT 500"""
            ).fetchall()
        violations = 0
        for row in rows:
            metadata = self._metadata(row["metadata"])
            summary = str(metadata.get("summary", "")).casefold()
            score_reason = str(metadata.get("score_reason", "")).casefold()
            if "motivation-score" in summary and not score_reason:
                violations += 1
        return {"checked": len(rows), "violations": violations}

    def _latest_circularity_violations(self) -> int:
        with self.storage.connect() as db:
            row = db.execute(
                """SELECT metadata FROM relevance_assessments WHERE kind = 'circularity.guard'
                   ORDER BY id DESC LIMIT 1"""
            ).fetchone()
        if not row:
            return 0
        return int(self._metadata(row["metadata"]).get("violations", 0))

    @staticmethod
    def _age_days(value: str) -> int:
        try:
            text = (value or "").replace("Z", "+00:00")
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return max(0, (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days)
        except (TypeError, ValueError):
            return 0
