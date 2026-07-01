from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.release_integrity import ReleaseIntegrityFramework
from kontinuum.core.continuous_governance import ContinuousGovernanceSystem


EXPECTED_VERSION = "34.1"


def main() -> int:
    issues = []
    if f'APP_VERSION = "{EXPECTED_VERSION}"' not in (ROOT / "01_system/kontinuum/version.py").read_text(encoding="utf-8"):
        issues.append("Zentrale APP_VERSION ist nicht 34.1.")
    try:
        framework = ReleaseIntegrityFramework(ROOT, EXPECTED_VERSION)
        required = framework.required_paths_check()
        issues.extend(f"Pflichtpfad fehlt: {path}" for path in required["missing"])
        paths = framework.path_consistency()
        if not paths.get("canonical_start", {}).get("ok", False):
            issues.append("Kanonischer Root-Startpfad START_KONTINUUM.bat ist nicht korrekt.")
        foundation_core = framework.foundation_core_check()
        if not foundation_core["ok"]:
            issues.append("Foundation-2.2-Pflichtprüfung FND-ID-048 ist nicht erfüllt.")
        canonical_architecture = framework.canonical_architecture_check()
        if not canonical_architecture["ok"]:
            issues.append("Canonical-Architecture-Pflichtprüfung ist nicht erfüllt.")
        if not canonical_architecture.get("artifact_lifecycle", {}).get("ok", False):
            issues.append("CAM-1.1-Artifact-Lifecycle-Pflichtprüfung ist nicht erfüllt.")
        canonical_database = framework.canonical_database_check()
        if not canonical_database.get("ok", False):
            issues.append("CAM-1.2-Canonical-Database-Pflichtprüfung ist nicht erfüllt.")
        canonical_api_registry = framework.canonical_api_registry_check()
        if not canonical_api_registry.get("ok", False):
            issues.append("CAM-1.3-Canonical-API-Registry-Pflichtprüfung ist nicht erfüllt.")
        canonical_artifacts = framework.canonical_artifacts_check()
        if not canonical_artifacts.get("ok", False):
            issues.append("CAM-1.4-Canonical-Artifact-Pflichtprüfung ist nicht erfüllt.")
        continuous_governance = ContinuousGovernanceSystem(ROOT, EXPECTED_VERSION).status()
        if not continuous_governance.get("ok", False):
            issues.append("Phase-3 Continuous Canonical Governance ist nicht vollständig aktiv.")
        for component in ("CGM", "DDE", "CIC", "GEL"):
            if not continuous_governance.get("components", {}).get(component, {}).get("active", False):
                issues.append(f"Phase-3-Komponente {component} ist nicht aktiv.")
        if not continuous_governance.get("checks", {}).get("baseline_reference", False):
            issues.append("Canonical Governance Baseline 34.1 ist nicht als immutable Referenz fix integriert.")
        if not continuous_governance.get("reports"):
            issues.append("Governance-Reports sind nicht generierbar.")
        integrity_status = framework.status()
        if not integrity_status["release_approved"]:
            issues.append("Release Integrity Gate ist nicht vollständig verifiziert.")
    except RuntimeError as exc:
        integrity_status = {"release_approved": False, "freigabe": "NEIN"}
        issues.append(str(exc))
    manifest_path = ROOT / "11_gui/gui_manifest.json"
    if manifest_path.is_file() and json.loads(manifest_path.read_text(encoding="utf-8")).get("version") != EXPECTED_VERSION:
        issues.append("GUI-Manifest ist nicht 34.1.")
    database = ROOT / "32_data/kontinuum.db"
    if database.is_file():
        with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                issues.append("SQLite-Integritätsprüfung fehlgeschlagen.")
    print(f"Kontinuum {EXPECTED_VERSION} Statusprüfung")
    for issue in issues:
        print(f"FEHLER: {issue}")
    if issues:
        print("Status: NICHT VERIFIZIERT")
        print("Freigabe: NEIN")
    else:
        print("Status: VERIFIZIERT")
        print("Freigabe: JA")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
