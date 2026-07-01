from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Projekt Kontinuum")
ACTIVE_VERSION = "34.1"
REPORT_ROOT = ROOT / "31_reports" / "archive_lifecycle"
TEXT_SUFFIXES = {".py", ".json", ".md", ".txt", ".bat", ".ps1", ".csv", ".yml", ".yaml", ".ini", ".toml"}
BINARY_SUFFIXES = {".exe", ".dll", ".zip", ".pdf", ".db", ".pyc", ".pyo"}
PROTECTED_PARTS = {"archive", "archives", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SCAN_ROOTS = {"11_gui", "13_tools", "14_documents", "16_installation", "17_tests", "22_project_chronicle", "24_config", "31_reports"}
MAX_HASH_BYTES = 20 * 1024 * 1024
VERSION_RE = re.compile(r"(?<!\d)(\d{1,2})[._](\d)(?!\d)")
DATE_RE = re.compile(r"20\d{2}[-_]\d{2}[-_]\d{2}|\b\d{2}\.\d{2}\.\d{2,4}\b")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(relative: str) -> dict:
    try:
        return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def add_path(container: set[str], value: str | None) -> None:
    if value:
        container.add(Path(value).as_posix())


def collect_active_paths() -> set[str]:
    active: set[str] = set()
    release = load_json("24_config/release_integrity_34_1.json")
    architecture = load_json("24_config/canonical_architecture_34_1.json")
    artifacts = load_json("24_config/canonical_artifacts_34_1.json")
    for key in ("required_paths", "foundation_required_paths", "canonical_architecture_required_paths", "chronicle_paths", "starter_paths", "gui_paths"):
        for item in release.get(key, []):
            add_path(active, item)
    for key in ("entrypoints", "registries"):
        for item in architecture.get(key, []):
            add_path(active, item)
    add_path(active, architecture.get("canonical_project_structure"))
    add_path(active, architecture.get("project_structure_archive"))
    for layer_items in architecture.get("layers", {}).values():
        for item in layer_items:
            add_path(active, item.get("path"))
    lifecycle = architecture.get("artifact_lifecycle", {})
    for key in ("policy", "documentation", "migration_archive", "migration_report_backup", "signed_evidence_archive"):
        add_path(active, lifecycle.get(key))
    add_path(active, artifacts.get("lifecycle_policy"))
    for item in artifacts.get("artifacts", []):
        if item.get("required"):
            add_path(active, item.get("path"))
    return active


def is_under(path: str, root: str) -> bool:
    root = root.rstrip("/")
    return path == root or path.startswith(root + "/")


def active_reason(relative: str, active_paths: set[str]) -> str:
    for active in active_paths:
        if is_under(relative, active):
            return f"canonical_or_required:{active}"
    return ""


def parse_version_from_name(name: str) -> tuple[int, int] | None:
    matches = VERSION_RE.findall(name)
    if not matches:
        return None
    versions = [(int(major), int(minor)) for major, minor in matches]
    return max(versions)


def version_label(version: tuple[int, int] | None) -> str:
    if not version:
        return ""
    return f"{version[0]}.{version[1]}"


def looks_historical(path: Path, relative: str) -> tuple[bool, str]:
    name = path.name
    version = parse_version_from_name(name)
    if version and version < (34, 1):
        return True, f"older_version_marker:{version_label(version)}"
    if name.startswith(("README_GUI_", "PROJEKTSTATUS_AKTUELL_", "START_GUI_", "START_KONTINUUM_", "TEST_KONTINUUM_", "SETUP_ORACLE_CLOUD_", "status_check_")) and "34_1" not in name:
        return True, "superseded_versioned_artifact"
    if name.startswith("RELEASE_") and "34_1" not in name:
        return True, "historical_release_chronicle"
    if name.startswith("PROJEKTSTRUKTUR_") and "34_1" not in name:
        return True, "historical_project_structure"
    if DATE_RE.search(name) and "2026_06_27" not in name and "2026-06-27" not in name:
        return True, "dated_historical_report_or_note"
    if "fundamentale Gedanken" in relative and name.casefold() != "roadmap.md":
        return True, "working_note_or_historical_thought_document"
    return False, ""


def likely_archive_target(relative: str, reason: str) -> str:
    first = relative.split("/", 1)[0]
    name = Path(relative).name
    if "test" in reason or first == "17_tests":
        sub = "tests"
    elif "release" in reason:
        sub = "releases"
    elif "report" in reason or "status" in name.casefold():
        sub = "reports"
    elif "migration" in reason:
        sub = "migrations"
    elif "legacy" in reason or parse_version_from_name(name):
        sub = "legacy"
    else:
        sub = "legacy"
    return f"{first}/archive/{sub}/{name}"


def file_hash(path: Path) -> str:
    if path.stat().st_size > MAX_HASH_BYTES:
        return f"large-file:{path.stat().st_size}"
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def collect_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        scan_root = ROOT / root_name
        if scan_root.exists():
            files.extend(p for p in scan_root.rglob("*") if p.is_file())
    return sorted(files, key=lambda p: rel(p).casefold())


def build_reference_index(files: list[Path]) -> list[tuple[str, str]]:
    indexed = []
    ignored_prefixes = ("31_reports/release_integrity/", "31_reports/archive_lifecycle/")
    for path in files:
        if path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        relative = rel(path)
        parts = set(Path(relative).parts)
        if parts & {"archive", "archives", "__pycache__"}:
            continue
        if relative.startswith(ignored_prefixes):
            continue
        try:
            indexed.append((relative, read_text(path)))
        except OSError:
            continue
    return indexed


def find_references(relative: str, indexed: list[tuple[str, str]], limit: int = 12) -> list[dict]:
    basename = Path(relative).name
    needles = {relative, basename}
    hits = []
    for source, text in indexed:
        if source == relative:
            continue
        for needle in needles:
            if needle and needle in text:
                hits.append({"source": source, "needle": needle})
                break
        if len(hits) >= limit:
            break
    return hits


def classify(files: list[Path], active_paths: set[str], indexed: list[tuple[str, str]]) -> dict:
    clearly_historical = []
    possible_active = []
    already_archived = []
    cache_or_generated = []
    duplicate_map: dict[str, list[str]] = defaultdict(list)

    for path in files:
        relative = rel(path)
        parts = set(Path(relative).parts)
        duplicate_map[file_hash(path)].append(relative)
        active = active_reason(relative, active_paths)
        references = find_references(relative, indexed)
        historical, reason = looks_historical(path, relative)

        if "__pycache__" in parts or path.suffix.casefold() in {".pyc", ".pyo"}:
            cache_or_generated.append({"path": relative, "reason": "generated_runtime_cache", "archive_target": None})
            continue
        if parts & {"archive", "archives"}:
            already_archived.append({"path": relative, "reason": "already_in_archive_area"})
            continue
        if active:
            possible_active.append({"path": relative, "reason": active, "references": references[:5]})
            continue
        if historical:
            clearly_historical.append({
                "path": relative,
                "reason": reason,
                "archive_target": likely_archive_target(relative, reason),
                "references": references,
                "phase2_safe_without_reference_update": not references,
            })
        elif references:
            possible_active.append({"path": relative, "reason": "referenced_noncanonical_or_context_file", "references": references[:8]})

    duplicates = [
        {"sha256": digest, "count": len(paths), "paths": paths}
        for digest, paths in sorted(duplicate_map.items(), key=lambda item: (-len(item[1]), item[1][0].casefold()))
        if len(paths) > 1
    ]
    return {
        "clearly_historical": clearly_historical,
        "possible_active_or_needs_review": possible_active,
        "already_archived": already_archived,
        "cache_or_generated": cache_or_generated,
        "duplicates": duplicates,
    }


def write_reports(result: dict) -> tuple[Path, Path, Path]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = REPORT_ROOT / f"phase1_archive_analysis_{stamp}.json"
    md_path = REPORT_ROOT / f"phase1_archive_analysis_{stamp}.md"
    schema_path = REPORT_ROOT / "archive_move_log_schema.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = result["counts"]
    lines = [
        "# Phase 1 Archive Lifecycle Analysis",
        "",
        f"Created at: {result['created_at']}",
        f"Project root: `{result['project_root']}`",
        "",
        "## Summary",
        "",
        f"- Files scanned: {counts['files_scanned']}",
        f"- Clearly historical candidates: {counts['clearly_historical']}",
        f"- Phase-2 safe without reference update: {counts['phase2_safe_without_reference_update']}",
        f"- Possibly active or needs review: {counts['possible_active_or_needs_review']}",
        f"- Already archived: {counts['already_archived']}",
        f"- Generated cache files: {counts['cache_or_generated']}",
        f"- Duplicate hash groups: {counts['duplicate_groups']}",
        "",
        "## Clearly Historical Candidates",
        "",
    ]
    for item in result["clearly_historical"][:120]:
        lines.append(f"- `{item['path']}` -> `{item['archive_target']}` ({item['reason']})")
    if len(result["clearly_historical"]) > 120:
        lines.append(f"- ... {len(result['clearly_historical']) - 120} more in JSON report")
    lines.extend(["", "## Possibly Active Or Needs Review", ""])
    for item in result["possible_active_or_needs_review"][:120]:
        refs = ", ".join(ref["source"] for ref in item.get("references", [])[:3])
        suffix = f"; refs: {refs}" if refs else ""
        lines.append(f"- `{item['path']}` ({item['reason']}{suffix})")
    if len(result["possible_active_or_needs_review"]) > 120:
        lines.append(f"- ... {len(result['possible_active_or_needs_review']) - 120} more in JSON report")
    lines.extend(["", "## Duplicate Groups", ""])
    for group in result["duplicates"][:80]:
        lines.append(f"- SHA-256 `{group['sha256'][:16]}...` ({group['count']} files): " + "; ".join(f"`{p}`" for p in group["paths"][:6]))
    if len(result["duplicates"]) > 80:
        lines.append(f"- ... {len(result['duplicates']) - 80} more in JSON report")
    lines.extend([
        "",
        "## Phase 2 Guardrail",
        "",
        "No files were moved by this analysis. Phase 2 may only move entries from `clearly_historical` after confirming that references remain empty or have been updated deliberately.",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    schema_path.write_text(
        "# Archive Move Log Schema\n\n"
        "Every future archive move must append a JSON object with these fields:\n\n"
        "- `timestamp_utc`\n"
        "- `original_path`\n"
        "- `archive_path`\n"
        "- `reason`\n"
        "- `safety_check`\n"
        "- `references_before`\n"
        "- `references_updated`\n"
        "- `verification_after_move`\n\n"
        "The log file is `31_reports/archive_lifecycle/archive_moves.jsonl`.\n",
        encoding="utf-8",
    )
    log_path = REPORT_ROOT / "archive_moves.jsonl"
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    return json_path, md_path, schema_path


def main() -> int:
    files = collect_files()
    active_paths = collect_active_paths()
    indexed = build_reference_index(files)
    classified = classify(files, active_paths, indexed)
    result = {
        "kind": "kontinuum.archive_lifecycle.phase1_analysis",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(ROOT),
        "active_version": ACTIVE_VERSION,
        "mode": "read_only_no_moves",
        "active_path_count": len(active_paths),
        "counts": {
            "files_scanned": len(files),
            "clearly_historical": len(classified["clearly_historical"]),
            "phase2_safe_without_reference_update": sum(1 for item in classified["clearly_historical"] if item.get("phase2_safe_without_reference_update")),
            "possible_active_or_needs_review": len(classified["possible_active_or_needs_review"]),
            "already_archived": len(classified["already_archived"]),
            "cache_or_generated": len(classified["cache_or_generated"]),
            "duplicate_groups": len(classified["duplicates"]),
        },
        **classified,
    }
    json_path, md_path, schema_path = write_reports(result)
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Log schema: {schema_path}")
    print(json.dumps(result["counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




