from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SYSTEM_PATH = ROOT / "01_system"
sys.path.insert(0, str(SYSTEM_PATH))

from kontinuum.core.conversation import ConversationManager
from kontinuum.core.storage import Storage


identity = {
    "name": "Kontinuum",
    "creator": "Raphael Schatz",
    "core_process": "Erkennen - Schaffen - Vollenden",
    "guiding_philosophy": "Der Weg ist das Ziel",
}
user = {"username": "Raphael Schatz", "full_name": "Raphael Schatz", "role": "SUPERADMIN"}

with tempfile.TemporaryDirectory() as temporary_directory:
    storage = Storage(Path(temporary_directory) / "kontinuum.db")
    conversation = ConversationManager(storage, identity, "23.0")
    conversation.bind_user(user)

    user_intent = conversation.classify("Wie ist mein Name?")
    assert user_intent.name == "truth.user_identity"
    assert "Raphael Schatz" in conversation.local_truth_answer(user_intent)

    combined = conversation.classify("Wie lautet dein Name und was ist dein Auftrag?")
    assert combined.name == "truth.identity_and_mission"
    assert "Kontinuum" in conversation.local_truth_answer(combined)
    assert "Auftrag" in conversation.local_truth_answer(combined)

    thought = conversation.classify("Blumen sind das Brot für die Seele")
    assert thought.input_type == "thought"

    follow_up = conversation.classify("Und wie lautet die Eulersche Zahl?")
    assert follow_up.is_follow_up

    conversation.log_turn("user", "Wie lautet die Eulersche Identität?", conversation.classify("Wie lautet die Eulersche Identität?"))
    conversation.log_turn("assistant", "e hoch i Pi plus 1 ist 0.", conversation.classify("Wie lautet die Eulersche Identität?"), "dialogue")
    conversation.log_turn("user", "Und wie lautet die Eulersche Zahl?", follow_up)
    turns = conversation.recent_context()
    assert [turn["role"] for turn in turns] == ["user", "assistant", "user"]
    assert turns[-1]["intent"] == "dialog.follow_up"

print("Kontinuum 23.0 conversation architecture tests passed")
