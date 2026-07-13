# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
from pathlib import Path
import shutil


class FileTools:
    @staticmethod
    def read_text(path: str | Path, max_chars: int = 200000) -> str:
        p = Path(path)
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]

    @staticmethod
    def write_text(path: str | Path, text: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    @staticmethod
    def copy(src: str | Path, dst: str | Path) -> None:
        d = Path(dst)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    @staticmethod
    def list_files(root: str | Path, pattern: str = "*") -> list[str]:
        return [str(p) for p in Path(root).rglob(pattern) if p.is_file()]
