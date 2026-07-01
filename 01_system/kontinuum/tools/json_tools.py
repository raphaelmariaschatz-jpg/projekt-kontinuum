from __future__ import annotations
import json
from pathlib import Path
from typing import Any


class JsonTools:
    @staticmethod
    def load(path: str | Path, default: Any = None) -> Any:
        p = Path(path)
        try:
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            return default
        return default

    @staticmethod
    def save(path: str | Path, data: Any) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def append_jsonl(path: str | Path, item: dict) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
