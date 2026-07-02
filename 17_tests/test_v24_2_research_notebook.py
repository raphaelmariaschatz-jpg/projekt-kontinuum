from __future__ import annotations

import json
import sys
import tempfile
import time
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.research_agent import ResearchAgent
from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION
from kontinuum.tools.search_engine_tools import SearchEngineTools


class SlowWeb:
    def fetch_text(self, url, timeout=6):
        time.sleep(2)
        return {"url": url, "error": "zu langsam"}


class SearchStub:
    @staticmethod
    def format_results(result):
        return "Treffer"


agent = ResearchAgent(tools={"web_tools": SlowWeb(), "search_engine_tools": SearchStub()})
agent.TOTAL_TIMEOUT = 0.1
started = time.monotonic()
partial = agent._build_sourced_answer(
    "Alpha",
    {"ok": True, "results": [{"title": "A", "url": "https://example.org/a", "snippet": "Alpha ist belegt."}]},
    SlowWeb(),
    started,
)
assert time.monotonic() - started < 1
assert "Teilantwort" in partial and "https://example.org/a" in partial

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "search_engine.json").write_text(
        json.dumps({
            "provider": "unknown",
            "fallback_providers": ["duckduckgo_html"],
            "fallback_base_urls": {"duckduckgo_html": "http://127.0.0.1:1/"},
            "timeout_seconds": 1,
        }),
        encoding="utf-8",
    )
    connector = SearchEngineTools(root)
    assert connector.MAX_RUNTIME == 8
    failed = connector.search("Alpha")
    assert failed["attempted_providers"] == ["unknown", "duckduckgo_html"]

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    document = root / "quelle.md"
    document.write_text(
        "Alpha ist ein lokaler Testbegriff. Alpha wird in dieser Quelle ausführlich und nachvollziehbar beschrieben.",
        encoding="utf-8",
    )
    system = KontinuumSystem(root)
    try:
        assert system.version == APP_VERSION
        completed = threading.Event()
        async_result = {}
        system.ask_async("Wie ist dein Name?", lambda answer, error: (async_result.update(answer=answer, error=error), completed.set()))
        assert completed.wait(2) and async_result["error"] is None and "Kontinuum" in async_result["answer"]
        assert "Quelle importiert" in system.ask(f'notizbuch import "{document}"')
        assert "Alpha ist ein lokaler Testbegriff" in system.ask("notizbuch frage Was ist Alpha?")
        assert "Quellen:" in system.ask("notizbuch frage Was ist Alpha?")
        assert "Notebook-Wissen übernommen" in system.ask("notizbuch lernen Alpha")
        status = system.ask("notizbuchstatus")
        assert f"Wissensnotizbuch {APP_VERSION}: 1" in status and "Quellen" in status
    finally:
        system.close()

print("Kontinuum 29.0 research and notebook regression tests passed")
