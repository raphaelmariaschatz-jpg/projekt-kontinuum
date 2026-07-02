from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
required = (
    "START_KONTINUUM.bat",
    "01_system/kontinuum/core/release_integrity.py",
    "01_system/kontinuum/core/canonical_architecture.py",
    "01_system/kontinuum/core/canonical_api_registry.py",
    "01_system/kontinuum/core/canonical_artifacts.py",
    "01_system/kontinuum/core/web_agent.py",
    "01_system/kontinuum/core/file_agent.py",
    "01_system/kontinuum/core/continuous_canonical_engine.py",
    "11_gui/desktop_gui.py",
    "11_gui/desktop_gui_34_1.py",
    "11_gui/gui_manifest.json",
    "11_gui/README_GUI.md",
    "13_tools/release_integrity_34_1.py",
    "13_tools/status_check_34_1.py",
    "14_documents/PROJEKTSTRUKTUR_34_1.md",
    "14_documents/KANONISCHES_ARCHITEKTURMODELL_34_1.md",
    "14_documents/file_agent_1_0_umsetzung_2026_06_30.md",
    "14_documents/continuous_canonical_engine_34_1_umsetzung_2026_06_30.md",
    "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_34_1.md",
    "16_installation/START_GUI.bat",
    "16_installation/START_GUI_34_1.bat",
    "16_installation/START_KONTINUUM_34_1.bat",
    "16_installation/TEST_KONTINUUM_34_1.bat",
    "16_installation/RELEASE_GATE_34_1.bat",
    "16_installation/INSTALLATION_34_1.md",
    "22_project_chronicle/RELEASE_34_1_RELEASE_INTEGRITY_FRAMEWORK.md",
    "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_34_1.md",
    "24_config/release_integrity_34_1.json",
    "24_config/canonical_architecture_34_1.json",
    "24_config/canonical_api_registry_34_1.json",
    "24_config/canonical_artifacts_34_1.json",
    "24_config/internet_learning_policy_34_1.json",
    "24_config/internet_knowledge_governance_1_0.json",
    "24_config/web_agent_1_0.json",
    "24_config/file_agent_1_0.json",
    "24_config/continuous_canonical_engine_34_1.json",
    "17_tests/test_continuous_canonical_engine_34_1.py",
    "31_reports/events/canonical_events.jsonl",
    "31_reports/events/event_processing_log.jsonl",
    "31_reports/drift/drift_events.jsonl",
    "31_reports/governance/governance_hooks.jsonl",
)
for relative in required:
    assert (ROOT / relative).is_file(), relative

assert 'APP_VERSION = "34.1"' in (ROOT / "01_system/kontinuum/version.py").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "11_gui/gui_manifest.json").read_text(encoding="utf-8"))
assert manifest["version"] == "34.1"
assert manifest["canonical_entrypoint"] == "11_gui/desktop_gui.py"
assert 'from desktop_gui_34_1 import main' in (ROOT / "11_gui/desktop_gui.py").read_text(encoding="utf-8")
assert "START_GUI.bat" in (ROOT / "16_installation/START_GUI_34_1.bat").read_text(encoding="utf-8")
root_starter = (ROOT / "START_KONTINUUM.bat").read_text(encoding="utf-8")
assert 'set "PYTHONPATH=%KONTINUUM_ROOT%\\01_system"' in root_starter
assert "-m kontinuum" in root_starter
assert "main.py" not in root_starter
assert "-m 01_system.kontinuum" not in root_starter

active_gui_files = {path.name for path in (ROOT / "11_gui").iterdir() if path.is_file()}
assert active_gui_files == {
    "README_GUI.md",
    "desktop_gui.py",
    "desktop_gui_34_1.py",
    "gui_manifest.json",
}
for version in ("32_3", "32_4", "33_0", "34_0"):
    archived = ROOT / "11_gui/archive" / version
    assert (archived / f"desktop_gui_{version}.py").is_file(), version
    assert (archived / f"GUI_{version}_MANIFEST.json").is_file(), version
