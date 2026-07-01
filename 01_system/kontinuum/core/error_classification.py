from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class Severity(IntEnum):
    LOW = 10
    MEDIUM = 20
    HIGH = 30
    CRITICAL = 40

    @property
    def label(self) -> str:
        return {
            Severity.LOW: "NIEDRIG",
            Severity.MEDIUM: "MITTEL",
            Severity.HIGH: "HOCH",
            Severity.CRITICAL: "KRITISCH",
        }[self]


@dataclass(frozen=True)
class DiagnosticFinding:
    code: str
    area: str
    error: str
    impact: str
    probable_cause: str
    evidence: str = ""
    status: str = "OFFEN"
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    severity: Severity | None = None
    solution: str = ""


class ErrorClassificationEngine:
    """Assigns deterministic priorities from impact tags."""

    CRITICAL = {"data_loss", "security", "identity_violation"}
    HIGH = {"wrong_answer", "routing_error"}
    MEDIUM = {"performance"}

    def classify(self, finding: DiagnosticFinding) -> Severity:
        if finding.severity is not None:
            return finding.severity
        tags = set(finding.tags)
        if tags & self.CRITICAL:
            return Severity.CRITICAL
        if tags & self.HIGH:
            return Severity.HIGH
        if tags & self.MEDIUM:
            return Severity.MEDIUM
        return Severity.LOW

    def apply(self, finding: DiagnosticFinding) -> DiagnosticFinding:
        data = dict(finding.__dict__)
        data["severity"] = self.classify(finding)
        return DiagnosticFinding(**data)
