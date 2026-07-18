from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.api_learning_connector import APILearningConnector
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        connector = system.api_learning_connector
        assert isinstance(connector, APILearningConnector)
        assert system.agent_config["api_learning_connector"] is connector
        status = connector.status()
        assert status["active"] is True
        assert status["network_fetch"] is False
        assert status["request_execution"] is False
        assert status["persistence"] is False
        assert status["memory_write"] is False
        assert status["capability_registry_write"] is False
        assert system.status()["api_learning_connector"]["active"] is True

        specification = {
            "openapi": "3.0.0",
            "info": {"title": "Local Test API", "version": "1.0"},
            "paths": {
                "/items": {
                    "get": {"operationId": "listItems"},
                    "post": {
                        "operationId": "createItem",
                        "api_key": "must-not-survive",
                    },
                }
            },
            "components": {
                "schemas": {"Item": {"type": "object"}},
                "securitySchemes": {"ExampleAuth": {"type": "apiKey"}},
            },
        }

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()[0]

        analysis = connector.analyze_local(
            source_name="public-openapi.json",
            content=json.dumps(specification),
            public_access=True,
            license_signal="test-only",
        )
        duplicate = connector.analyze_local(
            source_name="public-openapi.json",
            content=json.dumps(specification),
            public_access=True,
            license_signal="test-only",
        )
        assert analysis.source.source_type == "openapi"
        assert analysis.source.redaction_count == 1
        assert analysis.source.source_id == duplicate.source.source_id
        assert analysis.structure.api_structure_id == duplicate.structure.api_structure_id
        assert analysis.structure.service_name == "Local Test API"
        assert len(analysis.structure.operations) == 2
        assert analysis.structure.schemas == ["Item"]
        assert analysis.structure.auth_schemes == ["ExampleAuth"]
        assert "mutating_operation_present" in analysis.structure.risk_flags
        assert "secret_like_fields_redacted" in analysis.structure.risk_flags
        assert analysis.structure.governance_state == "REVIEW"
        assert analysis.structure.executable is False
        assert all(not item["executable"] for item in analysis.capability_candidates)
        assert all(not item["registry_write_allowed"] for item in analysis.capability_candidates)
        assert analysis.network_request_executed is False
        assert analysis.persistence_performed is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        for kwargs, expected_error in (
            (
                {
                    "source_name": "private.json",
                    "content": "{}",
                    "public_access": False,
                },
                PermissionError,
            ),
            (
                {
                    "source_name": "https://example.invalid/api?token=secret",
                    "content": "{}",
                    "public_access": True,
                },
                ValueError,
            ),
            (
                {
                    "source_name": "entity.xml",
                    "content": "<!DOCTYPE x [<!ENTITY e 'x'>]><x>&e;</x>",
                    "public_access": True,
                },
                ValueError,
            ),
        ):
            try:
                connector.analyze_local(**kwargs)
            except expected_error:
                pass
            else:
                raise AssertionError(f"Expected {expected_error.__name__}")
    finally:
        system.close()

print("API Learning Connector 1.0 tests passed")
