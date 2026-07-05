from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.request_router import RequestRouter
from kontinuum.core.conversation import Intent
from kontinuum.core.system import KontinuumSystem
from kontinuum.tools.path_tools import PathTools


IDENTITY_BLOCK = """identity:
  creator:
    id: creator_001
    name: Raphael Schatz
  user:
    preferred_address: Raphael
  assistant:
    name: Kontinuum
    short_name: K
"""


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "language_model.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "canonical_identity_34_1.json").write_text(
        json.dumps({
            "identity": {
                "creator": {"id": "creator_001", "name": "Raphael Schatz"},
                "user": {"preferred_address": "Raph"},
                "assistant": {"name": "Kontinuum", "short_name": "K"},
            }
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    decision = RequestRouter(PathTools(root)).decide(IDENTITY_BLOCK, Intent("dialog.thought", "thought"))
    assert decision.request_class == "Identity/Config"
    assert decision.selected_agent == "identity_manager"
    assert RequestRouter(PathTools(root)).decide("preferred_address: Raphael", Intent("dialog.thought", "thought")).selected_agent == "identity_manager"

    system = KontinuumSystem(root)
    try:
        assert system.ask("") == "Ich bin bereit, Raph."
        status = system.ask("identity status")
        assert "Creator: Raphael Schatz" in status
        assert "bevorzugte Anrede: Raph" in status
        assert "Assistant-Name: Kontinuum" in status
        assert "Short Name: K" in status
        assert "Speicherpfad:" in status
        assert "letzter Änderungszeitpunkt:" in status
        answer = system.ask(IDENTITY_BLOCK)
        identity_path = config / "canonical_identity.json"
        payload = json.loads(identity_path.read_text(encoding="utf-8"))
        backups = list((config / "history" / "canonical_identity_history").glob("canonical_identity_*.json"))
        memory_answer = system.ask("identitystatus")
        memory_agent = next(agent for agent in system.agents if agent.name == "memory")
        blocked = memory_agent.handle("speichere identity: creator: Test").answer

        assert "Ich habe die kanonische Identität gespeichert" in answer
        assert payload["creator"]["name"] == "Raphael Schatz"
        assert payload["user"]["preferred_address"] == "Raphael"
        assert payload["assistant"]["short_name"] == "K"
        assert backups
        assert "Canonical Identity Manager 1.0" in memory_answer
        assert "ausschließlich über den Canonical Identity Manager" in blocked
        assert "- lokale Datei: ja" in answer
        assert "- Memory: ja" in answer
    finally:
        system.close()

print("Identity/Config routing 34.1 test passed")
