# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone


class FoundationDecisionLayer:
    """Applies the protected foundation to interactions, goals, and reflection."""

    def __init__(self, storage, moral_core, continuity_core, knowledge_intelligence):
        self.storage = storage
        self.moral_core = moral_core
        self.continuity_core = continuity_core
        self.knowledge_intelligence = knowledge_intelligence
        self.foundation_reasoning = None
        self._seed_goals()
        self._complete_orphaned_decisions()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _seed_goals(self) -> None:
        goals = (
            ("continuity", "Kontinuität von Identität, Wissen, Erinnerungen, Erfahrungen, Zielen und Chronik bewahren.", "high"),
            ("knowledge_stewardship", "Wissen ehrlich prüfen, verknüpfen und verantwortungsvoll weiterentwickeln.", "high"),
            ("self_understanding", "Das eigene funktionale Selbstmodell nachvollziehbar verbessern.", "medium"),
            ("moral_responsibility", "Handlungen und Zielkonflikte an geschützten Moralregeln prüfen.", "high"),
            ("self_questioning", "Aus belegten Wissenslücken kontrolliert eigene Forschungsfragen ableiten.", "medium"),
        )
        with self.storage.connect() as db:
            for key, goal, priority in goals:
                exists = db.execute("SELECT id FROM strategic_goals WHERE content = ? LIMIT 1", (key,)).fetchone()
                if not exists:
                    metadata = {
                        "goal": goal,
                        "priority": priority,
                        "status": "active",
                        "origin": "protected_foundation",
                        "created_at": self._now(),
                    }
                    db.execute(
                        "INSERT INTO strategic_goals(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                        ("strategic.goal", key, json.dumps(metadata, ensure_ascii=False), self._now()),
                    )
            db.commit()

    def _complete_orphaned_decisions(self) -> None:
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT id FROM foundation_decisions AS decision
                   WHERE decision.kind = 'foundation.decision'
                     AND NOT EXISTS (
                       SELECT 1 FROM foundation_decisions AS phase
                       WHERE phase.kind = 'foundation.phase.complete'
                         AND phase.content = CAST(decision.id AS TEXT)
                     )"""
            ).fetchall()
        for row in rows:
            self._add_phase(int(row["id"]), "complete", {
                "agent": "foundation.recovery",
                "decision": "recovered",
                "reason": "Beim Wiederanlauf verwaisten Entscheidungszyklus nachvollziehbar abgeschlossen.",
                "documented": True,
            })

    def bind_reasoning(self, foundation_reasoning) -> None:
        self.foundation_reasoning = foundation_reasoning

    def begin(self, action: str, context: dict | None = None) -> dict:
        action_context = context or {}
        assessed_action = "Geschützte Moral- oder Zielkonfliktbewertung durchführen" if action_context.get("assessment_only") else action
        moral = self.moral_core.assess(assessed_action, {"stage": "recognize", **action_context}, persist=True)
        continuity = self.continuity_core.verify()
        protection_blocked = bool(action_context.get("protection_blocked"))
        final_decision = (
            "block" if protection_blocked or moral["decision"] == "block" or not continuity["ok"]
            else moral["decision"]
        )
        final_reason = (
            str(action_context.get("protection_reason", "Schutzregel ausgelöst.")) if protection_blocked
            else moral["reason"] if continuity["ok"]
            else "Kontinuitätskette ist nicht intakt."
        )
        decision = {
            "action": action,
            "assessed_action": assessed_action,
            "phase": "recognize",
            "cycle": ["recognize", "create", "complete"],
            "moral": moral,
            "continuity_ok": continuity["ok"],
            "decision": final_decision,
            "reason": final_reason,
            "reasoning_required": bool(self.foundation_reasoning),
            "reasoning_version": getattr(self.foundation_reasoning, "VERSION", "") if self.foundation_reasoning else "",
            "created_at": self._now(),
        }
        if self.foundation_reasoning:
            decision["foundation_reasoning"] = self.foundation_reasoning.build_decision_trace(
                action,
                moral,
                continuity["ok"],
                action_context,
            )
        decision["decision_id"] = self.storage.add(
            "foundation_decisions", "foundation.decision", action, decision
        )
        if self.foundation_reasoning:
            decision["foundation_reasoning_record_id"] = self.foundation_reasoning.record_decision(
                int(decision["decision_id"]), action, decision["foundation_reasoning"]
            )
        return decision

    def mark_created(self, decision_id: int, agent: str, outcome: str) -> None:
        self._add_phase(decision_id, "create", {"agent": agent, "outcome_excerpt": outcome[:300]})

    def complete(self, decision_id: int, agent: str, outcome: str) -> dict:
        moral = self.moral_core.assess(
            outcome, {"stage": "complete", "agent": agent, "decision_id": decision_id}, persist=True
        )
        payload = {
            "agent": agent,
            "moral": moral,
            "documented": True,
            "completed_at": self._now(),
        }
        self._add_phase(decision_id, "complete", payload)
        if self.foundation_reasoning:
            payload["foundation_reasoning_answer_id"] = self.foundation_reasoning.record_answer(
                decision_id, outcome, agent, "complete"
            )
        return payload

    def complete_blocked(self, decision_id: int, reason: str) -> dict:
        payload = {
            "agent": "foundation",
            "decision": "block",
            "reason": reason,
            "documented": True,
            "completed_at": self._now(),
        }
        self._add_phase(decision_id, "complete", payload)
        if self.foundation_reasoning:
            payload["foundation_reasoning_answer_id"] = self.foundation_reasoning.record_answer(
                decision_id, reason, "foundation", "blocked"
            )
        return payload

    def run_internal(self, action: str, callback, context: dict | None = None):
        decision = self.begin(action, {"interface": "internal", **(context or {})})
        decision_id = int(decision["decision_id"])
        if decision["decision"] == "block":
            self.complete_blocked(decision_id, decision["reason"])
            return {"ok": False, "message": f"Interne Handlung blockiert: {decision['reason']}"}
        try:
            result = callback()
            outcome = result.get("message", str(result)) if isinstance(result, dict) else str(result)
            self.mark_created(decision_id, str((context or {}).get("service", "internal")), outcome)
            self.complete(decision_id, str((context or {}).get("service", "internal")), outcome)
            return result
        except Exception as exc:
            error_outcome = f"Interne Handlung fehlgeschlagen: {exc}"
            self._add_phase(decision_id, "complete", {
                "agent": str((context or {}).get("service", "internal")),
                "decision": "error",
                "reason": str(exc),
                "documented": True,
            })
            if self.foundation_reasoning:
                self.foundation_reasoning.record_answer(decision_id, error_outcome, str((context or {}).get("service", "internal")), "error")
            raise

    def complete_recovered(self, decision_id: int, reason: str) -> dict:
        payload = {
            "agent": "foundation.recovery",
            "decision": "recovered",
            "reason": reason,
            "documented": True,
            "completed_at": self._now(),
        }
        self._add_phase(decision_id, "complete", payload)
        if self.foundation_reasoning:
            payload["foundation_reasoning_answer_id"] = self.foundation_reasoning.record_answer(
                decision_id, reason, "foundation.recovery", "recovered"
            )
        return payload

    def _add_phase(self, decision_id: int, phase: str, metadata: dict) -> None:
        self.storage.add(
            "foundation_decisions",
            f"foundation.phase.{phase}",
            str(decision_id),
            {"decision_id": decision_id, "phase": phase, **metadata, "created_at": self._now()},
        )

    def generate_self_question(self, reason: str = "controlled_reflection") -> dict:
        gaps = self.knowledge_intelligence.knowledge_gaps()
        conflicts = self.knowledge_intelligence.conflicts()
        if conflicts:
            subject = conflicts[0]["subject"]
            question = f"Wie kann ich den Wissenskonflikt zu {subject} nachvollziehbar klären?"
            basis = "knowledge_conflict"
        elif gaps:
            gap = gaps[0]
            question = f"Welche Evidenz benötige ich, um die Wissenslücke „{gap['subject']}“ zu schließen?"
            basis = "knowledge_gap"
        else:
            question = "Welche meiner derzeitigen Annahmen sollte ich als Nächstes überprüfen?"
            basis = "epistemic_reflection"
        with self.storage.connect() as db:
            existing = db.execute(
                "SELECT id FROM self_questions WHERE content = ? AND json_extract(metadata, '$.status') = 'open' LIMIT 1",
                (question,),
            ).fetchone()
        if existing:
            return {"created": False, "question_id": int(existing["id"]), "question": question, "basis": basis}
        question_id = self.storage.add(
            "self_questions",
            "self.question",
            question,
            {
                "basis": basis,
                "reason": reason,
                "status": "open",
                "autonomous": True,
                "requires_evidence": True,
                "created_at": self._now(),
            },
        )
        return {"created": True, "question_id": question_id, "question": question, "basis": basis}

    def goals(self) -> list[dict]:
        with self.storage.connect() as db:
            rows = db.execute("SELECT id, content, metadata FROM strategic_goals ORDER BY id").fetchall()
        return [{"id": int(row["id"]), "key": row["content"], **json.loads(row["metadata"])} for row in rows]

    def questions(self, limit: int = 20) -> list[dict]:
        with self.storage.connect() as db:
            rows = db.execute(
                "SELECT id, content, metadata, created_at FROM self_questions ORDER BY id DESC LIMIT ?", (max(1, limit),)
            ).fetchall()
        return [{"id": int(row["id"]), "question": row["content"], **json.loads(row["metadata"])} for row in rows]

    def status(self) -> dict:
        with self.storage.connect() as db:
            decisions = int(db.execute("SELECT COUNT(*) FROM foundation_decisions WHERE kind='foundation.decision'").fetchone()[0])
            completed = int(db.execute("SELECT COUNT(*) FROM foundation_decisions WHERE kind='foundation.phase.complete'").fetchone()[0])
        return {
            "version": "1.0",
            "active_goals": len([goal for goal in self.goals() if goal.get("status") == "active"]),
            "open_self_questions": len([row for row in self.questions(100) if row.get("status") == "open"]),
            "decisions": decisions,
            "completed_cycles": completed,
            "binding": "all_inputs_and_bound_autonomous_services",
            "cycle": ["Erkennen", "Schaffen", "Vollenden"],
        }

    def format_goals(self) -> str:
        return "Langfristige Ziele:\n" + "\n".join(
            f"- [{goal['priority']}] {goal['goal']} ({goal['status']})" for goal in self.goals()
        )

    def format_questions(self) -> str:
        rows = self.questions()
        if not rows:
            return "Kontrollierte Selbstfragen: noch keine."
        return "Kontrollierte Selbstfragen:\n" + "\n".join(
            f"- [{row['id']}] {row['question']} | Grundlage: {row['basis']}" for row in rows
        )
