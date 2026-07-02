from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.continuous_governance import ContinuousGovernanceSystem

manager = ContinuousGovernanceSystem(ROOT, release_version="34.1")
status = manager.status()
assert status["ok"], status
assert status["version"] == "1.0"
assert status["checks"]["stability"]
assert status["checks"]["enforcement"]
assert status["checks"]["verification_loop"]
assert status["checks"]["cgm"]
assert status["checks"]["dde"]
assert status["checks"]["cic"]
assert status["checks"]["gel"]
assert status["checks"]["baseline_reference"]
assert status["checks"]["reports_generable"]
assert status["components"]["CGM"]["active"]
assert status["components"]["DDE"]["active"]
assert status["components"]["CIC"]["active"]
assert status["components"]["GEL"]["active"]
assert status["baseline"]["status"] == "IMMUTABLE_READ_ONLY_REFERENCE"
assert 0 <= status["baseline_compliance_score"] <= 100
assert status["drift_classification"] in {"NONE", "LOW", "MEDIUM", "HIGH"}
assert "governance_status" in status["reports"]
assert (ROOT / status["reports"]["governance_status"]).is_file()
assert (ROOT / status["reports"]["drift"]).is_file()
assert (ROOT / status["reports"]["integrity"]).is_file()
assert (ROOT / status["reports"]["compliance"]).is_file()
assert status["mutation_policy"] == "read_only_classification; no_delete_no_auto_move; verified_change_only"
assert "Continuous Governance System 1.0: VERIFIZIERT" in manager.format_status()

active = manager.classify_artifact("14_documents/PROJEKTSTRUKTUR_34_1.md", context="test")
assert active.classification == "active"
review = manager.classify_artifact("30_import/new_source.txt", context="test")
assert review.classification == "review"
archive = manager.classify_artifact("14_documents/archive/legacy/Version 32.0.txt", context="test")
assert archive.classification == "active"
candidate = manager.classify_artifact("14_documents/README_GUI_33_0.md", context="test")
assert candidate.classification == "archive_candidate"

entry = manager.classify_and_log("24_config/continuous_governance_34_1.json", context="test")
assert entry["classification"] == "active"
log_path = ROOT / "31_reports/governance/phase3_continuous_governance_log.jsonl"
last = json.loads(log_path.read_text(encoding="utf-8-sig").splitlines()[-1])
assert last["path"] == "24_config/continuous_governance_34_1.json"
assert last["verification_status"] in {"VERIFIZIERT", "NICHT VERIFIZIERT"}

analysis = manager.monitor.run_full_analysis(write_reports=True)
assert analysis["component"] == "CGM"
assert analysis["baseline"]["ok"]
assert analysis["drift"]["component"] == "DDE"
assert analysis["integrity"]["component"] == "CIC"
assert analysis["baseline_compliance_score"] == status["baseline_compliance_score"]

print("Kontinuum 34.1 Continuous Governance tests passed")


