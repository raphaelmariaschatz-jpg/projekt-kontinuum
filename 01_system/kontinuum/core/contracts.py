# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StoredRecord:
    table: str
    kind: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, allowed_tables: tuple[str, ...]) -> None:
        if self.table not in allowed_tables:
            raise ValueError(f"Unknown table: {self.table}")
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("Record kind must be a non-empty string.")
        if not isinstance(self.content, str):
            raise ValueError("Record content must be a string.")
        if not isinstance(self.metadata, dict):
            raise ValueError("Record metadata must be an object.")


@dataclass(frozen=True)
class SearchHit:
    area: str
    file: str
    snippet: str
    archive: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "file": self.file,
            "snippet": self.snippet,
            "archive": self.archive,
        }
