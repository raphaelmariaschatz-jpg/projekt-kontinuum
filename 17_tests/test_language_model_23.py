from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.tools.language_model_tools import LanguageModelTools


class OllamaMock(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        self._send({"models": [{"name": "qwen2.5:3b"}]})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length))
        assert request["model"] == "qwen2.5:3b"
        assert request["messages"][0]["role"] == "system"
        self._send({"message": {"role": "assistant", "content": "Das ist eine deutsche Modellantwort."}})

    def _send(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), OllamaMock)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

with tempfile.TemporaryDirectory() as temporary_root:
    config_dir = Path(temporary_root) / "24_config"
    config_dir.mkdir()
    (config_dir / "language_model.json").write_text(
        json.dumps({"base_url": f"http://127.0.0.1:{server.server_port}"}),
        encoding="utf-8",
    )
    tool = LanguageModelTools(temporary_root)
    assert tool.status()["available"]
    result = tool.generate("Antworte auf Deutsch.")
    assert result["ok"]
    assert "deutsche Modellantwort" in result["answer"]

server.shutdown()
print("Kontinuum language model tests passed")
