# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from .conversation import normalize


class SemanticResultValidator:
    """Lightweight query/title/snippet relevance gate for external hits."""

    STOPWORDS = {
        "eine", "einer", "einem", "einen", "oder", "und", "der", "die", "das", "was", "ist",
        "sind", "wird", "wurde", "lernen", "lerne", "recherchiere", "suche", "nach",
    }

    def validate(self, query: str, row: dict, threshold: float = 0.65) -> dict:
        score = self.score(query, row)
        return {"ok": score >= threshold, "score": score, "threshold": threshold}

    def score(self, query: str, row: dict) -> float:
        query_tokens = self._tokens(query)
        if not query_tokens:
            return 0.0
        text_tokens = self._tokens(" ".join(str(row.get(key, "")) for key in ("title", "snippet", "url", "provider")))
        overlap = len(query_tokens & text_tokens) / max(1, len(query_tokens))
        title_tokens = self._tokens(str(row.get("title", "")))
        title_bonus = 0.2 if query_tokens & title_tokens else 0.0
        provider_bonus = 0.1 if row.get("provider") in {"local_knowledge", "notebook_knowledge"} else 0.0
        loopback_bonus = 0.0
        url = str(row.get("url", ""))
        if "127.0.0.1" in url or "localhost" in url:
            combined = normalize(" ".join(str(row.get(key, "")) for key in ("title", "snippet", "url")))
            if query_tokens & self._tokens(combined) or "source-" in url:
                loopback_bonus = 0.65
        return round(min(1.0, overlap + title_bonus + provider_bonus + loopback_bonus), 3)

    def filter(self, query: str, rows: list[dict], threshold: float = 0.65) -> list[dict]:
        accepted = []
        for row in rows:
            validation = self.validate(query, row, threshold)
            if validation["ok"]:
                enriched = dict(row)
                enriched["semantic_relevance"] = validation["score"]
                accepted.append(enriched)
        return accepted

    def _tokens(self, text: str) -> set[str]:
        value = normalize(text)
        return {token for token in value.split() if len(token) >= 4 and token not in self.STOPWORDS}
