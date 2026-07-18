from __future__ import annotations

from dataclasses import FrozenInstanceError
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.authentication_framework import CanonicalAuthenticationFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.authentication_framework
        assert isinstance(framework, CanonicalAuthenticationFramework)
        assert system.agent_config["authentication_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["identity_types"] == 10
        assert status["authentication_methods"] == 8
        assert status["assurance_levels"] == 5
        assert status["login_replacement"] is False
        assert status["authentication_execution"] is False
        assert status["session_creation"] is False
        assert status["authorization"] is False
        assert status["credential_storage"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["authentication_framework"]["active"] is True

        with system.storage.connect() as database:
            memories_before = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        observation = framework.build_observation(
            identity_id="creator_001",
            identity_type="CREATOR",
            authentication_method_id="local-password-argon2id",
            method_class="PASSWORD_ARGON2ID",
            assurance_level="AAL-2",
            authenticated_at="2026-07-18T10:00:00+02:00",
            valid_until="2026-07-18T11:00:00+02:00",
            session_id="session-observed-1",
            security_context={"trust_domain": "local_personal_runtime"},
            device_context={"binding_state": "not_bound"},
            origin={"component": "test_observer"},
            result="success",
            policy_version="observed-policy-1",
            audit_reference="audit-reference-only",
        )
        duplicate = framework.build_observation(
            identity_id="creator_001",
            identity_type="CREATOR",
            authentication_method_id="local-password-argon2id",
            method_class="PASSWORD_ARGON2ID",
            assurance_level="AAL-2",
            authenticated_at="2026-07-18T10:00:00+02:00",
            valid_until="2026-07-18T11:00:00+02:00",
            session_id="session-observed-1",
            security_context={"trust_domain": "local_personal_runtime"},
            device_context={"binding_state": "not_bound"},
            origin={"component": "test_observer"},
            result="success",
            policy_version="observed-policy-1",
            audit_reference="audit-reference-only",
        )
        assert observation.authentication_event_id == duplicate.authentication_event_id
        assert observation.authenticated_at == "2026-07-18T08:00:00Z"
        assert observation.issuer_attested is False
        assert observation.authentication_performed is False
        assert observation.authorization_usable is False
        assert observation.secret_material_present is False
        assert observation.direct_memory_write is False
        try:
            observation.result = "failure"
        except FrozenInstanceError:
            pass
        else:
            raise AssertionError("CAF observation was not frozen")

        try:
            framework.build_observation(
                identity_id="creator_001",
                identity_type="CREATOR",
                authentication_method_id="local-password-argon2id",
                method_class="PASSWORD_ARGON2ID",
                assurance_level="AAL-2",
                authenticated_at="2026-07-18T10:00:00Z",
                valid_until="2026-07-18T11:00:00Z",
                session_id="session-observed-2",
                security_context={"password": "must-not-enter-caf"},
                device_context={},
                origin={"component": "test_observer"},
                result="success",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("CAF observation accepted secret material")

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before
    finally:
        system.close()

print("Canonical Authentication Framework 1.0 tests passed")
