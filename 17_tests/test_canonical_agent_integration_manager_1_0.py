from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.storage import Storage
from kontinuum.core.system import KontinuumSystem
from kontinuum.foundation.canonical_agent_integration_manager import (
    AgentRegistryValidationError,
    CanonicalAgentIntegrationManager,
)
from kontinuum.tools.path_tools import PathTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    storage = Storage(root / "32_data" / "kontinuum.db")
    manager = CanonicalAgentIntegrationManager(PathTools(root), storage)

    assert manager.load_agents()["schema_version"] == "1.0"
    assert manager.get_agent("memory")
    assert manager.has_capability("memory", "memory.read")
    assert manager.find_by_capability("memory.read")[0]["name"] == "memory"

    registered = manager.register_agent(
        {
            "id": "agent_test",
            "name": "test_agent",
            "type": "internal",
            "status": "active",
            "version": "1.0",
            "description": "Testagent fuer CAIM.",
            "capabilities": ["test.run", "test.status"],
            "allowed_tools": [],
            "governance_required": True,
            "read_only": True,
            "entrypoint": "tests.TestAgent",
        },
        actor="test",
    )
    assert registered["ok"] is True
    assert manager.get_agent("agent_test")["governance_required"] is True

    try:
        manager.register_agent(
            {
                "id": "agent_test",
                "name": "another_test_agent",
                "type": "internal",
                "description": "Doppelte ID.",
                "capabilities": ["test.other"],
                "entrypoint": "tests.OtherAgent",
            },
            actor="test",
        )
        raise AssertionError("Doppelte Agent-ID wurde akzeptiert")
    except AgentRegistryValidationError:
        pass

    try:
        manager.register_agent(
            {
                "id": "agent_test_2",
                "name": "test_agent",
                "type": "internal",
                "description": "Doppelter Name.",
                "capabilities": ["test.other"],
                "entrypoint": "tests.OtherAgent",
            },
            actor="test",
        )
        raise AssertionError("Doppelter Agentenname wurde akzeptiert")
    except AgentRegistryValidationError:
        pass

    disabled = manager.disable_agent("agent_test", actor="test")
    assert disabled["ok"] is True
    assert manager.get_agent("agent_test")["status"] == "disabled"
    assert not manager.has_capability("agent_test", "test.run")

    enabled = manager.enable_agent("agent_test", actor="test")
    assert enabled["ok"] is True
    assert manager.get_agent("agent_test")["status"] == "active"
    assert manager.can_execute("agent_test") is True
    assert manager.governance_required("agent_test") is True

    external = manager.register_agent(
        {
            "id": "agent_external",
            "name": "external_agent",
            "type": "external_api",
            "status": "active",
            "description": "Externer Agent fuer Sicherheitsregeltest.",
            "capabilities": ["external.plan"],
            "entrypoint": "",
        },
        actor="test",
    )
    assert external["ok"] is True
    assert manager.get_agent("agent_external")["status"] == "experimental"
    assert manager.can_execute("agent_external") is False

    saved = manager.save_agents(actor="test")
    assert saved["ok"] is True
    assert manager.validate_agents()
    assert manager.integrity_status() == "ok"
    assert "Canonical Agent Integration Manager 1.0 Status" in manager.format_status()

    bad = manager._copy_data()
    bad["agents"][0]["name"] = bad["agents"][1]["name"]
    bad["hash"] = ""
    try:
        manager.validate_agents(bad)
        raise AssertionError("Doppelter Agentenname wurde akzeptiert")
    except AgentRegistryValidationError:
        pass

    bad_hash = manager._copy_data()
    bad_hash["hash"] = "broken"
    try:
        manager.validate_agents(bad_hash)
        raise AssertionError("Ungueltiger Datei-Hash wurde akzeptiert")
    except AgentRegistryValidationError:
        pass

    history = root / "24_config" / "history" / "canonical_agent_history"
    assert list(history.glob("canonical_agents_*.json"))
    governance_path = history / "canonical_agent_governance.jsonl"
    assert governance_path.exists()
    assert "agent_test" in governance_path.read_text(encoding="utf-8")
    with storage.connect() as database:
        governance = database.execute("SELECT COUNT(*) FROM audit_events WHERE kind = 'canonical_agent.change'").fetchone()[0]
    assert governance >= 4

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text("{\"enabled\": false}", encoding="utf-8")
    (config / "search_engine.json").write_text("{\"enabled\": false}", encoding="utf-8")
    (config / "language_model.json").write_text("{\"enabled\": false}", encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        assert "canonical_agent_integration_manager" in system.agent_config
        assert system.status()["canonical_agent_integration_manager"]["registered_agents"] >= 14
        answer = system.ask("caim status")
        assert "Canonical Agent Integration Manager 1.0 Status" in answer
        assert "registrierte Agenten" in answer
    finally:
        system.close()

print("Canonical Agent Integration Manager 1.0 tests passed")
