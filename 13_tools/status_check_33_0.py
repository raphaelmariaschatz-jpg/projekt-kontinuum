from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "33.0"


def main() -> int:
    issues = []
    if f'APP_VERSION = "{EXPECTED_VERSION}"' not in (ROOT / "01_system/kontinuum/version.py").read_text(encoding="utf-8"):
        issues.append("Zentrale APP_VERSION ist nicht 33.0.")
    required = (
        "01_system/kontinuum/core/autonomous_diagnostics.py",
        "01_system/kontinuum/core/foundation_integrity.py",
        "01_system/kontinuum/core/foundation_memory.py",
        "01_system/kontinuum/core/foundation_query.py",
        "01_system/kontinuum/core/foundation_reasoning.py",
        "01_system/kontinuum/core/error_classification.py",
        "01_system/kontinuum/core/solution_proposal.py",
        "01_system/kontinuum/agents/internal_diagnostic_agent.py",
        "11_gui/desktop_gui_33_0.py",
        "11_gui/GUI_33_0_MANIFEST.json",
        "16_installation/START_GUI_33_0.bat",
        "16_installation/START_KONTINUUM_33_0.bat",
        "16_installation/TEST_KONTINUUM_33_0.bat",
        "14_documents/PROJEKTSTRUKTUR_33_0.md",
        "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_33_0.md",
        "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_33_0.md",
        "17_tests/test_foundation_knowledge_protection_2.py",
        "17_tests/test_foundation_memory_layer_3.py",
        "17_tests/test_foundation_query_layer.py",
        "17_tests/test_foundation_reasoning_layer_4.py",
        "17_tests/test_guiding_principles_12.py",
        "14_documents/LEITPRINZIPIEN_2026_06_21.md",
    )
    issues.extend(f"Pflichtpfad fehlt: {item}" for item in required if not (ROOT / item).is_file())
    manifest = json.loads((ROOT / "11_gui/GUI_33_0_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("version") != EXPECTED_VERSION:
        issues.append("GUI-Manifest ist nicht 33.0.")
    database = ROOT / "32_data/kontinuum.db"
    if database.is_file():
        with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                issues.append("SQLite-Integritaetspruefung fehlgeschlagen.")
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'foundation_knowledge'"
            ).fetchone()
            if not table:
                issues.append("Foundation-Knowledge-Schutzklasse fehlt.")
            else:
                triggers = connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type = 'trigger' AND name IN (?, ?)",
                    ("protect_foundation_knowledge_update", "protect_foundation_knowledge_delete"),
                ).fetchone()[0]
                if triggers != 2:
                    issues.append("Foundation-Knowledge-Append-only-Schutz ist unvollstaendig.")
            memory_table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'foundation_memory'"
            ).fetchone()
            if not memory_table:
                issues.append("Foundation Memory Layer 3.0 fehlt.")
            else:
                memory_triggers = connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type = 'trigger' AND name IN (?, ?)",
                    ("protect_foundation_memory_update", "protect_foundation_memory_delete"),
                ).fetchone()[0]
                if memory_triggers != 2:
                    issues.append("Foundation-Memory-Append-only-Schutz ist unvollstaendig.")
                guiding_rows = connection.execute(
                    """SELECT COUNT(*), COUNT(DISTINCT json_extract(metadata, '$.rule_id'))
                       FROM foundation_memory
                       WHERE kind = 'foundation.memory'
                         AND json_extract(metadata, '$.guiding_principle') = 1
                         AND json_extract(metadata, '$.policy_status') = 'active_provisional'"""
                ).fetchone()
                if tuple(guiding_rows) != (12, 12):
                    issues.append("Die 12 vorlaeufigen Leitprinzipien sind nicht vollstaendig und eindeutig aktiv.")
                guiding_registry = connection.execute(
                    """SELECT 1 FROM foundation_knowledge
                       WHERE kind = 'foundation.knowledge' AND content = 'guiding.principles' LIMIT 1"""
                ).fetchone()
                if not guiding_registry:
                    issues.append("Geschuetzter Registereintrag guiding.principles fehlt.")
            reasoning_table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'foundation_reasoning'"
            ).fetchone()
            if not reasoning_table:
                issues.append("Foundation Reasoning Layer 4.0 fehlt.")
            else:
                reasoning_triggers = connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type = 'trigger' AND name IN (?, ?)",
                    ("protect_foundation_reasoning_update", "protect_foundation_reasoning_delete"),
                ).fetchone()[0]
                if reasoning_triggers != 2:
                    issues.append("Foundation-Reasoning-Append-only-Schutz ist unvollstaendig.")
    print(f"Kontinuum {EXPECTED_VERSION} Statuspruefung")
    for issue in issues:
        print(f"FEHLER: {issue}")
    print("Status: verifiziert" if not issues else "Status: fehlerhaft")
    return int(bool(issues))


if __name__ == "__main__":
    sys.exit(main())
