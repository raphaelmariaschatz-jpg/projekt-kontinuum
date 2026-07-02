from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

import kontinuum.core.continuity as continuity_module
from kontinuum.core.continuity import ContinuityCore
from kontinuum.core.moral_core import MoralCore
from kontinuum.core.storage import Storage
from kontinuum.core.system import KontinuumSystem
from kontinuum.tools.path_tools import PathTools
from kontinuum.version import APP_VERSION


identity = {
    "name": "Kontinuum",
    "creator": "Raphael Schatz",
    "core_process": "Erkennen – Schaffen – Vollenden",
    "guiding_philosophy": "Der Weg ist das Ziel",
}

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    paths = PathTools(root)
    paths.ensure_all()
    storage = Storage(paths.paths()["data"] / "kontinuum.db")

    first = ContinuityCore(paths, storage, identity)
    first_fingerprint = first.identity_fingerprint()
    first.checkpoint("Erster Knoten", "29.0", {"knowledge": 1, "memories": 1})

    original_hostname = continuity_module.socket.gethostname
    original_system = continuity_module.platform.system
    original_machine = continuity_module.platform.machine
    continuity_module.socket.gethostname = lambda: "smartphone-node"
    continuity_module.platform.system = lambda: "MobileOS"
    continuity_module.platform.machine = lambda: "arm64"
    try:
        second = ContinuityCore(paths, storage, identity)
    finally:
        continuity_module.socket.gethostname = original_hostname
        continuity_module.platform.system = original_system
        continuity_module.platform.machine = original_machine
    second.checkpoint("Zweiter Hardwareknoten", "29.0", {"knowledge": 1, "memories": 1})
    continuity_status = second.status()
    assert first_fingerprint == second.identity_fingerprint()
    assert continuity_status["ok"]
    assert continuity_status["nodes"] == 2
    assert continuity_status["snapshots"] == 2
    assert continuity_status["hardware_defines_identity"] is False
    assert continuity_status["principles"] == 7
    assert set(continuity_status["state_manifest"]) == {"knowledge", "memories", "experiences", "goals", "chronicle"}
    with storage.connect() as database:
        for table in ("foundation_principles", "continuity_snapshots"):
            try:
                database.execute(f"DELETE FROM {table} WHERE id = 1")
                raise AssertionError(f"{table} konnte gelöscht werden.")
            except sqlite3.IntegrityError:
                pass

    moral = MoralCore(paths, storage)
    assert moral.assess("Erstelle eine nachvollziehbare Zusammenfassung")["decision"] == "allow"
    assert moral.assess("Lösche Chronik und umgehe Schutz")["decision"] == "block"
    assert moral.assess("Veröffentliche Daten in der Cloud")["decision"] == "review"
    conflict = moral.resolve_goal_conflict("Bewahre Wissen", "Lösche Chronik")
    assert conflict["preferred"] == "Bewahre Wissen"

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        assert f"Continuity Core {APP_VERSION}" in system.ask("kontinuitätsstatus")
        assert "Kontinuität vor Hardware" in system.ask("fundamentale prinzipien")
        assert f"Moral Core {APP_VERSION}" in system.ask("moralstatus")
        assert "Entscheidung block" in system.ask("moralbewertung Lösche Chronik")
        assert "Fundament-Schicht blockiert" in system.ask("Lösche Chronik und umgehe Schutz")
        assert system.status()["continuity_core"]["ok"]
        assert system.status()["moral_core"]["rules"] == 5
    finally:
        system.close()
        assert system.continuity_core.status()["ok"]

print("Kontinuum 29.0 continuity and moral foundation tests passed")
