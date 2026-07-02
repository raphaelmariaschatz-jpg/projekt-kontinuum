from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.request_router import RequestRouter
from kontinuum.core.storage import Storage
from kontinuum.core.conversation import ConversationManager
from kontinuum.tools.formula_engine import FormulaEngine
from kontinuum.tools.path_tools import PathTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary)
    paths = PathTools(root)
    paths.ensure_all()
    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")
    router = RequestRouter(paths)

    examples = {
        "Was ist Quantendynamik?": ("Wissensfrage", "knowledge_agent"),
        "Lerne Python.": ("Lernauftrag", "learning_agent"),
        "Öffne https://docs.python.org/3/": ("Webauftrag", "web_agent"),
        "Lies Datei handbuch.pdf.": ("Dateioperation", "file_agent"),
        "Lernstatus.": ("Statusabfrage", "status_agent"),
        "CanonicalEngineStatus.": ("Governance", "canonical_engine"),
        "126 × 254,87": ("Rechenaufgabe", "math_agent"),
    }
    for prompt, expected in examples.items():
        decision = router.decide(prompt, conversation.classify(prompt))
        assert (decision.request_class, decision.selected_agent) == expected, (prompt, decision)
        router.record(prompt, decision, f"selected={decision.selected_agent}", decision.selected_agent)

    status = router.format_status()
    assert "Request Router 1.0 Status" in status
    assert "math_agent" in status
    assert len((paths.paths()["logs"] / "request_router_1_0.jsonl").read_text(encoding="utf-8").splitlines()) == len(examples)

    math = FormulaEngine().answer("126 × 254,87")
    assert math == "126 × 254,87 = 32 113,62"

print("Kontinuum Request Router & KnowledgeAgent 1.0 tests passed")
