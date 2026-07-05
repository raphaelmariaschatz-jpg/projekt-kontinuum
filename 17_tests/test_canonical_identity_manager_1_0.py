from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.conversation import Intent
from kontinuum.core.request_router import RequestRouter
from kontinuum.core.storage import Storage
from kontinuum.foundation.canonical_identity_manager import CanonicalIdentityManager, IdentityValidationError
from kontinuum.tools.path_tools import PathTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    storage = Storage(root / "32_data" / "kontinuum.db")
    manager = CanonicalIdentityManager(PathTools(root), storage)

    assert manager.get_creator_name() == "Raphael Schatz"
    assert manager.get_preferred_address() == "Raphael"
    assert manager.get_assistant()["short_name"] == "K"
    assert manager.has_role("creator", "super_admin")
    assert manager.is_creator("creator_001")
    assert manager.is_super_admin("creator")
    assert len(manager.identity_hash(manager.data)) == 64

    invalid = dict(manager.data)
    invalid.pop("creator")
    try:
        manager.validate(invalid)
        raise AssertionError("Ungültige Struktur wurde akzeptiert")
    except IdentityValidationError:
        pass

    result = manager.save({"user": {"preferred_address": "Raph"}}, actor="test", change="preferred_address_update")
    assert result["ok"] is True
    assert Path(result["backup"]).exists()
    assert json.loads((root / "24_config" / "canonical_identity.json").read_text(encoding="utf-8"))["user"]["preferred_address"] == "Raph"
    assert json.loads((root / "24_config" / "canonical_identity_34_1.json").read_text(encoding="utf-8"))["identity"]["user"]["preferred_address"] == "Raph"
    assert (root / "24_config" / "history" / "canonical_identity_history" / "canonical_identity_governance.jsonl").exists()
    with storage.connect() as database:
        governance = database.execute("SELECT COUNT(*) FROM audit_events WHERE kind = 'canonical_identity.change'").fetchone()[0]
        foundation_memory = database.execute("SELECT COUNT(*) FROM foundation_memory WHERE kind LIKE 'canonical_identity.%'").fetchone()[0]
    assert governance >= 1
    assert foundation_memory >= 1

    router = RequestRouter(PathTools(root))
    assert router.decide("creator:", Intent("dialog.thought", "thought")).selected_agent == "identity_manager"
    assert router.decide("preferred_address: Raphael", Intent("dialog.thought", "thought")).selected_agent == "identity_manager"
    assert router.decide("assistant:", Intent("dialog.thought", "thought")).selected_agent == "identity_manager"
    assert router.decide("role:", Intent("dialog.thought", "thought")).selected_agent == "identity_manager"

print("Canonical Identity Manager 1.0 tests passed")
