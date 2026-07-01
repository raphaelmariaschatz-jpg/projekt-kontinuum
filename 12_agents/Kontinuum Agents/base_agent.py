from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    agent: str
    handled: bool
    answer: str
    meta: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    name = "base"

    def __init__(self, storage=None, tools=None, config=None):
        self.storage = storage
        self.tools = tools or {}
        self.config = config or {}

    def can_handle(self, prompt: str) -> bool:
        return False

    def handle(self, prompt: str) -> AgentResult:
        return AgentResult(self.name, False, "")

    def remember(self, kind: str, content: str, meta: dict | None = None) -> None:
        if self.storage and hasattr(self.storage, "add_memory"):
            self.storage.add_memory(kind, content, meta or {})

    def add_edge(self, source: str, relation: str, target: str, meta: dict | None = None) -> None:
        if self.storage and hasattr(self.storage, "add_edge"):
            self.storage.add_edge(source, relation, target, meta or {})
