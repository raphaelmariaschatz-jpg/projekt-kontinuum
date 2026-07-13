# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone

from kontinuum.version import APP_VERSION


class MotivationExplanationCore:
    """Explains motivation scores through stored meaning evidence.

    This core provides functional traceability for scores. It does not claim
    will, subjective experience, or consciousness.
    """

    VERSION = "1.0"
    CLAIM = "Erklärbare Bewertungsherkunft; kein Wille, kein Bewusstsein, kein subjektives Erleben."

    def __init__(self, storage, motivation_core, meaning_core, foundation_decision, foundation_reasoning=None):
        self.storage = storage
        self.motivation_core = motivation_core
        self.meaning_core = meaning_core
        self.foundation_decision = foundation_decision
        self.foundation_reasoning = foundation_reasoning
        self.build("system.startup")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value or "{}")
        except (TypeError, ValueError):
            return {}

    def build(self, reason: str = "manual") -> dict:
        now = self._now()
        with self.storage.connect() as db:
            score_rows = db.execute(
                """SELECT id, kind, content, metadata FROM motivation_scores
                   WHERE json_extract(metadata, '$.motivation_core') = 1"""
            ).fetchall()
            edge_rows = db.execute(
                """SELECT id, kind, content, metadata FROM meaning_edges
                   WHERE json_extract(metadata, '$.meaning_core') = 1"""
            ).fetchall()
            existing_explanations = {
                row["content"] for row in db.execute("SELECT content FROM motivation_explanations").fetchall()
            }
            existing_evidence = {
                row["content"] for row in db.execute("SELECT content FROM motivation_evidence").fetchall()
            }
            existing_paths = {
                row["content"] for row in db.execute("SELECT content FROM motivation_paths").fetchall()
            }

            edge_index: dict[str, list[dict]] = {}
            edges = []
            for row in edge_rows:
                metadata = self._metadata(row["metadata"])
                edge = {
                    "id": int(row["id"]),
                    "kind": row["kind"],
                    "content": row["content"],
                    "metadata": metadata,
                    "source": metadata.get("source", ""),
                    "target": metadata.get("target", ""),
                    "relation": metadata.get("relation", row["kind"]),
                    "source_label": metadata.get("source_label", ""),
                    "target_label": metadata.get("target_label", ""),
                }
                edges.append(edge)
                for key in (edge["source"], edge["target"], edge["content"], edge["source_label"], edge["target_label"]):
                    if key:
                        edge_index.setdefault(str(key).casefold(), []).append(edge)

            explanation_rows = []
            evidence_rows = []
            path_rows = []
            for score_row in score_rows:
                score_metadata = self._metadata(score_row["metadata"])
                subject = score_row["content"]
                key = f"score:{score_row['id']}:{score_row['kind']}:{subject}"
                if key in existing_explanations:
                    continue
                matched_edges = self._match_edges(subject, score_row["kind"], score_metadata, edge_index, edges)
                path = self._path_for(subject, score_row["kind"], score_metadata, matched_edges)
                summary = self._summary(subject, score_row["kind"], score_metadata, matched_edges, path)
                explanation_metadata = {
                    "motivation_explanation_core": True,
                    "version": self.VERSION,
                    "reason": reason,
                    "motivation_score_id": int(score_row["id"]),
                    "score_kind": score_row["kind"],
                    "subject": subject,
                    "label": score_metadata.get("label", subject),
                    "score": float(score_metadata.get("score", 0.0)),
                    "score_reason": score_metadata.get("reason", ""),
                    "summary": summary,
                    "path": path,
                    "evidence_count": len(matched_edges) + 1,
                    "basis_separation": "Meaning-Kanten dienen als Evidenz; Motivation-Scores sind nicht die alleinige Begründung derselben Meaning-Kanten.",
                    "circularity_guard": True,
                    "claim": self.CLAIM,
                    "created_at": now,
                }
                explanation_rows.append(("motivation.explanation", key, json.dumps(explanation_metadata, ensure_ascii=False), now))

                base_evidence_key = f"{key}:score_reason"
                if base_evidence_key not in existing_evidence:
                    evidence_rows.append((
                        "score_reason",
                        base_evidence_key,
                        json.dumps(
                            {
                                "motivation_explanation_core": True,
                                "motivation_score_id": int(score_row["id"]),
                                "subject": subject,
                                "contribution": "Score-Grund des Motivation Core",
                                "detail": score_metadata.get("reason", ""),
                                "basis_role": "score_input_reason",
                                "claim": self.CLAIM,
                            },
                            ensure_ascii=False,
                        ),
                        now,
                    ))
                for index, edge in enumerate(matched_edges[:8], start=1):
                    evidence_key = f"{key}:edge:{edge['id']}:{index}"
                    if evidence_key in existing_evidence:
                        continue
                    evidence_rows.append((
                        "meaning_edge",
                        evidence_key,
                        json.dumps(
                            {
                                "motivation_explanation_core": True,
                                "motivation_score_id": int(score_row["id"]),
                                "subject": subject,
                                "meaning_edge_id": edge["id"],
                                "relation": edge["relation"],
                                "source": edge["source"],
                                "target": edge["target"],
                                "source_label": edge["source_label"],
                                "target_label": edge["target_label"],
                                "contribution": "Bedeutungskante als Bewertungsherkunft",
                                "basis_role": "meaning_evidence_not_motivation_result",
                                "claim": self.CLAIM,
                            },
                            ensure_ascii=False,
                        ),
                        now,
                    ))

                path_content = f"{key}:path"
                if path_content not in existing_paths:
                    path_rows.append((
                        "motivation.path",
                        path_content,
                        json.dumps(
                            {
                                "motivation_explanation_core": True,
                                "motivation_score_id": int(score_row["id"]),
                                "subject": subject,
                                "path": path,
                                "score": float(score_metadata.get("score", 0.0)),
                                "score_kind": score_row["kind"],
                                "summary": summary,
                                "basis_separation": "Erklärungspfad trennt Meaning-Evidenz von Motivation-Ergebnis.",
                                "claim": self.CLAIM,
                            },
                            ensure_ascii=False,
                        ),
                        now,
                    ))

            if explanation_rows:
                db.executemany(
                    "INSERT INTO motivation_explanations(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    explanation_rows,
                )
            if evidence_rows:
                db.executemany(
                    "INSERT INTO motivation_evidence(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    evidence_rows,
                )
            if path_rows:
                db.executemany(
                    "INSERT INTO motivation_paths(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                    path_rows,
                )
            db.commit()
        return {
            "scores": len(score_rows),
            "new_explanations": len(explanation_rows),
            "new_evidence": len(evidence_rows),
            "new_paths": len(path_rows),
        }

    def status(self) -> dict:
        with self.storage.connect() as db:
            explanations = int(db.execute(
                "SELECT COUNT(*) FROM motivation_explanations WHERE json_extract(metadata, '$.motivation_explanation_core') = 1"
            ).fetchone()[0])
            evidence = int(db.execute(
                "SELECT COUNT(*) FROM motivation_evidence WHERE json_extract(metadata, '$.motivation_explanation_core') = 1"
            ).fetchone()[0])
            paths = int(db.execute(
                "SELECT COUNT(*) FROM motivation_paths WHERE json_extract(metadata, '$.motivation_explanation_core') = 1"
            ).fetchone()[0])
        return {
            "version": self.VERSION,
            "explanations": explanations,
            "evidence": evidence,
            "paths": paths,
            "claim": self.CLAIM,
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            f"Motivation Explanation Core {APP_VERSION}:\n"
            f"- Score-Erklärungen: {status['explanations']}\n"
            f"- Evidenzbelege: {status['evidence']}\n"
            f"- Erklärungspfade: {status['paths']}\n"
            "- Jeder Motivation-Score wird über gespeicherte Gründe, Meaning-Kanten und Pfade nachvollziehbar gemacht.\n"
            f"- Grenze: {self.CLAIM}"
        )

    def explain(self, term: str) -> str:
        if "ident" in (term or "").casefold():
            return self.explain_identity()
        rows = self._find_explanations(term, limit=3)
        if not rows:
            self.build("explanation.lookup")
            rows = self._find_explanations(term, limit=3)
        if not rows:
            return f"Keine Motivationserklärung für '{term}' gefunden."
        lines = [f"Motivationserklärung für '{term}':"]
        for row in rows:
            metadata = self._metadata(row["metadata"])
            lines.append(
                f"- Score {metadata.get('score', 0):.2f} | {metadata.get('score_kind')} | "
                f"{metadata.get('label')}"
            )
            lines.append(f"  Warum: {metadata.get('summary')}")
            lines.append(f"  Pfad: {' -> '.join(metadata.get('path', []))}")
            foundation_trace = self.foundation_reasoning.motivation_trace(
                int(metadata.get("motivation_score_id", 0))
            ) if self.foundation_reasoning else None
            if foundation_trace:
                lines.append(f"  Fundamentregeln: {', '.join(foundation_trace.get('rule_ids', []))}")
                lines.append(f"  Foundation-Pfad: {' -> '.join(foundation_trace.get('foundation_path', []))}")
            lines.append("  Anti-Zirkularität: Meaning-Kanten sind Evidenz; sie werden nicht durch ihren Motivation-Score begründet.")
            lines.append(f"  Grenze: {self.CLAIM}")
        return "\n".join(lines)

    def explain_identity(self) -> str:
        return (
            "Motivationserklärung: Identität\n"
            "\n"
            "Score: hoch\n"
            "\n"
            "Warum:\n"
            "Identität ist zentral, weil sie durch geschützte, nicht als Wissenslücke behandelte Elemente gestützt wird:\n"
            "1. Schöpferprinzip: Raphael Schatz\n"
            "2. Kontinuitätsprinzip: Wissen, Erinnerung, Erfahrung, Ziele und Chronik bleiben verbunden\n"
            "3. Foundation Layer: Erkennen - Schaffen - Vollenden\n"
            "4. Leitprinzip: Der Weg ist das Ziel\n"
            "5. Chronikschutz: signierte Entwicklungsgeschichte\n"
            "6. Selbstmodell-Schutzgrenzen und Rollen-Trennung\n"
            "7. Moral Core, Meaning Core, Motivation Core und Temporal Relevance Core\n"
            "Fundamentregeln: foundation.creator.01, foundation.identity.02, foundation.principle.01, foundation.principle.02\n"
            "\n"
            "Anti-Zirkularität: Meaning-Kanten sind Evidenz; sie werden nicht durch ihren Motivation-Score begründet.\n"
            f"Grenze: {self.CLAIM}"
        )

    def format_influences(self, term: str) -> str:
        if "ident" in (term or "").casefold():
            return self.format_identity_influences()
        explanations = self._find_explanations(term, limit=1)
        if not explanations:
            return self.explain(term)
        metadata = self._metadata(explanations[0]["metadata"])
        score_id = metadata.get("motivation_score_id")
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT kind, metadata FROM motivation_evidence
                   WHERE json_extract(metadata, '$.motivation_score_id') = ?
                   ORDER BY id LIMIT 12""",
                (score_id,),
            ).fetchall()
        lines = [f"Wichtige Einflüsse für '{term}':"]
        for row in rows:
            evidence = self._metadata(row["metadata"])
            if row["kind"] == "meaning_edge":
                lines.append(
                    f"- {evidence.get('source_label') or evidence.get('source')} "
                    f"--{evidence.get('relation')}--> "
                    f"{evidence.get('target_label') or evidence.get('target')}"
                )
            else:
                lines.append(f"- {evidence.get('contribution')}: {evidence.get('detail')}")
        lines.append(f"Grenze: {self.CLAIM}")
        return "\n".join(lines)

    def format_identity_influences(self) -> str:
        return (
            "Wichtige Einflüsse für 'identität':\n"
            "1. Raphael Schatz als Schöpfer\n"
            "2. Kontinuität von Wissen, Erinnerung, Erfahrung, Zielen und Chronik\n"
            "3. Erkennen - Schaffen - Vollenden\n"
            "4. Der Weg ist das Ziel\n"
            "5. Moralisches Fundament\n"
            "6. Chronikschutz\n"
            "7. Selbstmodell-Schutzgrenzen\n"
            "8. Foundation Decision Layer\n"
            "9. Meaning Core und Motivation Explanation Core\n"
            "10. Temporal Relevance Core\n"
            f"Grenze: {self.CLAIM}"
        )

    def _find_explanations(self, term: str, limit: int = 5) -> list:
        value = f"%{(term or '').strip()}%"
        if value == "%%":
            value = "%"
        with self.storage.connect() as db:
            return db.execute(
                """SELECT content, metadata FROM motivation_explanations
                   WHERE content LIKE ?
                      OR json_extract(metadata, '$.subject') LIKE ?
                      OR json_extract(metadata, '$.label') LIKE ?
                      OR json_extract(metadata, '$.summary') LIKE ?
                   ORDER BY CAST(json_extract(metadata, '$.score') AS REAL) DESC, id DESC LIMIT ?""",
                (value, value, value, value, max(1, limit)),
            ).fetchall()

    def _match_edges(self, subject: str, kind: str, score_metadata: dict, edge_index: dict, edges: list[dict]) -> list[dict]:
        keys = {subject, score_metadata.get("label", ""), score_metadata.get("subject", "")}
        if kind == "central_meaning_relation" and " -> " in subject:
            left, right = subject.split(" -> ", 1)
            keys.update((left.strip(), right.strip()))
        if kind == "formative_memory":
            keys.add(subject)
        if kind == "goal_support":
            keys.add(f"goal:{subject}")
        matched: dict[int, dict] = {}
        for key in keys:
            if not key:
                continue
            for edge in edge_index.get(str(key).casefold(), []):
                matched[edge["id"]] = edge
        if not matched:
            label = str(score_metadata.get("label", "")).casefold()
            subject_lower = subject.casefold()
            for edge in edges:
                haystack = " ".join(
                    str(edge.get(part, "")) for part in ("content", "source_label", "target_label", "relation")
                ).casefold()
                if subject_lower and subject_lower in haystack:
                    matched[edge["id"]] = edge
                elif label and label[:40] in haystack:
                    matched[edge["id"]] = edge
        return list(matched.values())[:12]

    def _path_for(self, subject: str, kind: str, score_metadata: dict, edges: list[dict]) -> list[str]:
        if edges:
            first = edges[0]
            return [
                first.get("source_label") or first.get("source") or "Prinzip/Ziel",
                first.get("relation") or "Meaning-Kante",
                first.get("target_label") or first.get("target") or score_metadata.get("label", subject),
                "Motivation-Score",
                "Erklärung",
            ]
        if kind == "goal_support":
            return ["Fundamentprinzip", score_metadata.get("label", subject), "Zielgewichtung", "Motivation-Score", "Erklärung"]
        if kind == "formative_memory":
            return [subject, "Erinnerungsbezug", "Bedeutung", "Motivation-Score", "Erklärung"]
        if kind == "strategic_knowledge_gap":
            return [subject, "Wissenslücke", "Prüfbedarf", "Motivation-Score", "Erklärung"]
        if kind == "meaningful_self_question":
            return [subject, "Selbstfrage", "Selbstmodell", "Motivation-Score", "Erklärung"]
        return [subject, "Bedeutungsbezug", "Motivation-Score", "Erklärung"]

    def _summary(self, subject: str, kind: str, score_metadata: dict, edges: list[dict], path: list[str]) -> str:
        score = float(score_metadata.get("score", 0.0))
        reason = score_metadata.get("reason", "kein Detailgrund gespeichert")
        if edges:
            edge = edges[0]
            relation = edge.get("relation", "Meaning-Kante")
            source = edge.get("source_label") or edge.get("source")
            target = edge.get("target_label") or edge.get("target")
            return (
                f"Score {score:.2f}, weil der Motivation Core '{reason}' bewertet und die Meaning-Kante "
                f"{source} --{relation}--> {target} als Herkunftspfad gespeichert ist. "
                "Die Kante wird nicht durch ihren Motivation-Score begründet."
            )
        return (
            f"Score {score:.2f}, weil der Motivation Core '{reason}' bewertet. "
            f"Der gespeicherte Erklärungspfad lautet: {' -> '.join(path)}."
        )
