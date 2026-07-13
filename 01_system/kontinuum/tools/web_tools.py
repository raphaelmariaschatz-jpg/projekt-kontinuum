# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import re, shutil, socket, subprocess, time

from kontinuum.version import APP_VERSION


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.chunks = []
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "nav", "header", "footer", "form"}:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "br", "li", "h1", "h2", "h3"}:
            self.chunks.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "nav", "header", "footer", "form"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip_depth:
            return
        t = data.strip()
        if not t:
            return
        if self.in_title:
            self.title += t + " "
        self.chunks.append(t + " ")

    def text(self):
        return re.sub(r"\s+", " ", "".join(self.chunks)).strip()


class WebTools:
    USER_AGENT = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Projekt-Kontinuum/{APP_VERSION}"

    def internet_status(self) -> dict:
        try:
            socket.gethostbyname("www.mit.edu")
            dns_ok = True
        except Exception as exc:
            return {"internet_access": False, "message": f"DNS-Fehler: {exc}"}

        start = time.perf_counter()
        try:
            with socket.create_connection(("www.mit.edu", 443), timeout=8):
                ms = int((time.perf_counter() - start) * 1000)
                return {"internet_access": True, "message": f"Internetzugriff aktiv. TCP/443 erreichbar, {ms} ms."}
        except Exception as exc:
            return {"internet_access": False, "message": f"Verbindungsfehler: {exc}"}

    def fetch_text(self, url: str, timeout: int = 6) -> dict:
        try:
            req = Request(url, headers={"User-Agent": self.USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                html = resp.read(1_500_000).decode(charset, errors="replace")
            return self._extract(url, html)
        except HTTPError as exc:
            return {"url": url, "error": f"HTTP-Fehler {exc.code}: {exc.reason}"}
        except URLError as exc:
            html = self._curl_download(url, timeout) if "CERTIFICATE_VERIFY_FAILED" in str(exc.reason) else ""
            return self._extract(url, html) if html else {"url": url, "error": f"Netzwerkfehler: {exc.reason}"}
        except Exception as exc:
            return {"url": url, "error": f"Fehler beim Abruf: {exc}"}

    @staticmethod
    def _extract(url: str, document: str) -> dict:
        parser = _TextExtractor()
        parser.feed(document)
        text = parser.text()
        title = re.sub(r"\s+", " ", parser.title).strip()
        excerpt = text[:900] + ("..." if len(text) > 900 else "")
        return {
            "url": url,
            "title": title,
            "text": text,
            "summary": f"WebResearch aktiv: {url}\nTitel: {title}\nTextauszug:\n{excerpt}",
        }

    def _curl_download(self, url: str, timeout: int = 6) -> str:
        executable = shutil.which("curl.exe")
        if not executable:
            return ""
        try:
            result = subprocess.run(
                [
                    executable,
                    "--silent",
                    "--show-error",
                    "--location",
                    "--fail",
                    "--ssl-no-revoke",
                    "--max-time",
                    str(timeout),
                    "--max-filesize",
                    "1500000",
                    "--header",
                    f"User-Agent: {self.USER_AGENT}",
                    url,
                ],
                capture_output=True,
                check=False,
                timeout=timeout + 2,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""
