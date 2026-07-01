from __future__ import annotations


def validate_structure(path_tools) -> dict:
    paths = path_tools.paths()
    missing = [name for name, path in paths.items() if not path.is_dir()]
    forbidden = [
        str(path_tools.project_root() / "28_documents"),
        str(path_tools.project_root() / "29_memory"),
        str(paths["data"] / "29_memory"),
        str(paths["data"] / "32_data"),
    ]
    present_forbidden = [path for path in forbidden if __import__("pathlib").Path(path).exists()]
    return {
        "ok": not missing and not present_forbidden,
        "missing": missing,
        "forbidden_present": present_forbidden,
    }
