from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .conversation import Intent, normalize
from .request_router import RequestRouter, RouteDecision


class CapabilityRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class Capability:
    capability_id: str
    name: str
    description: str
    supported_intents: tuple[str, ...]
    priority: int
    governance_level: str
    allowed_agents: tuple[str, ...]
    prerequisites: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, value: dict) -> "Capability":
        required = {
            "capability_id",
            "name",
            "description",
            "supported_intents",
            "priority",
            "governance_level",
            "allowed_agents",
        }
        missing = required - set(value)
        if missing:
            raise CapabilityRegistryError(f"Capability-Pflichtfelder fehlen: {', '.join(sorted(missing))}")
        if not str(value.get("capability_id", "")).strip():
            raise CapabilityRegistryError("capability_id darf nicht leer sein.")
        if not isinstance(value.get("supported_intents"), list) or not value["supported_intents"]:
            raise CapabilityRegistryError(f"supported_intents fehlt fuer {value.get('capability_id')}")
        if not isinstance(value.get("allowed_agents"), list) or not value["allowed_agents"]:
            raise CapabilityRegistryError(f"allowed_agents fehlt fuer {value.get('capability_id')}")
        return cls(
            capability_id=str(value["capability_id"]).strip(),
            name=str(value["name"]).strip(),
            description=str(value["description"]).strip(),
            supported_intents=tuple(str(item) for item in value["supported_intents"]),
            priority=int(value["priority"]),
            governance_level=str(value["governance_level"]).strip(),
            allowed_agents=tuple(str(item) for item in value["allowed_agents"]),
            prerequisites=tuple(str(item) for item in value.get("prerequisites", [])),
        )

    def to_dict(self) -> dict:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "supported_intents": list(self.supported_intents),
            "priority": self.priority,
            "governance_level": self.governance_level,
            "allowed_agents": list(self.allowed_agents),
            "prerequisites": list(self.prerequisites),
        }


