# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EnterpriseScope:
    scope_id: str
    dimension_ids: list[str]
    dimensions: list[dict[str, Any]]
    relationships: list[dict[str, str]]
    industry_profile: str
    transactions_enabled: bool = False
    enterprise_data_processed: bool = False
    kpi_calculation_enabled: bool = False
    decision_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalEnterpriseFramework:
    """Read-only universal enterprise model without enterprise data."""

    VERSION = "1.0"
    CONFIG_RELATIVE = Path("24_config/cef_enterprise_model_1_0.json")

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self._resolve_config_path()
        self._config = self._load_config()
        self._dimensions = list(self._config["dimensions"])
        self._dimension_ids = [item["id"] for item in self._dimensions]
        self._relationships = list(self._config["relationships"])

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Enterprise Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "read_only_universal_enterprise_model",
            "dimensions": len(self._dimensions),
            "relationships": len(self._relationships),
            "enterprise_data_processing": False,
            "transactions": False,
            "kpi_calculation": False,
            "automatic_consulting": False,
            "decision_authority": False,
            "direct_memory_write": False,
        }

    def catalog(self) -> dict[str, Any]:
        return json.loads(
            json.dumps(
                {
                    "dimensions": self._dimensions,
                    "relationships": self._relationships,
                    "information_flow_model": self._config["information_flow_model"],
                    "software_boundaries": self._config["software_boundaries"],
                },
                ensure_ascii=True,
            )
        )

    def build_scope(
        self,
        *,
        dimension_ids: list[str],
        industry_profile: str = "generic",
    ) -> EnterpriseScope:
        profile = (industry_profile or "").strip().casefold()
        if profile != "generic":
            raise ValueError("CEF 1.0 supports only the generic universal core model")
        normalized = list(
            dict.fromkeys(
                str(dimension_id).strip().upper()
                for dimension_id in dimension_ids
                if str(dimension_id).strip()
            )
        )
        unknown = sorted(set(normalized) - set(self._dimension_ids))
        if unknown:
            raise ValueError("Unknown CEF dimension ids: " + ", ".join(unknown))
        ordered = [item for item in self._dimension_ids if item in normalized]
        selected = [item for item in self._dimensions if item["id"] in ordered]
        selected_names = {item["name"] for item in selected}
        relationships = [
            item
            for item in self._relationships
            if item["from"] in selected_names and item["to"] in selected_names
        ]
        payload = {
            "dimension_ids": ordered,
            "industry_profile": profile,
            "version": self.VERSION,
        }
        scope_id = "CEF-SCOPE-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return EnterpriseScope(
            scope_id=scope_id,
            dimension_ids=ordered,
            dimensions=json.loads(json.dumps(selected, ensure_ascii=True)),
            relationships=json.loads(json.dumps(relationships, ensure_ascii=True)),
            industry_profile=profile,
        )

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CEF enterprise model not found: {self.CONFIG_RELATIVE}")

    def _load_config(self) -> dict[str, Any]:
        data = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if data.get("version") != self.VERSION or data.get("abbreviation") != "CEF":
            raise ValueError("CEF enterprise model identity must be CEF 1.0")
        dimensions = data.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 10:
            raise ValueError("CEF must define exactly ten enterprise dimensions")
        expected = [f"CEF-D{index:02d}" for index in range(1, 11)]
        if [item.get("id") for item in dimensions] != expected:
            raise ValueError("CEF dimension ids must be ordered from CEF-D01 to CEF-D10")
        names = {item["name"] for item in dimensions}
        for relationship in data.get("relationships") or []:
            if relationship.get("from") not in names or relationship.get("to") not in names:
                raise ValueError("CEF relationship references an unknown dimension")
        return data
