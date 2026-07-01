from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
import os
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree


class _HTMLTextParser(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer", "form"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.title = ""
        self._in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        tag = tag.casefold()
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in {"h1", "h2", "h3", "p", "li", "pre", "code", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str):
        tag = tag.casefold()
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str):
        if self.skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title += text + " "
        self.parts.append(text + " ")

    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


class FileAgentService:
    VERSION = "1.0"
    SUPPORTED_SUFFIXES = {
        ".txt", ".md", ".json", ".csv", ".html", ".htm", ".pdf", ".docx",
        ".xlsx", ".py", ".js", ".css", ".log", ".epub", ".azw", ".azw3", ".kfx",
    }
    CODE_SUFFIXES = {".py", ".js", ".css", ".html", ".htm"}
    WINDOWS_PATH_PATTERN = re.compile(r"(?i)\b[a-z]:[\\/][^\s\"']+")
    FILE_SUFFIX_PATTERN = re.compile(r"(?i)([^\s\"']+\.(?:txt|md|json|csv|html|htm|pdf|docx|xlsx|py|js|css|log|epub|azw|azw3|kfx))")
    DEFAULT_CONFIG = {
        "enabled": True,
        "mode": "diagnostic_read_only",
        "max_files": 50,
        "max_file_size_mb": 400,
        "max_extract_chars": 500000,
        "recursive_default": False,
        "no_source_mutation": True,
        "no_executable_start": True,
        "write_review_queue": True,
        "supported_suffixes": sorted(SUPPORTED_SUFFIXES),
        "allowed_roots": [
            ".",
            "30_import",
            "14_documents",
            "04_knowledge",
            "06_learning",
        ],
    }

    def __init__(self, path_tools, storage=None, continuous_learning=None, canonical_engine=None):
        self.path_tools = path_tools
        self.storage = storage
        self.continuous_learning = continuous_learning
        self.canonical_engine = canonical_engine
        self.root = path_tools.project_root().resolve()
        self.config_path = path_tools.paths()["config"] / "file_agent_1_0.json"
        self.config = self._load_config()
        data = path_tools.paths()["data"]
        self.sources_dir = data / "file_agent_sources"
        self.review_dir = data / "file_agent_review"
        self.log_path = path_tools.paths()["logs"] / "file_agent_1_0.jsonl"
        for path in (self.sources_dir, self.review_dir, self.log_path.parent):
            path.mkdir(parents=True, exist_ok=True)
        self._last_file = ""
        self._last_errors: list[str] = []
        self._duplicates = 0
        self._last_learning_success = False

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        home = Path(os.environ.get("USERPROFILE", str(Path.home())))
        for candidate in (home / "Documents", home / "Dokumente"):
            value = str(candidate)
            if value not in config["allowed_roots"]:
                config["allowed_roots"].append(value)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    @classmethod
    def looks_like_file_command(cls, text: str) -> bool:
        lower = (text or "").casefold()
        markers = (
            "lies diese datei", "lies datei", "lese datei", "lerne aus dieser datei",
            "lerne aus datei", "öffne diese datei", "oeffne diese datei",
            "analysiere diese datei", "analysiere datei", "importiere diese datei",
            "importiere datei", "importiere pdf", "lerne aus ordner", "fileagentstatus",
        )
        return any(marker in lower for marker in markers) or bool(cls.WINDOWS_PATH_PATTERN.search(text or "")) or bool(cls.FILE_SUFFIX_PATTERN.search(text or ""))

    def status(self) -> dict:
        return {
            "active": bool(self.config.get("enabled", False)),
            "mode": self.config.get("mode", "diagnostic_read_only"),
            "allowed_roots": [str(path) for path in self._allowed_roots()],
            "supported_file_types": sorted(self.SUPPORTED_SUFFIXES),
            "last_file": self._last_file,
            "imported_files": len(list(self.sources_dir.glob("*.json"))),
            "last_errors": self._last_errors[-5:],
            "duplicates_detected": self._duplicates,
            "learning_handoff_success": self._last_learning_success,
            "limits": {
                "max_files": int(self.config.get("max_files", 50)),
                "max_file_size_mb": int(self.config.get("max_file_size_mb", 400)),
            },
        }

    def format_status(self) -> str:
        status = self.status()
        errors = "; ".join(status["last_errors"]) if status["last_errors"] else "-"
        return "\n".join([
            "FileAgent 1.0 Status:",
            f"- FileAgent aktiv: {'ja' if status['active'] else 'nein'}",
            f"- Modus: {status['mode']}",
            "- erlaubte Verzeichnisse: " + "; ".join(status["allowed_roots"]),
            "- unterstützte Dateitypen: " + ", ".join(status["supported_file_types"]),
            f"- zuletzt gelesene Datei: {status['last_file'] or '-'}",
            f"- Anzahl importierter Dateien: {status['imported_files']}",
            f"- letzte Fehler: {errors}",
            f"- Duplikate erkannt: {status['duplicates_detected']}",
            f"- Lernübergabe erfolgreich: {'ja' if status['learning_handoff_success'] else 'nein'}",
        ])

    def handle_command(self, text: str) -> dict:
        lower = (text or "").casefold().strip()
        if lower == "fileagentstatus":
            return {"ok": True, "message": self.format_status()}
        if "lerne aus ordner" in lower:
            target = self._extract_path(text, folder=True)
            return self.import_folder(target, recursive="rekursiv" in lower)
        target = self._extract_path(text, folder=False)
        return self.import_file(target, topic=self._topic(text))

    def import_folder(self, folder: str | Path, recursive: bool = False) -> dict:
        try:
            base = self._resolve_path(folder)
        except ValueError as exc:
            return self._error("", str(exc))
        if not base.is_dir():
            return self._error(str(base), "Ordner nicht gefunden oder nicht lesbar.")
        max_files = max(1, min(int(self.config.get("max_files", 50)), 50))
        iterator = base.rglob("*") if recursive else base.glob("*")
        files = [path for path in iterator if path.is_file()]
        read = []
        skipped = []
        errors = []
        for path in files[: max_files * 4]:
            if len(read) >= max_files:
                skipped.append({"path": str(path), "reason": "max_files erreicht"})
                continue
            if path.suffix.casefold() not in self.SUPPORTED_SUFFIXES:
                skipped.append({"path": str(path), "reason": "nicht unterstützter Dateityp"})
                continue
            result = self.import_file(path, topic=f"Ordnerimport {base.name}")
            if result.get("ok"):
                read.append(result)
            else:
                errors.append(result)
        message = self._format_folder(base, read, skipped, errors, recursive)
        return {"ok": not errors, "read": read, "skipped": skipped, "errors": errors, "message": message}

    def import_file(self, path: str | Path, topic: str = "") -> dict:
        if not self.config.get("enabled", False):
            return self._error(str(path), "FileAgent ist deaktiviert.")
        try:
            target = self._resolve_path(path)
        except ValueError as exc:
            return self._error(str(path), str(exc))
        if not target.is_file():
            return self._error(str(target), "Datei nicht gefunden oder nicht lesbar.")
        self._emit_event("FILE_READ_STARTED", str(target), {"topic": topic})
        suffix = target.suffix.casefold()
        if suffix not in self.SUPPORTED_SUFFIXES:
            return self._error(str(target), f"Unbekannter oder nicht unterstützter Dateityp: {suffix or '(ohne Endung)'}")
        size = target.stat().st_size
        max_bytes = int(self.config.get("max_file_size_mb", 400)) * 1024 * 1024
        if size > max_bytes:
            return self._error(str(target), f"Datei überschreitet Größenlimit: {size} Bytes.")
        digest = self._hash_file(target)
        try:
            extracted = self._extract(target)
        except Exception as exc:
            return self._error(str(target), f"Extraktion fehlgeschlagen: {exc}")
        self._emit_event("FILE_READ_COMPLETED", str(target), {
            "file_name": target.name,
            "file_type": suffix,
            "size_bytes": size,
            "sha256": digest,
            "analysis": extracted.get("analysis", {}),
        })
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "file_name": target.name,
            "path": str(target),
            "relative_path": self._relative(target),
            "file_type": suffix,
            "topic": topic or target.stem,
            "summary": self._summary(extracted["text"]),
            "excerpt": extracted["text"][:4000],
            "sha256": digest,
            "imported_at": now,
            "size_bytes": size,
            "learning_status": "queued_for_review",
            "read_only": True,
            "source": "file_agent_1_0",
            "analysis": extracted.get("analysis", {}),
            "sections_read": extracted.get("analysis", {}).get("sections_read", 1),
            "pages_read": extracted.get("analysis", {}).get("pages", 0),
        }
        stored = self._store(record)
        self._last_file = str(target)
        self._last_learning_success = bool(stored.get("learning_handoff_success"))
        return {"ok": True, **record, **stored, "message": self._format_file(record, stored)}

    def _store(self, record: dict) -> dict:
        key = record["sha256"]
        source_file = self.sources_dir / f"{key}.json"
        duplicate = source_file.exists()
        if duplicate:
            self._duplicates += 1
        source_record_id = None
        if not duplicate:
            source_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            (self.review_dir / f"{key}.json").write_text(
                json.dumps({**record, "review_status": "pending"}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            if self.storage and hasattr(self.storage, "add_source"):
                source_record_id = self.storage.add_source(
                    record["path"],
                    {
                        "title": record["file_name"],
                        "source_type": "file",
                        "file_type": record["file_type"],
                        "sha256": record["sha256"],
                        "agent": "file_agent",
                        "content_policy": "read_only_review",
                    },
                )
            if self.continuous_learning:
                self.continuous_learning.add_task(record["topic"], [record["file_name"]], origin="file_agent")
        self._log({**record, "duplicate": duplicate})
        self._emit_event("FILE_LEARNED", record["path"], {
            "file_name": record["file_name"],
            "sha256": record["sha256"],
            "record_path": str(source_file),
            "duplicate": duplicate,
            "learning_status": record["learning_status"],
            "internet_learning": False,
            "reviewed": False,
        }, affected_path=str(source_file))
        return {
            "duplicate": duplicate,
            "source_record_id": source_record_id,
            "record_path": str(source_file),
            "learning_handoff_success": bool(self.continuous_learning),
        }

    def _extract(self, path: Path) -> dict:
        suffix = path.suffix.casefold()
        if suffix in {".txt", ".md", ".py", ".js", ".css", ".log"}:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            analysis = self._code_analysis(text, suffix) if suffix in self.CODE_SUFFIXES else {}
        elif suffix in {".html", ".htm"}:
            parser = _HTMLTextParser()
            parser.feed(path.read_text(encoding="utf-8-sig", errors="replace"))
            text = parser.text()
            analysis = {"title": parser.title.strip()}
        elif suffix == ".json":
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
            value = json.loads(raw)
            text = json.dumps(value, ensure_ascii=False, indent=2)
            analysis = {"json_type": type(value).__name__, "keys": list(value.keys())[:30] if isinstance(value, dict) else []}
        elif suffix == ".csv":
            text, analysis = self._extract_csv(path)
        elif suffix == ".pdf":
            text, analysis = self._extract_pdf(path)
        elif suffix == ".docx":
            text, analysis = self._extract_docx(path)
        elif suffix == ".xlsx":
            text, analysis = self._extract_xlsx(path)
        elif suffix == ".epub":
            text, analysis = self._extract_epub(path)
        elif suffix in {".azw", ".azw3", ".kfx"}:
            text = self._extract_binary_strings(path)
            analysis = {"format": suffix.lstrip("."), "quality": "limited_text_strings"}
        else:
            raise ValueError(f"Nicht unterstütztes Format: {suffix}")
        limit = int(self.config.get("max_extract_chars", 500000))
        return {"text": text[:limit], "analysis": analysis}

    def _extract_csv(self, path: Path) -> tuple[str, dict]:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            sample = handle.read(20000)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            rows = list(csv.reader(handle, dialect))[:30]
        columns = rows[0] if rows else []
        text = "\n".join(", ".join(cell for cell in row) for row in rows)
        return text, {"columns": columns, "preview_rows": max(0, len(rows) - 1)}

    @staticmethod
    def _extract_pdf(path: Path) -> tuple[str, dict]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages), {"format": "pdf", "pages": len(pages), "sections_read": len([page for page in pages if page.strip()])}
        except Exception:
            raw = path.read_bytes()
            return FileAgentService._printable_strings(raw), {"format": "pdf", "pages": 0, "sections_read": 1, "quality": "fallback_printable_strings"}

    @staticmethod
    def _extract_docx(path: Path) -> tuple[str, dict]:
        texts = []
        tables = 0
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.startswith("word/") and name.endswith(".xml"):
                    root = ElementTree.fromstring(archive.read(name))
                    for node in root.iter():
                        tag = node.tag.rsplit("}", 1)[-1]
                        if tag == "t" and node.text:
                            texts.append(node.text)
                        elif tag == "tbl":
                            tables += 1
        return " ".join(texts), {"format": "docx", "tables": tables}

    @staticmethod
    def _extract_xlsx(path: Path) -> tuple[str, dict]:
        shared = []
        rows = []
        sheets = 0
        with zipfile.ZipFile(path) as archive:
            if "xl/sharedStrings.xml" in archive.namelist():
                root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
                for item in root.iter():
                    if item.tag.rsplit("}", 1)[-1] == "t" and item.text:
                        shared.append(item.text)
            for name in archive.namelist():
                if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                    sheets += 1
                    root = ElementTree.fromstring(archive.read(name))
                    for row in root.iter():
                        if row.tag.rsplit("}", 1)[-1] != "row":
                            continue
                        values = []
                        for cell in row:
                            if cell.tag.rsplit("}", 1)[-1] != "c":
                                continue
                            value_node = next((child for child in cell if child.tag.rsplit("}", 1)[-1] == "v"), None)
                            if value_node is None or value_node.text is None:
                                continue
                            if cell.attrib.get("t") == "s" and value_node.text.isdigit():
                                index = int(value_node.text)
                                values.append(shared[index] if index < len(shared) else value_node.text)
                            else:
                                values.append(value_node.text)
                        if values:
                            rows.append(values)
                        if len(rows) >= 30:
                            break
        columns = rows[0] if rows else []
        return "\n".join(", ".join(row) for row in rows), {"format": "xlsx", "sheets": sheets, "columns": columns}

    @staticmethod
    def _extract_epub(path: Path) -> tuple[str, dict]:
        texts = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith((".xhtml", ".html", ".htm")):
                    parser = _HTMLTextParser()
                    parser.feed(archive.read(name).decode("utf-8", errors="replace"))
                    texts.append(parser.text())
        return "\n".join(texts), {"format": "epub", "documents": len(texts)}

    @staticmethod
    def _extract_binary_strings(path: Path) -> str:
        return FileAgentService._printable_strings(path.read_bytes()[:5_000_000])

    @staticmethod
    def _printable_strings(raw: bytes) -> str:
        text = raw.decode("utf-8", errors="ignore")
        chunks = re.findall(r"[^\x00-\x1f\x7f]{20,}", text)
        return "\n".join(chunk.strip() for chunk in chunks[:200])

    @staticmethod
    def _code_analysis(text: str, suffix: str) -> dict:
        if suffix == ".py":
            functions = re.findall(r"^\s*def\s+([A-Za-z_]\w*)", text, flags=re.M)
            classes = re.findall(r"^\s*class\s+([A-Za-z_]\w*)", text, flags=re.M)
            comments = re.findall(r"^\s*#\s*(.+)", text, flags=re.M)[:20]
            language = "python"
        elif suffix == ".js":
            functions = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)|(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\(", text)
            functions = [a or b for a, b in functions]
            classes = re.findall(r"\bclass\s+([A-Za-z_$][\w$]*)", text)
            comments = re.findall(r"//\s*(.+)", text)[:20]
            language = "javascript"
        elif suffix == ".css":
            functions = []
            classes = re.findall(r"\.([A-Za-z_][\w-]*)", text)[:50]
            comments = re.findall(r"/\*\s*(.*?)\s*\*/", text, flags=re.S)[:20]
            language = "css"
        else:
            functions = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)", text)
            classes = re.findall(r"\bclass=[\"']([^\"']+)", text)[:50]
            comments = re.findall(r"<!--\s*(.*?)\s*-->", text, flags=re.S)[:20]
            language = "html"
        return {"language": language, "functions": functions[:50], "classes": classes[:50], "comments": [" ".join(c.split()) for c in comments]}

    def _resolve_path(self, value: str | Path) -> Path:
        raw = str(value or "").strip().strip('"')
        if not raw:
            raise ValueError("Kein Dateipfad angegeben.")
        path = Path(raw)
        if not path.is_absolute():
            path = self.root / path
        try:
            resolved = path.resolve()
        except OSError as exc:
            raise ValueError(str(exc)) from exc
        if not any(self._is_relative_to(resolved, root) for root in self._allowed_roots()):
            raise ValueError(f"Pfad ist nicht freigegeben: {resolved}")
        return resolved

    def _allowed_roots(self) -> list[Path]:
        roots = []
        for item in self.config.get("allowed_roots", []):
            root = (self.root / str(item)).resolve() if not Path(str(item)).is_absolute() else Path(str(item)).resolve()
            roots.append(root)
        return roots or [self.root]

    @staticmethod
    def _is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def _hash_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def _log(self, entry: dict) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), **entry}, ensure_ascii=False) + "\n")

    def _error(self, path: str, error: str) -> dict:
        self._last_errors.append(f"{path}: {error}" if path else error)
        self._last_learning_success = False
        self._log({"path": path, "error": error, "status": "error"})
        self._emit_event("FILE_READ_FAILED", path, {"error": error}, severity="medium")
        return {"ok": False, "path": path, "error": error, "message": f"Datei konnte nicht gelesen werden: {error}"}

    @staticmethod
    def _extract_path(text: str, folder: bool = False) -> str:
        quoted = re.search(r'"([^"]+)"|\'([^\']+)\'', text or "")
        if quoted:
            return quoted.group(1) or quoted.group(2)
        windows_path = FileAgentService.WINDOWS_PATH_PATTERN.search(text or "")
        if windows_path:
            return windows_path.group(0).rstrip(".,;:!?)]}")
        suffix_path = FileAgentService.FILE_SUFFIX_PATTERN.search(text or "")
        if suffix_path:
            return suffix_path.group(1).rstrip(".,;:!?)]}")
        keyword = "ordner" if folder else "datei"
        match = re.search(rf"{keyword}\s+(.+)$", text or "", flags=re.I)
        if match:
            return match.group(1).strip()
        match = re.search(r"lernquelle\s+(.+)$", text or "", flags=re.I)
        if match:
            return match.group(1).strip()
        return (text or "").split()[-1] if (text or "").split() else ""

    @staticmethod
    def _topic(text: str) -> str:
        cleaned = re.sub(r"\b(lies|lese|lerne|aus|dieser|diese|datei|öffne|oeffne|analysiere|importiere|ins|wissen|als|lernquelle|pdf)\b", " ", text or "", flags=re.I)
        cleaned = re.sub(r'"[^"]+"|\'[^\']+\'|\S+[\\/]\S+|\S+\.\w{1,5}",?', " ", cleaned)
        return " ".join(cleaned.split())[:160] or "FileAgent-Lernquelle"

    @staticmethod
    def _summary(text: str) -> str:
        clean = " ".join((text or "").split())
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        selected = [sentence for sentence in sentences if 30 <= len(sentence) <= 500][:4]
        return " ".join(selected)[:900] if selected else clean[:900]

    @staticmethod
    def _format_file(record: dict, stored: dict) -> str:
        analysis = record.get("analysis", {})
        return "\n".join([
            "FileAgent: Datei gelesen und als Lernquelle fuer Review gespeichert.",
            f"- Datei: {record['file_name']}",
            f"- Pfad: {record['path']}",
            f"- Typ: {record['file_type']}",
            f"- Größe: {record['size_bytes']} Bytes",
            f"- Hash: {record['sha256']}",
            f"- gelesene Seiten/Abschnitte: {analysis.get('pages', 0) or '-'} / {analysis.get('sections_read', record.get('sections_read', 1))}",
            f"- Lernstatus: {record['learning_status']}",
            f"- Duplikat: {'ja' if stored.get('duplicate') else 'nein'}",
            f"- Lernübergabe erfolgreich: {'ja' if stored.get('learning_handoff_success') else 'nein'}",
            f"- Kurzinhalt: {record['summary']}",
        ])

    def _emit_event(
        self,
        event_type: str,
        path: str,
        payload: dict | None = None,
        severity: str = "info",
        affected_path: str = "",
    ) -> None:
        engine = self.canonical_engine
        if not engine:
            return
        try:
            engine.ingest(
                event_type=event_type,
                source_component="file_agent",
                affected_path=affected_path or path,
                affected_object_id=path,
                severity=severity,
                payload={"path": path, **(payload or {})},
                provenance={"agent": "FileAgentService", "version": self.VERSION},
                governance_context={"file_learning": True, "requires_review": event_type == "FILE_LEARNED"},
            )
        except Exception as exc:
            self._last_errors.append(f"Canonical Event Bus: {exc}")

    @staticmethod
    def _format_folder(base: Path, read: list[dict], skipped: list[dict], errors: list[dict], recursive: bool) -> str:
        lines = [
            "FileAgent Ordnerimport abgeschlossen.",
            f"- Ordner: {base}",
            f"- rekursiv: {'ja' if recursive else 'nein'}",
            f"- gelesen: {len(read)}",
            f"- übersprungen: {len(skipped)}",
            f"- fehlerhaft: {len(errors)}",
        ]
        for item in read[:10]:
            lines.append(f"- gelesen: {item.get('file_name')} ({item.get('file_type')})")
        for item in skipped[:5]:
            lines.append(f"- übersprungen: {item.get('path')} | {item.get('reason')}")
        for item in errors[:5]:
            lines.append(f"- Fehler: {item.get('path')} | {item.get('error')}")
        return "\n".join(lines)
