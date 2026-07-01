from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.release_integrity import ReleaseIntegrityFramework


def main() -> int:
    parser = argparse.ArgumentParser(description="Kontinuum 34.1 Release Integrity Gate")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Erzeugt Vorabnachweise, verweigert aber ausdrücklich die Release-Freigabe.",
    )
    parser.add_argument("--json", action="store_true", help="Gibt den vollständigen Gate-Bericht aus.")
    arguments = parser.parse_args()
    framework = ReleaseIntegrityFramework(ROOT, "34.1")
    report = framework.run(include_tests=not arguments.skip_tests)
    if arguments.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Kontinuum 34.1 Release Integrity Framework 1.0")
        labels = {
            "baseline": "Baseline",
            "backup": "Backup",
            "audit_snapshot": "Audit-Snapshot",
            "rollback_test": "Rollback-Test",
            "legacy_scan": "Altversionssuche",
            "test_suite": "Testsuite",
            "version_consistency": "Versionskonsistenz",
            "chronicle_migration": "Chronikmigration",
            "entrypoints": "GUI-/Starter-/Wiedereinstiegspunkte",
            "foundation_core": "Foundation-Core-Pflichtprüfung",
            "canonical_architecture": "Canonical Architecture Manager",
            "canonical_database": "Canonical Database Manager 1.2",
            "canonical_api_registry": "Canonical API Registry 1.3",
            "canonical_artifacts": "Canonical Artifact Manager 1.4",
            "artifact_lifecycle": "CAM 1.1 Artifact Lifecycle Policy",
        }
        for name, passed in report["gates"].items():
            print(f"{labels.get(name, name)}: {'bestanden' if passed else 'NICHT BESTANDEN'}")
        print(f"Status: {report['status']}")
        print(f"Freigabe: {report['freigabe']}")
        print(f"Nachweis: {framework.report_root / 'release_gate.json'}")
    return 0 if report.get("release_approved") else 1


if __name__ == "__main__":
    raise SystemExit(main())
