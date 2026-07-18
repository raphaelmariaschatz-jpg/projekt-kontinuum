# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HumanInteractionPlan:
    plan_id: str
    goal: str
    detail_level: str
    dimension_ids: list[str]
    flow_stage_ids: list[str]
    quality_criterion_ids: list[str]
    disclosures: list[str]
    assumptions: list[str]
    supplied_sources: list[str]
    accessibility_requirements: list[str]
    human_decision_required: bool
    continuity_allowed: bool
    response_generated: bool = False
    decision_generated: bool = False
    preference_persisted: bool = False
    direct_memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalHumanInterfaceFramework:
    """Explicit interaction planning without response or interface control."""

    VERSION = "1.0"
    FRAMEWORK_CONFIG = Path("24_config/canonical_human_interface_framework_1_0.json")
    INTERACTION_CONFIG = Path("24_config/chif_interaction_model_1_0.json")
    DETAIL_LEVELS = frozenset({"concise", "balanced", "detailed"})

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.framework_path = self._resolve_config_path(self.FRAMEWORK_CONFIG)
        self.interaction_path = self._resolve_config_path(self.INTERACTION_CONFIG)
        self._framework = self._load_framework()
        self._interaction = self._load_interaction()
        self._dimensions = list(self._framework["interaction_dimensions"])
        self._flows = list(self._interaction["interaction_flow"])
        self._criteria = list(self._interaction["quality_criteria"])

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Human Interface Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_interaction_planning_only",
            "dimensions": len(self._dimensions),
            "flow_stages": len(self._flows),
            "quality_criteria": len(self._criteria),
            "response_generation": False,
            "gui_control": False,
            "automatic_personalization": False,
            "preference_persistence": False,
            "decision_authority": False,
            "direct_memory_write": False,
        }

    def list_dimensions(self) -> list[dict[str, Any]]:
        return self._copy(self._dimensions)

    def list_interaction_flow(self) -> list[dict[str, Any]]:
        return self._copy(self._flows)

    def list_quality_criteria(self) -> list[dict[str, Any]]:
        return self._copy(self._criteria)

    def build_plan(
        self,
        *,
        goal: str,
        detail_level: str = "balanced",
        uncertainty_present: bool = False,
        assumptions: list[str] | None = None,
        supplied_sources: list[str] | None = None,
        sources_required: bool = False,
        accessibility_requirements: list[str] | None = None,
        human_decision_required: bool = False,
        continuity_allowed: bool = False,
    ) -> HumanInteractionPlan:
        normalized_goal = (goal or "").strip()
        if not normalized_goal:
            raise ValueError("CHIF interaction goal must not be empty")
        normalized_detail = (detail_level or "").strip().casefold()
        if normalized_detail not in self.DETAIL_LEVELS:
            raise ValueError(f"Invalid CHIF detail level: {detail_level}")

        normalized_assumptions = self._normalize_strings(assumptions)
        normalized_sources = self._normalize_strings(supplied_sources)
        normalized_accessibility = self._normalize_strings(accessibility_requirements)

        disclosures: list[str] = []
        if normalized_assumptions:
            disclosures.append("state_assumptions")
        if uncertainty_present:
            disclosures.append("mark_uncertainty")
        if normalized_sources:
            disclosures.append("cite_supplied_sources")
        elif sources_required:
            disclosures.append("state_missing_sources")
        if human_decision_required:
            disclosures.append("preserve_human_decision_authority")
        if not continuity_allowed:
            disclosures.append("do_not_use_persistent_context")

        dimension_ids = [item["id"] for item in self._dimensions]
        flow_stage_ids = [item["stage"] for item in self._flows]
        quality_criterion_ids = [item["id"] for item in self._criteria]
        payload = {
            "goal": normalized_goal,
            "detail_level": normalized_detail,
            "dimension_ids": dimension_ids,
            "flow_stage_ids": flow_stage_ids,
            "quality_criterion_ids": quality_criterion_ids,
            "disclosures": disclosures,
            "assumptions": normalized_assumptions,
            "supplied_sources": normalized_sources,
            "accessibility_requirements": normalized_accessibility,
            "human_decision_required": bool(human_decision_required),
            "continuity_allowed": bool(continuity_allowed),
        }
        plan_id = "CHIF-PLAN-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return HumanInteractionPlan(plan_id=plan_id, **payload)

    def _load_framework(self) -> dict[str, Any]:
        data = self._read_json(self.framework_path)
        if data.get("version") != self.VERSION or data.get("abbreviation") != "CHIF":
            raise ValueError("CHIF framework identity must be CHIF 1.0")
        dimensions = data.get("interaction_dimensions")
        expected = [f"CHIF-{index:02d}" for index in range(1, 9)]
        if not isinstance(dimensions, list) or [item.get("id") for item in dimensions] != expected:
            raise ValueError("CHIF must define ordered dimensions CHIF-01 to CHIF-08")
        return data

    def _load_interaction(self) -> dict[str, Any]:
        data = self._read_json(self.interaction_path)
        if data.get("version") != self.VERSION or data.get("framework") != "Canonical Human Interface Framework":
            raise ValueError("CHIF interaction model identity must be CHIF 1.0")
        flows = data.get("interaction_flow")
        criteria = data.get("quality_criteria")
        expected_flows = [f"CHIF-FLOW-{index:02d}" for index in range(1, 6)]
        expected_criteria = [f"CHIF-QC-{index:02d}" for index in range(1, 8)]
        if not isinstance(flows, list) or [item.get("stage") for item in flows] != expected_flows:
            raise ValueError("CHIF must define ordered flow stages CHIF-FLOW-01 to CHIF-FLOW-05")
        if not isinstance(criteria, list) or [item.get("id") for item in criteria] != expected_criteria:
            raise ValueError("CHIF must define ordered quality criteria CHIF-QC-01 to CHIF-QC-07")
        dimension_ids = {f"CHIF-{index:02d}" for index in range(1, 9)}
        for item in flows:
            if not set(item.get("primary_dimensions", [])).issubset(dimension_ids):
                raise ValueError("CHIF flow contains an unknown interaction dimension")
        return data

    def _resolve_config_path(self, relative_path: Path) -> Path:
        primary = self.project_root / relative_path
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / relative_path
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CHIF configuration not found: {relative_path}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy(value: Any) -> Any:
        return json.loads(json.dumps(value, ensure_ascii=True))

    @staticmethod
    def _normalize_strings(values: list[str] | None) -> list[str]:
        return list(
            dict.fromkeys(
                text.strip()
                for value in (values or [])
                if (text := str(value)).strip()
            )
        )
