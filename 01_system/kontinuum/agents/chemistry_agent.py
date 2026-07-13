# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from .base_agent import BaseAgent, AgentResult


class ChemistryAgent(BaseAgent):
    name = "chemistry_agent"
    VERSION = "1.0"
    CAPABILITIES = {
        "lookup": "chemistry.lookup",
        "formula": "chemistry.formula",
        "cas": "chemistry.cas",
        "properties": "chemistry.properties",
        "safety": "chemistry.safety",
    }
    LOCAL_SUBSTANCES = {
        "ethanol": {
            "name": "Ethanol",
            "formula": "C2H6O",
            "cas": "64-17-5",
            "synonyms": ["Ethyl alcohol", "Alcohol"],
            "properties": {
                "substance_class": "alcohol",
                "molar_mass": "46.07 g/mol",
                "state": "liquid",
            },
            "safety": {
                "signal_word": "Danger",
                "hazards": ["flammable liquid"],
                "protective_notes": ["keep away from ignition sources", "use ventilation"],
                "review_required": True,
            },
        },
        "wasser": {
            "name": "Wasser",
            "formula": "H2O",
            "cas": "7732-18-5",
            "synonyms": ["Water"],
            "properties": {
                "substance_class": "inorganic compound",
                "molar_mass": "18.015 g/mol",
                "state": "liquid",
            },
            "safety": {
                "signal_word": "",
                "hazards": [],
                "protective_notes": [],
                "review_required": False,
            },
        },
        "natriumchlorid": {
            "name": "Natriumchlorid",
            "formula": "NaCl",
            "cas": "7647-14-5",
            "synonyms": ["Sodium chloride", "Kochsalz"],
            "properties": {
                "substance_class": "salt",
                "molar_mass": "58.44 g/mol",
                "state": "solid",
            },
            "safety": {
                "signal_word": "",
                "hazards": [],
                "protective_notes": [],
                "review_required": True,
            },
        },
    }
    FORMULA_PATTERN = re.compile(r"\b(?:[A-Z][a-z]?\d*){2,}\b")
    CAS_PATTERN = re.compile(r"\b\d{2,7}-\d{2}-\d\b")

    def can_handle(self, prompt: str) -> bool:
        value = (prompt or "").casefold()
        return (
            "chemistry." in value
            or "chemie" in value
            or "stoff" in value
            or "summenformel" in value
            or "cas" in value
            or any(name in value for name in self.LOCAL_SUBSTANCES)
            or bool(self.CAS_PATTERN.search(prompt or ""))
        )

    def handle(self, prompt: str) -> AgentResult:
        capability = self._capability(prompt)
        substance = self._substance(prompt)
        result = self._result_payload(prompt, capability, substance)
        self._record_governance(result)
        self._store_cmm_candidate(result)
        return AgentResult(
            self.name,
            True,
            self._format_answer(result),
            {
                "capability": capability,
                "chemistry_result": result,
                "read_only": True,
                "cmm_candidate": True,
            },
        )

    def _capability(self, prompt: str) -> str:
        value = (prompt or "").casefold()
        if self.CAS_PATTERN.search(prompt or "") or "cas" in value:
            return self.CAPABILITIES["cas"]
        if "sicherheit" in value or "gefahr" in value or "safety" in value:
            return self.CAPABILITIES["safety"]
        if "summenformel" in value or self.FORMULA_PATTERN.search(prompt or ""):
            return self.CAPABILITIES["formula"]
        if "eigenschaft" in value or "properties" in value:
            return self.CAPABILITIES["properties"]
        return self.CAPABILITIES["lookup"]

    def _substance(self, prompt: str) -> dict:
        value = (prompt or "").casefold()
        for key, substance in self.LOCAL_SUBSTANCES.items():
            names = [key, substance["name"].casefold(), *[item.casefold() for item in substance.get("synonyms", [])]]
            if any(name in value for name in names):
                return dict(substance)
        cas = self.CAS_PATTERN.search(prompt or "")
        formula = self.FORMULA_PATTERN.search(prompt or "")
        return {
            "name": cas.group(0) if cas else (formula.group(0) if formula else "Unbekannter Stoff"),
            "formula": formula.group(0) if formula else "",
            "cas": cas.group(0) if cas else "",
            "synonyms": [],
            "properties": {},
            "safety": {
                "signal_word": "",
                "hazards": [],
                "protective_notes": [],
                "review_required": True,
            },
        }

    def _result_payload(self, prompt: str, capability: str, substance: dict) -> dict:
        return {
            "agent": self.name,
            "version": self.VERSION,
            "capability": capability,
            "query": prompt,
            "result": substance,
            "provenance": {
                "source_type": "local_reference_or_review",
                "source": "chemistry_agent_1_0_local_reference",
                "confidence": "review_required",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "read_only": True,
            "cmm_candidate": True,
        }

    def _store_cmm_candidate(self, payload: dict) -> None:
        manager = self.config.get("canonical_memory_manager")
        if not manager:
            return
        result = payload.get("result", {})
        title = f"Chemistry Agent Kandidat: {result.get('name', 'Unbekannter Stoff')}"
        content = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        try:
            manager.save_memory(
                {
                    "class": "knowledge",
                    "title": title,
                    "content": content,
                    "source": "chemistry_agent_1_0",
                    "confidence": 0.5,
                    "importance": "medium",
                    "status": "active",
                },
                actor=self.name,
            )
        except Exception as exc:
            self._audit("chemistry.cmm_candidate_failed", payload.get("query", ""), {"error": str(exc)})

    def _record_governance(self, payload: dict) -> None:
        metadata = {
            "agent_id": "agent_chemistry",
            "agent": self.name,
            "capability": payload.get("capability", ""),
            "read_only": True,
            "cmm_candidate": True,
            "review_required": bool(payload.get("result", {}).get("safety", {}).get("review_required", True)),
            "source_type": payload.get("provenance", {}).get("source_type", ""),
        }
        self._audit("chemistry.execution", payload.get("query", ""), metadata)

    def _audit(self, kind: str, content: str, metadata: dict) -> None:
        if self.storage:
            self.storage.add("audit_events", kind, content, metadata)

    @staticmethod
    def _format_answer(payload: dict) -> str:
        result = payload.get("result", {})
        properties = result.get("properties", {})
        safety = result.get("safety", {})
        hazards = ", ".join(safety.get("hazards", [])) or "-"
        synonyms = ", ".join(result.get("synonyms", [])) or "-"
        return "\n".join([
            "Chemistry Agent 1.0: Stoffkarte (read-only, reviewpflichtig).",
            f"- Capability: {payload.get('capability', '')}",
            f"- Stoff: {result.get('name', '-')}",
            f"- Summenformel: {result.get('formula') or '-'}",
            f"- CAS: {result.get('cas') or '-'}",
            f"- Synonyme: {synonyms}",
            f"- Stoffklasse: {properties.get('substance_class', '-')}",
            f"- Molare Masse: {properties.get('molar_mass', '-')}",
            f"- Aggregatzustand: {properties.get('state', '-')}",
            f"- Signalwort: {safety.get('signal_word') or '-'}",
            f"- Gefahren: {hazards}",
            f"- Review erforderlich: {'ja' if safety.get('review_required', True) else 'nein'}",
            "- Externe Chemie-Tools: nicht verwendet.",
            "- CMM-Kandidat: ja.",
        ])
