# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CompetencyFocus:
    focus_id: str
    area_id: str
    area_name: str
    dimension: str
    goals: list[str]
    learning_targets: list[str]
    progression_basis: str
    evidence_required: bool
    review_required: bool
    automatic_assessment: bool
    persistence_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalAICompetencyFramework:
    """Read-only CAICF catalog and explicit learning-focus planner."""

    VERSION = "1.0"
    CONFIG_RELATIVE = Path("24_config/caicf_competency_matrix_1_0.json")
    DIMENSIONS = frozenset({"knowledge", "skills", "attitudes"})

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self._resolve_config_path()
        self._matrix = self._load_matrix()
        self._areas = {
            area["id"]: area for area in self._matrix["competency_areas"]
        }

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical AI Competency Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "read_only_competency_catalog",
            "competency_areas": len(self._areas),
            "dimensions": sorted(self.DIMENSIONS),
            "automatic_assessment": False,
            "learner_profile_persistence": False,
            "memory_handoff": False,
        }

    def list_areas(self) -> list[dict[str, str]]:
        return [
            {
                "id": area["id"],
                "name": area["name"],
                "description": area["description"],
            }
            for area in self._matrix["competency_areas"]
        ]

    def get_area(self, area_id: str) -> dict[str, Any]:
        area = self._areas.get((area_id or "").strip().upper())
        if area is None:
            raise KeyError(f"Unknown CAICF competency area: {area_id}")
        return json.loads(json.dumps(area, ensure_ascii=True))

    def plan_focus(self, *, area_id: str, dimension: str) -> CompetencyFocus:
        area = self.get_area(area_id)
        normalized_dimension = (dimension or "").strip().casefold()
        if normalized_dimension not in self.DIMENSIONS:
            allowed = ", ".join(sorted(self.DIMENSIONS))
            raise ValueError(f"dimension must be one of: {allowed}")

        payload = {
            "area_id": area["id"],
            "dimension": normalized_dimension,
            "goals": area["goals"],
            "targets": area["dimensions"][normalized_dimension],
        }
        focus_id = "CAICF-FOCUS-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        policy = self._matrix["progression_policy"]
        return CompetencyFocus(
            focus_id=focus_id,
            area_id=area["id"],
            area_name=area["name"],
            dimension=normalized_dimension,
            goals=list(area["goals"]),
            learning_targets=list(area["dimensions"][normalized_dimension]),
            progression_basis=policy["basis"],
            evidence_required=bool(policy["requires_evidence_for_progress"]),
            review_required=bool(policy["requires_review_for_memory_adoption"]),
            automatic_assessment=False,
            persistence_allowed=False,
        )

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        repository_root = Path(__file__).resolve().parents[3]
        fallback = repository_root / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CAICF matrix not found: {self.CONFIG_RELATIVE}")

    def _load_matrix(self) -> dict[str, Any]:
        data = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if data.get("version") != self.VERSION:
            raise ValueError("CAICF matrix version must be 1.0")
        areas = data.get("competency_areas")
        if not isinstance(areas, list) or len(areas) != 4:
            raise ValueError("CAICF matrix must define exactly four competency areas")
        area_ids: set[str] = set()
        for area in areas:
            area_id = str(area.get("id", "")).strip().upper()
            if not area_id or area_id in area_ids:
                raise ValueError("CAICF competency area ids must be unique")
            area_ids.add(area_id)
            dimensions = area.get("dimensions")
            if not isinstance(dimensions, dict) or set(dimensions) != self.DIMENSIONS:
                raise ValueError("Each CAICF area must define all three dimensions")
            if any(not isinstance(dimensions[name], list) for name in self.DIMENSIONS):
                raise ValueError("CAICF dimension targets must be arrays")
        return data
