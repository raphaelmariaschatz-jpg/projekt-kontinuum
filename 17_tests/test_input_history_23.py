from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
system_path = ROOT / "01_system" if (ROOT / "01_system").is_dir() else ROOT.parent / "01_system"
sys.path.insert(0, str(system_path))

from kontinuum.core.storage import Storage


with tempfile.TemporaryDirectory() as temp_directory:
    storage = Storage(Path(temp_directory) / "kontinuum.db")
    storage.add_memory("dialog.user", "Alte Eingabe", {"agent": "dialogue"})
    storage.add_memory("dialog.assistant", "Keine Benutzereingabe", {"agent": "dialogue"})
    storage.add_memory("user.input", "Frühere zentrale Eingabe", {"source": "system.ask"})
    storage.add_memory("dialog.user", "Doppelter Agenteneintrag", {"agent": "dialogue"})
    storage.add("events", "conversation.turn", "Neue zentrale Eingabe", {"role": "user", "session_id": "test"})
    storage.add("events", "conversation.turn", "Neue zentrale Antwort", {"role": "assistant", "session_id": "test"})
    storage.add_memory("dialog.user", "Doppelter neuer Agenteneintrag", {"agent": "dialogue"})

    rows = storage.user_inputs_for_local_date(datetime.now(timezone.utc).astimezone().date())
    assert [row["content"] for row in rows] == ["Alte Eingabe", "Frühere zentrale Eingabe", "Neue zentrale Eingabe"]

print("Kontinuum 23.0 input history tests passed")
