from __future__ import annotations
from pathlib import Path
import json


class ImportTools:
    @staticmethod
    def load_master_import(path: str | Path) -> dict:
        p = Path(path)
        return json.loads(p.read_text(encoding="utf-8-sig"))

    @staticmethod
    def summarize_master(data: dict) -> dict:
        return {
            "keys": list(data.keys()) if isinstance(data, dict) else [],
            "type": type(data).__name__,
        }
