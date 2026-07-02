from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.application_services import LocalKnowledgeService
from kontinuum.core.conversation import ConversationManager
from kontinuum.core.continuous_canonical_engine import ContinuousCanonicalEngine
from kontinuum.core.storage import Storage
from kontinuum.core.web_agent import WebAgentService
from kontinuum.tools.path_tools import PathTools


PYTHON_URL = "https://www.python.org/"
PYCHARM_URL = "https://www.jetbrains.com/help/pycharm/getting-started.html"
DOCS_URL = "https://docs.python.org/3/library/index.html"
DOCS_HOME = "https://docs.python.org/3/"


class FakeFetcher:
    def __init__(self):
        self.calls = []

    def __call__(self, url: str, timeout: int, max_bytes: int) -> dict:
        self.calls.append(url)
        pages = {
            PYTHON_URL: """
                <html><head><title>Welcome to Python.org</title></head>
                <body><nav>navigation</nav><h1>Python</h1>
                <p>Python is a programming language that lets you work quickly and integrate systems effectively.</p>
                <ul><li>Downloads</li><li>Documentation</li></ul>
                <a href="/doc/">Docs</a><footer>footer</footer></body></html>
            """,
            PYCHARM_URL: """
                <html><head><title>Getting started with PyCharm</title></head>
                <body><h1>Getting started</h1>
                <p>PyCharm helps create, run, and debug Python projects.</p>
                <pre>print("hello")</pre></body></html>
            """,
            DOCS_URL: """
                <html><head><title>The Python Standard Library</title></head>
                <body><h1>Library index</h1><p>This page links to library modules.</p>
                <a href="math.html">math</a>
                <a href="pathlib.html">pathlib</a>
                <a href="https://external.example/out">external</a></body></html>
            """,
            "https://docs.python.org/3/library/math.html": """
                <html><head><title>math</title></head><body><h1>math</h1>
                <p>The math module provides access to mathematical functions.</p></body></html>
            """,
            "https://docs.python.org/3/library/pathlib.html": """
                <html><head><title>pathlib</title></head><body><h1>pathlib</h1>
                <p>pathlib offers object-oriented filesystem paths.</p></body></html>
            """,
            DOCS_HOME: """
                <html><head><title>Python 3 documentation</title></head>
                <body><h1>Python 3 Documentation</h1>
                <a href="tutorial/index.html">Tutorial</a>
                <a href="library/index.html">Library</a>
                <a href="reference/index.html">Reference</a>
                <a href="howto/index.html">HOWTO</a>
                <a href="installing/index.html">Installing</a>
                <a href="using/index.html">Using</a>
                <a href="faq/index.html">FAQ</a>
                <a href="glossary.html">Glossary</a>
                <a href="/3.10/">Python 3.10</a>
                <a href="/3.11/">Python 3.11</a>
                <a href="/3.16/">Python 3.16</a>
                </body></html>
            """,
            "https://docs.python.org/3/tutorial/index.html": """
                <html><head><title>The Python Tutorial</title></head>
                <body><h1>Tutorial</h1><p>The tutorial introduces Python concepts.</p></body></html>
            """,
            "https://docs.python.org/3/reference/index.html": """
                <html><head><title>The Python Language Reference</title></head>
                <body><h1>Reference</h1><p>The reference describes syntax and semantics.</p></body></html>
            """,
            "https://docs.python.org/3/howto/index.html": """
                <html><head><title>Python HOWTOs</title></head>
                <body><h1>HOWTO</h1><p>HOWTO documents explain focused tasks.</p></body></html>
            """,
            "https://docs.python.org/3/installing/index.html": """
                <html><head><title>Installing Python Modules</title></head>
                <body><h1>Installing</h1><p>Installation guidance for Python modules.</p></body></html>
            """,
            "https://docs.python.org/3/using/index.html": """
                <html><head><title>Using Python</title></head>
                <body><h1>Using</h1><p>Using Python on different platforms.</p></body></html>
            """,
            "https://docs.python.org/3/faq/index.html": """
                <html><head><title>Python Frequently Asked Questions</title></head>
                <body><h1>FAQ</h1><p>Frequently asked Python questions.</p></body></html>
            """,
            "https://docs.python.org/3/glossary.html": """
                <html><head><title>Glossary</title></head>
                <body><h1>Glossary</h1><p>Definitions of Python terms.</p></body></html>
            """,
        }
        if url not in pages:
            return {"url": url, "error": "not found"}
        return {
            "url": url,
            "http_status": 200,
            "content_type": "text/html; charset=utf-8",
            "raw_text": pages[url],
            "bytes": len(pages[url].encode("utf-8")),
        }


