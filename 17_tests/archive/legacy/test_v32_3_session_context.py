from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.identity_router import IdentityRouter
from kontinuum.core.session_context import SessionContext
from kontinuum.version import APP_VERSION


identity = {"name": "Kontinuum", "creator": "Raphael Schatz"}
session = SessionContext(identity)
current = session.current()
assert current["display_name"] == "Raphael Schatz"
assert current["role"] == "SUPERADMIN"
assert current["is_creator"] is True
assert current["authenticated"] is True

status = session.format_status()
assert "Sessionstatus" in status
assert "Raphael Schatz" in status
assert "SUPERADMIN" in status

router = IdentityRouter(session, identity)
answer = router.answer("wer ist angemeldet")
assert answer and "Raphael Schatz" in answer and "lokal" in answer

print(f"Kontinuum {APP_VERSION} session context tests passed")
