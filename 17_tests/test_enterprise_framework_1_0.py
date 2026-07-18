from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.enterprise_framework import CanonicalEnterpriseFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.enterprise_framework
        assert isinstance(framework, CanonicalEnterpriseFramework)
        assert system.agent_config["enterprise_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["dimensions"] == 10
        assert status["relationships"] == 9
        assert status["enterprise_data_processing"] is False
        assert status["transactions"] is False
        assert status["kpi_calculation"] is False
        assert status["automatic_consulting"] is False
        assert status["decision_authority"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["enterprise_framework"]["active"] is True

        catalog = framework.catalog()
        assert [item["id"] for item in catalog["dimensions"]] == [
            f"CEF-D{index:02d}" for index in range(1, 11)
        ]
        assert catalog["software_boundaries"]["erp"].startswith("CEF does not")

        with system.storage.connect() as database:
            memories_before = database.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        scope = framework.build_scope(
            dimension_ids=["CEF-D01", "CEF-D02", "CEF-D03"],
        )
        duplicate = framework.build_scope(
            dimension_ids=["CEF-D01", "CEF-D02", "CEF-D03"],
        )
        assert scope.scope_id == duplicate.scope_id
        assert scope.dimension_ids == ["CEF-D01", "CEF-D02", "CEF-D03"]
        assert len(scope.relationships) == 2
        assert scope.industry_profile == "generic"
        assert scope.transactions_enabled is False
        assert scope.enterprise_data_processed is False
        assert scope.kpi_calculation_enabled is False
        assert scope.decision_authority is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        for kwargs in (
            {"dimension_ids": ["CEF-D11"]},
            {"dimension_ids": ["CEF-D01"], "industry_profile": "finance"},
        ):
            try:
                framework.build_scope(**kwargs)
            except ValueError:
                pass
            else:
                raise AssertionError("Unsupported CEF scope was accepted")
    finally:
        system.close()

print("Canonical Enterprise Framework 1.0 tests passed")
