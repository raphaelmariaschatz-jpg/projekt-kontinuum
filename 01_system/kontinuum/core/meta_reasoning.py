# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True)
class MetaReasoningReview:
    review_id: str
    target_type: str
    target_reference: str
    reasoning_summary: str
    assumptions: list[str]
    uncertainties: list[str]
    confidence: str
    alternatives_reviewed: list[str]
    preferred_path_rationale: str
    governance_alignment: dict[str, Any]
    revision_trigger: dict[str, Any]
    output_boundary: str
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MetaReasoningEngine:
    """Deterministic, explicit review of a supplied reasoning summary."""

    VERSION = "1.0"
    EVENT_KIND = "meta_reasoning.review"
    TARGET_TYPES = frozenset(
        {"answer", "decision", "plan", "architecture_assumption"}
    )

    def __init__(self, storage):
        self.storage = storage

    def status(self) -> dict[str, Any]:
        return {
            "name": "Meta-Reasoning",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_review_only",
            "automatic_live_review": False,
            "direct_memory_write": False,
            "self_modification": False,
            "event_kind": self.EVENT_KIND,
        }

    def assess(
        self,
        *,
        target_type: str,
        target_reference: str,
        reasoning_summary: str,
        assumptions: list[str] | None = None,
        uncertainties: list[str] | None = None,
        alternatives_reviewed: list[str] | None = None,
        preferred_path_rationale: str = "",
        governance_checks: dict[str, bool] | None = None,
    ) -> MetaReasoningReview:
        normalized_type = (target_type or "").strip().casefold()
        if normalized_type not in self.TARGET_TYPES:
            allowed = ", ".join(sorted(self.TARGET_TYPES))
            raise ValueError(f"target_type must be one of: {allowed}")

        reference = (target_reference or "").strip()
        summary = (reasoning_summary or "").strip()
        normalized_assumptions = self._clean_list(assumptions)
        normalized_uncertainties = self._clean_list(uncertainties)
        normalized_alternatives = self._clean_list(alternatives_reviewed)
        rationale = (preferred_path_rationale or "").strip()
        checks = {
            str(name).strip(): bool(value)
            for name, value in (governance_checks or {}).items()
            if str(name).strip()
        }
        blockers = sorted(name for name, passed in checks.items() if not passed)
        if blockers:
            governance_status = "blocked"
        elif checks:
            governance_status = "aligned"
        else:
            governance_status = "not_checked"

        confidence = self._confidence(
            summary=summary,
            uncertainties=normalized_uncertainties,
            blockers=blockers,
        )
        revision_reasons: list[str] = []
        if not summary:
            revision_reasons.append("missing_reasoning_summary")
        if normalized_uncertainties:
            revision_reasons.append("documented_uncertainty")
        if blockers:
            revision_reasons.append("governance_blocker")
        if confidence == "low":
            revision_reasons.append("low_confidence")

        warnings: list[str] = []
        if not checks:
            warnings.append("Governance alignment was not supplied and remains unchecked.")
        if not normalized_alternatives:
            warnings.append("No alternative path was supplied for review.")
        if not rationale:
            warnings.append("No preferred-path rationale was supplied.")

        payload = {
            "target_type": normalized_type,
            "target_reference": reference,
            "reasoning_summary": summary,
            "assumptions": normalized_assumptions,
            "uncertainties": normalized_uncertainties,
            "alternatives_reviewed": normalized_alternatives,
            "preferred_path_rationale": rationale,
            "governance_checks": checks,
        }
        review_id = "MR-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]

        return MetaReasoningReview(
            review_id=review_id,
            target_type=normalized_type,
            target_reference=reference,
            reasoning_summary=summary,
            assumptions=normalized_assumptions,
            uncertainties=normalized_uncertainties,
            confidence=confidence,
            alternatives_reviewed=normalized_alternatives,
            preferred_path_rationale=rationale,
            governance_alignment={
                "status": governance_status,
                "checks": checks,
                "blockers": blockers,
                "decision_authority": False,
            },
            revision_trigger={
                "required": bool(revision_reasons),
                "reasons": list(dict.fromkeys(revision_reasons)),
            },
            output_boundary="review_only",
            warnings=warnings,
        )

    def review(self, **kwargs: Any) -> MetaReasoningReview:
        result = self.assess(**kwargs)
        self.storage.add(
            "events",
            self.EVENT_KIND,
            result.target_reference or result.review_id,
            {
                "review_id": result.review_id,
                "target_type": result.target_type,
                "confidence": result.confidence,
                "governance_status": result.governance_alignment["status"],
                "revision_required": result.revision_trigger["required"],
                "output_boundary": result.output_boundary,
            },
        )
        return result

    @staticmethod
    def _clean_list(values: list[str] | None) -> list[str]:
        return list(
            dict.fromkeys(
                str(value).strip()
                for value in (values or [])
                if str(value).strip()
            )
        )

    @staticmethod
    def _confidence(
        *,
        summary: str,
        uncertainties: list[str],
        blockers: list[str],
    ) -> str:
        if not summary or blockers or len(uncertainties) >= 2:
            return "low"
        if uncertainties:
            return "medium"
        return "high"
