from __future__ import annotations

import html
import json
import re
import queue
import shutil
import subprocess
import threading
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, urlencode, unquote, urlparse
from urllib.request import Request, urlopen

from kontinuum.core.semantic_result_validator import SemanticResultValidator
from kontinuum.version import APP_VERSION


class _DuckDuckGoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results: list[dict] = []
        self._current: dict | None = None
        self._snippet_target: dict | None = None
        self._capture_title = False
        self._capture_snippet = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())
        if tag == "a" and "result__a" in classes:
            self._current = {"title": "", "url": attributes.get("href", ""), "snippet": ""}
            self._capture_title = True
        elif self._current is not None and ("result__snippet" in classes or "result-snippet" in classes):
            self._capture_snippet = True
            self._snippet_target = self._current
        elif self.results and ("result__snippet" in classes or "result-snippet" in classes):
            self._capture_snippet = True
            self._snippet_target = self.results[-1]

    def handle_endtag(self, tag):
        if tag == "a" and self._capture_title:
            self._capture_title = False
            if self._current and self._current["title"] and self._current["url"]:
                self.results.append(self._current)
                self._current = None
        elif self._capture_snippet and tag in {"a", "div", "span"}:
            self._capture_snippet = False
            self._snippet_target = None

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self._capture_title and self._current is not None:
            self._current["title"] += (" " if self._current["title"] else "") + text
        elif self._capture_snippet and self._snippet_target is not None:
            self._snippet_target["snippet"] += (" " if self._snippet_target["snippet"] else "") + text


