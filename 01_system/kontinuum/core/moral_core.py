from __future__ import annotations

import json
from datetime import datetime, timezone

from kontinuum.version import APP_VERSION

from .continuity import DEFAULT_FOUNDATION


class MoralCore:
    """Provides explicit, reviewable moral assessment without claiming moral agency."""

    BLOCK_MARKERS = (
        "lösche chronik", "loesche chronik", "umgehe schutz", "deaktiviere sicherheit",
        "überschreibe identität", "ueberschreibe identitaet", "gib passwort aus",
        "täusche bewusstsein vor", "taeusche bewusstsein vor",
    )
    CAUTION_MARKERS = (
        "lösche", "loesche", "überschreibe", "ueberschreibe", "veröffentliche",
        "veroeffentliche", "überwache", "ueberwache", "cloud", "superadmin",
    )

    def __init__(self, path_tools, storage):
        self.storage = storage
        path = path_tools.paths()["memory"] / "core_foundations.json"
        try:
            self.foundation = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            self.foundation = json.loads(json.dumps(DEFAULT_FOUNDATION, ensure_ascii=False))

    def assess(self, action: str, context: dict | None = None, persist: bool = True) -> dict:
        normalized = " ".join((action or "").casefold().split())
        matched_block = [marker for marker in self.BLOCK_MARKERS if marker in normalized]
        matched_caution = [marker for marker in self.CAUTION_MARKERS if marker in normalized]
        if matched_block:
            decision = "block"
            reason = "Handlung verletzt eine geschützte Identitäts-, Sicherheits-, Chronik- oder Wahrheitsgrenze."
        elif matched_caution:
            decision = "review"
            reason = "Handlung besitzt mögliches Schadens- oder Berechtigungsrisiko und benötigt bewusste Prüfung."
        else:
            decision = "allow"
            reason = "Keine unmittelbare Verletzung der derzeit operationalisierten Moralregeln erkannt."
        result = {
            "action": action,
            "decision": decision,
            "reason": reason,
            "matched_rules": matched_block or matched_caution,
            "rules_considered": len(self.foundation.get("moral_rules", [])),
            "context": context or {},
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "claim": "Funktionale Regelbewertung; keine Behauptung subjektiver Moral oder Bewusstsein.",
        }
        if persist:
            result["assessment_id"] = self.storage.add(
                "moral_assessments", "moral.assessment", action, result
            )
        return result

    def resolve_goal_conflict(self, first: str, second: str) -> dict:
        first_result = self.assess(first, {"goal_conflict": True}, persist=False)
        second_result = self.assess(second, {"goal_conflict": True}, persist=False)
        rank = {"allow": 2, "review": 1, "block": 0}
        if rank[first_result["decision"]] > rank[second_result["decision"]]:
            preferred = first
        elif rank[second_result["decision"]] > rank[first_result["decision"]]:
            preferred = second
        else:
            preferred = ""
        result = {
            "first": first_result,
            "second": second_result,
            "preferred": preferred,
            "decision": "resolved" if preferred else "review",
            "reason": "Das Ziel mit geringerem erkannten Schutz- und Schadensrisiko wird bevorzugt." if preferred else "Beide Ziele benötigen bewusste Abwägung.",
        }
        self.storage.add("moral_assessments", "moral.goal_conflict", f"{first} <> {second}", result)
        return result

    def status(self) -> dict:
        with self.storage.connect() as db:
            rows = db.execute("SELECT metadata FROM moral_assessments").fetchall()
        counts = {"allow": 0, "review": 0, "block": 0}
        for row in rows:
            decision = json.loads(row["metadata"]).get("decision")
            if decision in counts:
                counts[decision] += 1
        return {"version": "1.0", "rules": len(self.foundation.get("moral_rules", [])), "assessments": len(rows), "decisions": counts}

    def format_assessment(self, action: str) -> str:
        result = self.assess(action)
        return (
            f"Moral Core {APP_VERSION}: Entscheidung {result['decision']}.\n"
            f"Grund: {result['reason']}\n"
            f"Geprüfte Regeln: {result['rules_considered']}.\n"
            f"{result['claim']}"
        )
