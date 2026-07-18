# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectVisionAlignmentReview:
    review_id: str
    target_reference: str
    checked_principle_ids: list[str]
    aligned_principle_ids: list[str]
    gap_principle_ids: list[str]
    unchecked_principle_ids: list[str]
    status: str
    governance_review_required: bool
    decision_authority: bool = False
    automatic_change_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalProjectVisionFramework:
    """Read-only CPVF catalog and caller-evidence alignment review."""

    VERSION = "1.0"
    EVENT_KIND = "cpvf.alignment_review"
    CONFIG_RELATIVE = Path("24_config/cpvf_principles_1_0.json")

    def __init__(self, project_root: str | Path, storage):
        self.project_root = Path(project_root)
        self.storage = storage
        self.config_path = self._resolve_config_path()
        self._config = self._load_config()
        self._principles = list(self._config["principles"])
        self._principle_ids = [item["id"] for item in self._principles]
        self._goals = list(self._config["long_term_goals"])

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Project Vision Framework",
            "abbreviation": "CPVF",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_alignment_review_only",
            "principles": len(self._principles),
            "goal_areas": len(self._goals),
            "cvf_reserved_for_visual_perception": True,
            "decision_authority": False,
            "automatic_change": False,
            "direct_memory_write": False,
            "event_kind": self.EVENT_KIND,
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "principles": json.loads(json.dumps(self._principles, ensure_ascii=True)),
            "long_term_goals": json.loads(json.dumps(self._goals, ensure_ascii=True)),
        }

    def assess_alignment(
        self,
        *,
        target_reference: str,
        principle_checks: dict[str, bool],
    ) -> ProjectVisionAlignmentReview:
        reference = (target_reference or "").strip()
        if not reference:
            raise ValueError("target_reference is required")
        normalized = {
            str(principle_id).strip().upper(): bool(result)
            for principle_id, result in principle_checks.items()
            if str(principle_id).strip()
        }
        unknown = sorted(set(normalized) - set(self._principle_ids))
        if unknown:
            raise ValueError("Unknown CPVF principle ids: " + ", ".join(unknown))
        checked = [item for item in self._principle_ids if item in normalized]
        aligned = [item for item in checked if normalized[item]]
        gaps = [item for item in checked if not normalized[item]]
        unchecked = [item for item in self._principle_ids if item not in normalized]
        if gaps:
            status = "gaps_found"
        elif unchecked:
            status = "incomplete_review"
        else:
            status = "aligned"
        payload = {
            "target_reference": reference,
            "principle_checks": {item: normalized[item] for item in checked},
            "version": self.VERSION,
        }
        review_id = "CPVF-REVIEW-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return ProjectVisionAlignmentReview(
            review_id=review_id,
            target_reference=reference,
            checked_principle_ids=checked,
            aligned_principle_ids=aligned,
            gap_principle_ids=gaps,
            unchecked_principle_ids=unchecked,
            status=status,
            governance_review_required=status != "aligned",
        )

    def record_alignment(self, **kwargs: Any) -> ProjectVisionAlignmentReview:
        review = self.assess_alignment(**kwargs)
        self.storage.add(
            "events",
            self.EVENT_KIND,
            review.target_reference,
            {
                "review_id": review.review_id,
                "status": review.status,
                "checked_principle_ids": review.checked_principle_ids,
                "gap_principle_ids": review.gap_principle_ids,
                "unchecked_principle_ids": review.unchecked_principle_ids,
                "governance_review_required": review.governance_review_required,
                "decision_authority": False,
                "automatic_change_allowed": False,
            },
        )
        return review

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CPVF principles matrix not found: {self.CONFIG_RELATIVE}")

    def _load_config(self) -> dict[str, Any]:
        data = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if data.get("version") != self.VERSION or data.get("abbreviation") != "CPVF":
            raise ValueError("CPVF principles matrix identity must be CPVF 1.0")
        principles = data.get("principles")
        if not isinstance(principles, list) or len(principles) != 9:
            raise ValueError("CPVF must define exactly nine principles")
        expected = [f"CPVF-P{index:02d}" for index in range(1, 10)]
        if [item.get("id") for item in principles] != expected:
            raise ValueError("CPVF principle ids must be ordered from CPVF-P01 to CPVF-P09")
        goals = data.get("long_term_goals")
        if not isinstance(goals, list) or len(goals) != 4:
            raise ValueError("CPVF must define exactly four long-term goal areas")
        return data
