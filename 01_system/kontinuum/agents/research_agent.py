# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
import queue
import re
import threading
import time
from urllib.parse import urlparse
from .base_agent import BaseAgent, AgentResult


class ResearchAgent(BaseAgent):
    name = "research"
    TOTAL_TIMEOUT = 12
    FETCH_TIMEOUT = 6

    TRIGGERS = [
        "recherchiere",
        "recherche",
        "forsche",
        "untersuche",
        "quelle",
        "studie",
        "publikation",
        "paper",
        "internetsuche",
        "websuche",
        "suche im internet",
        "suchmaschinenstatus",
    ]
    CURRENT_MARKERS = (
        "heute",
        "aktuell",
        "aktuelle",
        "aktuellen",
        "neueste",
        "neuesten",
        "preise",
        "wetter",
        "nachrichten",
        "versionen",
        "gesetze",
        "produkte",
        "sport",
        "börse",
        "boerse",
    )

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower()
        return any(t in lower for t in self.TRIGGERS) or bool(re.search(r"https?://", prompt or ""))

    def handle(self, prompt: str) -> AgentResult:
        started = time.monotonic()
        web = self.tools.get("web_tools")
        search_engine = self.tools.get("search_engine_tools")
        lower = prompt.casefold().strip()
        source_ids = []
        topic = "Webrecherche"
        if lower == "suchmaschinenstatus":
            status = search_engine.status() if search_engine else {}
            return AgentResult(self.name, True, status.get("message", "Kein Suchmaschinen-Connector angebunden."))
        urls = re.findall(r"https?://[^\s]+", prompt or "")
        if urls and web:
            reports = []
            for url in urls[:3]:
                remaining = self.TOTAL_TIMEOUT - (time.monotonic() - started)
                if remaining <= 0:
                    break
                result = web.fetch_text(url, timeout=max(1, min(self.FETCH_TIMEOUT, int(remaining))))
                reports.append(result.get("summary", result.get("error", "Keine Antwort")))
                if self.storage and hasattr(self.storage, "add_source"):
                    source_ids.append(self.storage.add_source(
                        url,
                        {
                            "title": result.get("title", ""),
                            "agent": self.name,
                            "status": "error" if result.get("error") else "retrieved",
                        },
                    ))
            answer = "\n\n".join(reports)
            if len(reports) < len(urls[:3]):
                answer += "\n\nTeilantwort: Zeitbudget erreicht; weitere URLs wurden nicht mehr abgerufen."
        else:
            topic = re.sub(
                r"^(recherchiere|recherche|forsche|untersuche|internetsuche|websuche|suche\s+im\s+internet(?:\s+nach)?)\s*[:\-]?\s*",
                "",
                prompt.strip(),
                flags=re.I,
            )
            self.remember("research.topic", topic, {"agent": self.name, "content_policy": "references_only"})
            mode = self._search_mode(prompt)
            if search_engine:
                try:
                    result = search_engine.search(topic, mode=mode)
                except TypeError:
                    result = search_engine.search(topic)
            else:
                result = {
                "ok": False,
                "error": "Kein Suchmaschinen-Connector angebunden.",
                "results": [],
            }
            if self.storage and hasattr(self.storage, "add_source"):
                for row in result.get("results", []):
                    source_ids.append(self.storage.add_source(
                        row["url"],
                        {
                            "title": row.get("title", ""),
                            "snippet": row.get("snippet", ""),
                            "query": topic,
                            "agent": self.name,
                            "provider": row.get("provider", ""),
                            "content_policy": "references_only",
                        },
                    ))
            answer = self._build_sourced_answer(topic, result, web, started)
        platform = self.config.get("knowledge_platform")
        if platform and source_ids and answer:
            platform.integrate(
                answer,
                origin="research",
                title=f"Recherche: {topic}",
                locator=urls[0] if urls else "",
                source_record_ids=source_ids,
                extra={"query": topic},
            )
        return AgentResult(self.name, True, answer)

    def _search_mode(self, prompt: str) -> str:
        lower = (prompt or "").casefold()
        if "nur die lokale datenbank" in lower or "nur lokale datenbank" in lower or "ohne internet" in lower:
            return "local_only"
        if "internet und lokale datenbank" in lower or "lokale datenbank und internet" in lower:
            return "prefer_internet"
        if any(marker in lower for marker in self.CURRENT_MARKERS):
            return "prefer_internet"
        if any(marker in lower for marker in ("internetsuche", "websuche", "suche im internet", "nutze internet")):
            return "internet_only"
        return "default"

    def _build_sourced_answer(self, topic: str, search_result: dict, web, started: float | None = None) -> str:
        started = started or time.monotonic()
        if not search_result.get("ok"):
            return (
                "Teilantwort: Die Webrecherche konnte keine vollständigen Quellen abrufen.\n"
                f"Grund: {search_result.get('error', 'Unbekannter Fehler')}"
            )
        fetched = []
        domains = set()
        candidates = []
        for row in search_result.get("results", [])[:5]:
            domain = urlparse(row["url"]).netloc.casefold().removeprefix("www.")
            is_local_test_source = domain.startswith(("127.0.0.1:", "localhost:"))
            if domain in domains and not is_local_test_source:
                continue
            domains.add(domain)
            candidates.append(row)
        remaining = max(0.1, self.TOTAL_TIMEOUT - (time.monotonic() - started))
        completed: queue.Queue = queue.Queue()

        def fetch(row):
            try:
                completed.put((row, web.fetch_text(row["url"], timeout=self.FETCH_TIMEOUT)))
            except Exception as exc:
                completed.put((row, {"error": str(exc)}))

        for row in candidates if web else []:
            threading.Thread(target=fetch, args=(row,), daemon=True, name="KontinuumResearchFetch").start()
        deadline = time.monotonic() + remaining
        while len(fetched) < 2 and time.monotonic() < deadline:
            try:
                row, result = completed.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            text = str(result.get("text", "")).strip()
            if not self._usable_source(result, text):
                continue
            fetched.append({
                "title": result.get("title") or row.get("title", ""),
                "url": row["url"],
                "text": text[:3000],
                "snippet": row.get("snippet", ""),
            })

        if not fetched:
            return self._snippet_partial(topic, search_result)

        model = self.tools.get("language_model_tools")
        model_budget = max(1, min(8, int(self.TOTAL_TIMEOUT - (time.monotonic() - started))))
        if model:
            try:
                synthesis = model.generate_grounded_answer(topic, fetched, timeout_seconds=model_budget)
            except TypeError:
                synthesis = model.generate_grounded_answer(topic, fetched)
        else:
            synthesis = {"ok": False, "error": "Kein Sprachmodell angebunden."}
        if synthesis.get("ok") and re.search(r"\[\d+\]", synthesis.get("answer", "")):
            answer = synthesis["answer"]
        else:
            answer = self._extractive_fallback(topic, fetched)
        partial = time.monotonic() - started >= self.TOTAL_TIMEOUT or len(fetched) < 2
        lines = [("Teilantwort (Zeitbudget erreicht):\n" if partial else "") + answer, "", "Quellen:"]
        for index, source in enumerate(fetched, start=1):
            lines.append(f"[{index}] {source['title'] or source['url']}\n{source['url']}")
        return "\n".join(lines)

    @staticmethod
    def _snippet_partial(topic: str, search_result: dict) -> str:
        rows = search_result.get("results", [])[:5]
        if not rows:
            return "Teilantwort: Es konnten innerhalb des Zeitbudgets keine belastbaren Webtreffer gewonnen werden."
        lines = [f"Teilantwort zu „{topic}“ aus Suchtreffern; Quellenseiten konnten nicht rechtzeitig abgerufen werden:"]
        for index, row in enumerate(rows, start=1):
            lines.append(f"- {row.get('snippet') or row.get('title', 'Treffer')} [{index}]")
        lines.append("\nQuellen:")
        for index, row in enumerate(rows, start=1):
            lines.append(f"[{index}] {row.get('title', row['url'])}\n{row['url']}")
        return "\n".join(lines)

    @staticmethod
    def _usable_source(result: dict, text: str) -> bool:
        if not text or len(text) < 80:
            return False
        combined = f"{result.get('title', '')} {text[:1000]}".casefold()
        blocked_markers = (
            "captcha",
            "access denied",
            "zugriff verweigert",
            "enable javascript",
            "aktivieren sie javascript",
            "robot check",
            "security check",
            "einwilligung wir bitten sie an dieser stelle",
            "cookie-einstellungen",
        )
        return not any(marker in combined for marker in blocked_markers)

    @staticmethod
    def _extractive_fallback(topic: str, sources: list[dict]) -> str:
        lines = [
            "Belegte Kernaussagen aus den abgerufenen Quellen "
            "(automatische Zusammenfassung war nicht verfügbar):"
        ]
        keywords = {
            word.casefold()
            for word in re.findall(r"\w{4,}", topic)
            if word.casefold() not in {"eine", "einer", "einem", "einen", "oder", "sind", "wird", "was"}
        }
        for index, source in enumerate(sources, start=1):
            sentences = re.split(r"(?<=[.!?])\s+", source.get("text", ""))
            candidates = []
            for sentence in sentences:
                clean = " ".join(sentence.split()).strip()
                if not 25 <= len(clean) <= 700:
                    continue
                score = sum(keyword in clean.casefold() for keyword in keywords)
                candidates.append((score, clean))
            candidates.sort(key=lambda item: (item[0], -len(item[1])), reverse=True)
            selected = [sentence for score, sentence in candidates[:1] if score > 0]
            if not selected:
                selected = [sentence for _, sentence in candidates[:1]]
            excerpt = " ".join(selected).strip()
            lines.append(f"- {excerpt[:600]} [{index}]")
        return "\n".join(lines)
