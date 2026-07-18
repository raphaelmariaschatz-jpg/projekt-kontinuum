# (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any
from xml.etree import ElementTree


@dataclass(frozen=True)
class APISourceRecord:
    source_id: str
    source_name: str
    source_type: str
    content_hash: str
    license_signal: str
    public_access: bool
    quarantine_status: str
    redaction_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class APIStructureRecord:
    api_structure_id: str
    source_id: str
    format: str
    service_name: str
    operations: list[dict[str, str]]
    schemas: list[str]
    auth_schemes: list[str]
    risk_flags: list[str]
    governance_state: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class APILearningAnalysis:
    source: APISourceRecord
    structure: APIStructureRecord
    capability_candidates: list[dict[str, Any]]
    network_request_executed: bool = False
    persistence_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class APILearningConnector:
    """Local, non-executing parser for supplied public API source material."""

    VERSION = "1.0"
    MAX_SOURCE_BYTES = 1_048_576
    HTTP_METHODS = frozenset(
        {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
    )
    MUTATING_METHODS = frozenset({"post", "put", "patch", "delete"})
    SECRET_KEYS = frozenset(
        {
            "access_token",
            "api_key",
            "apikey",
            "authorization",
            "client_secret",
            "cookie",
            "password",
            "refresh_token",
            "secret",
            "token",
        }
    )
    SENSITIVE_REFERENCE = re.compile(
        r"(?i)(?:access_token|api_key|apikey|authorization|client_secret|cookie|password|refresh_token|secret|token)="
    )

    def status(self) -> dict[str, Any]:
        return {
            "name": "API Learning Connector",
            "version": self.VERSION,
            "active": True,
            "mode": "local_supplied_source_analysis_only",
            "max_source_bytes": self.MAX_SOURCE_BYTES,
            "network_fetch": False,
            "request_execution": False,
            "persistence": False,
            "memory_write": False,
            "capability_registry_write": False,
        }

    def analyze_local(
        self,
        *,
        source_name: str,
        content: str | bytes,
        public_access: bool,
        license_signal: str = "unknown",
    ) -> APILearningAnalysis:
        reference = (source_name or "").strip()
        if not reference:
            raise ValueError("source_name is required")
        if not public_access:
            raise PermissionError("Only explicitly public source material is admitted")
        if self.SENSITIVE_REFERENCE.search(reference) or re.search(
            r"://[^/@:]+:[^/@]+@", reference
        ):
            raise ValueError("Source reference contains possible credentials")

        raw = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        if len(raw) > self.MAX_SOURCE_BYTES:
            raise ValueError("API learning source exceeds the local analysis size limit")
        text = raw.decode("utf-8-sig", errors="strict")
        if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
            raise ValueError("DTD and entity declarations are not allowed")

        content_hash = sha256(raw).hexdigest()
        parsed, source_type, redactions = self._parse_and_redact(reference, text)
        service_name, operations, schemas, auth_schemes = self._extract(
            source_type, reference, parsed
        )
        risk_flags = self._risk_flags(operations, redactions)
        source_id = "API-SOURCE-" + content_hash[:16]
        structure_payload = {
            "source_id": source_id,
            "format": source_type,
            "service_name": service_name,
            "operations": operations,
            "schemas": schemas,
            "auth_schemes": auth_schemes,
            "risk_flags": risk_flags,
        }
        structure_id = "API-STRUCTURE-" + sha256(
            json.dumps(
                structure_payload, ensure_ascii=True, sort_keys=True
            ).encode("ascii")
        ).hexdigest()[:16]

        source = APISourceRecord(
            source_id=source_id,
            source_name=reference,
            source_type=source_type,
            content_hash=content_hash,
            license_signal=(license_signal or "unknown").strip() or "unknown",
            public_access=True,
            quarantine_status="analyzed_in_memory_not_persisted",
            redaction_count=redactions,
        )
        structure = APIStructureRecord(
            api_structure_id=structure_id,
            source_id=source_id,
            format=source_type,
            service_name=service_name,
            operations=operations,
            schemas=schemas,
            auth_schemes=auth_schemes,
            risk_flags=risk_flags,
            governance_state="REVIEW",
        )
        return APILearningAnalysis(
            source=source,
            structure=structure,
            capability_candidates=self._capability_candidates(
                structure_id, operations
            ),
        )

    def _parse_and_redact(
        self, source_name: str, text: str
    ) -> tuple[Any, str, int]:
        stripped = text.lstrip()
        if stripped.startswith(("{", "[")):
            parsed = json.loads(text)
            redacted, count = self._redact(parsed)
            if isinstance(redacted, dict) and (
                "openapi" in redacted or "swagger" in redacted
            ):
                return redacted, "openapi", count
            if isinstance(redacted, dict) and "item" in redacted:
                return redacted, "postman", count
            return redacted, "json_document", count
        if stripped.startswith("<"):
            root = ElementTree.fromstring(text)
            kind = "wsdl" if self._local_name(root.tag) == "definitions" else "xml_document"
            return root, kind, 0
        suffix = Path(source_name).suffix.casefold()
        if "rfc" in source_name.casefold():
            return text, "rfc", 0
        if suffix in {".md", ".markdown"}:
            return text, "markdown", 0
        return text, "text_document", 0

    def _redact(self, value: Any) -> tuple[Any, int]:
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            count = 0
            for key, item in value.items():
                if str(key).casefold() in self.SECRET_KEYS:
                    result[str(key)] = "[REDACTED]"
                    count += 1
                else:
                    cleaned, nested_count = self._redact(item)
                    result[str(key)] = cleaned
                    count += nested_count
            return result, count
        if isinstance(value, list):
            result_list: list[Any] = []
            count = 0
            for item in value:
                cleaned, nested_count = self._redact(item)
                result_list.append(cleaned)
                count += nested_count
            return result_list, count
        return value, 0

    def _extract(
        self, source_type: str, source_name: str, parsed: Any
    ) -> tuple[str, list[dict[str, str]], list[str], list[str]]:
        if source_type == "openapi":
            info = parsed.get("info") or {}
            service_name = str(info.get("title") or Path(source_name).stem)
            operations: list[dict[str, str]] = []
            for path, path_item in (parsed.get("paths") or {}).items():
                if not isinstance(path_item, dict):
                    continue
                for method, operation in path_item.items():
                    normalized_method = str(method).casefold()
                    if normalized_method not in self.HTTP_METHODS:
                        continue
                    operation_data = operation if isinstance(operation, dict) else {}
                    operations.append(
                        {
                            "method": normalized_method.upper(),
                            "path": str(path),
                            "operation_id": str(operation_data.get("operationId") or ""),
                        }
                    )
            components = parsed.get("components") or {}
            schemas = sorted(str(name) for name in (components.get("schemas") or {}))
            auth_schemes = sorted(
                str(name) for name in (components.get("securitySchemes") or {})
            )
            return service_name, operations, schemas, auth_schemes
        if source_type == "postman":
            info = parsed.get("info") or {}
            operations = []
            self._collect_postman_operations(parsed.get("item") or [], operations)
            return str(info.get("name") or Path(source_name).stem), operations, [], []
        if source_type == "wsdl":
            operations = [
                {"method": "SOAP", "path": "", "operation_id": str(node.get("name") or "")}
                for node in parsed.iter()
                if self._local_name(node.tag) == "operation"
            ]
            return str(parsed.get("name") or Path(source_name).stem), operations, [], []
        return Path(source_name).stem, [], [], []

    def _collect_postman_operations(
        self, items: list[Any], operations: list[dict[str, str]]
    ) -> None:
        for item in items:
            if not isinstance(item, dict):
                continue
            nested = item.get("item")
            if isinstance(nested, list):
                self._collect_postman_operations(nested, operations)
            request = item.get("request")
            if not isinstance(request, dict):
                continue
            method = str(request.get("method") or "GET").upper()
            url = request.get("url")
            path = ""
            if isinstance(url, dict):
                path = "/" + "/".join(str(part) for part in (url.get("path") or []))
            elif isinstance(url, str):
                path = url.split("?", 1)[0]
            operations.append(
                {"method": method, "path": path, "operation_id": str(item.get("name") or "")}
            )

    def _risk_flags(
        self, operations: list[dict[str, str]], redactions: int
    ) -> list[str]:
        flags: list[str] = []
        if any(op["method"].casefold() in self.MUTATING_METHODS for op in operations):
            flags.append("mutating_operation_present")
        if redactions:
            flags.append("secret_like_fields_redacted")
        if not operations:
            flags.append("no_operations_extracted")
        return flags

    def _capability_candidates(
        self, structure_id: str, operations: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        for index, operation in enumerate(operations, start=1):
            mutating = operation["method"].casefold() in self.MUTATING_METHODS
            candidates.append(
                {
                    "candidate_id": f"{structure_id}-C{index:03d}",
                    "method": operation["method"],
                    "path": operation["path"],
                    "operation_id": operation["operation_id"],
                    "status": "candidate_only",
                    "governance_level": "blocked" if mutating else "human_approval",
                    "executable": False,
                    "registry_write_allowed": False,
                }
            )
        return candidates

    @staticmethod
    def _local_name(tag: str) -> str:
        return str(tag).rsplit("}", 1)[-1]
