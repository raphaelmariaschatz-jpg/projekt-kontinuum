# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "32.4"


def main() -> int:
    issues: list[str] = []
    version_file = ROOT / "01_system" / "kontinuum" / "version.py"
    if f'APP_VERSION = "{EXPECTED_VERSION}"' not in version_file.read_text(encoding="utf-8"):
        issues.append("Zentrale APP_VERSION ist nicht 32.4.")

    manifest_path = ROOT / "11_gui" / "GUI_32_4_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != EXPECTED_VERSION:
        issues.append("GUI-Manifest ist nicht 32.4.")

    required = (
        "11_gui/desktop_gui_32_4.py",
        "16_installation/START_GUI_32_4.bat",
        "16_installation/START_KONTINUUM_32_4.bat",
        "16_installation/TEST_KONTINUUM_32_4.bat",
        "14_documents/PROJEKTSTRUKTUR_32_4.md",
        "14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_32_4.md",
        "22_project_chronicle/EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_32_4.md",
    )
    for relative in required:
        if not (ROOT / relative).is_file():
            issues.append(f"Pflichtpfad fehlt: {relative}")

    database_path = ROOT / "32_data" / "kontinuum.db"
    open_cycles = "nicht geprüft"
    if database_path.is_file():
        connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
        try:
            open_cycles = connection.execute(
                """SELECT COUNT(*) FROM foundation_decisions AS decision
                   WHERE decision.kind = 'foundation.decision'
                     AND NOT EXISTS (
                       SELECT 1 FROM foundation_decisions AS phase
                       WHERE phase.kind = 'foundation.phase.complete'
                         AND phase.content = CAST(decision.id AS TEXT)
                     )"""
            ).fetchone()[0]
        finally:
            connection.close()
        if open_cycles != 0:
            issues.append(f"Offene Foundation-Zyklen: {open_cycles}")

    print(f"Kontinuum {EXPECTED_VERSION} Statusprüfung")
    print(f"Projektwurzel: {ROOT}")
    print(f"Offene Foundation-Zyklen: {open_cycles}")
    if issues:
        for issue in issues:
            print(f"FEHLER: {issue}")
        return 1
    print("Status: verifiziert")
    return 0


if __name__ == "__main__":
    sys.exit(main())
