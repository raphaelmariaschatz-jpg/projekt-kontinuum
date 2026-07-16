from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.canonical_reflective_layer import CanonicalReflectiveLayer
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        crl = system.canonical_reflective_layer
        assert isinstance(crl, CanonicalReflectiveLayer)
        status = crl.status()
        assert status["version"] == "1.0"
        assert status["direct_memory_write"] is False

        with system.storage.connect() as database:
            before_memory = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            before_events = database.execute("SELECT COUNT(*) FROM events WHERE kind = 'crl.reflection'").fetchone()[0]

        answer = system.ask("crl Welche Entwicklungsmuster zeigen Architektur und Governance?")
        assert "CRL 1.0" in answer
        assert "Governance" in answer
        assert "CRL schreibt nicht direkt in Memory" in answer

        with system.storage.connect() as database:
            after_memory = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            after_events = database.execute("SELECT COUNT(*) FROM events WHERE kind = 'crl.reflection'").fetchone()[0]

        assert after_memory == before_memory
        assert after_events == before_events + 1

        blocked = crl.assess("Ich bin bewusst und habe Qualia.")
        assert blocked.allowed is False
        assert blocked.memory_handoff_allowed is False
    finally:
        system.close()

print("Canonical Reflective Layer 1.0 tests passed")
