from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.conversation import ConversationManager
from kontinuum.core.continuous_canonical_engine import ContinuousCanonicalEngine
from kontinuum.core.file_agent import FileAgentService
from kontinuum.core.storage import Storage
from kontinuum.tools.path_tools import PathTools


class FakeLearning:
    def __init__(self):
        self.tasks = []

    def add_task(self, subject, topics=None, origin=""):
        self.tasks.append((subject, topics or [], origin))
        return len(self.tasks)


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary)
    paths = PathTools(root)
    paths.ensure_all()
    (root / "14_documents").mkdir(exist_ok=True)
    (root / "30_import").mkdir(exist_ok=True)
    (root / "Documents").mkdir(exist_ok=True)
    (root / "24_config").mkdir(exist_ok=True)
    (root / "24_config" / "file_agent_1_0.json").write_text(
        json.dumps(
            {
                "enabled": True,
                "mode": "diagnostic_read_only",
                "max_files": 50,
                "max_file_size_mb": 400,
                "allowed_roots": [".", "30_import", "14_documents", str(root / "Documents")],
                "no_source_mutation": True,
            }
        ),
        encoding="utf-8",
    )
    test_txt = root / "30_import" / "test.txt"
    test_txt.write_text("Dies ist eine Testdatei. Sie enthält Lernstoff für Kontinuum.", encoding="utf-8")
    example_md = root / "30_import" / "beispiel.md"
    example_md.write_text("# Beispiel\n\nDiese Markdown-Datei erklärt einen Lerninhalt ausführlich genug.", encoding="utf-8")
    example_py = root / "30_import" / "beispiel.py"
    example_py.write_text(
        "# Kommentar zur Funktion\nclass Beispiel:\n    pass\n\ndef addiere(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    pdf = root / "30_import" / "beispiel.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nstream\nImportiere PDF als Lernquelle mit Textinhalt.\nendstream\nendobj\n%%EOF")
    phenol = root / "Documents" / "Phenol.pdf"
    phenol.write_bytes(
        b"%PDF-1.4\n1 0 obj\n<<>>\nstream\nPhenol ist ein aromatischer Alkohol. "
        b"Die Hydroxygruppe am Benzolring bestimmt Saeureeigenschaften und Reaktivitaet.\nendstream\nendobj\n%%EOF"
    )
    unknown = root / "30_import" / "beispiel.xyz"
    unknown.write_text("unbekannt", encoding="utf-8")
    (root / "14_documents" / "a.md").write_text("# A\n\nOrdner Lerninhalt A.", encoding="utf-8")
    (root / "14_documents" / "b.txt").write_text("Ordner Lerninhalt B.", encoding="utf-8")

    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    canonical_engine = ContinuousCanonicalEngine(root, path_tools=paths, release_version="34.1", strict_config=False)
    learning = FakeLearning()
    agent = FileAgentService(paths, storage=storage, continuous_learning=learning, canonical_engine=canonical_engine)
    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")

    assert conversation.classify("lies Datei 30_import/test.txt").input_type == "command"
    assert agent.looks_like_file_command("lerne aus Datei 30_import/beispiel.md")

    txt_result = agent.handle_command("lies Datei 30_import/test.txt")
    assert txt_result["ok"], txt_result
    assert "test.txt" in txt_result["message"]

    md_result = agent.handle_command("lerne aus Datei 30_import/beispiel.md")
    assert md_result["ok"], md_result
    assert md_result["file_type"] == ".md"

    py_result = agent.handle_command("analysiere Datei 30_import/beispiel.py")
    assert py_result["ok"], py_result
    assert py_result["analysis"]["language"] == "python"
    assert "addiere" in py_result["analysis"]["functions"]
    assert "Beispiel" in py_result["analysis"]["classes"]

    pdf_result = agent.handle_command("importiere PDF als Lernquelle 30_import/beispiel.pdf")
    assert pdf_result["ok"], pdf_result
    assert pdf_result["file_type"] == ".pdf"
    assert "gelesene Seiten/Abschnitte" in pdf_result["message"]

    phenol_result = agent.handle_command(f"benutze für den Bericht über Phenol \"{phenol}\"")
    assert phenol_result["ok"], phenol_result
    assert phenol_result["file_name"] == "Phenol.pdf"
    assert "Phenol" in phenol_result["message"]

    missing_documents = agent.handle_command(f"benutze für den Bericht über Phenol \"{root / 'Dokuments' / 'Phenol.pdf'}\"")
    assert not missing_documents["ok"]
    assert missing_documents["message"].startswith("Datei konnte nicht gelesen werden:")

    folder_result = agent.handle_command("lerne aus Ordner 14_documents")
    assert folder_result["ok"], folder_result
    assert len(folder_result["read"]) == 2

    duplicate = agent.handle_command("lerne aus Datei 30_import/test.txt")
    assert duplicate["ok"]
    assert duplicate["duplicate"] is True
    assert agent.status()["duplicates_detected"] >= 1

    blocked = agent.handle_command(f"lies Datei \"{Path(temporary).parent / 'outside.txt'}\"")
    assert not blocked["ok"]
    assert "nicht freigegeben" in blocked["error"]

    unsupported = agent.handle_command("lies Datei 30_import/beispiel.xyz")
    assert not unsupported["ok"]
    assert "nicht unterstützter Dateityp" in unsupported["error"]

    event_types = [
        json.loads(line)["event"]["event_type"]
        for line in canonical_engine.event_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for expected in {"FILE_READ_STARTED", "FILE_READ_COMPLETED", "FILE_LEARNED", "FILE_READ_FAILED"}:
        assert expected in event_types, expected
    assert "Letztes Event: -" not in canonical_engine.format_status()

    status = agent.handle_command("fileagentstatus")
    assert status["ok"]
    assert "FileAgent aktiv: ja" in status["message"]
    assert "Duplikate erkannt" in status["message"]

    with sqlite3.connect(paths.paths()["data"] / "kontinuum.db") as database:
        assert database.execute("SELECT COUNT(*) FROM sources WHERE kind = 'research.source'").fetchone()[0] >= 6
        assert database.execute("SELECT COUNT(*) FROM knowledge_items").fetchone()[0] == 0

    assert len(list((paths.paths()["data"] / "file_agent_sources").glob("*.json"))) >= 6
    assert len(list((paths.paths()["data"] / "file_agent_review").glob("*.json"))) >= 6
    assert learning.tasks

policy = json.loads((ROOT / "24_config" / "file_agent_1_0.json").read_text(encoding="utf-8"))
assert policy["enabled"] is True
assert policy["mode"] == "diagnostic_read_only"
assert policy["max_files"] == 50
assert policy["max_file_size_mb"] == 400
assert policy["no_source_mutation"] is True
assert ".pdf" in policy["supported_suffixes"]
assert ".docx" in policy["supported_suffixes"]
assert ".xlsx" in policy["supported_suffixes"]
assert ".azw3" in policy["supported_suffixes"]

print("Kontinuum FileAgent 1.0 tests passed")
