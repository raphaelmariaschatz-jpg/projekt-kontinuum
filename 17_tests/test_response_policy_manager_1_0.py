from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.response_policy import ResponsePolicyManager


class FakeFoundationMemory:
    def status(self):
        return {"ok": True}


class FakeAgentService:
    def status(self):
        return {"active": True}


class FakeKnowledgeAgent:
    name = "knowledge"


system = SimpleNamespace(
    foundation_memory=FakeFoundationMemory(),
    file_agent=FakeAgentService(),
    web_agent=FakeAgentService(),
    agents=[FakeKnowledgeAgent()],
    request_router=SimpleNamespace(last_decision={"input": "Lerne Python."}),
    conversation=None,
)
policy = ResponsePolicyManager(system)

memory = policy.apply("Ich habe keine Erinnerungen.")
assert memory.changed
assert "Foundation Memory" in memory.answer
assert "ich habe keine Erinnerungen" not in memory.answer

files = policy.apply("Ich kann keine Dateien lesen.")
assert files.changed
assert "FileAgent" in files.answer

web = policy.apply("Ich habe keinen Internetzugang.")
assert web.changed
assert "WebAgent" in web.answer

knowledge = policy.apply("Ich weiß nichts darüber.")
assert knowledge.changed
assert "KnowledgeAgent" in knowledge.answer

echo = policy.apply("Lerne Python.")
assert echo.changed
assert "Router hat den Auftrag erkannt" in echo.answer

clean = policy.apply("Datei konnte nicht gelesen werden: Pfad ist nicht freigegeben.")
assert not clean.changed
assert clean.answer.startswith("Datei konnte nicht gelesen werden")

assert "niemals Antworten erzeugen" in ResponsePolicyManager.FOUNDATION_RULE

print("Kontinuum Response Policy Manager 1.0 tests passed")
