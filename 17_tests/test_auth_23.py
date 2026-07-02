from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.auth import AuthManager


with tempfile.TemporaryDirectory() as temporary_root:
    root = Path(temporary_root)
    (root / "32_data").mkdir()
    (root / "10_security").mkdir()
    password_hash = hashlib.sha256(b"richtiges-testpasswort").hexdigest()
    user = {
        "username": "Raphael Schatz",
        "full_name": "Raphael Schatz",
        "role": "SUPERADMIN",
        "is_superadmin": True,
        "password_hash": password_hash,
        "permissions": {"can_execute_admin_commands": True},
    }
    (root / "32_data" / "auth_config.json").write_text(json.dumps(user), encoding="utf-8")
    (root / "10_security" / "auth_security_master.json").write_text(
        json.dumps({"security_entries": [user]}),
        encoding="utf-8",
    )
    auth = AuthManager(root)
    assert auth.status()["configured"]
    assert auth.status()["consistent"]
    verified = auth.verify_login("Raphael Schatz", "richtiges-testpasswort")
    assert verified["is_superadmin"]
    assert verified["authenticated"]
    assert auth.verify_superadmin_confirmation(verified, "richtiges-testpasswort", "Kostentest")
    assert not auth.verify_superadmin_confirmation(verified, "falsch", "Kostentest")
    assert not auth.verify_superadmin_confirmation({"role": "SUPERADMIN"}, "richtiges-testpasswort", "Kostentest")
    assert auth.verify_login("Raphael Schatz", "falsch") is None
    assert auth.verify_login("Unbekannt", "richtiges-testpasswort") is None

print("Kontinuum auth tests passed")
