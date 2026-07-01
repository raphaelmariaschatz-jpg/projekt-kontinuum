from __future__ import annotations

import fnmatch
import os
import time
from pathlib import Path

from .contracts import SearchHit


class SearchRouter:
    """Indexed active-knowledge search with explicit opt-in archive search."""

    MAX_RUNTIME = 30
    MAX_RESULTS = 50
    TEXT_SUFFIXES = {".json", ".md", ".txt", ".py"}
    EXCLUDED_SUFFIXES = {".zip", ".exe", ".dll", ".db", ".sqlite", ".bin", ".onnx", ".pt", ".pth", ".model"}
    EXCLUDED_DIRECTORIES = {"__pycache__"}
    EXCLUDED_DIRECTORY_PATTERNS = ("vosk-model*",)

    def __init__(self, path_tools, storage=None):
        self.path_tools = path_tools
        self.storage = storage
        self._indexed = False
        self.progress_handler = None
        self.last_refresh = {"timed_out": False, "elapsed": 0, "indexed": 0, "area": ""}

    def set_progress_handler(self, handler) -> None:
        self.progress_handler = handler

    def _emit_progress(self, area: str, indexed: int, started: float, timed_out: bool = False) -> None:
        if callable(self.progress_handler):
            self.progress_handler({
                "area": area,
                "hits": indexed,
                "elapsed": int(time.monotonic() - started),
                "timed_out": timed_out,
            })

    @classmethod
    def _is_excluded_path(cls, value: str | Path) -> bool:
        path = Path(value)
        return (
            path.suffix.casefold() in cls.EXCLUDED_SUFFIXES
            or any(part.casefold() in cls.EXCLUDED_DIRECTORIES for part in path.parts)
            or any(
                fnmatch.fnmatch(part.casefold(), pattern)
                for part in path.parts
                for pattern in cls.EXCLUDED_DIRECTORY_PATTERNS
            )
        )

    def _areas(self, include_archive: bool = False) -> list[tuple[str, Path, bool]]:
        paths = self.path_tools.paths()
        areas = [
            ("04_knowledge", paths["knowledge"], False),
            ("03_memory", paths["memory"], False),
            ("06_learning", paths["learning"], False),
            ("22_project_chronicle", paths["chronicle"], False),
            ("26_research", paths["research"], False),
        ]
        if include_archive:
            areas.append(("02_versions", paths["versions"], True))
        return areas

    def refresh_index(self, include_archive: bool = False, term: str = "") -> int:
        if not self.storage:
            return 0
        started = time.monotonic()
        indexed = 0
        matches = 0
        normalized_term = term.casefold()
        timed_out = False
        current_area = ""
        last_reported_second = -1
        for area, root, archive in self._areas(include_archive):
            current_area = area
            if not root.exists():
                continue
            for directory, directories, files in os.walk(root):
                directories[:] = [
                    name for name in directories
                    if name.casefold() not in self.EXCLUDED_DIRECTORIES
                    and not any(fnmatch.fnmatch(name.casefold(), pattern) for pattern in self.EXCLUDED_DIRECTORY_PATTERNS)
                ]
                for name in files:
                    elapsed = time.monotonic() - started
                    if include_archive and elapsed >= self.MAX_RUNTIME:
                        timed_out = True
                        break
                    file = Path(directory) / name
                    suffix = file.suffix.casefold()
                    if suffix in self.EXCLUDED_SUFFIXES or suffix not in self.TEXT_SUFFIXES:
                        continue
                    try:
                        content = file.read_text(encoding="utf-8-sig", errors="replace")
                        self.storage.index_file(str(file), area, content, file.stat().st_mtime_ns, archive)
                        indexed += 1
                        if normalized_term and normalized_term in content.casefold():
                            matches += 1
                    except OSError:
                        continue
                    second = int(elapsed)
                    if second != last_reported_second:
                        self._emit_progress(area, matches, started)
                        last_reported_second = second
                if timed_out:
                    break
            if timed_out:
                break
        self._indexed = True
        self.last_refresh = {
            "timed_out": timed_out,
            "elapsed": int(time.monotonic() - started),
            "indexed": indexed,
            "area": current_area,
        }
        self._emit_progress(current_area, matches, started, timed_out)
        return indexed

    def search(self, term: str, limit: int = 20, include_archive: bool = False) -> dict:
        limit = max(1, min(int(limit), self.MAX_RESULTS))
        if not self._indexed or include_archive:
            self.refresh_index(include_archive=include_archive, term=term)
        hits: list[dict] = []
        searched = [area for area, _, _ in self._areas(include_archive)]
        if self.storage:
            for row in self.storage.search_files(term, self.MAX_RESULTS * 4, include_archive):
                if self._is_excluded_path(row["path"]):
                    continue
                hits.append(SearchHit(
                    area=row["area"],
                    file=row["path"],
                    snippet=row.get("snippet", ""),
                    archive=bool(row.get("archive")),
                ).as_dict())
                if len(hits) >= limit:
                    break
            searched.append("32_data/kontinuum.db")
            if len(hits) < limit:
                hits.extend(
                    SearchHit(
                        area=f"32_data/{row['table']}",
                        file=str(self.storage.database),
                        snippet=row["content"][:260],
                    ).as_dict()
                    for row in self.storage.search(term, limit - len(hits))
                )
        return {
            "term": term,
            "hits": hits[:limit],
            "searched": searched,
            "include_archive": include_archive,
            "timed_out": bool(self.last_refresh.get("timed_out")) if include_archive else False,
            "elapsed": int(self.last_refresh.get("elapsed", 0)) if include_archive else 0,
        }

    def search_archive(self, term: str, limit: int = MAX_RESULTS) -> dict:
        return self.search(term, limit=limit, include_archive=True)

    @staticmethod
    def format(result: dict) -> str:
        hits = result["hits"]
        term = result["term"]
        if result.get("timed_out"):
            return "Archivsuche abgebrochen:\nZeitlimit erreicht.\nBitte Suchbegriff eingrenzen."
        scope = "aktives Wissen und Archiv" if result.get("include_archive") else "aktives Wissen"
        if not hits:
            return f"Keine Treffer für: {term} ({scope})"
        lines = [f"{len(hits)} Treffer für \"{term}\" ({scope}):"]
        for hit in hits[:12]:
            label = f"{hit['area']} / Archiv" if hit.get("archive") else hit["area"]
            lines.append(f"- [{label}] {hit['snippet'] or Path(hit['file']).name}")
        return "\n".join(lines)
