from __future__ import annotations

"""Historical local-HTTP research harness, excluded from release gates.

The current connector path remains covered by test_search_engine_connector_23.py.
This older end-to-end fixture can exhaust page-fetch budgets depending on local
thread scheduling and is retained only for explicit manual compatibility runs.
"""

import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem


class ResearchMock(BaseHTTPRequestHandler):
    port = 0

    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path.startswith("/html/"):
            body = f"""
            <html><body>
            <a class="result__a" href="http://127.0.0.1:{self.port}/source-a">Quelle A</a>
            <a class="result__snippet">A beschreibt den geprüften Sachverhalt.</a>
            <a class="result__a" href="http://127.0.0.1:{self.port}/source-b">Quelle B</a>
            <a class="result__snippet">B bestätigt den Sachverhalt.</a>
            </body></html>
            """.encode("utf-8")
        elif self.path == "/source-a":
            body = b"<html><title>Quelle A</title><body><p>Alpha wurde im Jahr 2024 geprueft. Die Quelle beschreibt Methode, Ergebnis und Grenzen ausfuehrlich. Die Untersuchung wurde dokumentiert und kann unabhaengig nachvollzogen werden.</p></body></html>"
        elif self.path == "/source-b":
            body = b"<html><title>Quelle B</title><body><p>Eine zweite Quelle bestaetigt Alpha. Sie vergleicht mehrere Beobachtungen, nennt ihre Datengrundlage und beschreibt die verbleibende Unsicherheit der Aussage.</p></body></html>"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), ResearchMock)
server.daemon_threads = True
ResearchMock.port = server.server_port
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "search_engine.json").write_text(
        json.dumps({
            "base_url": f"http://127.0.0.1:{server.server_port}/html/",
            "provider": "duckduckgo_html",
            "provider_order": ["duckduckgo_html"],
            "fallback_providers": [],
            "max_results": 2,
            "timeout_seconds": 10
        }),
        encoding="utf-8",
    )
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")

    system = KontinuumSystem(root)
    captured = {}

    def grounded(question, sources):
        captured["question"] = question
        captured["sources"] = sources
        return {"ok": True, "answer": "Alpha wurde geprüft [1] und durch eine zweite Quelle bestätigt [2]."}

    system.tools["language_model_tools"].generate_grounded_answer = grounded
    try:
        answer = system.ask("Was ist Alpha?")
        assert "Alpha wurde geprüft [1]" in answer, answer
        assert "Quellen:" in answer
        assert f"http://127.0.0.1:{server.server_port}/source-a" in answer
        assert len(captured["sources"]) == 2
        assert any("Alpha wurde im Jahr 2024" in source["text"] for source in captured["sources"])
        research = next(agent for agent in system.agents if agent.name == "research")
        assert not research._usable_source({"title": "Captcha Page"}, "Captcha " * 100)
        fallback = research._extractive_fallback("Was ist Alpha?", captured["sources"])
        assert "Alpha wurde im Jahr 2024" in fallback and "[1]" in fallback
        with system.storage.connect() as database:
            stored = database.execute("SELECT COUNT(*) FROM sources WHERE kind = 'research.source'").fetchone()[0]
        assert stored == 2
    finally:
        system.close()

server.shutdown()
server.server_close()
print("Kontinuum sourced research tests passed")
