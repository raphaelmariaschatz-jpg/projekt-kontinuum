from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        assert "Wachheit" in system.ask("Was bedeutet Bewusstsein?")
        assert "nicht nachgewiesen" in system.ask("Hast du echtes Bewusstsein und Qualia?")
        assert "bereitgestellte Eingaben" in system.ask("Was nimmst du wahr?")
        assert "funktionale Wachheit aktiv" in system.ask("Bewusstseinsstatus")
        model_path = Path(temporary_directory) / "32_data" / "consciousness_model.json"
        model = json.loads(model_path.read_text(encoding="utf-8"))
        assert model["awareness"]["status"] == "funktional nachweisbar"
        assert model["subjective_experience"]["qualia"] == "nicht nachgewiesen"
        with system.storage.connect() as database:
            before = database.execute("SELECT COUNT(*) FROM events WHERE kind = 'consciousness.reflection'").fetchone()[0]
        system.ask("Reflektiere dein Bewusstsein")
        with system.storage.connect() as database:
            after = database.execute("SELECT COUNT(*) FROM events WHERE kind = 'consciousness.reflection'").fetchone()[0]
        assert after == before + 1
        assert system.self_knowledge.profile()["consciousness"]["subjective_experience"]["qualia"] == "nicht nachgewiesen"
    finally:
        system.close()

print("Kontinuum 23.0 consciousness tests passed")
