from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    config = Path(temporary_directory) / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text(
        json.dumps({"enabled": False}),
        encoding="utf-8",
    )
    (config / "search_engine.json").write_text(
        json.dumps({"enabled": False}),
        encoding="utf-8",
    )
    system = KontinuumSystem(temporary_directory)
    try:
        system.set_user_context({"username": "Raphael Schatz", "full_name": "Raphael Schatz", "role": "SUPERADMIN"})

        assert "Raphael Schatz" in system.ask("Wie ist mein Name?")
        combined = system.ask("Wie lautet dein Name und was ist dein Auftrag?")
        assert "Kontinuum" in combined and "Auftrag" in combined

        calls = []

        def model_answer(prompt, context=None, local_truths=None, user=None):
            calls.append({"prompt": prompt, "context": context or [], "local_truths": local_truths or {}, "user": user or {}})
            return {"ok": True, "answer": f"Modellantwort: {prompt}"}

        system.tools["language_model_tools"].generate = model_answer
        assert system.ask("Wie lautet die Eulersche Identität?").startswith("Modellantwort:")
        assert system.ask("Und wie lautet die Eulersche Zahl?").startswith("Modellantwort:")
        assert any(turn["content"] == "Wie lautet die Eulersche Identität?" for turn in calls[-1]["context"])
        assert calls[-1]["user"]["full_name"] == "Raphael Schatz"
        assert calls[-1]["local_truths"]["system_name"] == "Kontinuum"

        assert system.ask("Blumen sind das Brot für die Seele").startswith("Modellantwort:")
        system.ask("lerne Chemie")
        system.ask("Wie lautet die Eulersche Identität?")
        assert all(turn.get("intent") != "command" for turn in calls[-1]["context"])

        db = system.storage.connect()
        try:
            rows = db.execute(
                "SELECT content, metadata FROM events WHERE kind = 'conversation.turn' ORDER BY id"
            ).fetchall()
        finally:
            db.close()
        metadata = [json.loads(row["metadata"]) for row in rows]
        assert len(rows) == 14
        assert all(item["session_id"] == system.conversation.session_id for item in metadata)
        assert metadata[-2]["input_type"] == "question"
        assert metadata[-1]["agent"] == "knowledge_agent"
    finally:
        system.close()

print("Kontinuum 23.0 conversation system tests passed")
