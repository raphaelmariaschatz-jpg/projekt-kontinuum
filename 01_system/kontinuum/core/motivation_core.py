from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone

from kontinuum.version import APP_VERSION


class MotivationCore:
    """Weights meaning without claiming will, desire, or consciousness."""

    VERSION = "1.0"

    def __init__(self, storage, meaning_core, foundation_decision, knowledge_intelligence):
        self.storage = storage
        self.meaning_core = meaning_core
        self.foundation_decision = foundation_decision
        self.knowledge_intelligence = knowledge_intelligence
        self.recalculate("system.startup")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def recalculate(self, reason: str = "manual") -> dict:
        scores = [
            *self._score_meaning_edges(),
            *self._score_goals(),
            *self._score_memories(),
            *self._score_gaps(),
            *self._score_self_questions(),
        ]
        report = {
            "motivation_core": True,
            "version": self.VERSION,
            "reason": reason,
            "scores": len(scores),
            "claim": "Funktionale Bedeutungsgewichtung; kein Wille, kein Bewusstsein.",
            "created_at": self._now(),
        }
        report_id = self._ensure_report("motivation.report", f"Motivation Core {APP_VERSION} Bewertungslauf", report)
        for score in scores:
            score["report_id"] = report_id
        self._ensure_scores(scores)
        return {"report_id": report_id, "scores": len(scores)}

    def status(self) -> dict:
        with self.storage.connect() as db:
            scores = int(db.execute(
                "SELECT COUNT(*) FROM motivation_scores WHERE json_extract(metadata, '$.motivation_core') = 1"
            ).fetchone()[0])
            reports = int(db.execute(
                "SELECT COUNT(*) FROM motivation_reports WHERE json_extract(metadata, '$.motivation_core') = 1"
            ).fetchone()[0])
            by_kind = {
                row["kind"]: int(row["count"])
                for row in db.execute(
                    """SELECT kind, COUNT(*) AS count FROM motivation_scores
                       WHERE json_extract(metadata, '$.motivation_core') = 1 GROUP BY kind"""
                ).fetchall()
            }
        return {
            "version": self.VERSION,
            "scores": scores,
            "reports": reports,
            "score_kinds": by_kind,
            "top": self.top(limit=5),
            "claim": "Motivation = gewichtete Bedeutung im Systemkontext, nicht Wille.",
        }

    def format_status(self) -> str:
        status = self.status()
        lines = [
            f"Motivation Core {APP_VERSION}:",
            f"- Bewertungseinträge: {status['scores']}",
            f"- Bewertungsläufe: {status['reports']}",
            f"- Kategorien: {status['score_kinds']}",
            "- Motivation = gewichtete Bedeutung im Systemkontext, nicht Wille.",
            "Zentrale Bewertungen:",
        ]
        for row in status["top"]:
            lines.append(f"- {row['score']:.2f} | {row['kind']} | {row['label']}")
        return "\n".join(lines)

    def format_priorities(self, category: str = "") -> str:
        rows = self.top(category=category, limit=12)
        if not rows:
            return "Keine Motivationsprioritäten gefunden."
        title = f"Motivationsprioritäten ({category}):" if category else "Motivationsprioritäten:"
        lines = [title]
        for row in rows:
            lines.append(f"- {row['score']:.2f} | {row['kind']} | {row['label']} | Grund: {row['reason']}")
        return "\n".join(lines)

    def top(self, category: str = "", limit: int = 10) -> list[dict]:
        params: list = []
        where = "WHERE json_extract(metadata, '$.motivation_core') = 1"
        if category:
            where += " AND kind = ?"
            params.append(category)
        params.append(max(25, limit * 8))
        with self.storage.connect() as db:
            rows = db.execute(
                f"""SELECT kind, content, metadata FROM motivation_scores
                    {where}
                    ORDER BY CAST(json_extract(metadata, '$.score') AS REAL) DESC, id DESC LIMIT ?""",
                tuple(params),
            ).fetchall()
        result = []
        for row in rows:
            metadata = self._metadata(row["metadata"])
            if not self._score_visible(row["kind"], row["content"], metadata):
                continue
            result.append({
                "kind": row["kind"],
                "subject": row["content"],
                "label": metadata.get("label", row["content"]),
                "score": float(metadata.get("score", 0.0)),
                "reason": metadata.get("reason", ""),
            })
            if len(result) >= max(1, limit):
                break
        return result

    def _score_visible(self, kind: str, content: str, metadata: dict) -> bool:
        if kind != "strategic_knowledge_gap":
            return True
        label = str(metadata.get("label", content))
        subject = f"{content} {label}"
        return not (
            self.knowledge_intelligence._is_foundation_knowledge(subject)
            or self.knowledge_intelligence._is_report_output(subject)
        )

    def _score_meaning_edges(self) -> list[dict]:
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT kind, content, metadata FROM meaning_edges
                   WHERE json_extract(metadata, '$.meaning_core') = 1"""
            ).fetchall()
        degree: dict[str, int] = {}
        parsed = []
        for row in rows:
            metadata = self._metadata(row["metadata"])
            source = metadata.get("source", "")
            target = metadata.get("target", "")
            degree[source] = degree.get(source, 0) + 1
            degree[target] = degree.get(target, 0) + 1
            parsed.append((row, metadata, source, target))
        scores = []
        for row, metadata, source, target in parsed:
            centrality = degree.get(source, 0) + degree.get(target, 0)
            relation_weight = {
                "principle_to_identity": 1.0,
                "principle_to_goal": 0.95,
                "goal_to_action": 0.8,
                "action_to_memory": 0.7,
                "memory_to_chronicle": 0.75,
                "chronicle_to_identity": 0.9,
            }.get(row["kind"], 0.5)
            score = min(1.0, relation_weight * math.log1p(centrality) / 5.0)
            scores.append(self._score(
                "central_meaning_relation",
                row["content"],
                metadata.get("relation", row["kind"]),
                score,
                f"Zentralität {centrality}, Relation {row['kind']}.",
            ))
        return scores

    def _score_goals(self) -> list[dict]:
        goals = self.foundation_decision.goals()
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT metadata FROM meaning_edges
                   WHERE kind IN ('principle_to_goal', 'goal_to_action')
                     AND json_extract(metadata, '$.meaning_core') = 1"""
            ).fetchall()
        support: dict[str, int] = {}
        for row in rows:
            metadata = self._metadata(row["metadata"])
            for key in ("source", "target"):
                value = metadata.get(key, "")
                if value.startswith("goal:"):
                    support[value.removeprefix("goal:")] = support.get(value.removeprefix("goal:"), 0) + 1
        scores = []
        for goal in goals:
            priority_weight = {"high": 1.0, "medium": 0.7, "low": 0.45}.get(goal.get("priority"), 0.5)
            support_count = support.get(goal["key"], 0)
            score = min(1.0, priority_weight * 0.55 + math.log1p(support_count) / 6.0)
            scores.append(self._score(
                "goal_support",
                goal["key"],
                goal.get("goal", goal["key"]),
                score,
                f"Priorität {goal.get('priority')}, {support_count} Bedeutungsstützen.",
            ))
        return scores

    def _score_memories(self) -> list[dict]:
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT content, metadata FROM meaning_nodes
                   WHERE kind = 'memory' AND json_extract(metadata, '$.meaning_core') = 1
                   ORDER BY id DESC LIMIT 200"""
            ).fetchall()
            edge_counts = {
                row["node"]: int(row["count"])
                for row in db.execute(
                    """SELECT json_extract(metadata, '$.target') AS node, COUNT(*) AS count
                       FROM meaning_edges WHERE json_extract(metadata, '$.target') LIKE 'memory:%'
                       GROUP BY node"""
                ).fetchall()
            }
        scores = []
        for row in rows:
            metadata = self._metadata(row["metadata"])
            count = edge_counts.get(row["content"], 0)
            content = metadata.get("label", row["content"])
            keyword_bonus = 0.25 if any(word in content.casefold() for word in ("identität", "kontinuit", "moral", "meaning", "bedeutung", "schöpfer")) else 0
            score = min(1.0, 0.25 + math.log1p(count) / 4.0 + keyword_bonus)
            scores.append(self._score(
                "formative_memory",
                row["content"],
                content[:220],
                score,
                f"{count} Bedeutungsbeziehungen plus inhaltliche Prägungsmarker.",
            ))
        return scores

    def _score_gaps(self) -> list[dict]:
        scores = []
        for index, gap in enumerate(self.knowledge_intelligence.knowledge_gaps()[:30], start=1):
            subject = str(gap.get("subject", "Wissenslücke"))
            marker_bonus = 0.25 if any(word in subject.casefold() for word in ("identität", "kontinuit", "moral", "wissen", "quelle", "selbst")) else 0
            score = max(0.1, min(1.0, 0.8 - (index - 1) * 0.015 + marker_bonus))
            scores.append(self._score(
                "strategic_knowledge_gap",
                subject,
                subject[:220],
                score,
                "Hohe strategische Bedeutung durch offene Wissenslücke und epistemische Priorität.",
            ))
        return scores

    def _score_self_questions(self) -> list[dict]:
        scores = []
        for question in self.foundation_decision.questions(30):
            label = question.get("question", "")
            basis_weight = {"knowledge_conflict": 1.0, "knowledge_gap": 0.85, "epistemic_reflection": 0.65}.get(question.get("basis"), 0.5)
            marker_bonus = 0.1 if any(word in label.casefold() for word in ("ich", "meiner", "selbst", "annahmen", "evidenz")) else 0
            score = min(1.0, basis_weight + marker_bonus)
            scores.append(self._score(
                "meaningful_self_question",
                f"self_question:{question['id']}",
                label,
                score,
                f"Grundlage {question.get('basis')} mit Evidenzpflicht.",
            ))
        return scores

    def _score(self, kind: str, subject: str, label: str, score: float, reason: str) -> dict:
        return {
            "kind": kind,
            "subject": subject,
            "label": label,
            "score": round(float(score), 4),
            "reason": reason,
            "motivation_core": True,
            "claim": "Funktionale Bedeutungsgewichtung; kein Wille, kein Bewusstsein.",
            "created_at": self._now(),
        }

    def _ensure_score(self, kind: str, subject: str, metadata: dict) -> int:
        with self.storage.connect() as db:
            existing = db.execute(
                "SELECT id FROM motivation_scores WHERE kind = ? AND content = ? LIMIT 1",
                (kind, subject),
            ).fetchone()
        if existing:
            return int(existing["id"])
        return self.storage.add("motivation_scores", kind, subject, metadata)

    def _ensure_scores(self, scores: list[dict]) -> int:
        if not scores:
            return 0
        now = self._now()
        added = 0
        with self.storage.connect() as db:
            existing = {
                (row["kind"], row["content"])
                for row in db.execute("SELECT kind, content FROM motivation_scores").fetchall()
            }
            for score in scores:
                key = (score["kind"], score["subject"])
                if key in existing:
                    continue
                try:
                    db.execute(
                        "INSERT INTO motivation_scores(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                        (
                            score["kind"],
                            score["subject"],
                            json.dumps(score, ensure_ascii=False),
                            now,
                        ),
                    )
                    added += 1
                    existing.add(key)
                except sqlite3.IntegrityError:
                    pass
            db.commit()
        return added

    def _ensure_report(self, kind: str, content: str, metadata: dict) -> int:
        with self.storage.connect() as db:
            existing = db.execute(
                "SELECT id FROM motivation_reports WHERE kind = ? AND content = ? LIMIT 1",
                (kind, content),
            ).fetchone()
        if existing:
            return int(existing["id"])
        return self.storage.add("motivation_reports", kind, content, metadata)

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value or "{}")
        except (TypeError, ValueError):
            return {}
