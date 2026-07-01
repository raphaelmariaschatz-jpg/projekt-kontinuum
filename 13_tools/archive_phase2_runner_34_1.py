from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Projekt Kontinuum")
ANALYSIS = ROOT / "31_reports" / "archive_lifecycle" / "phase1_archive_analysis_20260627_094324.json"
LOG = ROOT / "31_reports" / "archive_lifecycle" / "archive_moves.jsonl"
REPORT_ROOT = ROOT / "31_reports" / "archive_lifecycle"
ALLOWED_ARCHIVE_SEGMENTS = {"legacy", "reports", "tmp", "cache", "migrations"}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_analysis() -> list[dict]:
    data = json.loads(ANALYSIS.read_text(encoding="utf-8-sig"))
    return [item for item in data["clearly_historical"] if item.get("phase2_safe_without_reference_update")]


def moved_originals() -> set[str]:
    if not LOG.exists():
        return set()
    originals = set()
    for line in LOG.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except ValueError:
            continue
        originals.add(item.get("original_path", ""))
    return originals


def normalize_target(target: str) -> str:
    parts = list(Path(target).parts)
    if "archive" in parts:
        idx = parts.index("archive")
        if idx + 1 < len(parts) and parts[idx + 1] == "tests":
            parts[idx + 1] = "legacy"
        if idx + 1 < len(parts) and parts[idx + 1] == "releases":
            parts[idx + 1] = "legacy"
    return Path(*parts).as_posix()


def validate_target(target: str) -> None:
    parts = Path(target).parts
    if "archive" not in parts:
        raise RuntimeError(f"Archive target is outside archive structure: {target}")
    idx = parts.index("archive")
    if idx + 1 >= len(parts) or parts[idx + 1] not in ALLOWED_ARCHIVE_SEGMENTS:
        raise RuntimeError(f"Archive target uses invalid segment: {target}")


def select_items(count: int) -> list[dict]:
    done = moved_originals()
    remaining = [item for item in load_analysis() if item["path"] not in done]
    return remaining[:count]


def move_wave(wave: int, count: int) -> dict:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.touch(exist_ok=True)
    items = select_items(count)
    moved = []
    for item in items:
        source = ROOT / item["path"]
        archive_target = normalize_target(item["archive_target"])
        target = ROOT / archive_target
        validate_target(archive_target)
        if not source.is_file():
            raise RuntimeError(f"Source missing before move: {item['path']}")
        if target.exists():
            raise RuntimeError(f"Archive target already exists: {item['archive_target']}")
        source_hash = sha256(source)
        source_size = source.stat().st_size
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        target_hash = sha256(target)
        if source_hash != target_hash:
            raise RuntimeError(f"Hash mismatch after move: {item['path']}")
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "phase": "phase2",
            "wave": wave,
            "original_path": item["path"],
            "archive_path": archive_target,
            "reason": item["reason"],
            "size_bytes": source_size,
            "sha256_before": source_hash,
            "sha256_after": target_hash,
            "safety_check": {
                "phase1_safe_without_reference_update": True,
                "source_existed_before_move": True,
                "target_inside_archive_structure": True,
                "target_did_not_exist_before_move": True,
                "hash_verified_after_move": True,
                "no_delete_performed": True,
            },
            "references_before": item.get("references", []),
            "references_updated": [],
            "verification_after_move": "pending_wave_verification",
            "rollback": {
                "original_path": item["path"],
                "archive_path": archive_target,
                "possible_until": "wave_completion_plus_24h",
            },
        }
        with LOG.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        moved.append(entry)
    wave_path = REPORT_ROOT / f"phase2_wave_{wave}_moves.json"
    wave_path.write_text(json.dumps({"wave": wave, "moved_count": len(moved), "moves": moved}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"wave": wave, "moved_count": len(moved), "move_report": str(wave_path), "moves": moved}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", type=int, required=True)
    parser.add_argument("--count", type=int, required=True)
    args = parser.parse_args()
    result = move_wave(args.wave, args.count)
    print(json.dumps({"wave": result["wave"], "moved_count": result["moved_count"], "move_report": result["move_report"]}, ensure_ascii=False))
    for item in result["moves"]:
        print(f"{item['original_path']} -> {item['archive_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
