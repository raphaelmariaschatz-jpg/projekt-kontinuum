# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CanonicalTokenSequence:
    sequence_id: str
    document_id: str
    language: str
    tokenizer_type: str
    tokenizer_version: str
    tokens: list[dict[str, Any]]
    completed_stage_ids: list[str]
    model_independent: bool = True
    model_invoked: bool = False
    semantic_representation_generated: bool = False
    training_performed: bool = False
    direct_memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalLanguageProcessingFramework:
    """Canonical token-contract validation without tokenization or model use."""

    VERSION = "1.0"
    FRAMEWORK_CONFIG = Path("24_config/canonical_language_processing_framework_1_0.json")
    TOKEN_CONFIG = Path("24_config/clpf_token_schema_1_0.json")
    PIPELINE_CONFIG = Path("24_config/clpf_processing_pipeline_1_0.json")

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.framework_path = self._resolve_config_path(self.FRAMEWORK_CONFIG)
        self.token_path = self._resolve_config_path(self.TOKEN_CONFIG)
        self.pipeline_path = self._resolve_config_path(self.PIPELINE_CONFIG)
        self._framework = self._read_json(self.framework_path)
        self._token_schema = self._read_json(self.token_path)
        self._pipeline = self._read_json(self.pipeline_path)
        self._validate_configs()
        self._steps = list(self._framework["processing_steps"])
        self._token_fields = dict(self._token_schema["token_object"])
        self._stages = list(self._pipeline["stages"])
        self._tokenizer_types = {
            str(value).casefold()
            for value in self._token_fields["tokenizer_type"]["allowed_values"]
        }

    def status(self) -> dict[str, Any]:
        return {
            "name": "Canonical Language Processing Framework",
            "version": self.VERSION,
            "active": True,
            "mode": "explicit_token_contract_validation_only",
            "processing_steps": len(self._steps),
            "token_fields": len(self._token_fields),
            "tokenization": False,
            "model_integration": False,
            "semantic_inference": False,
            "training": False,
            "fine_tuning": False,
            "weight_management": False,
            "direct_memory_write": False,
        }

    def list_processing_steps(self) -> list[dict[str, Any]]:
        return self._copy(self._steps)

    def token_schema(self) -> dict[str, Any]:
        return self._copy(self._token_fields)

    def build_token_sequence(
        self,
        *,
        document_id: str,
        language: str,
        tokenizer_type: str,
        tokenizer_version: str,
        tokens: list[dict[str, Any]],
    ) -> CanonicalTokenSequence:
        normalized_document = (document_id or "").strip()
        normalized_language = (language or "").strip().casefold()
        normalized_tokenizer = (tokenizer_type or "").strip().casefold()
        normalized_version = (tokenizer_version or "").strip()
        if not normalized_document:
            raise ValueError("CLPF document_id must not be empty")
        if not normalized_language:
            raise ValueError("CLPF language must not be empty")
        if normalized_tokenizer not in self._tokenizer_types:
            raise ValueError(f"Unsupported CLPF tokenizer type: {tokenizer_type}")
        if not normalized_version:
            raise ValueError("CLPF tokenizer_version must not be empty")
        if not isinstance(tokens, list) or not tokens:
            raise ValueError("CLPF token sequence must contain at least one token")

        canonical_tokens = [
            self._validate_token(
                token,
                index=index,
                document_id=normalized_document,
                language=normalized_language,
                tokenizer_type=normalized_tokenizer,
            )
            for index, token in enumerate(tokens)
        ]
        token_ids = [item["token_id"] for item in canonical_tokens]
        if len(token_ids) != len(set(token_ids)):
            raise ValueError("CLPF token_id values must be unique within a sequence")

        payload = {
            "document_id": normalized_document,
            "language": normalized_language,
            "tokenizer_type": normalized_tokenizer,
            "tokenizer_version": normalized_version,
            "tokens": canonical_tokens,
            "completed_stage_ids": ["CLPF-01", "CLPF-02", "CLPF-03"],
        }
        sequence_id = "CLPF-SEQ-" + sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()[:16]
        return CanonicalTokenSequence(sequence_id=sequence_id, **payload)

    def _validate_token(
        self,
        token: dict[str, Any],
        *,
        index: int,
        document_id: str,
        language: str,
        tokenizer_type: str,
    ) -> dict[str, Any]:
        if not isinstance(token, dict):
            raise ValueError(f"CLPF token at index {index} must be an object")
        required = {
            "token_id",
            "surface",
            "position",
            "span",
            "sentence_id",
            "document_id",
            "metadata",
        }
        missing = sorted(required - set(token))
        if missing:
            raise ValueError("CLPF token is missing fields: " + ", ".join(missing))

        canonical = self._copy(token)
        canonical["token_id"] = str(canonical["token_id"]).strip()
        canonical["surface"] = str(canonical["surface"])
        canonical["normalized_surface"] = str(
            canonical.get("normalized_surface", canonical["surface"])
        )
        canonical["tokenizer_type"] = str(
            canonical.get("tokenizer_type", tokenizer_type)
        ).strip().casefold()
        canonical["tokenizer_local_id"] = str(
            canonical.get("tokenizer_local_id", "")
        )
        canonical["language"] = str(canonical.get("language", language)).strip().casefold()
        canonical["sentence_id"] = str(canonical["sentence_id"]).strip()
        canonical["document_id"] = str(canonical["document_id"]).strip()
        if not canonical["token_id"] or not canonical["sentence_id"]:
            raise ValueError("CLPF token_id and sentence_id must not be empty")
        if canonical["document_id"] != document_id:
            raise ValueError("CLPF token document_id must match its sequence")
        if canonical["language"] != language:
            raise ValueError("CLPF token language must match its sequence")
        if canonical["tokenizer_type"] != tokenizer_type:
            raise ValueError("CLPF token tokenizer_type must match its sequence")

        position = canonical["position"]
        span = canonical["span"]
        metadata = canonical["metadata"]
        if not isinstance(position, dict) or not isinstance(span, dict):
            raise ValueError("CLPF token position and span must be objects")
        if not isinstance(metadata, dict):
            raise ValueError("CLPF token metadata must be an object")
        absolute_index = position.get("absolute_index")
        if not isinstance(absolute_index, int) or absolute_index != index:
            raise ValueError("CLPF absolute token indexes must be contiguous from zero")
        source_start = span.get("source_start")
        source_end = span.get("source_end")
        if (
            not isinstance(source_start, int)
            or not isinstance(source_end, int)
            or source_start < 0
            or source_end < source_start
        ):
            raise ValueError("CLPF token span must be a valid non-negative range")
        return canonical

    def _validate_configs(self) -> None:
        if self._framework.get("version") != self.VERSION or self._framework.get("abbreviation") != "CLPF":
            raise ValueError("CLPF framework identity must be CLPF 1.0")
        expected_steps = [f"CLPF-{index:02d}" for index in range(1, 7)]
        steps = self._framework.get("processing_steps")
        if not isinstance(steps, list) or [item.get("id") for item in steps] != expected_steps:
            raise ValueError("CLPF must define ordered processing steps CLPF-01 to CLPF-06")
        if self._token_schema.get("version") != self.VERSION:
            raise ValueError("CLPF token schema version must be 1.0")
        token_object = self._token_schema.get("token_object")
        if not isinstance(token_object, dict) or len(token_object) != 11:
            raise ValueError("CLPF token schema must define exactly eleven fields")
        stages = self._pipeline.get("stages")
        if self._pipeline.get("version") != self.VERSION or not isinstance(stages, list):
            raise ValueError("CLPF pipeline identity must be version 1.0")
        if [item.get("id") for item in stages] != expected_steps:
            raise ValueError("CLPF pipeline stages must match the framework steps")

    def _resolve_config_path(self, relative_path: Path) -> Path:
        primary = self.project_root / relative_path
        if primary.is_file():
            return primary
        fallback = Path(__file__).resolve().parents[3] / relative_path
        if fallback.is_file():
            return fallback
        raise FileNotFoundError(f"CLPF configuration not found: {relative_path}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))

    @staticmethod
    def _copy(value: Any) -> Any:
        return json.loads(json.dumps(value, ensure_ascii=True))
