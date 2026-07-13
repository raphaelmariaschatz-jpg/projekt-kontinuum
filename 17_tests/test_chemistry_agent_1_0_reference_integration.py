from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.chemistry_agent import ChemistryAgent
from kontinuum.core.conversation import ConversationManager
from kontinuum.core.request_router import RequestRouter
from kontinuum.core.storage import Storage
from kontinuum.core.system import KontinuumSystem
from kontinuum.foundation.canonical_agent_integration_manager import CanonicalAgentIntegrationManager
from kontinuum.foundation.canonical_memory_manager import CanonicalMemoryManager
from kontinuum.tools.path_tools import PathTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    paths = PathTools(root)
    paths.ensure_all()
    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    cmm = CanonicalMemoryManager(paths, storage)
    caim = CanonicalAgentIntegrationManager(paths, storage)

    assert caim.get_agent("chemistry_agent")
    assert caim.has_capability("chemistry_agent", "chemistry.lookup")
    assert caim.find_by_capability("chemistry.safety")[0]["name"] == "chemistry_agent"

    agent = ChemistryAgent(storage=storage, config={"canonical_memory_manager": cmm})
    assert agent.can_handle("Was ist Ethanol?")
    result = agent.handle("Was ist Ethanol?")
    assert result.handled
    assert result.agent == "chemistry_agent"
    assert "Ethanol" in result.answer
    assert "C2H6O" in result.answer
    assert result.meta["capability"] == "chemistry.lookup"

    safety = agent.handle("Welche Gefahrstoff-Sicherheit hat Ethanol?")
    assert safety.meta["capability"] == "chemistry.safety"
    assert "Review erforderlich: ja" in safety.answer

    router = RequestRouter(paths)
    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")
    intent = conversation.classify("Was ist Ethanol?")
    decision = router.decide("Was ist Ethanol?", intent)
    assert decision.selected_agent == "capability:chemistry.lookup"

    memories = cmm.search_memory("chemistry_agent", memory_class="knowledge")
    assert memories
    with storage.connect() as database:
        audit_count = database.execute("SELECT COUNT(*) FROM audit_events WHERE kind = 'chemistry.execution'").fetchone()[0]
    assert audit_count >= 2

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text("{\"enabled\": false}", encoding="utf-8")
    (config / "search_engine.json").write_text("{\"enabled\": false}", encoding="utf-8")
    (config / "language_model.json").write_text("{\"enabled\": false}", encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        registry = system.canonical_agent_integration_manager
        assert registry.get_agent("chemistry_agent")
        assert registry.has_capability("chemistry_agent", "chemistry.lookup")
        assert any(agent.name == "chemistry_agent" for agent in system.agents)

        answer = system.ask("Was ist Ethanol?")
        assert "Chemistry Agent 1.0" in answer
        assert "C2H6O" in answer
        assert "CMM-Kandidat: ja" in answer

        cmm_rows = system.canonical_memory_manager.search_memory("Ethanol", memory_class="knowledge")
        assert cmm_rows
        with system.storage.connect() as database:
            audit_count = database.execute("SELECT COUNT(*) FROM audit_events WHERE kind = 'chemistry.execution'").fetchone()[0]
        assert audit_count >= 1
    finally:
        system.close()

print("Chemistry Agent 1.0 reference integration tests passed")