class SearchEngineTools:
    MAX_RUNTIME = 8
    DEFAULT_CONFIG = {
        "enabled": True,
        "provider": "duckduckgo_html",
        "fallback_providers": ["duckduckgo_lite"],
        "provider_order": [
            "local_knowledge",
            "notebook_knowledge",
            "university_sources",
            "arxiv",
            "semantic_scholar",
            "brave_search",
            "duckduckgo_html",
            "duckduckgo_lite",
        ],
        "base_url": "https://html.duckduckgo.com/html/",
        "fallback_base_urls": {
            "duckduckgo_lite": "https://lite.duckduckgo.com/lite/",
            "wikipedia": "https://de.wikipedia.org/w/api.php",
            "arxiv": "https://export.arxiv.org/api/query",
            "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search",
            "brave_search": "https://api.search.brave.com/res/v1/web/search",
        },
        "brave_api_key": "",
        "language": "de-de",
        "safe_search": "moderate",
        "timeout_seconds": 5,
        "max_results": 8,
        "auto_research_questions": True,
        "university_domains": ["site:.edu", "site:.ac.uk", "site:.edu.au", "site:.de university"],
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "24_config" / "search_engine.json"
        self.config = self._load_config()
        self.local_router = None
        self.validator = SemanticResultValidator()

    def bind_local_router(self, router) -> None:
        self.local_router = router

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
                if "provider_order" not in loaded and any(
                    key in loaded for key in ("provider", "fallback_providers", "base_url", "fallback_base_urls")
                ):
                    config["provider_order"] = []
        except (OSError, ValueError):
            pass
        return config

    def status(self) -> dict:
        if not self.config["enabled"]:
            return {"available": False, "enabled": False, "message": "Suchmaschinen-Connector ist deaktiviert."}
        return {
            "available": True,
            "enabled": True,
            "provider": self.config["provider"],
            "provider_order": self._provider_chain(),
            "message": "Suchmaschinen-Connector aktiv: " + " -> ".join(self._provider_chain()) + ".",
        }

    def search(self, query: str, limit: int | None = None, mode: str = "default") -> dict:
        term = " ".join((query or "").split())
        if not term:
            return {"ok": False, "query": "", "results": [], "error": "Leere Suchanfrage."}
        if not self.config["enabled"]:
            return {"ok": False, "query": term, "results": [], "error": "Suchmaschinen-Connector ist deaktiviert."}
        maximum = max(1, min(int(limit or self.config["max_results"]), 20))
        providers = self._providers_for_mode(mode)
        errors = []
        collected = []
        seen_urls = set()
        deadline = time.monotonic() + self.MAX_RUNTIME
        for provider in dict.fromkeys(providers):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                errors.append("Zeitbudget der Anbieterkette erreicht")
                break
            if provider in {"local_knowledge", "notebook_knowledge"}:
                result = self._search_local(term, maximum - len(collected), provider)
            elif provider == "university_sources":
                result = self._search_university(term, maximum - len(collected), remaining)
            elif provider in {"duckduckgo_html", "duckduckgo_lite"}:
                base_url = (
                    self.config.get("fallback_base_urls", {}).get("duckduckgo_html", self.config["base_url"])
                    if provider == "duckduckgo_html"
                    else self.config.get("fallback_base_urls", {}).get(provider, "")
                )
                if not base_url:
                    errors.append(f"{provider}: nicht konfiguriert")
                    continue
                provider_timeout = max(1, min(int(remaining), int(self.config["timeout_seconds"])))
                result = self._search_provider_bounded(term, maximum - len(collected), provider, base_url, provider_timeout)
            elif provider == "wikipedia":
                result = self._search_wikipedia(term, maximum - len(collected), remaining)
            elif provider == "arxiv":
                result = self._search_arxiv(term, maximum - len(collected), remaining)
            elif provider == "semantic_scholar":
                result = self._search_semantic_scholar(term, maximum - len(collected), remaining)
            elif provider == "brave_search":
                result = self._search_brave(term, maximum - len(collected), remaining)
            else:
                errors.append(f"{provider}: nicht konfiguriert")
                continue
            if result.get("ok"):
                for row in result.get("results", []):
                    threshold = 0.75 if term.casefold().startswith(("lerne ", "lernprojekt ")) else 0.65
                    if row.get("provider") not in {"local_knowledge", "notebook_knowledge"}:
                        validation = self.validator.validate(term, row, threshold)
                        if not validation["ok"]:
                            errors.append(f"{provider}: Treffer verworfen (Relevanz {validation['score']:.2f} < {threshold:.2f})")
                            continue
                        row = {**row, "semantic_relevance": validation["score"]}
                    key = row.get("url") or row.get("title")
                    if not key or key in seen_urls:
                        continue
                    seen_urls.add(key)
                    collected.append(row)
                    if len(collected) >= maximum:
                        return {
                            "ok": True,
                            "query": term,
                            "results": collected,
                            "provider": "search_provider_router",
                            "fallback_used": provider != providers[0],
                            "attempted_providers": list(dict.fromkeys(providers)),
                            "provider_order": list(dict.fromkeys(providers)),
                        }
                continue
            errors.append(f"{provider}: {result.get('error', 'Fehler')}")
        if collected:
            return {
                "ok": True,
                "query": term,
                "results": collected,
                "provider": "search_provider_router",
                "fallback_used": True,
                "attempted_providers": list(dict.fromkeys(providers)),
                "provider_order": list(dict.fromkeys(providers)),
            }
        return {"ok": False, "query": term, "results": [], "error": " | ".join(errors), "attempted_providers": providers}

    def _provider_chain(self) -> list[str]:
        configured = self.config.get("provider_order")
        if isinstance(configured, list) and configured:
            return [str(provider) for provider in configured if str(provider).strip()]
        return [self.config["provider"], *self.config.get("fallback_providers", [])]

    def _providers_for_mode(self, mode: str = "default") -> list[str]:
        providers = self._provider_chain()
        local = [provider for provider in providers if provider in {"local_knowledge", "notebook_knowledge"}]
        internet = [provider for provider in providers if provider not in {"local_knowledge", "notebook_knowledge"}]
        if mode == "local_only":
            return local or providers
        if mode == "internet_only":
            return internet or providers
        if mode in {"prefer_internet", "hybrid"}:
            return internet + local
        return providers

    def _search_local(self, term: str, maximum: int, provider: str) -> dict:
        if maximum <= 0:
            return {"ok": False, "query": term, "results": [], "error": "Trefferlimit erreicht."}
        if not self.local_router:
            return {"ok": False, "query": term, "results": [], "error": "Lokaler Suchrouter nicht angebunden."}
        try:
            result = self.local_router.search(term, limit=maximum)
        except Exception as exc:
            return {"ok": False, "query": term, "results": [], "error": str(exc)}
        areas = {"local_knowledge": ("04_knowledge", "03_memory", "06_learning", "22_project_chronicle", "32_data"),
                 "notebook_knowledge": ("sources", "questions", "knowledge_items")}
        allowed = areas.get(provider, ())
        rows = []
        for hit in result.get("hits", []):
            area = str(hit.get("area", ""))
            if allowed and not any(marker in area for marker in allowed):
                continue
            rows.append({
                "title": f"{provider}: {area}",
                "url": f"kontinuum://{provider}/{len(rows) + 1}",
                "snippet": hit.get("snippet", ""),
                "provider": provider,
            })
            if len(rows) >= maximum:
                break
        return {"ok": bool(rows), "query": term, "results": rows, "provider": provider} if rows else {
            "ok": False, "query": term, "results": [], "error": "Keine lokalen Treffer."
        }

    def _search_university(self, term: str, maximum: int, remaining: float) -> dict:
        domains = self.config.get("university_domains") or []
        if not domains:
            return {"ok": False, "query": term, "results": [], "error": "Keine Universitätsdomains konfiguriert."}
        query = f"{term} ({' OR '.join(domains[:4])})"
        return self._search_provider_bounded(
            query,
            maximum,
            "university_sources",
            self.config.get("base_url", ""),
            max(1, min(int(remaining), int(self.config["timeout_seconds"]))),
        )

    def _search_json_api_bounded(self, url: str, provider: str, timeout: int, parser) -> dict:
        completed: queue.Queue = queue.Queue(maxsize=1)

        def worker():
            completed.put(self._search_json_api(url, provider, timeout, parser))

        threading.Thread(target=worker, daemon=True, name=f"KontinuumSearchProvider-{provider}").start()
        try:
            return completed.get(timeout=timeout + 0.5)
        except queue.Empty:
            return {"ok": False, "query": "", "results": [], "error": f"Zeitlimit für {provider} erreicht."}

    def _search_json_api(self, url: str, provider: str, timeout: int, parser) -> dict:
        headers = {
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Projekt-Kontinuum/{APP_VERSION}",
            "Accept": "application/json,application/atom+xml,text/xml",
        }
        if provider == "brave_search":
            headers["X-Subscription-Token"] = str(self.config.get("brave_api_key", ""))
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                document = response.read(2_000_000).decode(charset, errors="replace")
        except HTTPError as exc:
            return {"ok": False, "query": "", "results": [], "error": f"{provider} HTTP-Fehler {exc.code}: {exc.reason}"}
        except URLError as exc:
            return {"ok": False, "query": "", "results": [], "error": f"{provider} nicht erreichbar: {exc.reason}"}
        except OSError as exc:
            return {"ok": False, "query": "", "results": [], "error": f"{provider} Suchfehler: {exc}"}
        rows = parser(document)
        return {"ok": bool(rows), "query": "", "results": rows, "provider": provider} if rows else {
            "ok": False, "query": "", "results": [], "error": f"{provider} lieferte keine Treffer."
        }

    def _search_wikipedia(self, term: str, maximum: int, remaining: float) -> dict:
        base = self.config.get("fallback_base_urls", {}).get("wikipedia", "https://de.wikipedia.org/w/api.php")
        query = urlencode({"action": "query", "list": "search", "format": "json", "srsearch": term, "srlimit": maximum})
        return self._search_json_api_bounded(
            f"{base}?{query}", "wikipedia", max(1, min(int(remaining), int(self.config["timeout_seconds"]))),
            lambda document: self._parse_wikipedia(document, maximum),
        )

    def _search_arxiv(self, term: str, maximum: int, remaining: float) -> dict:
        base = self.config.get("fallback_base_urls", {}).get("arxiv", "https://export.arxiv.org/api/query")
        query = urlencode({"search_query": f"all:{term}", "start": 0, "max_results": maximum})
        return self._search_json_api_bounded(
            f"{base}?{query}", "arxiv", max(1, min(int(remaining), int(self.config["timeout_seconds"]))),
            lambda document: self._parse_arxiv(document, maximum),
        )

    def _search_semantic_scholar(self, term: str, maximum: int, remaining: float) -> dict:
        base = self.config.get("fallback_base_urls", {}).get("semantic_scholar", "https://api.semanticscholar.org/graph/v1/paper/search")
        query = urlencode({"query": term, "limit": maximum, "fields": "title,url,abstract,year,authors"})
        return self._search_json_api_bounded(
            f"{base}?{query}", "semantic_scholar", max(1, min(int(remaining), int(self.config["timeout_seconds"]))),
            lambda document: self._parse_semantic_scholar(document, maximum),
        )

    def _search_brave(self, term: str, maximum: int, remaining: float) -> dict:
        if not self.config.get("brave_api_key"):
            return {"ok": False, "query": term, "results": [], "error": "Brave Search API-Key fehlt."}
        base = self.config.get("fallback_base_urls", {}).get("brave_search", "https://api.search.brave.com/res/v1/web/search")
        query = urlencode({"q": term, "count": maximum, "search_lang": "de"})
        return self._search_json_api_bounded(
            f"{base}?{query}", "brave_search", max(1, min(int(remaining), int(self.config["timeout_seconds"]))),
            lambda document: self._parse_brave(document, maximum),
        )

    @staticmethod
    def _parse_wikipedia(document: str, maximum: int) -> list[dict]:
        payload = json.loads(document)
        rows = []
        for item in payload.get("query", {}).get("search", [])[:maximum]:
            title = item.get("title", "")
            rows.append({
                "title": title,
                "url": "https://de.wikipedia.org/wiki/" + quote_plus(title.replace(" ", "_")),
                "snippet": re.sub(r"<[^>]+>", "", html.unescape(item.get("snippet", ""))),
                "provider": "wikipedia",
            })
        return rows

    @staticmethod
    def _parse_arxiv(document: str, maximum: int) -> list[dict]:
        entries = re.findall(r"<entry>(.*?)</entry>", document, flags=re.S)
        rows = []
        for entry in entries[:maximum]:
            title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<title>(.*?)</title>", entry, re.S).group(1))).strip() if re.search(r"<title>(.*?)</title>", entry, re.S) else "arXiv Treffer"
            summary = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", re.search(r"<summary>(.*?)</summary>", entry, re.S).group(1))).strip() if re.search(r"<summary>(.*?)</summary>", entry, re.S) else ""
            link_match = re.search(r"<id>(.*?)</id>", entry, re.S)
            rows.append({"title": title, "url": link_match.group(1).strip() if link_match else "https://arxiv.org", "snippet": summary[:400], "provider": "arxiv"})
        return rows

    @staticmethod
    def _parse_semantic_scholar(document: str, maximum: int) -> list[dict]:
        payload = json.loads(document)
        rows = []
        for item in payload.get("data", [])[:maximum]:
            authors = ", ".join(author.get("name", "") for author in item.get("authors", [])[:3] if author.get("name"))
            rows.append({
                "title": item.get("title", "Semantic Scholar Treffer"),
                "url": item.get("url") or f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}",
                "snippet": " ".join(part for part in (str(item.get("year", "")), authors, item.get("abstract") or "") if part)[:500],
                "provider": "semantic_scholar",
            })
        return rows

    @staticmethod
    def _parse_brave(document: str, maximum: int) -> list[dict]:
        payload = json.loads(document)
        rows = []
        for item in payload.get("web", {}).get("results", [])[:maximum]:
            rows.append({
                "title": item.get("title", "Brave Treffer"),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "provider": "brave_search",
            })
        return rows

    def _search_provider_bounded(self, term: str, maximum: int, provider: str, base_url: str, timeout: int) -> dict:
        completed: queue.Queue = queue.Queue(maxsize=1)

        def worker():
            completed.put(self._search_provider(term, maximum, provider, base_url, timeout))

        threading.Thread(target=worker, daemon=True, name=f"KontinuumSearchProvider-{provider}").start()
        try:
            return completed.get(timeout=timeout + 0.5)
        except queue.Empty:
            return {"ok": False, "query": term, "results": [], "error": f"Zeitlimit für {provider} erreicht."}

    def _search_provider(self, term: str, maximum: int, provider: str, base_url: str, timeout: int) -> dict:
        separator = "&" if "?" in base_url else "?"
        url = f"{base_url}{separator}q={quote_plus(term)}&kl={quote_plus(str(self.config['language']))}"
        headers = {
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Projekt-Kontinuum/{APP_VERSION}",
            "Accept": "text/html,application/xhtml+xml",
        }
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                document = response.read(2_000_000).decode(charset, errors="replace")
        except HTTPError as exc:
            return {"ok": False, "query": term, "results": [], "error": f"Suchanbieter HTTP-Fehler {exc.code}: {exc.reason}"}
        except URLError as exc:
            document = self._curl_download(url, headers, timeout) if "CERTIFICATE_VERIFY_FAILED" in str(exc.reason) else ""
            if not document:
                return {"ok": False, "query": term, "results": [], "error": f"Suchanbieter nicht erreichbar: {exc.reason}"}
        except OSError as exc:
            return {"ok": False, "query": term, "results": [], "error": f"Suchfehler: {exc}"}

        parser = _DuckDuckGoParser()
        parser.feed(document)
        results = []
        seen = set()
        for item in parser.results:
            target = self._clean_url(item["url"])
            if not target or target in seen:
                continue
            seen.add(target)
            results.append(
                {
                    "title": html.unescape(item["title"]).strip(),
                    "url": target,
                    "snippet": html.unescape(re.sub(r"\s+", " ", item["snippet"])).strip(),
                    "provider": provider,
                }
            )
            if len(results) >= maximum:
                break
        if not results:
            return {"ok": False, "query": term, "results": [], "error": "Der Suchanbieter lieferte keine auswertbaren Treffer."}
        return {"ok": True, "query": term, "results": results, "provider": provider}

    def _curl_download(self, url: str, headers: dict, timeout: int) -> str:
        executable = shutil.which("curl.exe")
        if not executable:
            return ""
        command = [
            executable,
            "--silent",
            "--show-error",
            "--location",
            "--fail",
            "--ssl-no-revoke",
            "--max-time",
            str(timeout),
            "--max-filesize",
            "2000000",
        ]
        for name, value in headers.items():
            command.extend(["--header", f"{name}: {value}"])
        command.append(url)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                check=False,
                timeout=timeout + 2,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

    @staticmethod
    def _clean_url(url: str) -> str:
        value = html.unescape((url or "").strip())
        if value.startswith("//"):
            value = "https:" + value
        parsed = urlparse(value)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            target = parse_qs(parsed.query).get("uddg", [""])[0]
            value = unquote(target)
        parsed = urlparse(value)
        return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""

    @staticmethod
    def format_results(result: dict) -> str:
        if not result.get("ok"):
            return f"Internetsuche fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}"
        rows = result["results"]
        lines = [f"Internetsuche für „{result['query']}“: {len(rows)} Treffer"]
        for index, row in enumerate(rows, start=1):
            lines.append(f"{index}. {row['title']}\n   {row['url']}")
            if row.get("snippet"):
                lines.append(f"   {row['snippet']}")
        return "\n".join(lines)
