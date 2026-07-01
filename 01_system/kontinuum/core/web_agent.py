from __future__ import annotations

import hashlib
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from kontinuum.version import APP_VERSION
from .continuous_canonical_engine import ContinuousCanonicalEngine


class _WebPageParser(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer", "form", "aside"}
    TEXT_TAGS = {"title", "h1", "h2", "h3", "h4", "p", "li", "pre", "code"}

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.skip_depth = 0
        self.capture: str | None = None
        self.title = ""
        self.headings: list[str] = []
        self.paragraphs: list[str] = []
        self.lists: list[str] = []
        self.code_blocks: list[str] = []
        self.links: list[dict] = []
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        tag = tag.casefold()
        attributes = dict(attrs)
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if tag == "a":
            href = attributes.get("href", "").strip()
            if href:
                absolute, _ = urldefrag(urljoin(self.base_url, href))
                if absolute.startswith(("http://", "https://")):
                    self.links.append({"url": absolute, "text": ""})
        if tag in self.TEXT_TAGS:
            self.capture = tag
            self._buffer = []

    def handle_endtag(self, tag: str):
        tag = tag.casefold()
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == self.capture:
            text = " ".join(" ".join(self._buffer).split()).strip()
            if text:
                if tag == "title":
                    self.title = text
                elif tag.startswith("h"):
                    self.headings.append(text)
                elif tag == "li":
                    self.lists.append(text)
                elif tag in {"pre", "code"}:
                    self.code_blocks.append(text)
                else:
                    self.paragraphs.append(text)
            self.capture = None
            self._buffer = []

    def handle_data(self, data: str):
        if self.skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self.capture:
            self._buffer.append(text)
        if self.links:
            self.links[-1]["text"] = " ".join((self.links[-1].get("text", ""), text)).strip()[:160]

    def main_text(self) -> str:
        parts = [*self.headings, *self.paragraphs, *self.lists, *self.code_blocks]
        return "\n".join(part for part in parts if part).strip()


class WebAgentService:
    VERSION = "1.0"
    URL_PATTERN = re.compile(r"https?://[^\s<>()\"']+", re.I)
    USER_AGENT = f"Projekt-Kontinuum/{APP_VERSION} WebAgent/{VERSION}"
    DOCUMENT_SUFFIXES = {
        ".7z", ".avi", ".bin", ".dmg", ".doc", ".docx", ".exe", ".gz", ".iso",
        ".mp3", ".mp4", ".pdf", ".ppt", ".pptx", ".rar", ".tar", ".tgz", ".xls",
        ".xlsx", ".zip",
    }
    PYTHON_DOCS_PREFERRED_PREFIXES = (
        "/3/tutorial/",
        "/3/library/",
        "/3/reference/",
        "/3/howto/",
        "/3/installing/",
        "/3/using/",
        "/3/faq/",
    )
    PYTHON_DOCS_PREFERRED_EXACT = {"/3/", "/3/glossary.html"}
    PYTHON_VERSION_PATH = re.compile(r"^/3\.\d+(/|$)")

    DEFAULT_CONFIG = {
        "enabled": True,
        "mode": "diagnostic_review_only",
        "request_timeout_seconds": 8,
        "max_response_bytes": 1200000,
        "max_pages": 20,
        "documentation_max_pages": 50,
        "max_depth": 2,
        "documentation_max_depth": 3,
        "same_domain_preferred": True,
        "respect_robots_txt": True,
        "no_direct_memory_write": True,
        "no_automatic_canonical_adoption": True,
        "write_review_queue": True,
        "providers": ["direct_http_get", "html_text_extractor", "controlled_crawler"],
    }

    def __init__(self, path_tools, storage=None, continuous_learning=None, fetcher=None, canonical_engine=None):
        self.path_tools = path_tools
        self.storage = storage
        self.continuous_learning = continuous_learning
        self.fetcher = fetcher or self._http_get
        self.canonical_engine = canonical_engine
        self.config_path = path_tools.paths()["config"] / "web_agent_1_0.json"
        self.config = self._load_config()
        data = path_tools.paths()["data"]
        self.sources_dir = data / "web_agent_sources"
        self.queue_dir = data / "internet_learning_queue"
        self.review_dir = data / "internet_learning_review"
        self.progress_dir = data / "web_agent_progress"
        self.log_path = path_tools.paths()["logs"] / "web_agent_1_0.jsonl"
        for path in (self.sources_dir, self.queue_dir, self.review_dir, self.progress_dir, self.log_path.parent):
            path.mkdir(parents=True, exist_ok=True)
        self._last_url = ""
        self._last_fetch = ""
        self._last_errors: list[str] = []

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    @classmethod
    def urls_in(cls, text: str) -> list[str]:
        urls = []
        for match in cls.URL_PATTERN.findall(text or ""):
            url = match.rstrip(".,;:!?)]}»”'")
            if url not in urls:
                urls.append(url)
        return urls

    @classmethod
    def is_web_command(cls, text: str) -> bool:
        if not cls.urls_in(text):
            return False
        lower = (text or "").casefold()
        markers = (
            "lerne", "lies", "lese", "öffne", "oeffne", "nutze", "webseite",
            "url", "link", "crawl", "alle links", "nacheinander alle links",
        )
        return any(marker in lower for marker in markers) or True

    def status(self) -> dict:
        return {
            "active": bool(self.config.get("enabled", False)),
            "mode": self.config.get("mode", "diagnostic_review_only"),
            "last_fetch": self._last_fetch,
            "last_url": self._last_url,
            "last_errors": self._last_errors[-5:],
            "stored_web_sources": len(list(self.sources_dir.glob("*.json"))),
            "crawl_limits": {
                "max_pages": int(self.config.get("max_pages", 20)),
                "max_depth": int(self.config.get("max_depth", 2)),
                "same_domain_preferred": bool(self.config.get("same_domain_preferred", True)),
                "respect_robots_txt": bool(self.config.get("respect_robots_txt", True)),
            },
            "providers": list(self.config.get("providers", [])),
            "review_queue": str(self.queue_dir),
        }

    def format_status(self) -> str:
        status = self.status()
        errors = "; ".join(status["last_errors"]) if status["last_errors"] else "-"
        return "\n".join([
            "WebAgent 1.0 Status:",
            f"- WebAgent aktiv: {'ja' if status['active'] else 'nein'}",
            f"- Modus: {status['mode']}",
            f"- letzter Abruf: {status['last_fetch'] or '-'}",
            f"- letzte URL: {status['last_url'] or '-'}",
            f"- letzte Fehler: {errors}",
            f"- gespeicherte Webquellen: {status['stored_web_sources']}",
            f"- Crawl-Limits: max_pages={status['crawl_limits']['max_pages']}, max_depth={status['crawl_limits']['max_depth']}",
            "- verfügbare Provider: " + ", ".join(status["providers"]),
        ])

    def handle_command(self, text: str) -> dict:
        urls = self.urls_in(text)
        if not urls:
            return {"ok": False, "message": "Keine URL im WebAgent-Auftrag erkannt."}
        lower = text.casefold()
        crawl = any(marker in lower for marker in ("alle links", "nacheinander alle links", "öffne alle", "oeffne alle", "crawl"))
        if crawl:
            return self.crawl(urls[0], command=text)
        result = self.learn_url(urls[0], topic=self._topic(text), command=text)
        return {"ok": result.get("ok", False), "mode": "single_url", "pages": [result], "message": self._format_single(result)}

    def learn_url(self, url: str, topic: str = "", command: str = "", depth: int = 0) -> dict:
        if not self.config.get("enabled", False):
            return {"ok": False, "url": url, "error": "WebAgent ist deaktiviert."}
        if self._blocked_download(url):
            return self._skip(url, "Große oder binäre Downloads werden ohne Freigabe nicht abgerufen.", event_type="WEB_SOURCE_SKIPPED")
        if self.config.get("respect_robots_txt", True) and not self._robots_allowed(url):
            return self._skip(url, "robots.txt blockiert den Abruf.", event_type="WEB_ROBOTS_BLOCKED")
        self._emit_event("WEB_FETCH_STARTED", url, {"depth": depth, "command": command})
        fetched = self.fetcher(url, int(self.config.get("request_timeout_seconds", 8)), int(self.config.get("max_response_bytes", 1200000)))
        if fetched.get("error"):
            self._emit_event("WEB_FETCH_FAILED", url, {"depth": depth, "error": fetched["error"]}, severity="medium")
            return self._error(url, fetched["error"])
        self._emit_event("WEB_FETCH_COMPLETED", url, {
            "depth": depth,
            "http_status": fetched.get("http_status", 0),
            "bytes": fetched.get("bytes", 0),
        })
        page = self._extract(fetched)
        page["topic"] = topic or page.get("title") or url
        page["command"] = command
        page["depth"] = depth
        stored = self._store(page)
        self._last_url = url
        self._last_fetch = page["retrieved_at"]
        return {**page, **stored, "ok": True}

    def crawl(self, start_url: str, max_pages: int | None = None, max_depth: int | None = None, command: str = "") -> dict:
        doc_scope = self._documentation_scope(start_url, command)
        default_pages = self.config.get("documentation_max_pages", 50) if doc_scope["is_documentation"] else self.config.get("max_pages", 20)
        default_depth = self.config.get("documentation_max_depth", 3) if doc_scope["is_documentation"] else self.config.get("max_depth", 2)
        hard_page_limit = 50 if doc_scope["is_documentation"] else 20
        hard_depth_limit = 3 if doc_scope["is_documentation"] else 2
        limit_pages = max(1, min(int(max_pages or default_pages), hard_page_limit))
        limit_depth = max(0, min(int(max_depth if max_depth is not None else default_depth), hard_depth_limit))
        root_domain = urlparse(start_url).netloc.casefold()
        queue = deque([(start_url, 0, 0)])
        seen = set()
        pages = []
        skipped: list[dict] = []
        topics = set()
        self._emit_event("WEB_CRAWL_STARTED", start_url, {
            "max_pages": limit_pages,
            "max_depth": limit_depth,
            "documentation_plan": doc_scope["is_documentation"],
            "scope_prefix": doc_scope["path_prefix"],
        })
        while queue and len(pages) < limit_pages:
            url, depth, _priority = queue.popleft()
            if url in seen or depth > limit_depth:
                continue
            seen.add(url)
            result = self.learn_url(url, topic=f"Crawl {start_url}", command="crawl", depth=depth)
            pages.append(result)
            if result.get("ok"):
                topics.update(self._topics_from_page(result, doc_scope))
            if not result.get("ok") or depth >= limit_depth:
                continue
            accepted, skipped_links = self._scoped_links(result.get("links", []), root_domain, doc_scope)
            skipped.extend(skipped_links)
            for skipped_link in skipped_links:
                self._emit_event("WEB_SOURCE_SKIPPED", skipped_link["url"], {
                    "start_url": start_url,
                    "reason": skipped_link["reason"],
                    "from_url": url,
                })
            for link, priority in accepted:
                if link not in seen and len(seen) + len(queue) < limit_pages * 3:
                    queue.append((link, depth + 1, priority))
            queue = deque(sorted(queue, key=lambda item: (item[2], item[1], item[0])))
            self._save_crawl_progress(start_url, pages, skipped, queue, limit_pages, limit_depth, doc_scope)
        ok_pages = [page for page in pages if page.get("ok")]
        if queue:
            for url, depth, _priority in list(queue)[:100]:
                skipped.append({"url": url, "reason": "Crawl-Limit erreicht", "depth": depth})
        progress = self._save_crawl_progress(start_url, pages, skipped, queue, limit_pages, limit_depth, doc_scope)
        result = {
            "ok": bool(ok_pages),
            "mode": "crawl",
            "start_url": start_url,
            "visited": len(pages),
            "stored": len(ok_pages),
            "max_pages": limit_pages,
            "max_depth": limit_depth,
            "documentation_plan": doc_scope["is_documentation"],
            "topics": sorted(topics),
            "skipped": skipped,
            "progress_file": str(progress),
            "pages": pages,
            "message": self._format_crawl(start_url, pages, skipped, sorted(topics), limit_pages, limit_depth, progress, doc_scope),
        }
        self._emit_event("WEB_CRAWL_COMPLETED", start_url, {
            "visited": len(pages),
            "stored": len(ok_pages),
            "skipped": len(skipped),
            "topics": sorted(topics),
            "progress_file": str(progress),
        })
        return result

    def _http_get(self, url: str, timeout: int, max_bytes: int) -> dict:
        request = Request(url, headers={"User-Agent": self.USER_AGENT, "Accept": "text/html,text/plain,application/xhtml+xml"})
        try:
            with urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get("content-type", "")
                charset = response.headers.get_content_charset() or "utf-8"
                raw = response.read(max(1, max_bytes))
                status = int(getattr(response, "status", 200))
        except HTTPError as exc:
            return {"url": url, "error": f"HTTP-Fehler {exc.code}: {exc.reason}", "http_status": exc.code}
        except URLError as exc:
            return {"url": url, "error": f"Netzwerkfehler: {exc.reason}"}
        except OSError as exc:
            return {"url": url, "error": f"Abruffehler: {exc}"}
        return {
            "url": url,
            "http_status": status,
            "content_type": content_type,
            "raw_text": raw.decode(charset, errors="replace"),
            "bytes": len(raw),
        }

    def _extract(self, fetched: dict) -> dict:
        url = fetched["url"]
        raw_text = str(fetched.get("raw_text", ""))
        parser = _WebPageParser(url)
        if "html" in str(fetched.get("content_type", "")).casefold() or "<html" in raw_text[:500].casefold():
            parser.feed(raw_text)
            text = parser.main_text()
            title = parser.title
            links = self._dedupe_links(parser.links)
            headings = parser.headings
            code_blocks = parser.code_blocks[:20]
        else:
            text = " ".join(raw_text.split())
            title = ""
            links = []
            headings = []
            code_blocks = []
        digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        return {
            "url": url,
            "http_status": fetched.get("http_status", 0),
            "content_type": fetched.get("content_type", ""),
            "title": title or url,
            "headings": headings[:30],
            "text": text,
            "links": links,
            "code_blocks": code_blocks,
            "retrieved_at": now,
            "sha256": digest,
            "bytes": int(fetched.get("bytes", len(raw_text.encode("utf-8", errors="replace")))),
            "summary": self._summary(text),
            "learning_summary": self._learning_summary(title or url, text),
            "source": "web_agent_1_0",
        }

    def _store(self, page: dict) -> dict:
        key = hashlib.sha256(f"{page['url']}|{page['sha256']}".encode("utf-8")).hexdigest()
        source_file = self.sources_dir / f"{key}.json"
        duplicate = source_file.exists()
        record = {
            "url": page["url"],
            "title": page["title"],
            "topic": page.get("topic", ""),
            "retrieved_at": page["retrieved_at"],
            "sha256": page["sha256"],
            "summary": page["summary"],
            "learning_summary": page["learning_summary"],
            "http_status": page["http_status"],
            "links": page["links"],
            "review_required": True,
            "write_to_memory_directly": False,
            "status": "queued_for_review",
            "policy": "web_agent_1_0",
        }
        if not duplicate:
            source_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            queue_file = self.queue_dir / f"webagent_{key}.json"
            review_file = self.review_dir / f"webagent_{key}.json"
            queue_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            review_file.write_text(json.dumps({**record, "review_status": "pending"}, ensure_ascii=False, indent=2), encoding="utf-8")
            if self.storage and hasattr(self.storage, "add_source"):
                source_id = self.storage.add_source(page["url"], {**record, "agent": "web_agent"})
            else:
                source_id = None
            if self.continuous_learning and page.get("topic"):
                self.continuous_learning.add_task(page["topic"], [page["title"]], origin="web_agent")
        else:
            source_id = None
        self._log({**record, "duplicate": duplicate})
        stored = {"duplicate": duplicate, "source_record_id": source_id, "record_path": str(source_file)}
        self._emit_event("WEB_SOURCE_LEARNED", page["url"], {
            "title": page["title"],
            "topic": page.get("topic", ""),
            "record_path": str(source_file),
            "duplicate": duplicate,
            "review_required": True,
            "internet_learning": True,
            "reviewed": False,
        }, affected_path=str(source_file))
        return stored

    def _log(self, entry: dict) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), **entry}, ensure_ascii=False) + "\n")

    def _emit_event(
        self,
        event_type: str,
        url: str,
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
                source_component="web_agent",
                affected_path=affected_path,
                affected_object_id=url,
                severity=severity,
                payload={"url": url, **(payload or {})},
                provenance={"agent": "WebAgentService", "version": self.VERSION},
                governance_context={"internet_learning": True, "requires_review": event_type == "WEB_SOURCE_LEARNED"},
            )
        except Exception as exc:
            self._last_errors.append(f"Canonical Event Bus: {exc}")

    def _error(self, url: str, error: str) -> dict:
        self._last_url = url
        self._last_fetch = datetime.now(timezone.utc).isoformat()
        self._last_errors.append(f"{url}: {error}")
        self._log({"url": url, "error": error, "status": "error"})
        return {"ok": False, "url": url, "error": error}

    def _skip(self, url: str, reason: str, event_type: str = "WEB_SOURCE_SKIPPED") -> dict:
        self._last_url = url
        self._last_fetch = datetime.now(timezone.utc).isoformat()
        self._last_errors.append(f"{url}: {reason}")
        self._log({"url": url, "skip_reason": reason, "status": "skipped"})
        self._emit_event(event_type, url, {"reason": reason})
        return {"ok": False, "url": url, "error": reason, "skipped": True, "skip_reason": reason}

    def _robots_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.hostname in {"localhost", "127.0.0.1"}:
            return True
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
            return parser.can_fetch(self.USER_AGENT, url)
        except Exception:
            return True

    def _blocked_download(self, url: str) -> bool:
        return Path(urlparse(url).path).suffix.casefold() in self.DOCUMENT_SUFFIXES

    @staticmethod
    def _dedupe_links(links: list[dict]) -> list[dict]:
        seen = set()
        result = []
        for link in links:
            url = link.get("url", "")
            if not url or url in seen:
                continue
            seen.add(url)
            result.append({"url": url, "text": link.get("text", "")})
        return result[:200]

    @staticmethod
    def _internal_links(links: list[dict], root_domain: str) -> list[str]:
        result = []
        for link in links:
            url = link.get("url", "")
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"}:
                continue
            if parsed.netloc.casefold() != root_domain:
                continue
            if Path(parsed.path).suffix.casefold() in WebAgentService.DOCUMENT_SUFFIXES:
                continue
            if url not in result:
                result.append(url)
        return result

    @classmethod
    def _documentation_scope(cls, start_url: str, command: str = "") -> dict:
        parsed = urlparse(start_url)
        path = parsed.path or "/"
        lower_command = (command or "").casefold()
        is_python_docs = parsed.netloc.casefold() == "docs.python.org" and (path == "/3/" or path.startswith("/3/"))
        return {
            "is_documentation": is_python_docs,
            "domain": parsed.netloc.casefold(),
            "path_prefix": "/3/" if is_python_docs else "/",
            "allow_all_versions": "alle versionen" in lower_command or "versionsarchiv" in lower_command,
            "preferred_prefixes": cls.PYTHON_DOCS_PREFERRED_PREFIXES if is_python_docs else (),
            "preferred_exact": cls.PYTHON_DOCS_PREFERRED_EXACT if is_python_docs else set(),
        }

    @classmethod
    def _scoped_links(cls, links: list[dict], root_domain: str, scope: dict) -> tuple[list[tuple[str, int]], list[dict]]:
        accepted: list[tuple[str, int]] = []
        skipped: list[dict] = []
        for link in links:
            url = link.get("url", "")
            parsed = urlparse(url)
            path = parsed.path or "/"
            if parsed.scheme not in {"http", "https"}:
                skipped.append({"url": url, "reason": "Nicht unterstütztes URL-Schema"})
                continue
            if parsed.netloc.casefold() != root_domain:
                skipped.append({"url": url, "reason": "Außerhalb der Start-Domain"})
                continue
            if Path(path).suffix.casefold() in cls.DOCUMENT_SUFFIXES:
                skipped.append({"url": url, "reason": "Binärer oder großer Download"})
                continue
            if scope.get("is_documentation"):
                if cls.PYTHON_VERSION_PATH.match(path) and not scope.get("allow_all_versions"):
                    skipped.append({"url": url, "reason": "Versionsarchiv ohne ausdrücklichen Auftrag 'alle Versionen'"})
                    continue
                if not (path == "/3/" or path.startswith("/3/")):
                    skipped.append({"url": url, "reason": "Außerhalb der aktuellen /3/-Dokumentation"})
                    continue
            priority = cls._link_priority(url, scope)
            if (url, priority) not in accepted:
                accepted.append((url, priority))
        return sorted(accepted, key=lambda item: (item[1], item[0])), skipped

    @classmethod
    def _link_priority(cls, url: str, scope: dict) -> int:
        if not scope.get("is_documentation"):
            return 20
        path = urlparse(url).path or "/"
        if path in scope.get("preferred_exact", set()):
            return 0
        for index, prefix in enumerate(scope.get("preferred_prefixes", ())):
            if path.startswith(prefix):
                return 1 + index
        return 30

    @classmethod
    def _topics_from_page(cls, page: dict, scope: dict) -> list[str]:
        topics = []
        if scope.get("is_documentation"):
            path = urlparse(page.get("url", "")).path or ""
            mapping = {
                "/3/tutorial/": "tutorial",
                "/3/library/": "library",
                "/3/reference/": "reference",
                "/3/howto/": "howto",
                "/3/installing/": "installing",
                "/3/using/": "using",
                "/3/faq/": "faq",
                "/3/glossary.html": "glossary",
            }
            for prefix, topic in mapping.items():
                if path == prefix or path.startswith(prefix):
                    topics.append(topic)
        for heading in page.get("headings", [])[:5]:
            if heading:
                topics.append(heading[:80])
        return topics

    def _save_crawl_progress(
        self,
        start_url: str,
        pages: list[dict],
        skipped: list[dict],
        queue: deque,
        max_pages: int,
        max_depth: int,
        scope: dict,
    ) -> Path:
        key = hashlib.sha256(start_url.encode("utf-8")).hexdigest()[:16]
        path = self.progress_dir / f"crawl_{key}.json"
        record = {
            "start_url": start_url,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "documentation_plan": scope.get("is_documentation", False),
            "scope": {
                "domain": scope.get("domain", ""),
                "path_prefix": scope.get("path_prefix", ""),
                "allow_all_versions": scope.get("allow_all_versions", False),
            },
            "limits": {"max_pages": max_pages, "max_depth": max_depth},
            "learned_pages": [
                {"url": page.get("url", ""), "title": page.get("title", ""), "record_path": page.get("record_path", "")}
                for page in pages if page.get("ok")
            ],
            "skipped_pages": skipped,
            "next_queue": [{"url": item[0], "depth": item[1], "priority": item[2]} for item in list(queue)[:100]],
        }
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _topic(text: str) -> str:
        cleaned = WebAgentService.URL_PATTERN.sub("", text or "")
        cleaned = re.sub(r"\b(lerne|lies|lese|öffne|oeffne|nutze|auch|hier|zum|lernen|webseite|url)\b", " ", cleaned, flags=re.I)
        return " ".join(cleaned.split())[:160] or "WebAgent-Lernquelle"

    @staticmethod
    def _summary(text: str) -> str:
        clean = " ".join((text or "").split())
        return clean[:700]

    @staticmethod
    def _learning_summary(title: str, text: str) -> str:
        clean = " ".join((text or "").split())
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        selected = [sentence for sentence in sentences if 40 <= len(sentence) <= 500][:5]
        body = " ".join(selected) if selected else clean[:1000]
        return f"{title}: {body}"[:1600]

    @staticmethod
    def _format_single(result: dict) -> str:
        if not result.get("ok"):
            return f"WebAgent: Abruf fehlgeschlagen: {result.get('url')}\nGrund: {result.get('error')}"
        return "\n".join([
            "WebAgent: URL abgerufen und fuer Review gespeichert.",
            f"- URL: {result['url']}",
            f"- HTTP: {result.get('http_status', 0)}",
            f"- Titel: {result.get('title', '')}",
            f"- Hash: {result.get('sha256', '')}",
            f"- erkannte Links: {len(result.get('links', []))}",
            f"- Duplikat: {'ja' if result.get('duplicate') else 'nein'}",
            f"- Lernzusammenfassung: {result.get('learning_summary', '')[:700]}",
        ])

    @staticmethod
    def _format_crawl(
        start_url: str,
        pages: list[dict],
        skipped: list[dict],
        topics: list[str],
        max_pages: int,
        max_depth: int,
        progress: Path,
        scope: dict,
    ) -> str:
        ok_pages = [page for page in pages if page.get("ok")]
        learned = [f"  - {page.get('url')} ({page.get('title', '')})" for page in ok_pages[:20]]
        skipped_lines = [f"  - {item.get('url')} | Grund: {item.get('reason', '-')}" for item in skipped[:20]]
        next_hint = "Kapitel mit Priorität fortsetzen: tutorial, library, reference, howto, installing, using, faq, glossary."
        if not scope.get("is_documentation"):
            next_hint = "Fortsetzung aus der gespeicherten Crawl-Queue mit denselben Limits."
        lines = [
            "WebAgent Crawl abgeschlossen.",
            f"- Start-URL: {start_url}",
            f"- Modus: {'Dokumentationsplan' if scope.get('is_documentation') else 'kontrollierter Crawl'}",
            f"- tatsächlich gelernte Seiten: {len(ok_pages)}",
            *learned,
            f"- übersprungene Seiten: {len(skipped)}",
            *skipped_lines,
            f"- erkannte Themenbereiche: {', '.join(topics[:20]) if topics else '-'}",
            f"- gespeicherte Lernobjekte: {len(ok_pages)} Webquellen/Review-Objekte",
            f"- Limits: max_pages={max_pages}, max_depth={max_depth}",
            f"- Fortschritt: {progress}",
            f"- nächste empfohlene Crawl-Fortsetzung: {next_hint}",
        ]
        return "\n".join(lines)
