from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.capability_resolution_engine import CapabilityResolutionEngine
from kontinuum.core.conversation import Intent
from kontinuum.core.request_router import RequestRouter, RouteDecision
from kontinuum.tools.path_tools import PathTools


class FakeCAIM:
    def __init__(self, executable: set[str] | None = None):
        data = json.loads((ROOT / "24_config" / "canonical_agents.json").read_text(encoding="utf-8-sig"))
        self.agents = [dict(agent) for agent in data["agents"]]
        self.executable = executable

    def find_by_capability(self, capability: str, active_only: bool = True) -> list[dict]:
        needle = capability.casefold()
        return [
            dict(agent)
            for agent in self.agents
            if needle in {str(item).casefold() for item in agent.get("capabilities", [])}
            and (not active_only or agent.get("status") == "active")
        ]

    def get_agent(self, agent_id_or_name: str) -> dict | None:
        needle = agent_id_or_name.casefold()
        for agent in self.agents:
            if agent["id"].casefold() == needle or agent["name"].casefold() == needle:
                return dict(agent)
        return None

    def can_execute(self, agent_id_or_name: str) -> bool:
        agent = self.get_agent(agent_id_or_name)
        if not agent or agent.get("status") != "active":
            return False
        if self.executable is not None:
            return agent["id"] in self.executable or agent["name"] in self.executable
        return agent.get("type") not in {"external_api", "experimental", "disabled"}


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    paths = PathTools(Path(temporary))
    paths.ensure_all()
    registry = ROOT / "24_config" / "capability_registry_34_1.json"
    router = RequestRouter(paths)
    caim = FakeCAIM()
    engine = CapabilityResolutionEngine(caim, router, paths, registry_path=registry)

    validation = engine.validate_registry()
    assert validation["ok"]
    assert validation["capabilities"] == 46
    assert validation["unknown_allowed_agents"] == []

    lookup = engine.lookup("chemistry.lookup")
    assert lookup is not None
    assert lookup["capability_id"] == "chemistry.lookup"
    assert lookup["allowed_agents"] == ["chemistry_agent"]
    assert lookup["governance_level"] == "governance_required"

    chemistry = engine.resolve("Was ist Ethanol?", Intent("dialog.question", "question"))
    assert chemistry["required_capability"] == "chemistry.lookup"
    assert chemistry["recommended_agent"] == "chemistry_agent"
    assert chemistry["governance_required"] is True
    assert chemistry["governance_gate"]["ok"] is True
    assert chemistry["review_required"] is True
    assert chemistry["cmm_relevant"] is True
    assert chemistry["execution_allowed"] is True
    assert "RequestRouter" in chemistry["sources"]
    assert "CapabilityRegistry" in chemistry["sources"]

    git = engine.resolve("git status", Intent("command", "command"))
    assert git["required_capability"] == "git.status"
    assert git["recommended_agent"] == "git_agent"
    assert git["execution_allowed"] is True

    routed = router.decide("Bitte lies C:/Temp/beispiel.txt", Intent("command", "command"))
    routed_resolution = engine.resolve("Bitte lies C:/Temp/beispiel.txt", Intent("command", "command"), routed)
    assert routed.selected_agent == "file_agent"
    assert routed_resolution["required_capability"] == "file.read"
    assert routed_resolution["recommended_agent"] == "file_agent"

    blocked = CapabilityResolutionEngine(
        caim,
        router,
        paths,
        registry_path=registry,
        governance_context={"cam_status_ok": False, "foundation_rules_ok": True, "ccp_status_ok": True},
    ).resolve("git status", Intent("command", "command"))
    assert blocked["required_capability"] == "git.status"
    assert blocked["governance_gate"]["ok"] is False
    assert blocked["recommended_agent"] == ""
    assert blocked["execution_allowed"] is False
    assert blocked["priority"] == "blocked_by_governance"

    unknown_decision = RouteDecision("Sonderfall", "capability:not.registered", "fixture")
    unknown = engine.resolve("Unbekannte Sonderfaehigkeit", Intent("command", "command"), unknown_decision)
    assert unknown["required_capability"] == "not.registered"
    assert unknown["capability"] is None
    assert unknown["candidate_agents"] == []
    assert unknown["priority"] == "fallback_required"

    no_permission = CapabilityResolutionEngine(
        FakeCAIM(executable=set()),
        router,
        paths,
        registry_path=registry,
    ).resolve("git status", Intent("command", "command"))
    assert no_permission["recommended_agent"] == "git_agent"
    assert no_permission["execution_allowed"] is False

    multi = engine.resolve_many("Pruefe git status, analysiere danach Code und lies anschliessend C:/Temp/beispiel.txt")
    assert [item["required_capability"] for item in multi[:3]] == ["git.status", "code.inspect", "file.read"]

print("Capability Resolution Engine 1.0 tests passed")