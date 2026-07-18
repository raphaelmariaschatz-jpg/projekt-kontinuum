from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.deployment_framework import CanonicalDeploymentFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.deployment_framework
        assert isinstance(framework, CanonicalDeploymentFramework)
        assert system.agent_config["deployment_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["canonical_core_entries"] == 16
        assert status["deployment_profiles"] == 3
        assert status["optional_frameworks"] == 8
        assert status["deployment_execution"] is False
        assert status["configuration_mutation"] is False
        assert status["source_forks"] is False
        assert status["license_enforcement"] is False
        assert status["decision_authority"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["deployment_framework"]["active"] is True

        assert [item["id"] for item in framework.list_profiles()] == [
            "CDFX-PROFILE-PERSONAL-1-0",
            "CDFX-PROFILE-ENTERPRISE-1-0",
            "CDFX-PROFILE-RESEARCH-1-0",
        ]
        assert len(framework.list_canonical_core()) == 16

        with system.storage.connect() as database:
            memories_before = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        valid = framework.validate_profile(
            profile_id="CDFX-PROFILE-PERSONAL-1-0",
            enabled_optional_framework_ids=["CDFX-OPT-001", "CDFX-OPT-002"],
        )
        duplicate = framework.validate_profile(
            profile_id="CDFX-PROFILE-PERSONAL-1-0",
            enabled_optional_framework_ids=["CDFX-OPT-001", "CDFX-OPT-002"],
        )
        assert valid.validation_id == duplicate.validation_id
        assert valid.valid is True
        assert valid.errors == []
        assert valid.license_profile == "personal-local"
        assert valid.deployment_performed is False
        assert valid.configuration_mutated is False
        assert valid.source_fork_created is False
        assert valid.decision_authority is False

        invalid = framework.validate_profile(
            profile_id="CDFX-PROFILE-PERSONAL-1-0",
            enabled_optional_framework_ids=["CDFX-OPT-003"],
            disabled_core_ids=["CDFX-CORE-002"],
            license_profile="enterprise-governed",
        )
        assert invalid.valid is False
        assert "canonical_core_disable_forbidden:CDFX-CORE-002" in invalid.errors
        assert "framework_not_allowed:CDFX-OPT-003:personal" in invalid.errors
        assert "license_profile_mismatch" in invalid.errors

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        try:
            framework.validate_profile(profile_id="CDFX-PROFILE-UNKNOWN-1-0")
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown CDFX profile was accepted")
    finally:
        system.close()

print("Canonical Deployment Framework 1.0 tests passed")