class FakeLearning:
    def __init__(self):
        self.tasks = []

    def add_task(self, subject, topics=None, origin=""):
        self.tasks.append((subject, topics or [], origin))
        return len(self.tasks)


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    paths = PathTools(Path(temporary))
    paths.ensure_all()
    config = paths.paths()["config"]
    config.mkdir(parents=True, exist_ok=True)
    (config / "web_agent_1_0.json").write_text(
        json.dumps(
            {
                "enabled": True,
                "mode": "diagnostic_review_only",
                "respect_robots_txt": False,
                "max_pages": 20,
                "max_depth": 2,
                "no_direct_memory_write": True,
                "no_automatic_canonical_adoption": True,
            }
        ),
        encoding="utf-8",
    )
    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    canonical_engine = ContinuousCanonicalEngine(Path(temporary), path_tools=paths, release_version="34.1", strict_config=False)
    learning = FakeLearning()
    fetcher = FakeFetcher()
    web_agent = WebAgentService(paths, storage=storage, continuous_learning=learning, fetcher=fetcher, canonical_engine=canonical_engine)

    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")
    assert conversation.classify(f"lerne auch hier: {PYTHON_URL}").input_type == "command"
    assert web_agent.urls_in(f"nutze zum Lernen auch {PYCHARM_URL}") == [PYCHARM_URL]

    python_result = web_agent.handle_command(f"lerne auch hier: {PYTHON_URL}")
    assert python_result["ok"], python_result
    assert "Welcome to Python.org" in python_result["message"]
    assert len(list((paths.paths()["data"] / "web_agent_sources").glob("*.json"))) == 1
    assert len(list((paths.paths()["data"] / "internet_learning_review").glob("webagent_*.json"))) == 1

    pycharm_result = web_agent.handle_command(f"nutze zum Lernen auch {PYCHARM_URL}")
    assert pycharm_result["ok"], pycharm_result
    assert "PyCharm" in pycharm_result["message"]

    crawl = web_agent.handle_command(f"öffne nacheinander alle Links auf folgender Webseite und lerne den Inhalt {DOCS_URL}")
    assert crawl["ok"], crawl
    assert crawl["mode"] == "crawl"
    assert crawl["stored"] == 3
    assert "https://external.example/out" not in fetcher.calls

    docs_crawl = web_agent.handle_command(
        f"gehe auf die Internetseite {DOCS_HOME} öffne nacheinander alle Links und lerne alle Dokumentationen über Python"
    )
    assert docs_crawl["ok"], docs_crawl
    assert docs_crawl["documentation_plan"]
    assert docs_crawl["max_pages"] == 50
    assert docs_crawl["max_depth"] == 3
    assert "https://docs.python.org/3/tutorial/index.html" in fetcher.calls
    assert "https://docs.python.org/3/library/index.html" in fetcher.calls
    assert "https://docs.python.org/3/reference/index.html" in fetcher.calls
    assert "https://docs.python.org/3.10/" not in fetcher.calls
    assert "https://docs.python.org/3.11/" not in fetcher.calls
    assert "https://docs.python.org/3.16/" not in fetcher.calls
    assert any("Versionsarchiv" in item["reason"] for item in docs_crawl["skipped"])
    assert "tatsächlich gelernte Seiten" in docs_crawl["message"]
    assert "übersprungene Seiten" in docs_crawl["message"]
    assert "nächste empfohlene Crawl-Fortsetzung" in docs_crawl["message"]

    failed = web_agent.learn_url("https://docs.python.org/3/missing.html")
    assert not failed["ok"]
    web_agent.config["respect_robots_txt"] = True
    web_agent._robots_allowed = lambda _url: False
    blocked = web_agent.learn_url("https://docs.python.org/3/blocked.html")
    assert blocked["skip_reason"] == "robots.txt blockiert den Abruf."

    events = [
        json.loads(line)["event"]["event_type"]
        for line in canonical_engine.event_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for expected in {
        "WEB_FETCH_STARTED",
        "WEB_FETCH_COMPLETED",
        "WEB_FETCH_FAILED",
        "WEB_CRAWL_STARTED",
        "WEB_CRAWL_COMPLETED",
        "WEB_SOURCE_LEARNED",
        "WEB_SOURCE_SKIPPED",
        "WEB_ROBOTS_BLOCKED",
    }:
        assert expected in events, expected
    assert "Letztes Event: -" not in canonical_engine.format_status()
    assert "https://docs.python.org/3/library/math.html" in fetcher.calls
    assert "https://docs.python.org/3/library/pathlib.html" in fetcher.calls

    status = web_agent.format_status()
    assert "WebAgent aktiv: ja" in status
    assert "max_pages=20" in status
    assert "direct_http_get" in status
    stored_web_sources = web_agent.status()["stored_web_sources"]
    assert stored_web_sources >= 13

    with storage.connect() as database:
        assert database.execute("SELECT COUNT(*) FROM sources WHERE kind = 'research.source'").fetchone()[0] == stored_web_sources
        assert database.execute("SELECT COUNT(*) FROM knowledge_items").fetchone()[0] == 0
        assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == 0

    math_answer = LocalKnowledgeService().answer("binomische Formeln nach vorherigem Mathematik-Lernstatus")
    assert math_answer and "(a + b)" in math_answer[0]
    assert learning.tasks

policy = json.loads((ROOT / "24_config" / "web_agent_1_0.json").read_text(encoding="utf-8"))
assert policy["enabled"] is True
assert policy["no_direct_memory_write"] is True
assert policy["no_automatic_canonical_adoption"] is True
assert policy["max_pages"] == 20
assert policy["max_depth"] == 2

print("Kontinuum WebAgent 1.0 tests passed")
