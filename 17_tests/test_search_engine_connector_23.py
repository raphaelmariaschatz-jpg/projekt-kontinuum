from __future__ import annotations

import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem
from kontinuum.tools.search_engine_tools import SearchEngineTools


DOCUMENT = """
<html><body>
<div class="result">
  <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Falpha">Alpha Quelle</a>
  <a class="result__snippet">Eine belastbare Alpha-Fundstelle.</a>
</div>
<div class="result">
  <a class="result__a" href="https://example.net/beta">Beta Quelle</a>
  <a class="result__snippet">Eine zweite Fundstelle.</a>
</div>
</body></html>
"""


class SearchMock(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path.startswith("/source-"):
            body = (
                "<html><title>Lokale Quelle</title><body><p>"
                "Quantendynamik wird in dieser lokalen Testquelle belastbar beschrieben und nachvollziehbar belegt."
                "</p></body></html>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        assert "q=Quantendynamik" in self.path
        local_document = DOCUMENT.replace(
            "https%3A%2F%2Fexample.org%2Falpha",
            f"http%3A%2F%2F127.0.0.1%3A{server.server_port}%2Fsource-a",
        ).replace("https://example.net/beta", f"http://127.0.0.1:{server.server_port}/source-b")
        body = local_document.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), SearchMock)
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "search_engine.json").write_text(
        json.dumps({"provider_order": ["duckduckgo_html"], "base_url": f"http://127.0.0.1:{server.server_port}/html/"}),
        encoding="utf-8",
    )
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")

    connector = SearchEngineTools(root)
    assert connector.status()["provider_order"] == ["duckduckgo_html"]
    result = connector.search("Quantendynamik")
    assert result["ok"]
    assert len(result["results"]) == 2
    assert result["results"][0]["url"] == f"http://127.0.0.1:{server.server_port}/source-a"
    assert result["results"][0]["snippet"] == "Eine belastbare Alpha-Fundstelle."
    assert "Alpha Quelle" in connector.format_results(result)

    system = KontinuumSystem(root)
    try:
        answer = system.ask("recherchiere Quantendynamik")
        assert "Quantendynamik" in answer
        assert f"http://127.0.0.1:{server.server_port}/source-a" in answer
        with system.storage.connect() as database:
            sources = database.execute(
                "SELECT content, metadata FROM sources WHERE kind = 'research.source' ORDER BY id"
            ).fetchall()
        assert len(sources) == 2, f"Antwort: {answer}\nQuellen: {[(row['content'], row['metadata']) for row in sources]}"
        assert json.loads(sources[0]["metadata"])["content_policy"] == "references_only"
        assert "Suchmaschinen-Connector aktiv" in system.ask("suchmaschinenstatus")
    finally:
        system.close()

server.shutdown()
server.server_close()

router = SearchEngineTools(Path(tempfile.gettempdir()))
router.config["provider_order"] = ["local_knowledge", "notebook_knowledge", "university_sources", "arxiv", "semantic_scholar", "brave_search", "duckduckgo_html"]
assert router.status()["provider_order"][:3] == ["local_knowledge", "notebook_knowledge", "university_sources"]

wiki_rows = SearchEngineTools._parse_wikipedia(
    json.dumps({"query": {"search": [{"title": "Kontinuum", "snippet": "Projekt <b>Kontinuum</b>"}]}}),
    3,
)
assert wiki_rows[0]["provider"] == "wikipedia"

semantic_rows = SearchEngineTools._parse_semantic_scholar(
    json.dumps({"data": [{"title": "Meaning Graphs", "url": "https://example.org/paper", "year": 2026, "authors": [{"name": "A"}], "abstract": "Graph explanation."}]}),
    3,
)
assert semantic_rows[0]["provider"] == "semantic_scholar"

brave_rows = SearchEngineTools._parse_brave(
    json.dumps({"web": {"results": [{"title": "Brave Treffer", "url": "https://example.org", "description": "Beschreibung"}]}}),
    3,
)
assert brave_rows[0]["provider"] == "brave_search"
print("Kontinuum search engine connector tests passed")
