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
        assert "belegbare" in system.ask("Was bedeutet Selbsterkenntnis?")
        assert "Stärken" in system.ask("Was sind deine Stärken?")
        assert "kein menschliches Selbst" in system.ask("Hast du Emotionen?")
        assert "nicht belegt" in system.ask("Wie wirkst du auf andere?")
        assert "blinden Flecken" in system.ask("Welche blinden Flecken hast du?")
        model = json.loads((Path(temporary_directory) / "32_data" / "self_model.json").read_text(encoding="utf-8"))
        assert model["identity"]["name"] == "Kontinuum"
        assert model["limitations"]
        with system.storage.connect() as database:
            before = database.execute("SELECT COUNT(*) FROM events WHERE kind = 'self_knowledge.reflection'").fetchone()[0]
        system.ask("Reflektiere dich selbst")
        with system.storage.connect() as database:
            after = database.execute("SELECT COUNT(*) FROM events WHERE kind = 'self_knowledge.reflection'").fetchone()[0]
        assert after == before + 1
    finally:
        system.close()

print("Kontinuum 23.0 self knowledge tests passed")
