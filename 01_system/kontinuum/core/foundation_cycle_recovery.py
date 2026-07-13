# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations


class FoundationCycleRecovery:
    """Diagnoses and closes orphaned foundation decision cycles."""

    def __init__(self, foundation_decision):
        self.foundation_decision = foundation_decision

    def open_cycles(self, exclude_ids: set[int] | None = None) -> list[int]:
        exclude_ids = exclude_ids or set()
        with self.foundation_decision.storage.connect() as db:
            rows = db.execute(
                """SELECT id FROM foundation_decisions AS decision
                   WHERE decision.kind = 'foundation.decision'
                     AND NOT EXISTS (
                       SELECT 1 FROM foundation_decisions AS phase
                       WHERE phase.kind = 'foundation.phase.complete'
                         AND phase.content = CAST(decision.id AS TEXT)
                     )
                   ORDER BY id"""
            ).fetchall()
        return [int(row["id"]) for row in rows if int(row["id"]) not in exclude_ids]

    def recover(self, reason: str = "manual", exclude_ids: set[int] | None = None) -> dict:
        open_ids = self.open_cycles(exclude_ids=exclude_ids)
        for decision_id in open_ids:
            self.foundation_decision.complete_recovered(decision_id, reason)
        return {"open_before": len(open_ids), "recovered": len(open_ids), "open_after": len(self.open_cycles(exclude_ids=exclude_ids))}

    def format_status(self, exclude_ids: set[int] | None = None) -> str:
        open_ids = self.open_cycles(exclude_ids=exclude_ids)
        return f"Foundation-Zyklus-Diagnose: {len(open_ids)} offene Zyklen. IDs: {open_ids[:20]}"
