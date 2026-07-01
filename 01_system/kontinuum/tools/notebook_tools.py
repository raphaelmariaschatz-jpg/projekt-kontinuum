from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


class NotebookTools:
    TEXT_SUFFIXES = {".txt", ".md", ".json", ".py", ".csv", ".html", ".htm"}

    def __init__(self, project_root: str | Path, storage=None, web=None):
        self.project_root = Path(project_root)
        self.storage = storage
        self.web = web
        self.memory_core = None
        self.knowledge_platform = None

    def bind(self, storage) -> None:
        self.storage = storage

    def import_source(self, locator: str) -> dict:
        value = (locator or "").strip().strip('"')
        if not value:
            return {"ok": False, "error": "Keine Quelle angegeben."}
        if urlparse(value).scheme in {"http", "https"}:
            result = self.web.fetch_text(value, timeout=8) if self.web else {"error": "Web-Tool fehlt."}
            if result.get("error"):
                return {"ok": False, "error": result["error"]}
            text = str(result.get("text", "")).strip()
            title = result.get("title") or value
            source_type = "web"
        else:
            path = Path(value)
            if not path.is_absolute():
                path = self.project_root / path
            if not path.is_file():
                return {"ok": False, "error": f"Quelle nicht gefunden: {path}"}
            try:
                text = self._read_file(path)
            except (OSError, ValueError) as exc:
                return {"ok": False, "error": str(exc)}
            value = str(path)
            title = path.name
            source_type = path.suffix.casefold().lstrip(".") or "text"
        if not text.strip():
            return {"ok": False, "error": "Die Quelle enthält keinen auswertbaren Text."}
        source_id = self.storage.add(
            "knowledge_items",
            "notebook.source",
            text[:500_000],
            {"locator": value, "title": title, "source_type": source_type, "content_policy": "local_notebook"},
        )
        source_record_id = self.storage.add_source(
            value,
            {"title": title, "source_type": source_type, "notebook_source_id": source_id},
        )
        summary = self._summarize(text)
        integration = None
        if self.knowledge_platform:
            integration = self.knowledge_platform.integrate_notebook_source(
                source_id,
                source_record_id,
                title,
                value,
                summary,
            )
        elif self.memory_core:
            self.memory_core.remember(
                f"Notebook-Quelle {title}: {value}",
                owner="Kontinuum",
                explicit=True,
                source="knowledge_notebook",
            )
        return {
            "ok": True,
            "id": source_id,
            "source_record_id": source_record_id,
            "title": title,
            "characters": len(text),
            "summary": summary,
            "integration": integration,
        }

    def list_sources(self) -> list[dict]:
        with self.storage.connect() as database:
            rows = database.execute(
                "SELECT id, metadata, created_at FROM knowledge_items WHERE kind = 'notebook.source' ORDER BY id"
            ).fetchall()
        result = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            result.append({"id": row["id"], "created_at": row["created_at"], **metadata})
        return result

    def summarize(self, source_id: int | None = None) -> str:
        sources = self._source_rows(source_id)
        if not sources:
            return "Das Wissensnotizbuch enthält noch keine Quellen."
        lines = ["Wissensnotizbuch-Zusammenfassung:"]
        for row in sources[:10]:
            lines.append(f"[{row['id']}] {row['title']}: {self._summarize(row['content'])}")
        return "\n".join(lines)

    def answer(self, question: str) -> str:
        sources = self._source_rows()
        if not sources:
            return "Das Wissensnotizbuch enthält noch keine Quellen."
        keywords = {word for word in re.findall(r"\w{4,}", question.casefold())}
        evidence = []
        for source in sources:
            for sentence in re.split(r"(?<=[.!?])\s+", source["content"]):
                clean = " ".join(sentence.split()).strip()
                if not 30 <= len(clean) <= 700:
                    continue
                score = sum(keyword in clean.casefold() for keyword in keywords)
                if score:
                    evidence.append((score, clean, source))
        evidence.sort(key=lambda item: (item[0], -len(item[1])), reverse=True)
        selected = evidence[:5]
        if not selected:
            return "In den importierten Quellen wurde keine belastbare Antwortstelle gefunden."
        lines = ["Antwort aus dem Wissensnotizbuch:"]
        citations = {}
        for _, sentence, source in selected:
            citations[source["id"]] = source
            lines.append(f"- {sentence} [{source['id']}]")
        lines.append("\nQuellen:")
        for source in citations.values():
            lines.append(f"[{source['id']}] {source['title']}\n{source['locator']}")
        return "\n".join(lines)

    def learn(self, subject: str = "Wissensnotizbuch") -> str:
        sources = self._source_rows()
        if not sources:
            return "Keine Notebook-Quellen zum Lernen vorhanden."
        self.storage.ensure_learning_task(subject, [row["title"] for row in sources[:20]], "knowledge_notebook")
        for row in sources:
            self.storage.add_edge(subject, "belegt durch Quelle", row["locator"], {"notebook_source_id": row["id"]})
        return f"Notebook-Wissen übernommen: Lernauftrag „{subject}“, Quellen im Wissensgraph: {len(sources)}."

    def _source_rows(self, source_id: int | None = None) -> list[dict]:
        query = "SELECT id, content, metadata FROM knowledge_items WHERE kind = 'notebook.source'"
        params = ()
        if source_id is not None:
            query += " AND id = ?"
            params = (source_id,)
        query += " ORDER BY id"
        with self.storage.connect() as database:
            rows = database.execute(query, params).fetchall()
        result = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            result.append({
                "id": int(row["id"]),
                "content": row["content"],
                "title": metadata.get("title", f"Quelle {row['id']}"),
                "locator": metadata.get("locator", ""),
            })
        return result

    def _read_file(self, path: Path) -> str:
        suffix = path.suffix.casefold()
        if suffix in self.TEXT_SUFFIXES:
            return path.read_text(encoding="utf-8-sig", errors="replace")
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise ValueError("PDF-Import benötigt das optionale Paket pypdf.") from exc
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        raise ValueError(f"Nicht unterstütztes Quellenformat: {suffix or '(ohne Endung)'}")

    @staticmethod
    def _summarize(text: str) -> str:
        sentences = [
            " ".join(sentence.split()).strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if len(" ".join(sentence.split()).strip()) >= 30
        ]
        return " ".join(sentences[:3])[:900] or "Keine kompakte Zusammenfassung möglich."
