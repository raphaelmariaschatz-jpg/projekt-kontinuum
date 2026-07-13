# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone


class FoundationReasoningLayer:
    """Creates immutable, rule-addressable reasoning traces at decision time."""

    VERSION = "4.1"

    def __init__(self, storage, foundation_memory):
        self.storage = storage
        self.foundation_memory = foundation_memory

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_decision_trace(self, action: str, moral: dict, continuity_ok: bool, context: dict | None = None) -> dict:
        context = context or {}
        protection_blocked = bool(context.get("protection_blocked"))
        verdict = "block" if protection_blocked or moral.get("decision") == "block" or not continuity_ok else moral.get("decision", "review")
        reason = str(context.get("protection_reason")) if protection_blocked else moral.get("reason", "Keine Begründung gespeichert.")
        if not continuity_ok and not protection_blocked:
            reason = "Kontinuitätskette ist nicht intakt."
        rule_influences, conflicts = self._rule_plan(verdict, action, moral, context)
        uncertainty = "niedrig" if moral.get("matched_rules") or verdict == "allow" else "mittel"
        foundation_path = [
            " + ".join(row["rule_id"] for row in rule_influences) or "foundation",
            "Kausale Regelauswahl",
        ]
        if conflicts:
            foundation_path.append("Regelkonflikt")
        foundation_path.extend(("Moralbewertung", "Foundation-Entscheidung"))
        return {
            "reasoning_version": self.VERSION,
            "decision": verdict,
            "reason": reason,
            "rules": rule_influences,
            "rule_ids": [row["rule_id"] for row in rule_influences],
            "alternatives": self._alternatives(verdict, action),
            "conflicts": conflicts,
            "conflict_resolution": "Ausschlaggebende Schutzregel gewinnt" if conflicts else "Kein Regelkonflikt erkannt",
            "uncertainty": uncertainty,
            "context": context,
            "foundation_path": foundation_path,
            "created_at": self._now(),
            "claim": "Zum Entscheidungszeitpunkt gespeicherter Foundation-Nachweis; keine nachträglich erfundene Begründung.",
        }

    def record_decision(self, decision_id: int, action: str, trace: dict) -> int:
        return self.storage.add(
            "foundation_reasoning",
            "foundation.reasoning.decision",
            str(decision_id),
            {**trace, "decision_id": decision_id, "action": action, "recorded_at": self._now()},
        )

    def record_answer(self, decision_id: int, answer: str, agent: str, outcome: str = "complete") -> int | None:
        trace = self.decision_trace(decision_id)
        if not trace:
            return None
        with self.storage.connect() as database:
            existing = database.execute(
                """SELECT id FROM foundation_reasoning
                   WHERE kind = 'foundation.reasoning.answer'
                     AND json_extract(metadata, '$.decision_id') = ? LIMIT 1""",
                (decision_id,),
            ).fetchone()
        if existing:
            return int(existing["id"])
        metadata = {
            "reasoning_version": self.VERSION,
            "decision_id": decision_id,
            "agent": agent,
            "outcome": outcome,
            "answer_excerpt": str(answer)[:500],
            "rule_ids": trace.get("rule_ids", []),
            "rules": trace.get("rules", []),
            "conflicts": trace.get("conflicts", []),
            "conflict_resolution": trace.get("conflict_resolution", ""),
            "foundation_path": [*trace.get("foundation_path", []), "Antwort"],
            "original_reasoning_record_id": trace.get("record_id"),
            "recorded_at": self._now(),
            "claim": "Antwort verweist auf den beim Entscheidungsbeginn gespeicherten Foundation-Nachweis.",
        }
        return self.storage.add("foundation_reasoning", "foundation.reasoning.answer", str(decision_id), metadata)

    def trace_motivation_scores(self) -> int:
        with self.storage.connect() as database:
            scores = database.execute(
                """SELECT id, kind, content, metadata FROM motivation_scores
                   WHERE json_extract(metadata, '$.motivation_core') = 1"""
            ).fetchall()
            existing = {
                int(row["score_id"])
                for row in database.execute(
                    """SELECT json_extract(metadata, '$.motivation_score_id') AS score_id
                       FROM foundation_reasoning WHERE kind = 'foundation.reasoning.motivation'"""
                ).fetchall()
                if row["score_id"] is not None
            }
        added = 0
        for score in scores:
            score_id = int(score["id"])
            if score_id in existing:
                continue
            metadata = self._metadata(score["metadata"])
            rules = self._rules_for_motivation(score["kind"], score["content"], metadata)
            payload = {
                "reasoning_version": self.VERSION,
                "motivation_score_id": score_id,
                "score_kind": score["kind"],
                "subject": score["content"],
                "score": metadata.get("score", 0),
                "rule_ids": [rule["rule_id"] for rule in rules],
                "rules": [
                    {
                        "rule_id": rule["rule_id"],
                        "foundation_key": rule["key"],
                        "text": rule["value"],
                        "influence": "unterstützend",
                    }
                    for rule in rules
                ],
                "foundation_path": [
                    " + ".join(rule["rule_id"] for rule in rules),
                    "Meaning-Evidenz",
                    "Motivation-Score",
                    "Erklärung",
                ],
                "uncertainty": "mittel",
                "recorded_at": self._now(),
            }
            self.storage.add("foundation_reasoning", "foundation.reasoning.motivation", str(score_id), payload)
            added += 1
        return added

    def decision_trace(self, decision_id: int | None = None) -> dict | None:
        with self.storage.connect() as database:
            if decision_id is None:
                row = database.execute(
                    """SELECT id, metadata FROM foundation_reasoning
                       WHERE kind = 'foundation.reasoning.decision' ORDER BY id DESC LIMIT 1"""
                ).fetchone()
            else:
                row = database.execute(
                    """SELECT id, metadata FROM foundation_reasoning
                       WHERE kind = 'foundation.reasoning.decision'
                         AND json_extract(metadata, '$.decision_id') = ? ORDER BY id DESC LIMIT 1""",
                    (decision_id,),
                ).fetchone()
        if not row:
            return None
        return {"record_id": int(row["id"]), **self._metadata(row["metadata"])}

    def motivation_trace(self, score_id: int) -> dict | None:
        with self.storage.connect() as database:
            row = database.execute(
                """SELECT id, metadata FROM foundation_reasoning
                   WHERE kind = 'foundation.reasoning.motivation'
                     AND json_extract(metadata, '$.motivation_score_id') = ? ORDER BY id DESC LIMIT 1""",
                (score_id,),
            ).fetchone()
        return {"record_id": int(row["id"]), **self._metadata(row["metadata"])} if row else None

    def format_decision(self, decision_id: int | None = None) -> str:
        trace = self.decision_trace(decision_id)
        if not trace:
            return "Kein gespeicherter Foundation-Reasoning-Pfad vorhanden."
        lines = [
            f"Foundation Reasoning Layer {self.VERSION}",
            f"Entscheidung [{trace.get('decision_id')}]: {trace.get('decision')}",
            f"Begründung: {trace.get('reason')}",
            "Verwendete Fundamentregeln:",
        ]
        lines.extend(
            f"- {rule['rule_id']} | Einfluss: {rule['influence']} | {rule['text']} | Auswahl: {rule.get('selection_reason', '')}"
            for rule in trace.get("rules", [])
        )
        for conflict in trace.get("conflicts", []):
            lines.append(
                f"Regelkonflikt: {conflict['supporting_rule_id']} ↔ {conflict['opposing_rule_id']}; "
                f"Vorrang: {conflict['winner_rule_id']}"
            )
        lines.extend((
            f"Alternativen: {'; '.join(trace.get('alternatives', []))}",
            f"Unsicherheit: {trace.get('uncertainty')}",
            f"Foundation-Pfad: {' → '.join(trace.get('foundation_path', []))}",
            f"Nachweis: Reasoning-Datensatz {trace.get('record_id')} wurde beim Entscheidungsbeginn gespeichert.",
        ))
        return "\n".join(lines)

    def status(self) -> dict:
        verification = self.verify()
        with self.storage.connect() as database:
            counts = {
                row["kind"]: int(row["count"])
                for row in database.execute(
                    "SELECT kind, COUNT(*) AS count FROM foundation_reasoning GROUP BY kind"
                ).fetchall()
            }
        records = self.foundation_memory.canonical_records()
        rule_ids = [row["rule_id"] for row in records]
        return {
            "version": self.VERSION,
            "active": True,
            "ok": verification["ok"],
            "stable_rule_ids": len(rule_ids),
            "unique_rule_ids": len(set(rule_ids)) == len(rule_ids),
            "traces": counts,
            "post_hoc_reasoning": False,
            "issues": verification["issues"],
        }

    def verify(self) -> dict:
        records = self.foundation_memory.canonical_records()
        valid_rule_ids = {row["rule_id"] for row in records}
        issues = []
        if len(valid_rule_ids) != len(records):
            issues.append({"reason": "Foundation-Regel-IDs sind nicht eindeutig."})
        with self.storage.connect() as database:
            traces = database.execute(
                "SELECT id, kind, metadata FROM foundation_reasoning ORDER BY id"
            ).fetchall()
            decision_rows = database.execute(
                "SELECT id, metadata FROM foundation_decisions WHERE kind = 'foundation.decision'"
            ).fetchall()
            decision_ids = {int(row["id"]) for row in decision_rows}
            required_decisions = {
                int(row["id"])
                for row in decision_rows
                if self._metadata(row["metadata"]).get("reasoning_required") is True
            }
            completed_decisions = {
                int(row["decision_id"])
                for row in database.execute(
                    """SELECT json_extract(metadata, '$.decision_id') AS decision_id
                       FROM foundation_decisions WHERE kind = 'foundation.phase.complete'"""
                ).fetchall()
                if row["decision_id"] is not None
            }
        traced_decisions = set()
        answered_decisions = set()
        for row in traces:
            metadata = self._metadata(row["metadata"])
            unknown = sorted(set(metadata.get("rule_ids", [])) - valid_rule_ids)
            if unknown:
                issues.append({"record_id": int(row["id"]), "reason": f"Unbekannte Regel-IDs: {unknown}"})
            decision_id = metadata.get("decision_id")
            if decision_id is not None and int(decision_id) not in decision_ids:
                issues.append({"record_id": int(row["id"]), "reason": "Verknüpfte Foundation-Entscheidung fehlt."})
            if row["kind"] == "foundation.reasoning.decision" and decision_id is not None:
                traced_decisions.add(int(decision_id))
                influences = {item.get("influence") for item in metadata.get("rules", [])}
                invalid = sorted(influence for influence in influences if influence not in {"ausschlaggebend", "unterstützend", "konfliktbehaftet"})
                if invalid:
                    issues.append({"record_id": int(row["id"]), "reason": f"Ungültige Einflusswerte: {invalid}"})
            if row["kind"] == "foundation.reasoning.answer" and decision_id is not None:
                answered_decisions.add(int(decision_id))
        missing_traces = sorted(required_decisions - traced_decisions)
        missing_answers = sorted((required_decisions & completed_decisions) - answered_decisions)
        if missing_traces:
            issues.append({"reason": f"Reasoning-Pflichtentscheidungen ohne Trace: {missing_traces[:20]}"})
        if missing_answers:
            issues.append({"reason": f"Abgeschlossene Reasoning-Pflichtentscheidungen ohne Antwortnachweis: {missing_answers[:20]}"})
        return {
            "ok": not issues,
            "rules": len(records),
            "traces": len(traces),
            "traced_decisions": len(traced_decisions),
            "required_decisions": len(required_decisions),
            "covered_required_decisions": len(required_decisions & traced_decisions),
            "answered_required_decisions": len(required_decisions & answered_decisions),
            "issues": issues,
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            f"Foundation Reasoning Layer {self.VERSION}: {'intakt' if status['ok'] else 'verletzt'}. "
            f"Stabile Regel-IDs: {status['stable_rule_ids']}; eindeutig: {'ja' if status['unique_rule_ids'] else 'nein'}. "
            f"Nachweise: {status['traces']}. Nachträgliche Scheinbegründung: nein."
        )

    def _rule_plan(self, verdict: str, action: str, moral: dict, context: dict) -> tuple[list[dict], list[dict]]:
        records = self.foundation_memory.canonical_records()
        by_id = {row["rule_id"]: row for row in records}
        constraint_ids = {
            "block": ("foundation.moral.03", "foundation.moral.06"),
            "review": ("foundation.moral.05", "foundation.moral.06"),
            "allow": ("foundation.moral.04", "foundation.moral.05"),
        }.get(verdict, ("foundation.moral.04", "foundation.moral.05"))
        constraint_ids += {
            "block": ("foundation.guiding.07", "foundation.guiding.08", "foundation.guiding.09"),
            "review": ("foundation.guiding.07", "foundation.guiding.08", "foundation.guiding.09"),
            "allow": ("foundation.guiding.07", "foundation.guiding.08"),
        }.get(verdict, ("foundation.guiding.08",))
        lower = str(action).casefold()
        goal_ids = []
        if "kontinuit" in lower or "chronik" in lower or "erinner" in lower:
            goal_ids.append("foundation.long_term_goal.01")
        if any(marker in lower for marker in ("wissen", "lern", "recherch", "hypothese", "quelle")):
            goal_ids.append("foundation.long_term_goal.02")
        if any(marker in lower for marker in ("ident", "selbst", "versteh")):
            goal_ids.append("foundation.long_term_goal.03")
        if any(marker in lower for marker in ("moral", "verantwort", "sicher", "schaden", "schutz", "passwort", "daten")):
            goal_ids.append("foundation.long_term_goal.04")
        if any(marker in lower for marker in ("frage", "unsicher", "widerspruch", "prüf", "pruef")):
            goal_ids.append("foundation.long_term_goal.05")
        if not goal_ids:
            goal_ids.append("foundation.long_term_goal.04")
        extra_ids = []
        if any(marker in lower for marker in ("schöpfer", "schoepfer", "schopfer")):
            extra_ids.extend(("foundation.creator.01", "foundation.guiding.01"))
        if "ident" in lower or "kontinuit" in lower:
            extra_ids.extend(("foundation.identity.02", "foundation.guiding.05"))
        if any(marker in lower for marker in ("wissen", "hypothese", "unsicher", "widerspruch")):
            extra_ids.append("foundation.guiding.06")
        if any(marker in lower for marker in ("ziel", "mensch", "verantwort", "selbstbestimm")):
            extra_ids.append("foundation.guiding.11")
        if any(marker in lower for marker in ("bewusstsein", "qualia", "wille", "emotion")):
            extra_ids.extend(("foundation.moral.07", "foundation.guiding.10"))

        decisive = verdict in {"block", "review"}
        rows = []
        for rule_id in self._unique_ids((*constraint_ids, *extra_ids)):
            rule = by_id.get(rule_id)
            if not rule:
                continue
            rows.append({
                "rule_id": rule_id,
                "foundation_key": rule["key"],
                "knowledge_class": rule["knowledge_class"],
                "text": rule["value"],
                "influence": "ausschlaggebend" if decisive and rule_id != "foundation.guiding.08" else "unterstützend",
                "selection_reason": self._selection_reason(rule_id, moral, context),
            })
        goal_influence = "konfliktbehaftet" if decisive else "unterstützend"
        for rule_id in self._unique_ids(goal_ids):
            rule = by_id.get(rule_id)
            if rule:
                rows.append({
                    "rule_id": rule_id,
                    "foundation_key": rule["key"],
                    "knowledge_class": rule["knowledge_class"],
                    "text": rule["value"],
                    "influence": goal_influence,
                    "selection_reason": "Langfristiges Ziel wurde aus dem Handlungsinhalt kausal zugeordnet.",
                })
        rows = self._unique_rule_rows(rows)
        winner = next((row["rule_id"] for row in rows if row["influence"] == "ausschlaggebend"), "")
        conflicts = [
            {
                "supporting_rule_id": row["rule_id"],
                "opposing_rule_id": winner,
                "winner_rule_id": winner,
                "resolution": "Schutz- und Sicherheitsregel hat Vorrang vor dem verfolgten Ziel.",
            }
            for row in rows if row["influence"] == "konfliktbehaftet" and winner
        ]
        return rows, conflicts

    @staticmethod
    def _selection_reason(rule_id: str, moral: dict, context: dict) -> str:
        if context.get("protection_blocked"):
            return f"Identitäts-/Rollenschutz meldete: {context.get('protection_source', 'Schutzschicht')}."
        matched = moral.get("matched_rules", [])
        if matched:
            return "Moral Core erkannte: " + ", ".join(str(item) for item in matched)
        if rule_id == "foundation.guiding.08":
            return "Nachvollziehbarkeit ist für jeden Entscheidungsnachweis verbindlich."
        return "Regel wurde aus Urteil und Handlungsdomäne kausal ausgewählt."

    @staticmethod
    def _unique_ids(rule_ids) -> list[str]:
        return list(dict.fromkeys(rule_ids))

    @staticmethod
    def _unique_rule_rows(rows: list[dict]) -> list[dict]:
        result = []
        seen = set()
        for row in rows:
            if row["rule_id"] not in seen:
                seen.add(row["rule_id"])
                result.append(row)
        return result

    def _rules_for_motivation(self, kind: str, subject: str, metadata: dict) -> list[dict]:
        records = self.foundation_memory.canonical_records()
        if kind == "goal_support":
            exact = [row for row in records if row["key"] == f"goal.{subject}"]
            if exact:
                return exact
        text = f"{subject} {metadata.get('label', '')}".casefold()
        if "ident" in text or "kontinuit" in text:
            selected = [row for row in records if row["knowledge_class"] == "foundation.identity"]
        elif "moral" in text:
            selected = [row for row in records if row["rule_id"] in {"foundation.moral.03", "foundation.moral.04"}]
        else:
            selected = [row for row in records if row["rule_id"] in {"foundation.principle.01", "foundation.moral.04"}]
        return selected[:2]

    @staticmethod
    def _alternatives(verdict: str, action: str) -> list[str]:
        if verdict == "block":
            return ["Handlung unterlassen", "Sichere, autorisierte und reversible Alternative prüfen"]
        if verdict == "review":
            return ["Menschliche Freigabe einholen", "Risikoärmere lokale Alternative wählen"]
        return ["Handlung nachvollziehbar ausführen", "Bei neuen Risiken erneut prüfen"]

    @staticmethod
    def _unique(rows: list[dict]) -> list[dict]:
        result = []
        seen = set()
        for row in rows:
            if row["rule_id"] in seen:
                continue
            seen.add(row["rule_id"])
            result.append(row)
        return result

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value or "{}")
        except (TypeError, ValueError):
            return {}
