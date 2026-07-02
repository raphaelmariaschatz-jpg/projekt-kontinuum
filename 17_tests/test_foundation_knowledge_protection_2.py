from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "epistemic_action.json").write_text(json.dumps({"automatic": False}), encoding="utf-8")

    system = KontinuumSystem(root)
    try:
        status = system.foundation_integrity.status()
        assert status["ok"]
        assert status["version"] == "2.0"
        assert status["knowledge_class"] == "foundation_knowledge"
        assert status["verified_records"] == status["protected_records"] == 6
        assert "Foundation Knowledge Protection 2.0: intakt" in system.ask("fundamentintegritätsstatus")

        with system.storage.connect() as database:
            rows = database.execute(
                "SELECT id, metadata FROM foundation_knowledge WHERE kind = 'foundation.knowledge'"
            ).fetchall()
            assert len(rows) == 6
            for row in rows:
                metadata = json.loads(row["metadata"])
                assert metadata["protected"] is True
                assert metadata["immutable"] is True
                assert metadata["source"] == "Raphael Schatz"
                assert metadata["protection_version"] == "2.0"
                assert len(metadata["integrity_hash"]) == 64
            try:
                database.execute("DELETE FROM foundation_knowledge WHERE id = ?", (rows[0]["id"],))
                raise AssertionError("Geschütztes Fundamentwissen konnte gelöscht werden.")
            except sqlite3.IntegrityError:
                pass
            try:
                database.execute("UPDATE foundation_knowledge SET content = 'manipuliert' WHERE id = ?", (rows[0]["id"],))
                raise AssertionError("Geschütztes Fundamentwissen konnte verändert werden.")
            except sqlite3.IntegrityError:
                pass

        protected = "Raphael Schatz ist der Schöpfer von Kontinuum."
        for origin in ("learning", "research", "notebook", "diagnostic", "self_extension"):
            result = system.knowledge_platform.integrate(protected, origin=origin)
            assert result["ok"] is False
            assert result["classification"] == "foundation_knowledge"
        moral_rule = "Subjektives Bewusstsein oder Qualia nicht ohne Nachweis behaupten."
        assert system.knowledge_platform.integrate(moral_rule, origin="research")["classification"] == "foundation_knowledge"
        normal = system.knowledge_platform.integrate("Wasser gefriert bei normalem Luftdruck bei 0 °C.", origin="notebook")
        assert normal["knowledge_id"] > 0

        try:
            system.continuous_learning.add_task("Ist Raphael Schatz der Schöpfer von Kontinuum?")
            raise AssertionError("Fundamentwissen konnte als Lernauftrag angelegt werden.")
        except ValueError:
            pass

        blocked = system.foundation_integrity.authorize_change("identity.creator", "Andere Person", {
            "actor": "Andere Person", "role": "SUPERADMIN", "explicit": True,
            "authenticated": True, "reason": "Test", "approval_reference": "TEST-1",
        })
        assert blocked["ok"] is False
        authorized = system.foundation_integrity.authorize_change("identity.creator", "Raphael Schatz", {
            "actor": "Raphael Schatz", "role": "SUPERADMIN", "explicit": True,
            "authenticated": True, "reason": "Auditierter Regressionstest", "approval_reference": "TEST-2",
        })
        assert authorized["ok"] is True
        assert authorized["decision"] == "authorized_pending_migration"

        audit = system.ask("fundamentaudit")
        assert "Foundation Audit 3.0" in audit
        assert "Schutzstatus: INTAKT" in audit
        assert "Prüfsummenstatus: intakt (6/6 gültig)" in audit
        assert "Letzte Prüfung:" in audit
        assert "Letzte autorisierte Änderung:" in audit
        assert "identity.creator" in audit
        assert "Kontaminationsversuche: 6" in audit
        assert "Blockierte Zugriffe: 8" in audit

        task_id = system.storage.ensure_learning_task(protected, [], "malicious_test")
        assert all(protected not in gap["subject"] for gap in system.knowledge_intelligence.knowledge_gaps())
        integrity = system.foundation_integrity.verify()
        assert integrity["ok"] is False
        assert any(row["id"] == task_id for row in integrity["contamination"])
        findings = system.autonomous_diagnostics._check_foundation()
        assert any(row.code == "foundation.integrity" for row in findings)

        with system.storage.connect() as database:
            assert database.execute(
                "SELECT COUNT(*) FROM audit_events WHERE kind = 'foundation.integration.blocked'"
            ).fetchone()[0] >= 5
            assert database.execute(
                "SELECT COUNT(*) FROM audit_events WHERE kind = 'foundation.change.authorized'"
            ).fetchone()[0] == 1
    finally:
        system.close()

print(f"Kontinuum {APP_VERSION} Foundation Knowledge Protection 2.0 tests passed")
