from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.continuous_learning import ContinuousLearningService
from kontinuum.core.storage import Storage
from kontinuum.tools.path_tools import PathTools


with tempfile.TemporaryDirectory() as temporary_directory:
    root = Path(temporary_directory)
    paths = PathTools(root)
    paths.ensure_all()
    (paths.paths()["knowledge"] / "chemie_grundlagen.md").write_text(
        "Chemie behandelt Atombau, Bindungen und Reaktionen. Dieser Volltext darf nicht in die Datenbank kopiert werden.",
        encoding="utf-8",
    )
    (paths.paths()["config"] / "continuous_learning.json").write_text(
        json.dumps(
            {
                "enabled": True,
                "interval_seconds": 1,
                "startup_delay_seconds": 0,
                "max_references_per_cycle": 2,
                "max_files_scanned_per_cycle": 50,
                "default_subjects": [],
            }
        ),
        encoding="utf-8",
    )

    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    service = ContinuousLearningService(paths, storage)
    service.add_task("Chemie", ["Atombau", "Bindungen"])
    result = service.run_cycle("test")
    assert result["references_added"] == 1

    db = storage.connect()
    try:
        source = db.execute("SELECT content, metadata FROM sources WHERE kind = 'learning.reference'").fetchone()
        assert source["content"].endswith("chemie_grundlagen.md")
        assert "Dieser Volltext" not in source["content"]
        assert json.loads(source["metadata"])["policy"] == "references_only"
    finally:
        db.close()

    assert service.start()
    time.sleep(0.2)
    assert service.is_running()
    assert service.stop()
    assert not service.is_running()

print("Kontinuum 23.0 continuous learning tests passed")
