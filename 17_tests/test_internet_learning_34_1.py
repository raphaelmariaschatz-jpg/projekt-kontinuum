from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.internet_learning import InternetLearningService
from kontinuum.tools.path_tools import PathTools


ikg = json.loads((ROOT / "24_config" / "internet_knowledge_governance_1_0.json").read_text(encoding="utf-8"))
assert ikg["status"] == "policy_only_no_automatic_knowledge_adoption"
assert "direct_memory_write_request" in ikg["automatic_rejection"]
assert ikg["review_rules"]["queue_directory"] == "32_data/internet_learning_queue"
assert ikg["review_rules"]["review_directory"] == "32_data/internet_learning_review"
assert "sha256" in ikg["provenance_required_fields"]


def write_policy(paths: PathTools, payload: dict) -> None:
    config = paths.paths()["config"]
    config.mkdir(parents=True, exist_ok=True)
    (config / "internet_learning_policy_34_1.json").write_text(json.dumps(payload), encoding="utf-8")


class Fetcher:
    def __init__(self):
        self.calls = []

    def __call__(self, url, timeout, max_bytes):
        self.calls.append((url, timeout, max_bytes))
        return {
            "url": url,
            "title": "Testquelle",
            "text": f"Peer-reviewed public documentation from {url}. Alpha Beta Gamma.",
            "bytes": 120,
        }


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    paths = PathTools(Path(temporary_root))
    paths.ensure_all()
    service = InternetLearningService(paths)
    assert service.status()["enabled"] is True
    result = service.run_cycle("test")
    assert result["ok"] is False
    assert "Internet-Lernen pausiert: Internet nicht verfügbar oder keine verwertbaren Quellen." in result["message"]
    assert service.start()
    assert service.is_running()
    assert service.set_enabled(False)
    assert service.status()["enabled"] is False
    assert not service.is_running()
    assert service.set_enabled(True)
    assert service.status()["enabled"] is True
    assert service.is_running()
    assert service.stop()
    assert not service.is_running()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    paths = PathTools(Path(temporary_root))
    paths.ensure_all()
    write_policy(
        paths,
        {
            "continuous_internet_learning_enabled": True,
            "startup_delay_seconds": 60,
            "cycle_interval_seconds": 60,
            "max_requests_per_minute": 1,
            "min_delay_between_requests_seconds": 0,
            "max_download_mb_per_hour": 1,
            "max_sources_per_cycle": 2,
            "seed_sources": [
                {"url": "https://example.org/a", "source_class": "technical_documentation", "title": "A"},
                {"url": "https://example.org/b", "source_class": "technical_documentation", "title": "B"},
            ],
        },
    )
    fetcher = Fetcher()
    service = InternetLearningService(paths, fetcher=fetcher)
    assert service.start()
    assert service.is_running()
    assert service.stop()
    assert not service.is_running()

    result = service.run_cycle("test")
    assert result["new_findings"] == 1
    assert len(fetcher.calls) == 1
    assert service.status()["new_findings"] == 1
    assert service.status()["bandwidth_limit_active"] is True
    assert service.status()["bandwidth_limit_percent"] == 10
    assert service.status()["write_to_memory_directly"] is False

    queue_files = list((paths.paths()["data"] / "internet_learning_queue").glob("*.json"))
    review_files = list((paths.paths()["data"] / "internet_learning_review").glob("*.json"))
    assert len(queue_files) == 1
    assert len(review_files) == 1
    record = json.loads(queue_files[0].read_text(encoding="utf-8"))
    assert record["url"] == "https://example.org/a"
    assert record["sha256"]
    assert record["retrieved_at"]
    assert record["summary"]
    assert record["review_required"] is True
    assert record["write_to_memory_directly"] is False
    assert not (paths.paths()["data"] / "kontinuum.db").exists()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    paths = PathTools(Path(temporary_root))
    paths.ensure_all()
    write_policy(paths, {"enabled": True, "startup_delay_seconds": 0, "seed_sources": []})
    service = InternetLearningService(paths)
    result = service.run_cycle("test")
    assert result["ok"] is False
    assert "Internet-Lernen pausiert: Internet nicht verfügbar oder keine verwertbaren Quellen." in result["message"]

gui_source = (ROOT / "11_gui" / "desktop_gui_34_1.py").read_text(encoding="utf-8")
assert "Internet-Lernen" in gui_source
assert "Internet-Lernen: Aktiv" in gui_source
assert "Internet-Lernen deaktivieren" in gui_source
assert "set_enabled(False)" in gui_source
assert "toggle_internet_learning" in gui_source
assert "_refresh_internet_learning_status" in gui_source

print("Kontinuum 34.1 internet learning tests passed")
