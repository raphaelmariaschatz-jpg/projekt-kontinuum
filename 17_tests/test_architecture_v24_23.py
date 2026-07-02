from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.agent_registry import AgentRouter, build_agents
from kontinuum.core.auth import AuthManager
from kontinuum.core.storage import Storage


with tempfile.TemporaryDirectory() as temporary_root:
    root = Path(temporary_root)
    (root / "32_data").mkdir()
    (root / "10_security").mkdir()
    legacy_hash = hashlib.sha256(b"migration-test-password").hexdigest()
    user = {
        "username": "Raphael Schatz",
        "full_name": "Raphael Schatz",
        "role": "SUPERADMIN",
        "is_superadmin": True,
        "password_hash": legacy_hash,
        "permissions": {"can_execute_admin_commands": True},
    }
    (root / "32_data" / "auth_config.json").write_text(json.dumps(user), encoding="utf-8")
    (root / "10_security" / "auth_security_master.json").write_text(
        json.dumps({"security_entries": [dict(user)]}),
        encoding="utf-8",
    )
    auth = AuthManager(root)
    assert auth.verify_login("Raphael Schatz", "migration-test-password")
    active = json.loads((root / "32_data" / "auth_config.json").read_text(encoding="utf-8"))
    master = json.loads((root / "10_security" / "auth_security_master.json").read_text(encoding="utf-8"))
    assert active["password_hash"].startswith("$argon2id$")
    assert active["password_hash"] == master["security_entries"][0]["password_hash"]
    assert auth.verify_login("Raphael Schatz", "migration-test-password")

with tempfile.TemporaryDirectory() as temporary_root:
    storage = Storage(Path(temporary_root) / "kontinuum.db")
    storage.add("events", "test.event", "indexed contract", {"valid": True})
    try:
        storage.add("events", "", "invalid", {})
        raise AssertionError("Empty record kind accepted.")
    except ValueError:
        pass
    connection = storage.connect()
    try:
        indexes = connection.execute("PRAGMA index_list(events)").fetchall()
    finally:
        connection.close()
    assert any("kind_created" in row["name"] for row in indexes)

agents = build_agents()
router = AgentRouter(agents)
assert router.diagnose("pythonstatus", "command")["selected"] == "python"
assert router.diagnose("wingetstatus", "command")["selected"] == "winget"
assert router.diagnose("Eine freie Aussage", "dialog.thought")["selected"] == "dialogue"

print("Kontinuum version 24 architecture foundation tests passed")
