# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
from pathlib import Path


class SearchTools:
    """Suchreihenfolge: Wissen zuerst, Altversionen zuletzt."""

    def __init__(self, path_tools=None):
        self.path_tools = path_tools

    def search_all(self, term: str) -> dict:
        if not self.path_tools:
            return {"answer": f"Suchrouter aktiv, aber PathTools nicht angebunden. Suchbegriff: {term}"}

        paths = self.path_tools.paths()
        order = [
            ("04_knowledge", paths["knowledge"]),
            ("03_memory", paths["memory"]),
            ("06_learning", paths["learning"]),
            ("32_data", paths["data"]),
            ("22_project_chronicle", paths["chronicle"]),
            ("02_versions", paths["versions"]),
        ]

        hits = []
        needle = term.lower()
        for label, root in order:
            if not root.exists():
                continue
            for file in root.rglob("*"):
                if file.is_file() and file.suffix.lower() in {".txt", ".md", ".json", ".py"}:
                    try:
                        text = file.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        continue
                    if needle in text.lower() or needle in file.name.lower():
                        hits.append({"area": label, "file": str(file)})
                        if len(hits) >= 20:
                            break
            if len(hits) >= 20:
                break

        if not hits:
            return {"answer": f"Keine Treffer für: {term}", "hits": []}
        lines = [f"{len(hits)} Treffer für „{term}“:"]
        lines += [f"- [{h['area']}] {h['file']}" for h in hits[:12]]
        return {"answer": "\n".join(lines), "hits": hits}
