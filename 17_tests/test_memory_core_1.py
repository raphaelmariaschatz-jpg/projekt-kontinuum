from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.memory_core import MemoryCore
from kontinuum.core.storage import Storage
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    storage = Storage(Path(temporary_root) / "memory.db")
    core = MemoryCore(storage)

    first = core.remember(
        "Version 24.1 ist umgesetzt, Tests bestanden, offen: externer Webrecherche-Test überschreitet 3 Minuten",
        owner="Raphael",
    )
    assert first["layer"] == "project"
    assert first["structured"]["projekt"] == "Kontinuum"
    assert first["structured"]["version"] == "24.1"
    assert first["structured"]["status"] == "umgesetzt"
    assert first["structured"]["tests"] == "bestanden"
    assert "Webrecherche" in first["structured"]["offen"]

    replacement = core.remember("Version 24.1 ist abgeschlossen", owner="Raphael")
    assert replacement["action"] == "replace"
    assert replacement["replaces"] == first["id"]
    assert core.contradictions()
    assert core.recall("24.1")[0]["metadata"]["value"] == "abgeschlossen"

    uncertain = core.remember("Vielleicht ist die neue Architektur dauerhaft stabil", owner="Raphael")
    assert uncertain["status"] == "uncertain"
    transient = core.observe("Heute regnet es", owner="Raphael")
    assert transient["action"] == "discard"

    source = core.remember("Notebook-Quelle Handbuch: https://example.org/handbuch", owner="Kontinuum")
    assert source["layer"] == "sources"
    assert core.link(replacement["id"], source["id"])
    updated = core.update(replacement["id"], "Version 24.1 ist veröffentlicht", owner="Raphael")
    assert updated["id"] and updated["value"] == "veröffentlicht"
    assert core.status()["layers"]["relationships"] >= 1
    assert core.forget(str(source["id"])) == 1

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "language_model.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        system.set_user_context({"username": "Raphael", "full_name": "Raphael Schatz", "role": "SUPERADMIN"})
        stored = system.ask("merke dir Ich bevorzuge lokale, prüfbare Systeme")
        assert "Erinnerung store" in stored and "preferences" not in stored
        assert "lokale, prüfbare Systeme" in system.ask("was weißt du über lokale")
        system.ask("Version 25 ist geplant")
        assert "version:25" in system.ask("zeige projekterinnerungen")
        system.ask("merke dir offener Bug: PDF-Import prüfen")
        assert "PDF-Import" in system.ask("zeige offene punkte")
        row = system.memory_core.recall("PDF-Import")[0]
        assert "Erinnerung" in system.ask(f"aktualisiere erinnerung {row['id']}: offener Bug: PDF-Import und OCR prüfen")
        assert "OCR" in system.ask("was weißt du über OCR")
        assert "Memory-Core 1.0" in system.ask("gedächtnisstatus")
        memory_status = system.status()["memory_core"]
        assert memory_status["total"] >= 3
        assert memory_status["layers"]["short_term"] > 0
        assert memory_status["layers"]["episodic"] >= memory_status["layers"]["short_term"]
    finally:
        system.close()

print("Kontinuum Memory-Core 1.0 tests passed")
