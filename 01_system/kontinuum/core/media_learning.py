# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MediaLearningRecommendation:
    recommendation_id: str
    learning_goal: str
    topic_structure: str
    complexity: str
    media_type_ids: list[str]
    reasons: list[str]
    overload_reduced: bool
    media_generated: bool = False
    preference_persisted: bool = False
    decision_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalMediaLearningFramework:
    """Situational media-type recommendation without generation or profiling."""

    VERSION = "1.0"
    CONFIG_RELATIVE = Path("24_config/cmlf_media_types_1_0.json")
    GOALS = frozenset({"understand", "practice", "apply", "reflect"})
    STRUCTURES = frozenset({"concept", "relationship", "process", "action"})
    COMPLEXITIES = frozenset({"low", "medium", "high"})

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self._resolve_config_path()
        self._config = self._load_config()
        self._media_types = list(self._config["media_types"])
        self._media_ids = [item["id"] for item in self._media_types]

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Media Learning Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "situational_recommendation_only",
            "media_types": len(self._media_types),
            "automatic_media_generation": False,
            "preference_persistence": False,
            "learner_profile": False,
            "decision_authority": False,
            "direct_memory_write": False,
        }

    def list_media_types(self) -> list[dict[str, Any]]:
        return json.loads(json.dumps(self._media_types, ensure_ascii=True))

    def recommend(
        self,
        *,
        learning_goal: str,
        topic_structure: str,
        complexity: str,
        user_preference: str = "",
        accessibility_media: str = "",
        overload_risk: bool = False,
        evidence_need: bool = False,
        practical_prerequisites_met: bool = False,
    ) -> MediaLearningRecommendation:
        goal = self._validate_value(learning_goal, self.GOALS, "learning_goal")
        structure = self._validate_value(topic_structure, self.STRUCTURES, "topic_structure")
        level = self._validate_value(complexity, self.COMPLEXITIES, "complexity")
        preference = self._validate_media_id(user_preference)
        accessibility = self._validate_media_id(accessibility_media)

        media_ids: list[str] = []
        reasons: list[str] = []
        if accessibility:
            media_ids.append(accessibility)
            reasons.append("explicit_accessibility_medium")
        else:
            primary = self._primary_media(
                goal=goal,
                structure=structure,
                practical_prerequisites_met=practical_prerequisites_met,
            )
            media_ids.append(primary)
            reasons.append(f"primary_for_{goal}_{structure}")

        reduce_media = bool(overload_risk or level == "high")
        if not reduce_media:
            if preference and preference not in media_ids:
                media_ids.append(preference)
                reasons.append("explicit_situational_preference")
            elif evidence_need and "CMLF-M01" not in media_ids:
                media_ids.append("CMLF-M01")
                reasons.append("text_added_for_evidence_traceability")
        else:
            reasons.append("media_variety_reduced_for_overload")

        media_ids = media_ids[:2]
        payload = {
            "learning_goal": goal,
            "topic_structure": structure,
            "complexity": level,
            "media_type_ids": media_ids,
            "reasons": reasons,
            "overload_reduced": reduce_media,
        }
        recommendation_id = "CMLF-REC-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return MediaLearningRecommendation(
            recommendation_id=recommendation_id,
            learning_goal=goal,
            topic_structure=structure,
            complexity=level,
            media_type_ids=media_ids,
            reasons=reasons,
            overload_reduced=reduce_media,
        )

    def _primary_media(
        self,
        *,
        goal: str,
        structure: str,
        practical_prerequisites_met: bool,
    ) -> str:
        if goal == "reflect":
            return "CMLF-M07"
        if goal == "practice":
            return "CMLF-M03"
        if goal == "apply" or structure == "action":
            return "CMLF-M06" if practical_prerequisites_met else "CMLF-M03"
        if structure in {"relationship", "process"}:
            return "CMLF-M02"
        return "CMLF-M01"

    def _validate_media_id(self, value: str) -> str:
        normalized = (value or "").strip().upper()
        if normalized and normalized not in self._media_ids:
            raise ValueError(f"Unknown CMLF media type: {value}")
        return normalized

    @staticmethod
    def _validate_value(value: str, allowed: frozenset[str], field: str) -> str:
        normalized = (value or "").strip().casefold()
        if normalized not in allowed:
            raise ValueError(f"Invalid {field}: {value}")
        return normalized

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CMLF media matrix not found: {self.CONFIG_RELATIVE}")

    def _load_config(self) -> dict[str, Any]:
        data = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if data.get("version") != self.VERSION or data.get("abbreviation") != "CMLF":
            raise ValueError("CMLF media matrix identity must be CMLF 1.0")
        media_types = data.get("media_types")
        if not isinstance(media_types, list) or len(media_types) != 7:
            raise ValueError("CMLF must define exactly seven media types")
        expected = [f"CMLF-M{index:02d}" for index in range(1, 8)]
        if [item.get("id") for item in media_types] != expected:
            raise ValueError("CMLF media ids must be ordered from CMLF-M01 to CMLF-M07")
        return data
