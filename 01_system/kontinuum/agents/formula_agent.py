# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import re

from .base_agent import AgentResult, BaseAgent
from kontinuum.tools.formula_engine import FormulaEngine


class FormulaAgent(BaseAgent):
    name = "formula"

    def __init__(self, storage=None, tools=None, config=None):
        super().__init__(storage=storage, tools=tools, config=config)
        self.engine = FormulaEngine()

    def can_handle(self, prompt: str) -> bool:
        text = (prompt or "").strip()
        lower = text.casefold()
        return (
            lower in {"formelstatus", "formelnstatus"}
            or any(word in lower for word in (
                "formel", "berechne", "rechne", "wieviel ist", "wie viel ist", "ohmsch", "hook", "pythagoras",
                "einstein", "wasser", "sauerstoff", "phenol", "benzol", "ethanol", "methanol", "aceton",
                "essigsäure", "essigsaure", "natriumchlorid", "schwefelsäure", "schwefelsaure",
            ))
            or bool(re.search(r"\b[A-Za-z]\s*=\s*[A-Za-z]", text))
            or bool(re.search(r"\b(?:[A-Z][a-z]?\d*){2,}\b", text))
            or bool(re.fullmatch(r"[0-9\s,.+\-*/×xX·÷^%()√²³]+[=?!.]*", text))
        )

    def handle(self, prompt: str) -> AgentResult:
        answer = self.engine.answer(prompt)
        return AgentResult(self.name, bool(answer), answer or "Die Formel konnte nicht sicher erkannt werden.")
