from __future__ import annotations
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import re, socket, time


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = False
        self.chunks = []
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip = True
        if tag == "title":
            self.in_title = True
        if tag in {"p", "br", "li", "h1", "h2", "h3"}:
            self.chunks.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip = False
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip:
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

    def fetch_text(self, url: str) -> dict:
        try:
            req = Request(url, headers={"User-Agent": "Projekt-Kontinuum/23.0"})
            with urlopen(req, timeout=12) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                html = resp.read(1_500_000).decode(charset, errors="replace")
            parser = _TextExtractor()
            parser.feed(html)
            text = parser.text()
            title = re.sub(r"\s+", " ", parser.title).strip()
            excerpt = text[:900] + ("..." if len(text) > 900 else "")
            return {
                "url": url,
                "title": title,
                "text": text,
                "summary": f"WebResearch aktiv: {url}\nTitel: {title}\nTextauszug:\n{excerpt}"
            }
        except HTTPError as exc:
            return {"url": url, "error": f"HTTP-Fehler {exc.code}: {exc.reason}"}
        except URLError as exc:
            return {"url": url, "error": f"Netzwerkfehler: {exc.reason}"}
        except Exception as exc:
            return {"url": url, "error": f"Fehler beim Abruf: {exc}"}
