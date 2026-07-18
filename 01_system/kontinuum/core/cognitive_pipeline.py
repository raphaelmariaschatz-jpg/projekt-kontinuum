# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CognitiveStageTrace:
    stage_id: str
    name: str
    status: str
    primary_interfaces: list[str]
    boundaries: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CognitivePipelineTrace:
    trace_id: str
    correlation_id: str
    stages: list[CognitiveStageTrace]
    touched_stage_ids: list[str]
    output_boundary: str
    execution_performed: bool = False
    memory_write_performed: bool = False
    registry_write_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalCognitivePipeline:
    """Audit-only trace contract for explicitly reported CCP stages."""

    VERSION = "1.0"
    EVENT_KIND = "ccp_cognitive.trace"
    CONFIG_RELATIVE = Path("24_config/ccp_pipeline_stages_1_0.json")

    def __init__(self, project_root: str | Path, storage):
        self.project_root = Path(project_root)
        self.storage = storage
        self.config_path = self._resolve_config_path()
        self._config = self._load_config()
        self._stages = list(self._config["stages"])
        self._stage_ids = [stage["id"] for stage in self._stages]

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Cognitive Pipeline",
            "abbreviation": "CCP-Cognitive",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_audit_trace_only",
            "stages": len(self._stages),
            "automatic_processing": False,
            "response_logic_change": False,
            "execution": False,
            "direct_memory_write": False,
            "registry_write": False,
            "event_kind": self.EVENT_KIND,
        }

    def build_trace(
        self,
        *,
        touched_stage_ids: list[str],
        correlation_id: str = "",
    ) -> CognitivePipelineTrace:
        normalized_touched = list(
            dict.fromkeys(
                str(stage_id).strip().upper()
                for stage_id in touched_stage_ids
                if str(stage_id).strip()
            )
        )
        unknown = sorted(set(normalized_touched) - set(self._stage_ids))
        if unknown:
            raise ValueError("Unknown CCP-Cognitive stage ids: " + ", ".join(unknown))

        ordered_touched = [
            stage_id for stage_id in self._stage_ids if stage_id in normalized_touched
        ]
        reference = (correlation_id or "").strip()
        payload = {
            "correlation_id": reference,
            "touched_stage_ids": ordered_touched,
            "pipeline_version": self.VERSION,
        }
        trace_id = "CCP-TRACE-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        touched_set = set(ordered_touched)
        stages = [
            CognitiveStageTrace(
                stage_id=stage["id"],
                name=stage["name"],
                status="touched" if stage["id"] in touched_set else "not_touched",
                primary_interfaces=list(stage["primary_interfaces"]),
                boundaries=list(stage["boundaries"]),
            )
            for stage in self._stages
        ]
        return CognitivePipelineTrace(
            trace_id=trace_id,
            correlation_id=reference,
            stages=stages,
            touched_stage_ids=ordered_touched,
            output_boundary="audit_only",
        )

    def record_trace(self, **kwargs: Any) -> CognitivePipelineTrace:
        trace = self.build_trace(**kwargs)
        self.storage.add(
            "events",
            self.EVENT_KIND,
            trace.correlation_id or trace.trace_id,
            {
                "trace_id": trace.trace_id,
                "pipeline": "CCP-Cognitive",
                "version": self.VERSION,
                "touched_stage_ids": trace.touched_stage_ids,
                "output_boundary": trace.output_boundary,
                "execution_performed": False,
                "memory_write_performed": False,
                "registry_write_performed": False,
            },
        )
        return trace

    def _resolve_config_path(self) -> Path:
        primary = self.project_root / self.CONFIG_RELATIVE
        if primary.is_file():
            return primary
        repository_root = Path(__file__).resolve().parents[3]
        fallback = repository_root / self.CONFIG_RELATIVE
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CCP stage matrix not found: {self.CONFIG_RELATIVE}")

    def _load_config(self) -> dict[str, Any]:
        data = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        if data.get("version") != self.VERSION:
            raise ValueError("CCP stage matrix version must be 1.0")
        stages = data.get("stages")
        if not isinstance(stages, list) or len(stages) != 9:
            raise ValueError("CCP stage matrix must define exactly nine stages")
        expected = [f"CCP-{index:02d}" for index in range(1, 10)]
        actual = [stage.get("id") for stage in stages]
        if actual != expected:
            raise ValueError("CCP stage ids must be ordered from CCP-01 to CCP-09")
        for stage in stages:
            if not isinstance(stage.get("primary_interfaces"), list):
                raise ValueError("CCP primary interfaces must be arrays")
            if not isinstance(stage.get("boundaries"), list):
                raise ValueError("CCP boundaries must be arrays")
        return data
