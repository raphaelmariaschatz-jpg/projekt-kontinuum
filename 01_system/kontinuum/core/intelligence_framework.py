# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class IntelligenceDimensionMapping:
    mapping_id: str
    correlation_id: str
    touched_dimension_ids: list[str]
    dimensions: list[dict[str, Any]]
    output_boundary: str
    score_generated: bool = False
    decision_generated: bool = False
    execution_performed: bool = False
    self_modification_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalIntelligenceFramework:
    """Audit-only mapping of explicitly reported intelligence dimensions."""

    VERSION = "1.0"
    EVENT_KIND = "cif.dimension_mapping"
    CONFIG_RELATIVE = Path("24_config/cif_intelligence_dimensions_1_0.json")

    def __init__(self, project_root: str | Path, storage):
        self.project_root = Path(project_root)
        self.storage = storage
        self.config_path = self._resolve_config_path()
        self._config = self._load_config()
        self._dimensions = list(self._config["dimensions"])
        self._dimension_ids = [item["id"] for item in self._dimensions]

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Intelligence Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_audit_mapping_only",
            "dimensions": len(self._dimensions),
            "metrics": False,
            "scoring": False,
            "decision_authority": False,
            "execution": False,
            "self_modification": False,
            "direct_memory_write": False,
            "event_kind": self.EVENT_KIND,
        }

    def list_dimensions(self) -> list[dict[str, Any]]:
        return json.loads(json.dumps(self._dimensions, ensure_ascii=True))

    def build_mapping(
        self,
        *,
        touched_dimension_ids: list[str],
        correlation_id: str = "",
    ) -> IntelligenceDimensionMapping:
        normalized = list(
            dict.fromkeys(
                str(dimension_id).strip().upper()
                for dimension_id in touched_dimension_ids
                if str(dimension_id).strip()
            )
        )
        unknown = sorted(set(normalized) - set(self._dimension_ids))
        if unknown:
            raise ValueError("Unknown CIF dimension ids: " + ", ".join(unknown))
        ordered = [item for item in self._dimension_ids if item in normalized]
        selected = [
            json.loads(json.dumps(item, ensure_ascii=True))
            for item in self._dimensions
            if item["id"] in ordered
        ]
        reference = (correlation_id or "").strip()
        payload = {
            "correlation_id": reference,
            "touched_dimension_ids": ordered,
            "framework_version": self.VERSION,
        }
        mapping_id = "CIF-MAP-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return IntelligenceDimensionMapping(
            mapping_id=mapping_id,
            correlation_id=reference,
            touched_dimension_ids=ordered,
            dimensions=selected,
            output_boundary="audit_only",
        )

    def record_mapping(self, **kwargs: Any) -> IntelligenceDimensionMapping:
        mapping = self.build_mapping(**kwargs)
        self.storage.add(
            "events",
            self.EVENT_KIND,
            mapping.correlation_id or mapping.mapping_id,
            {
                "mapping_id": mapping.mapping_id,
                "touched_dimension_ids": mapping.touched_dimension_ids,
                "output_boundary": mapping.output_boundary,
                "score_generated": False,
                "decision_generated": False,
                "execution_performed": False,
                "self_modification_performed": False,
            },
        )
        return mapping

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CIF dimension matrix not found: {self.CONFIG_RELATIVE}")

    def _load_config(self) -> dict[str, Any]:
        data = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if data.get("version") != self.VERSION:
            raise ValueError("CIF dimension matrix version must be 1.0")
        dimensions = data.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 8:
            raise ValueError("CIF matrix must define exactly eight dimensions")
        expected = [f"CIF-{index:02d}" for index in range(1, 9)]
        if [item.get("id") for item in dimensions] != expected:
            raise ValueError("CIF dimension ids must be ordered from CIF-01 to CIF-08")
        for item in dimensions:
            if not isinstance(item.get("related_ccp_stages"), list):
                raise ValueError("CIF related CCP stages must be arrays")
            if not isinstance(item.get("boundaries"), list):
                raise ValueError("CIF boundaries must be arrays")
        return data
