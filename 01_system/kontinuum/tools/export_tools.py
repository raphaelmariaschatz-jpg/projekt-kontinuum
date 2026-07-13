# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
from pathlib import Path
import json


class ExportTools:
    @staticmethod
    def export_json(path: str | Path, data) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def export_markdown(path: str | Path, title: str, body: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
