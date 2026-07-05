from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.application_services import PromptOrchestrator
from kontinuum.core.conversation import ConversationManager
from kontinuum.core.file_agent import FileAgentService
from kontinuum.core.storage import Storage
from kontinuum.tools.path_tools import PathTools


class FakeMemoryCore:
    def observe(self, text: str, owner: str = "") -> dict:
        return {"ok": True, "text": text, "owner": owner}


class FakeDiagnostics:
    def __init__(self):
        self.triggers = []

    def run(self, trigger: str = "automatic.startup") -> dict:
        self.triggers.append(trigger)
        return {
            "ok": False,
            "count": 1,
            "highest_severity": "MEDIUM",
            "message": "Autonomous Diagnostics: 1 Fund, höchster Schweregrad MEDIUM.",
            "findings": [
                {
                    "title": "Testfund",
                    "area": "routing",
                    "severity": "MEDIUM",
                    "evidence": "simulierter Routinghinweis",
                }
            ],
        }


class FakeStatus:
    def __init__(self, label: str):
        self.label = label

    def format_status(self) -> str:
        return f"{self.label}: ok"


class FakeCodeAgent(FakeStatus):
    def status(self) -> dict:
        return {"active": True, "label": self.label}


class FakeGuard:
    def should_integrate(self, *args, **kwargs) -> bool:
        return False


class FakeKnowledgePlatform:
    def integrate(self, *args, **kwargs) -> None:
        raise AssertionError("Regressionstest darf keine Dialogantwort integrieren.")


class FakeFoundationDecision:
    def mark_created(self, *args, **kwargs) -> None:
        raise AssertionError("Kein Foundation-Decision-Zyklus im Regressionstest erwartet.")

    def complete(self, *args, **kwargs) -> None:
        raise AssertionError("Kein Foundation-Decision-Zyklus im Regressionstest erwartet.")


class FakeSystem:
    version = "34.1"

    def __init__(self, root: Path):
        self.path_tools = PathTools(root)
        self.path_tools.ensure_all()
        config_path = self.path_tools.paths()["config"] / "file_agent_1_0.json"
        config_path.write_text(
            json.dumps(
                {
                    "enabled": True,
                    "mode": "diagnostic_read_only",
                    "allowed_roots": ["."],
                    "no_source_mutation": True,
                }
            ),
            encoding="utf-8",
        )
        self.storage = Storage(self.path_tools.paths()["data"] / "kontinuum.db")
        self.conversation = ConversationManager(
            self.storage,
            {
                "name": "Kontinuum",
                "creator": "Raphael",
                "core_process": "Erkennen - Schaffen - Vollenden",
                "guiding_philosophy": "Der Weg ist das Ziel",
                "address_user_as": "Raphael",
            },
            self.version,
        )
        self.agent_config = {}
        self.agents = []
        self.tools = {}
        self.search_mode = "Automatisch"
        self._foundation_context = SimpleNamespace(decision_id=None)
        self.foundation_decision = FakeFoundationDecision()
        self.memory_core = FakeMemoryCore()
        self.knowledge_contamination_guard = FakeGuard()
        self.knowledge_platform = FakeKnowledgePlatform()
        self.file_agent = FileAgentService(self.path_tools, storage=self.storage)
        self.autonomous_diagnostics = FakeDiagnostics()
        self.canonical_agent_integration_manager = FakeStatus("CAIM")
        self.canonical_memory_manager = FakeStatus("CMM")
        self.identity_manager = FakeStatus("CIM")
        self.code_agent = FakeCodeAgent("CodeAgent")

    def status(self) -> dict:
        return {"ok": True, "version": self.version}


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary)
    system = FakeSystem(root)
    project = root / "Projekt Kontinuum"
    project.mkdir()
    orchestrator = PromptOrchestrator(system)
    system.request_router = orchestrator.request_router

    prompt = (
        f'Du hast Vollzugriff auf deinen Projektordner "{project}".\n'
        "Bitte mache einen vollständigen Funktionstest und schreibe einen Bericht über Fehler, "
        "Schwachstellen und gewünschte Erweiterungen."
    )
    answer = orchestrator.handle(prompt)

    assert "FileAgent: Projektordner freigegeben:" in answer
    assert str(project.resolve()) in answer
    assert "[DIAGNOSTIKBERICHT]" in answer
    assert "1. Gefundene Fehler:" in answer
    assert "2. Gefundene Schwachstellen:" in answer
    assert "3. Gewünschte Erweiterungen:" in answer
    assert "Ein vollständiger automatischer Funktionstest ist noch nicht vollständig angebunden." in answer
    assert answer.strip() != f"FileAgent: Projektordner freigegeben: {project.resolve()}"
    assert system.autonomous_diagnostics.triggers == ["user.function_test_report"]

    pure_answer = orchestrator.handle(f'Du hast Vollzugriff auf deinen Projektordner "{project}".')
    assert "FileAgent: Projektordner freigegeben:" in pure_answer
    assert "[DIAGNOSTIKBERICHT]" not in pure_answer

print("Kontinuum Multi-Intent FileAgent Diagnostics 34.1 tests passed")
