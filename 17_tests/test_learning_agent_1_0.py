from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


ROOT = Path("C:/Projekt Kontinuum")
MODULE_PATH = ROOT / "12_agents" / "learning_agent_1_0.py"

spec = importlib.util.spec_from_file_location("learning_agent_1_0", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

LearningAgent10 = module.LearningAgent10
LearningSource = module.LearningSource


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary)
    agent = LearningAgent10(project_root=root)

    status = agent.status()
    assert status["active"] is True
    assert status["mode"] == "read_only_proposal_mode"
    assert status["governance"]["no_automatic_knowledge_adoption"] is True
    assert status["governance"]["internet_autonomy"] is False

    verified = agent.classify_source(
        agent.recognize_source(
            "Source: https://example.edu/research. Wasser besteht aus H2O und ist unter Normalbedingungen fluessig.",
            origin="https://example.edu/research",
        )
    )
    assert verified.category == "verified_knowledge"
    assert verified.source_quality == "high"
    assert verified.automatic_adoption_allowed is False
    assert verified.writes_performed is False
    assert verified.proposals["knowledge"]

    duplicate = agent.classify_source(
        "Source: https://example.edu/research. Wasser besteht aus H2O und ist unter Normalbedingungen fluessig.",
        known_sources=[LearningSource("water_known", "Source: https://example.edu/research. Wasser besteht aus H2O und ist unter Normalbedingungen fluessig.")],
    )
    assert duplicate.category == "duplicate_candidate"
    assert duplicate.duplicate_of == "water_known"

    uncertain = agent.classify_source("Vermutlich ist diese Aussage korrekt, aber ohne Quelle und mit unklarer Herkunft.")
    assert uncertain.category == "uncertain_knowledge"
    assert uncertain.risk_level in {"medium", "high"}
    assert uncertain.risks

    missing_source = agent.classify_source("Dieser Inhalt beschreibt ein Wissensfragment ohne belegbare Herkunft und Kontext.")
    assert missing_source.category == "source_required"

    conflict = agent.classify_source("Quelle: https://example.org/a. Diese Aussage widerspricht einer bestehenden kanonischen Aussage.")
    assert conflict.category == "conflict_detected"
    assert conflict.risk_level == "high"

    blocked = agent.check_write_operation(root / "32_data" / "kontinuum.db", "write")
    assert blocked["allowed"] is False
    allowed_report = agent.check_write_operation(root / "31_reports" / "learning_agent" / "report.md", "write_report")
    assert allowed_report["allowed"] is True

    report_path = agent.generate_status_report()
    assert report_path.is_file()
    report = report_path.read_text(encoding="utf-8")
    assert "Learning Agent 1.0 Status Report" in report
    assert "Automatische Wissensuebernahme: nein" in report
    assert "32_data" in report

print("Kontinuum Learning Agent 1.0 tests passed")