@dataclass
class CapabilityResolution:
    intent: str
    request_class: str
    text: str
    required_capability: str
    capability: dict | None = None
    candidate_agents: list[dict] = field(default_factory=list)
    recommended_agent: str = ""
    priority: str = "unknown"
    governance_required: bool = False
    governance_gate: dict = field(default_factory=dict)
    human_approval_required: bool = False
    read_only: bool = True
    review_required: bool = True
    cmm_relevant: bool = True
    execution_allowed: bool = False
    reason: str = ""
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class CapabilityResolutionEngine:
    """Deterministic resolver between RequestRouter, governance and agents."""

    VERSION = "1.0"
    REGISTRY_FILE = "capability_registry_34_1.json"
    GOVERNANCE_LEVELS_REQUIRING_REVIEW = {"controlled", "governance_required", "foundation"}
    DIRECT_CAPABILITY_BY_AGENT = {
        "canonical_engine": "governance.architecture",
        "canonical_git_manager": "governance.git",
        "code_agent": "code.inspect",
        "config_fallback": "identity.read",
        "diagnostic_agent": "architecture.status",
        "dialogue_agent": "memory.read",
        "file_agent": "file.read",
        "git_agent": "git.status",
        "identity_manager": "identity.write",
        "knowledge_agent": "memory.read",
        "learning_agent": "learning.run",
        "math_agent": "memory.read",
        "memory_agent": "memory.write",
        "programming_agent": "code.inspect",
        "status_agent": "architecture.status",
        "vision_agent": "vision.inspect",
        "web_agent": "web.read",
    }
    CAPABILITY_BY_REQUEST_CLASS = {
        "Administration": "architecture.status",
        "Bildanalyse": "vision.inspect",
        "Canonical Git Governance": "governance.git",
        "Codeanalyse": "code.inspect",
        "Dateioperation": "file.read",
        "Diagnose": "architecture.status",
        "Git": "git.status",
        "Governance": "governance.architecture",
        "Identity/Config": "identity.write",
        "Konfiguration": "identity.read",
        "Lernauftrag": "learning.run",
        "Memory": "memory.write",
        "Programmierung": "code.inspect",
        "Rechenaufgabe": "memory.read",
        "Statusabfrage": "architecture.status",
        "Webauftrag": "web.read",
        "Wissensfrage": "memory.read",
    }
    CAPABILITY_MARKERS = (
        ("file.status", ("fileagent testen", "teste den fileagent", "fileagentstatus", "fileagent status")),
        ("code.inspect", ("code analysieren", "codeanalyse", "projektkarte", "quellcode")),
        ("governance.architecture", ("governance", "canonical", "freigabe", "release gate", "prufauftrag", "prüfauftrag")),
        ("memory.write", ("merke", "speichere", "erinnerung")),
        ("web.read", ("internet", "websuche", "url", "http://", "https://")),
        ("git.status", ("git status", "gitstatus")),
        ("vision.inspect", ("bild", "vision", ".png", ".jpg", ".jpeg")),
    )
    READ_ONLY_SUFFIXES = (".read", ".status", ".inspect", ".lookup", ".formula", ".cas", ".properties", ".safety", ".map")
    HUMAN_APPROVAL_MARKERS = ("losche", "lösche", "delete", "extern", "external_api", "release", "produktiv", "schreibzugriff")
    REVIEW_PREFIXES = ("governance.", "identity.", "canonical_", "knowledge.", "learning.", "source.")
    CMM_PREFIXES = ("knowledge.", "memory.", "canonical_memory.", "identity.", "canonical_identity.", "chemistry.")

    def __init__(
        self,
        caim=None,
        router: RequestRouter | None = None,
        path_tools=None,
        registry_path: str | Path | None = None,
        governance_context: dict | None = None,
    ):
        self.caim = caim
        self.path_tools = path_tools
        self.router = router or (RequestRouter(path_tools) if path_tools else None)
        self.registry_path = self._resolve_registry_path(registry_path, path_tools)
        self.registry = self._load_registry()
        self.capabilities = {item.capability_id: item for item in self.registry}
        self.governance_context = governance_context or {}

    def resolve(self, text: str, intent: Intent | str | None = None, decision: RouteDecision | None = None) -> dict:
        resolved_intent = self._intent_name(intent)
        route = decision or self._route(text, intent)
        capability_id = self._required_capability(text, route)
        capability = self.capabilities.get(capability_id)
        candidates = self._candidate_agents(capability) if capability else []
        ranked = self._rank_candidates(capability, candidates) if capability else []
        governance_required = self._governance_required(capability, ranked)
        gate = self._governance_gate(capability, governance_required)
        human_approval = self._human_approval_required(text, capability, ranked, governance_required)
        recommended = ranked[0]["name"] if ranked and gate["ok"] and not human_approval else ""
        read_only = self._is_read_only(capability, ranked)
        review = self._review_required(capability, governance_required, human_approval, gate)
        cmm = self._cmm_relevant(capability, review)
        execution_allowed = bool(recommended and not human_approval and gate["ok"] and self._can_execute(recommended))
        resolution = CapabilityResolution(
            intent=resolved_intent,
            request_class=route.request_class if route else "",
            text=(text or "").strip(),
            required_capability=capability_id,
            capability=capability.to_dict() if capability else None,
            candidate_agents=ranked,
            recommended_agent=recommended,
            priority=self._priority(capability, ranked, gate, human_approval),
            governance_required=governance_required,
            governance_gate=gate,
            human_approval_required=human_approval,
            read_only=read_only,
            review_required=review,
            cmm_relevant=cmm,
            execution_allowed=execution_allowed,
            reason=self._reason(capability_id, capability, ranked, gate, human_approval),
            sources=self._sources(route, capability, ranked),
        )
        return resolution.to_dict()

    def resolve_many(self, text: str, intents: list[Intent | str] | None = None) -> list[dict]:
        segments = self.split_multi_intent(text) or [(text or "").strip()]
        results = []
        for index, segment in enumerate(segment for segment in segments if segment):
            intent = intents[index] if intents and index < len(intents) else None
            results.append(self.resolve(segment, intent=intent))
        return results

    def lookup(self, capability_id: str) -> dict | None:
        capability = self.capabilities.get(capability_id)
        return capability.to_dict() if capability else None

    def validate_registry(self) -> dict:
        return {
            "ok": bool(self.capabilities),
            "path": str(self.registry_path) if self.registry_path else "",
            "capabilities": len(self.capabilities),
            "unknown_allowed_agents": self._unknown_allowed_agents(),
        }

    def status(self) -> dict:
        validation = self.validate_registry()
        return {
            "version": self.VERSION,
            "mode": "deterministic_registry_resolution",
            "registry_path": validation["path"],
            "registered_capabilities": validation["capabilities"],
            "registry_ok": validation["ok"] and not validation["unknown_allowed_agents"],
            "unknown_allowed_agents": validation["unknown_allowed_agents"],
            "caim_connected": self.caim is not None,
            "router_connected": self.router is not None,
            "executes_agents": False,
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Capability Resolution Engine 1.0 Status:",
            f"- Modus: {status['mode']}",
            f"- Registry: {status['registry_path']}",
            f"- registrierte Capabilities: {status['registered_capabilities']}",
            f"- Registry ok: {'ja' if status['registry_ok'] else 'nein'}",
            f"- CAIM angebunden: {'ja' if status['caim_connected'] else 'nein'}",
            f"- Router angebunden: {'ja' if status['router_connected'] else 'nein'}",
            f"- führt Agenten aus: {'ja' if status['executes_agents'] else 'nein'}",
        ])

    def split_multi_intent(self, text: str) -> list[str]:
        value = (text or "").strip()
        if not value:
            return []
        lines = [line.strip(" .") for line in value.splitlines() if line.strip()]
        segments: list[str] = []
        for line in lines:
            protected = re.sub(r"(?i)\b[a-z]:[\\/][^\r\n\"']+", lambda match: match.group(0).replace(" und ", " __UND__ "), line)
            protected = re.sub(r"(?i),\s+", "; ", protected)
            protected = re.sub(r"(?i)\s+und\s+(?=(teste|prüfe|pruefe|erstelle|mache|fuehre|führe|analysiere|lies|lese)\b)", "; ", protected)
            protected = re.sub(r"(?i)\b(teste|prüfe|pruefe|erstelle|mache|fuehre|führe|analysiere|lies|lese)\s+(?:danach|anschliessend|anschließend)\s+", r"\1 ", protected)
            parts = re.split(r"(?i)(?:\b(?:bitte|danach|anschliessend|anschließend|und dann)\b|;)", protected)
            for part in parts:
                cleaned = part.replace("__UND__", "und").strip(" .,:;\t")
                if cleaned:
                    segments.append(cleaned)
        return self._merge_short_segments(segments)

    def _resolve_registry_path(self, registry_path: str | Path | None, path_tools) -> Path | None:
        if registry_path:
            return Path(registry_path)
        if path_tools:
            return path_tools.paths()["config"] / self.REGISTRY_FILE
        return None

    def _load_registry(self) -> tuple[Capability, ...]:
        if not self.registry_path or not self.registry_path.exists():
            return ()
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise CapabilityRegistryError(f"Capability Registry ungueltig: {self.registry_path}") from exc
        if data.get("schema_version") != self.VERSION:
            raise CapabilityRegistryError("Capability Registry schema_version 1.0 fehlt.")
        capabilities = data.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            raise CapabilityRegistryError("Capability Registry enthaelt keine Capabilities.")
        rows = tuple(Capability.from_dict(item) for item in capabilities)
        ids = [item.capability_id for item in rows]
        if len(ids) != len(set(ids)):
            raise CapabilityRegistryError("Doppelte capability_id in Capability Registry.")
        return rows

    def _route(self, text: str, intent: Intent | str | None) -> RouteDecision | None:
        if not self.router:
            return None
        try:
            intent_obj = intent if isinstance(intent, Intent) else None
            return self.router.decide(text, intent_obj)
        except Exception:
            return None

    def _required_capability(self, text: str, route: RouteDecision | None) -> str:
        if route and route.selected_agent.startswith("capability:"):
            return route.selected_agent.split(":", 1)[1]
        marker_capability = self._marker_capability(text)
        if marker_capability:
            return marker_capability
        if route:
            return self.DIRECT_CAPABILITY_BY_AGENT.get(route.selected_agent) or self.CAPABILITY_BY_REQUEST_CLASS.get(route.request_class) or "unknown"
        return "unknown"

    def _marker_capability(self, text: str) -> str:
        value = normalize(text)
        for capability, markers in self.CAPABILITY_MARKERS:
            if any(marker in value for marker in markers):
                return capability
        return ""

    def _candidate_agents(self, capability: Capability | None) -> list[dict]:
        if not capability:
            return []
        rows: dict[str, dict] = {}
        if self.caim and hasattr(self.caim, "find_by_capability"):
            try:
                for candidate in self.caim.find_by_capability(capability.capability_id):
                    if candidate.get("name") in capability.allowed_agents:
                        rows[candidate.get("name", "")] = dict(candidate)
            except Exception:
                pass
        if self.caim and hasattr(self.caim, "get_agent"):
            for agent_name in capability.allowed_agents:
                try:
                    agent = self.caim.get_agent(agent_name)
                except Exception:
                    agent = None
                if agent:
                    rows[agent.get("name", agent_name)] = dict(agent)
        if not rows:
            for agent_name in capability.allowed_agents:
                rows[agent_name] = {
                    "id": agent_name,
                    "name": agent_name,
                    "status": "unknown",
                    "type": "unknown",
                    "capabilities": [capability.capability_id],
                    "governance_required": capability.governance_level in self.GOVERNANCE_LEVELS_REQUIRING_REVIEW,
                    "read_only": capability.capability_id.endswith(self.READ_ONLY_SUFFIXES),
                }
        return list(rows.values())

    def _rank_candidates(self, capability: Capability | None, candidates: list[dict]) -> list[dict]:
        if not capability:
            return []
        ranked = []
        for candidate in candidates:
            score = self._candidate_score(capability, candidate)
            ranked.append({**candidate, "resolution_score": score})
        return sorted(ranked, key=lambda item: (-item["resolution_score"], item.get("name", "")))

    def _candidate_score(self, capability: Capability, candidate: dict) -> int:
        capabilities = {str(item).casefold() for item in candidate.get("capabilities", [])}
        score = 100 if capability.capability_id.casefold() in capabilities else 20
        if candidate.get("status") == "active":
            score += 20
        if candidate.get("read_only"):
            score += 8
        if candidate.get("type") in {"internal", "foundation"}:
            score += 6
        if self._can_execute(candidate.get("id") or candidate.get("name")):
            score += 5
        if candidate.get("name") in capability.allowed_agents:
            score += 4
        if candidate.get("governance_required"):
            score -= 2
        score -= max(capability.priority, 0) // 20
        return score

    def _can_execute(self, agent_id_or_name: str | None) -> bool:
        if not agent_id_or_name:
            return False
        if not self.caim or not hasattr(self.caim, "can_execute"):
            return False
        try:
            return bool(self.caim.can_execute(agent_id_or_name))
        except Exception:
            return False

    def _governance_required(self, capability: Capability | None, candidates: list[dict]) -> bool:
        if not capability:
            return False
        if capability.governance_level in self.GOVERNANCE_LEVELS_REQUIRING_REVIEW:
            return True
        return bool(candidates and candidates[0].get("governance_required"))

    def _governance_gate(self, capability: Capability | None, governance_required: bool) -> dict:
        if not capability:
            return {"ok": False, "reason": "unknown_capability", "checks": {}}
        checks = {
            "foundation_rules_ok": self._context_bool("foundation_rules_ok", True),
            "cam_status_ok": self._context_bool("cam_status_ok", True),
            "ccp_status_ok": self._context_bool("ccp_status_ok", True),
            "governance_rules_ok": self._context_bool("governance_rules_ok", True),
        }
        ok = all(checks.values())
        if governance_required and "governance_review_required" in capability.prerequisites:
            checks["governance_review_required"] = True
        return {
            "ok": ok,
            "reason": "passed" if ok else "blocked_by_governance_prerequisite",
            "checks": checks,
            "prerequisites": list(capability.prerequisites),
        }

    def _context_bool(self, key: str, default: bool) -> bool:
        return bool(self.governance_context.get(key, default))

    def _is_read_only(self, capability: Capability | None, candidates: list[dict]) -> bool:
        if not capability:
            return True
        if capability.capability_id.endswith(self.READ_ONLY_SUFFIXES):
            return True
        return bool(candidates) and all(bool(candidate.get("read_only")) for candidate in candidates)

    def _human_approval_required(self, text: str, capability: Capability | None, candidates: list[dict], governance: bool) -> bool:
        value = normalize(text)
        external = any(candidate.get("type") in {"external_api", "experimental"} for candidate in candidates)
        controlled_write = bool(capability and capability.governance_level == "controlled" and not self._is_read_only(capability, candidates))
        explicit_risk = any(marker in value for marker in self.HUMAN_APPROVAL_MARKERS)
        return external or explicit_risk or (governance and controlled_write and explicit_risk)

    def _review_required(self, capability: Capability | None, governance: bool, human_approval: bool, gate: dict) -> bool:
        if not capability:
            return True
        return human_approval or governance or not gate.get("ok", False) or capability.capability_id.startswith(self.REVIEW_PREFIXES)

    def _cmm_relevant(self, capability: Capability | None, review_required: bool) -> bool:
        if not capability:
            return False
        return review_required or capability.capability_id.startswith(self.CMM_PREFIXES)

    @staticmethod
    def _intent_name(intent: Intent | str | None) -> str:
        if isinstance(intent, Intent):
            return intent.name
        return str(intent or "")

    @staticmethod
    def _priority(capability: Capability | None, candidates: list[dict], gate: dict, human_approval: bool) -> str:
        if not capability:
            return "fallback_required"
        if not gate.get("ok", False):
            return "blocked_by_governance"
        if human_approval:
            return "human_review"
        if candidates:
            return "direct_orchestrator_handoff"
        return "capability_unresolved"

    @staticmethod
    def _reason(capability_id: str, capability: Capability | None, candidates: list[dict], gate: dict, human_approval: bool) -> str:
        if not capability:
            return f"Capability {capability_id} ist nicht in der kanonischen Registry registriert."
        if not candidates:
            return f"Capability {capability_id} ist registriert, aber kein erlaubter Agent ist verfuegbar."
        if not gate.get("ok", False):
            return f"Capability {capability_id} wurde erkannt, aber Governance-Voraussetzungen blockieren die Auswahl."
        if human_approval:
            return f"Capability {capability_id} hat Kandidaten, benoetigt aber menschliche Freigabe."
        return f"Capability {capability_id} wurde auf {candidates[0].get('name', 'unbekannt')} priorisiert."

    @staticmethod
    def _sources(route: RouteDecision | None, capability: Capability | None, candidates: list[dict]) -> list[str]:
        sources = ["CapabilityRegistry"] if capability else []
        if route:
            sources.append("RequestRouter")
        if candidates:
            sources.append("CAIM" if any(candidate.get("status") == "active" for candidate in candidates) else "CapabilityRegistry.allowed_agents")
        return sources

    def _unknown_allowed_agents(self) -> list[str]:
        if not self.caim or not hasattr(self.caim, "get_agent"):
            return []
        unknown: list[str] = []
        for capability in self.registry:
            for agent_name in capability.allowed_agents:
                try:
                    exists = self.caim.get_agent(agent_name)
                except Exception:
                    exists = True
                if not exists:
                    unknown.append(f"{capability.capability_id}:{agent_name}")
        return sorted(set(unknown))

    @staticmethod
    def _merge_short_segments(segments: list[str]) -> list[str]:
        merged: list[str] = []
        for segment in segments:
            if merged and len(segment.split()) == 1 and not re.match(r"(?i)^(teste|prüfe|pruefe|erstelle|mache|fuehre|führe|analysiere|lies|lese)\\b", segment):
                merged[-1] = f"{merged[-1]} {segment}".strip()
            else:
                merged.append(segment)
        return merged