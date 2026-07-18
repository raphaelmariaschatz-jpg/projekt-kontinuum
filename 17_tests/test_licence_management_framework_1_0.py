from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.licence_management_framework import (
    CanonicalLicenceManagementSystemFramework,
)
from kontinuum.core.system import KontinuumSystem


def declaration() -> dict:
    return {
        "licence_id": "LIC-KONTINUUM-2026-0001",
        "licence_type": "PRIVATE",
        "schema_version": "1.0",
        "licence_version": "1.0",
        "owner_reference": "identity:creator_001",
        "issuer_reference": "governance:local-owner",
        "licensed_subject": {
            "subject_type": "INSTALLATION",
            "subject_id": "installation:test-only",
        },
        "origin": "explicit_test_declaration",
        "status": "ACTIVE",
        "valid_from": "2026-07-01T00:00:00Z",
        "valid_until": "2026-08-01T00:00:00Z",
        "licence_profile_reference": "profile:personal-local",
        "scope": ["local_test_use"],
        "constraints": ["no_enforcement_effect"],
        "provenance": {"reference": "test-fixture"},
        "history_reference": "history:test-fixture",
        "integrity": {"state": "not_cryptographically_verified"},
    }


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.licence_management_framework
        assert isinstance(framework, CanonicalLicenceManagementSystemFramework)
        assert system.agent_config["licence_management_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["required_fields"] == 17
        assert status["starter_licence_types"] == 6
        assert status["lifecycle_statuses"] == 10
        assert status["licence_assurance_levels"] == 4
        assert status["licence_enforcement"] is False
        assert status["licence_issuance"] is False
        assert status["authorization"] is False
        assert status["authentication"] is False
        assert status["legal_decision"] is False
        assert status["registry_mutation"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["licence_management_framework"]["active"] is True

        with system.storage.connect() as database:
            memories_before = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        valid = framework.review_declaration(
            declaration=declaration(),
            checked_at="2026-07-18T12:00:00+02:00",
            licence_assurance_level="MEDIUM",
        )
        duplicate = framework.review_declaration(
            declaration=declaration(),
            checked_at="2026-07-18T12:00:00+02:00",
            licence_assurance_level="MEDIUM",
        )
        assert valid.review_id == duplicate.review_id
        assert valid.structurally_valid is True
        assert valid.findings == []
        assert valid.checked_at == "2026-07-18T10:00:00Z"
        assert valid.enforcement_performed is False
        assert valid.licence_issued is False
        assert valid.authorization_granted is False
        assert valid.authentication_performed is False
        assert valid.legal_decision_made is False
        assert valid.registry_mutated is False
        assert valid.direct_memory_write is False

        invalid_declaration = declaration()
        invalid_declaration["licence_type"] = "UNREGISTERED"
        invalid_declaration["integrity"] = {"private_key": "forbidden-test-value"}
        invalid = framework.review_declaration(
            declaration=invalid_declaration,
            checked_at="2026-08-02T00:00:00Z",
            licence_assurance_level="LOW",
        )
        assert invalid.structurally_valid is False
        assert "unregistered_licence_type" in invalid.findings
        assert "forbidden_secret_field:integrity.private_key" in invalid.findings
        assert "expired_at_check_time" in invalid.findings

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before
    finally:
        system.close()

print("Canonical Licence Management System Framework 1.0 tests passed")
