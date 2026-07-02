from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem
from kontinuum.tools.maintenance_tools import MaintenanceTools


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    (root / "24_config").mkdir()
    (root / "27_logs").mkdir()
    protected = root / "09_backups" / "__pycache__"
    protected.mkdir(parents=True)
    (protected / "keep.pyc").write_bytes(b"protected")
    cache = root / "01_system" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "remove.pyc").write_bytes(b"cache")
    obsolete = root / "17_tests" / "Projekt_Kontinuum_Test"
    obsolete.mkdir(parents=True)
    (obsolete / "old.txt").write_text("old", encoding="utf-8")
    structure = root / "14_documents" / "dateiliste.txt"
    structure.parent.mkdir(parents=True)
    structure.write_text("old structure", encoding="utf-8")
    config = {
        "structure_report_archive_after_days": 0,
        "functional_backup_review_after_days": 0,
    }
    (root / "24_config" / "retention_policy.json").write_text(json.dumps(config), encoding="utf-8")
    tool = MaintenanceTools(root)
    status = tool.status()
    assert status["valuable_artifacts"]["before_release"] == "retain"
    assert status["valuable_artifacts"]["after_release"] == "archive"
    assert status["valuable_artifacts"]["deletion"] == "manual_only_after_explicit_review"
    assert len(status["valuable_artifacts"]["release_requirements"]) == 5
    inspection = tool.inspect()
    assert inspection["mode"] == "inspection"
    assert cache.exists() and obsolete.exists() and structure.exists()
    assert all("09_backups" not in row["relative_path"] for row in inspection["candidates"])
    assert {row["category"] for row in inspection["candidates"]} == {"cache", "obsolete_test_copy", "structure_report"}
    executed = tool.execute()
    assert executed["ok"]
    assert not cache.exists()
    assert not obsolete.exists()
    assert not structure.exists()
    assert (root / "31_reports" / "archive" / "dateiliste.txt").is_file()
    assert protected.is_dir()
    assert (root / "27_logs" / "maintenance_cleanup_audit.log").is_file()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "retention_policy.json").write_text(json.dumps({"obsolete_test_copies_keep": 1}), encoding="utf-8")
    tests = root / "17_tests"
    for name in ("Projekt_Kontinuum_Test", "Projekt_Kontinuum_Backup_Vor_Patch"):
        copy = tests / name
        copy.mkdir(parents=True)
        (copy / "old.txt").write_text(name, encoding="utf-8")
    tool = MaintenanceTools(root)
    inspection = tool.inspect()
    obsolete_candidates = [row for row in inspection["candidates"] if row["category"] == "obsolete_test_copy"]
    assert len(obsolete_candidates) == 1
    executed = tool.execute()
    assert executed["ok"]
    assert sum(path.is_dir() for path in tests.iterdir()) == 1

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "language_model.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        answer = system.ask("wartungsmodus bereinigung prüfen")
        assert "Es wurde nichts gelöscht" in answer
        assert "Sicherer Wartungsmodus aktiv" in system.ask("wartungsmodus status")
        assert "Bereinigung ausgeführt" in system.ask("wartungsmodus bereinigung ausführen")
    finally:
        system.close()

print("Kontinuum maintenance retention tests passed")