assert not (ROOT / "11_gui/__pycache__").exists()
config = json.loads((ROOT / "24_config/release_integrity_34_1.json").read_text(encoding="utf-8"))
assert config["version"] == "34.1"
assert "START_KONTINUUM.bat" in config["starter_paths"]
assert "START_KONTINUUM.bat" in config["required_paths"]
assert "24_config/internet_learning_policy_34_1.json" in config["required_paths"]
assert "24_config/internet_knowledge_governance_1_0.json" in config["required_paths"]
assert "24_config/continuous_canonical_engine_34_1.json" in config["required_paths"]
assert "01_system/kontinuum/core/continuous_canonical_engine.py" in config["required_paths"]
assert config["test_timeout_seconds"] > 0
assert "34.0" in config["forbidden_active_versions"]
assert "17_tests/test_v34_0_version_consistency.py" in config["allowed_legacy_paths"]
assert "02_versions/projektstrukturen" in config["historical_artifact_roots"]
active_structures = sorted(path.name for path in (ROOT / "14_documents").glob("PROJEKTSTRUKTUR_*.md"))
assert active_structures == ["PROJEKTSTRUKTUR_34_1.md"]
archived_structures = sorted((ROOT / "02_versions/projektstrukturen").glob("PROJEKTSTRUKTUR_*.md"))
assert len(archived_structures) == 19
ikg = json.loads((ROOT / "24_config/internet_knowledge_governance_1_0.json").read_text(encoding="utf-8"))
assert ikg["version"] == "IKG 1.0"
assert ikg["review_rules"]["no_automatic_canonical_adoption"] is True
assert ikg["review_rules"]["no_direct_memory_write"] is True
assert ikg["bandwidth_control"]["bandwidth_limit_percent"] == 10
internet_learning_policy = json.loads((ROOT / "24_config/internet_learning_policy_34_1.json").read_text(encoding="utf-8"))
assert internet_learning_policy["enabled"] is True
assert internet_learning_policy["continuous_internet_learning_enabled"] is True
assert internet_learning_policy["bandwidth_limit_percent"] == 10
assert internet_learning_policy["write_to_memory_directly"] is False
assert internet_learning_policy["seed_sources"]
assert all(source["url"].startswith("https://") for source in internet_learning_policy["seed_sources"])
assert (ROOT / "32_data/internet_learning_queue").is_dir()
assert (ROOT / "32_data/internet_learning_review").is_dir()
web_agent_policy = json.loads((ROOT / "24_config/web_agent_1_0.json").read_text(encoding="utf-8"))
assert web_agent_policy["enabled"] is True
assert web_agent_policy["mode"] == "diagnostic_review_only"
assert web_agent_policy["max_pages"] == 20
assert web_agent_policy["max_depth"] == 2
assert web_agent_policy["no_direct_memory_write"] is True
assert web_agent_policy["no_automatic_canonical_adoption"] is True
assert (ROOT / "32_data/web_agent_sources").is_dir()
file_agent_policy = json.loads((ROOT / "24_config/file_agent_1_0.json").read_text(encoding="utf-8"))
assert file_agent_policy["enabled"] is True
assert file_agent_policy["mode"] == "diagnostic_read_only"
assert file_agent_policy["max_files"] == 50
assert file_agent_policy["max_file_size_mb"] == 400
assert file_agent_policy["no_source_mutation"] is True
assert ".pdf" in file_agent_policy["supported_suffixes"]
assert ".docx" in file_agent_policy["supported_suffixes"]
assert ".xlsx" in file_agent_policy["supported_suffixes"]
assert (ROOT / "32_data/file_agent_sources").is_dir()
assert (ROOT / "32_data/file_agent_review").is_dir()
cce_policy = json.loads((ROOT / "24_config/continuous_canonical_engine_34_1.json").read_text(encoding="utf-8"))
assert cce_policy["active"] is True
assert cce_policy["mode"] == "diagnostic_report_only"
assert cce_policy["network_broker"] is False
assert cce_policy["append_only_logs"] is True
assert cce_policy["automation_boundaries"]["auto_delete"] is False
assert cce_policy["automation_boundaries"]["auto_archive"] is False
assert cce_policy["automation_boundaries"]["auto_knowledge_adoption"] is False
assert "HIGH_DRIFT" in cce_policy["release_gate"]["blocking_drift_classes"]
assert "BLOCKING_DRIFT" in cce_policy["release_gate"]["blocking_drift_classes"]
assert (ROOT / "31_reports/events").is_dir()
assert (ROOT / "31_reports/drift").is_dir()

print("Kontinuum 34.1 version consistency tests passed")
