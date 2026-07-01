from __future__ import annotations

import ast
import json
import os
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CodeAgentService:
    VERSION = "1.0"
    MODE = "diagnostic_read_only"
    COMMAND_MARKERS = (
        "analysiere code",
        "analysiere projekt",
        "erkläre code",
        "erklaere code",
        "finde einstiegspunkte",
        "erstelle projektkarte",
        "welche sprache ist",
        "codeagent ",
        "codeagentstatus",
    )
    DEFAULT_CONFIG = {
        "enabled": True,
        "mode": MODE,
        "read_only": True,
        "auto_memory_write": False,
        "max_file_size_bytes": 1_000_000,
        "max_project_files": 250,
        "allowed_roots": [
            ".",
            "01_system",
            "11_gui",
            "13_tools",
            "14_documents",
            "17_tests",
            "24_config",
            "30_import",
            "32_data",
        ],
    }
    DEFAULT_LANGUAGE_REGISTRY = {
        "python": {
            "extensions": [".py"],
            "comment_markers": ["#"],
            "import_patterns": [r"^\s*import\s+([\w.]+)", r"^\s*from\s+([\w.]+)\s+import\s+"],
            "function_patterns": [r"^\s*def\s+([A-Za-z_]\w*)\s*\("],
            "class_patterns": [r"^\s*class\s+([A-Za-z_]\w*)"],
            "entrypoint_patterns": [r"if\s+__name__\s*==\s*['\"]__main__['\"]"],
            "package_files": ["pyproject.toml", "requirements.txt", "setup.py"],
            "known_risks": ["eval(", "exec(", "shell=True", "pickle.loads", "subprocess."],
            "recommended_parser": "ast",
        },
        "javascript": {
            "extensions": [".js", ".jsx"],
            "comment_markers": ["//", "/*"],
            "import_patterns": [r"\bimport\s+.*?\s+from\s+['\"]([^'\"]+)", r"\brequire\(['\"]([^'\"]+)"],
            "function_patterns": [r"\bfunction\s+([A-Za-z_$][\w$]*)", r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\("],
            "class_patterns": [r"\bclass\s+([A-Za-z_$][\w$]*)"],
            "entrypoint_patterns": [r"if\s*\(\s*require\.main\s*===\s*module\s*\)"],
            "package_files": ["package.json"],
            "known_risks": ["eval(", "innerHTML", "child_process", "document.write"],
            "recommended_parser": "regex",
        },
        "typescript": {
            "extensions": [".ts", ".tsx"],
            "comment_markers": ["//", "/*"],
            "import_patterns": [r"\bimport\s+.*?\s+from\s+['\"]([^'\"]+)"],
            "function_patterns": [r"\bfunction\s+([A-Za-z_$][\w$]*)", r"\b(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\("],
            "class_patterns": [r"\bclass\s+([A-Za-z_$][\w$]*)"],
            "entrypoint_patterns": [],
            "package_files": ["package.json", "tsconfig.json"],
            "known_risks": ["eval(", "innerHTML", "child_process"],
            "recommended_parser": "regex",
        },
        "html": {"extensions": [".html"], "comment_markers": ["<!--"], "import_patterns": [r"<script[^>]+src=['\"]([^'\"]+)"], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [r"<html"], "package_files": [], "known_risks": ["<script", "onerror=", "onclick="], "recommended_parser": "regex"},
        "css": {"extensions": [".css"], "comment_markers": ["/*"], "import_patterns": [r"@import\s+['\"]([^'\"]+)"], "function_patterns": [], "class_patterns": [r"\.([A-Za-z_][\w-]*)"], "entrypoint_patterns": [], "package_files": [], "known_risks": ["!important"], "recommended_parser": "regex"},
        "shell": {"extensions": [".sh"], "comment_markers": ["#"], "import_patterns": [r"^\s*source\s+(.+)", r"^\s*\.\s+(.+)"], "function_patterns": [r"^\s*([A-Za-z_]\w*)\s*\(\)\s*\{"], "class_patterns": [], "entrypoint_patterns": [r"^#!"], "package_files": [], "known_risks": ["rm -rf", "curl | sh", "sudo "], "recommended_parser": "regex"},
        "batch": {"extensions": [".bat"], "comment_markers": ["rem", "::"], "import_patterns": [r"\bcall\s+(.+)"], "function_patterns": [r"^:([A-Za-z_]\w*)"], "class_patterns": [], "entrypoint_patterns": [r"@echo off"], "package_files": [], "known_risks": ["del /", "rmdir", "format "], "recommended_parser": "regex"},
        "powershell": {"extensions": [".ps1"], "comment_markers": ["#"], "import_patterns": [r"\bImport-Module\s+([^\s]+)"], "function_patterns": [r"\bfunction\s+([A-Za-z_][\w-]*)"], "class_patterns": [r"\bclass\s+([A-Za-z_]\w*)"], "entrypoint_patterns": [], "package_files": [], "known_risks": ["Invoke-Expression", "Remove-Item", "Start-Process"], "recommended_parser": "regex"},
        "json": {"extensions": [".json"], "comment_markers": [], "import_patterns": [], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [], "package_files": ["package.json"], "known_risks": ["password", "secret", "token"], "recommended_parser": "json"},
        "yaml": {"extensions": [".yaml", ".yml"], "comment_markers": ["#"], "import_patterns": [], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [], "package_files": [], "known_risks": ["password", "secret", "token"], "recommended_parser": "regex"},
        "toml": {"extensions": [".toml"], "comment_markers": ["#"], "import_patterns": [], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [], "package_files": ["pyproject.toml"], "known_risks": ["password", "secret", "token"], "recommended_parser": "regex"},
        "ini": {"extensions": [".ini"], "comment_markers": [";", "#"], "import_patterns": [], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [], "package_files": [], "known_risks": ["password", "secret", "token"], "recommended_parser": "regex"},
        "env_example": {"extensions": [".env.example"], "comment_markers": ["#"], "import_patterns": [], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [], "package_files": [], "known_risks": ["SECRET=", "TOKEN=", "PASSWORD="], "recommended_parser": "regex"},
        "markdown": {"extensions": [".md", ".txt"], "comment_markers": [], "import_patterns": [], "function_patterns": [], "class_patterns": [], "entrypoint_patterns": [], "package_files": ["README.md"], "known_risks": ["TODO", "FIXME"], "recommended_parser": "text"},
    }

    def __init__(self, path_tools, storage: Any | None = None, canonical_engine: Any | None = None):
        self.path_tools = path_tools
        self.storage = storage
        self.canonical_engine = canonical_engine
        self.root = path_tools.project_root().resolve()
        self.config_path = path_tools.paths()["config"] / "code_agent_1_0.json"
        self.registry_path = path_tools.paths()["config"] / "code_agent_language_registry.json"
        self.config = self._load_config()
        self.language_registry = self._load_language_registry()
        self.output_dir = path_tools.paths()["data"] / "code_agent_analyses"
        self.log_path = path_tools.paths()["logs"] / "code_agent_1_0.jsonl"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.touch(exist_ok=True)
        self._last_result: dict[str, Any] = {}
        self._last_errors: list[str] = []

    def _load_config(self) -> dict[str, Any]:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    def _load_language_registry(self) -> dict[str, Any]:
        try:
            loaded = json.loads(self.registry_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                merged = dict(self.DEFAULT_LANGUAGE_REGISTRY)
                merged.update(loaded)
                return merged
        except (OSError, ValueError):
            pass
        return dict(self.DEFAULT_LANGUAGE_REGISTRY)

    @classmethod
    def looks_like_code_command(cls, text: str) -> bool:
        lower = (text or "").casefold().strip()
        return any(marker in lower for marker in cls.COMMAND_MARKERS)

    def handle_command(self, text: str) -> dict[str, Any]:
        lower = (text or "").casefold().strip(" .!?")
        if lower == "codeagentstatus":
            return {"ok": True, "message": self.format_status(), "result": self.status()}
        path = self._extract_path(text)
        if any(marker in lower for marker in ("analysiere projekt", "erstelle projektkarte")):
            result = self.analyze_project(path)
            return {"ok": result["status"] == "ok", "message": self.format_project(result), "result": result}
        if "finde einstiegspunkte" in lower:
            result = self.create_project_map(path)
            return {"ok": result["status"] == "ok", "message": self.format_entrypoints(result), "result": result}
        result = self.analyze_file(path)
        return {"ok": result["status"] == "ok", "message": self.format_file(result), "result": result}

    def status(self) -> dict[str, Any]:
        return {
            "active": bool(self.config.get("enabled", False)),
            "mode": self.config.get("mode", self.MODE),
            "read_only": True,
            "languages": sorted(self.language_registry),
            "supported_extensions": sorted(self._extension_map()),
            "allowed_roots": [str(path) for path in self._allowed_roots()],
            "last_source_path": self._last_result.get("source_path", ""),
            "last_status": self._last_result.get("status", ""),
            "last_export_path": self._last_result.get("export_path", ""),
            "last_errors": self._last_errors[-5:],
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "CodeAgent 1.0 Status:",
            f"- CodeAgent aktiv: {'ja' if status['active'] else 'nein'}",
            f"- Modus: {status['mode']}",
            "- read-only: ja",
            "- Sprachen: " + ", ".join(status["languages"]),
            "- unterstützte Endungen: " + ", ".join(status["supported_extensions"]),
            "- erlaubte Verzeichnisse: " + "; ".join(status["allowed_roots"]),
            f"- letzte Quelle: {status['last_source_path'] or '-'}",
            f"- letzter Status: {status['last_status'] or '-'}",
            f"- letzter JSON-Export: {status['last_export_path'] or '-'}",
        ])

    def analyze_file(self, path: str) -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._finish(self._error_result(result, str(exc)))
        result["source_path"] = str(resolved)
        if not resolved.is_file():
            return self._finish(self._error_result(result, "Datei nicht gefunden oder nicht lesbar."))
        if resolved.stat().st_size > int(self.config.get("max_file_size_bytes", 1_000_000)):
            result["warnings"].append("Datei überschreitet Größenlimit; Analyse abgebrochen.")
            return self._finish(self._error_result(result, "Datei ist zu groß für die read-only Analyse."))
        try:
            content = resolved.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as exc:
            return self._finish(self._error_result(result, str(exc)))
        language = self.detect_language(str(resolved), content)
        if language["language"] == "unknown":
            return self._finish(self._error_result(result, "Nicht unterstützter Dateityp."))
        result.update(language)
        result.update(self.extract_symbols(str(resolved), content))
        result.update(self.summarize_code(str(resolved), content))
        result["status"] = "ok"
        return self._finish(result)

    def analyze_project(self, path: str) -> dict[str, Any]:
        project_map = self.create_project_map(path)
        if project_map["status"] != "ok":
            return project_map
        return project_map

    def detect_language(self, path: str, content: str) -> dict[str, Any]:
        suffix = self._suffix(Path(path))
        for language, spec in self.language_registry.items():
            if suffix in spec.get("extensions", []):
                return {
                    "language": language,
                    "file_type": self._file_type(language),
                    "language_confidence": 0.95,
                    "recommended_parser": spec.get("recommended_parser", "regex"),
                }
        if content.startswith("#!/") and "python" in content.splitlines()[0].casefold():
            return {"language": "python", "file_type": "source", "language_confidence": 0.7, "recommended_parser": "ast"}
        return {"language": "unknown", "file_type": "unsupported", "language_confidence": 0.0, "recommended_parser": ""}

    def summarize_code(self, path: str, content: str) -> dict[str, Any]:
        lines = content.splitlines()
        risks = self._risks(path, content)
        todos = [line.strip() for line in lines if re.search(r"\b(TODO|FIXME|HACK)\b", line, flags=re.I)][:20]
        summary = (
            f"{Path(path).name}: {len(lines)} Zeilen, "
            f"{len(todos)} TODO/FIXME-Hinweise, {len(risks)} Risiko-Hinweise."
        )
        return {
            "summary": summary,
            "risks": risks,
            "warnings": todos,
            "line_count": len(lines),
            "memory_write_performed": False,
        }

    def extract_symbols(self, path: str, content: str) -> dict[str, Any]:
        language = self.detect_language(path, content)["language"]
        imports: list[str] = []
        functions: list[str] = []
        classes: list[str] = []
        entrypoints: list[str] = []
        if language == "python":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        imports.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
            except SyntaxError as exc:
                return {"detected_symbols": {"functions": [], "classes": []}, "imports": [], "dependencies": [], "entrypoints": [], "warnings": [f"Python-AST konnte nicht gelesen werden: {exc}"]}
        spec = self.language_registry.get(language, {})
        if language != "python":
            functions = self._collect_patterns(content, spec.get("function_patterns", []))
            classes = self._collect_patterns(content, spec.get("class_patterns", []))
            imports = self._collect_patterns(content, spec.get("import_patterns", []))
        entrypoints = self._collect_patterns(content, spec.get("entrypoint_patterns", []))
        if Path(path).name in spec.get("package_files", []):
            entrypoints.append(Path(path).name)
        return {
            "detected_symbols": {"functions": sorted(set(functions)), "classes": sorted(set(classes))},
            "imports": sorted(set(imports)),
            "dependencies": sorted(set(imports)),
            "entrypoints": sorted(set(entrypoints)),
        }

    def create_project_map(self, path: str) -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._finish(self._error_result(result, str(exc)))
        result["source_path"] = str(resolved)
        if not resolved.is_dir():
            return self.analyze_file(str(resolved))
        files = []
        skipped = []
        language_counts: Counter[str] = Counter()
        entrypoints = []
        configs = []
        docs = []
        tests = []
        risks = []
        max_files = int(self.config.get("max_project_files", 250))
        for candidate in self._iter_project_files(resolved):
            if len(files) >= max_files:
                result["warnings"].append(f"Projektanalyse auf {max_files} Dateien begrenzt.")
                break
            if candidate.stat().st_size > int(self.config.get("max_file_size_bytes", 1_000_000)):
                skipped.append({"path": str(candidate), "reason": "too_large"})
                continue
            suffix = self._suffix(candidate)
            if suffix not in self._extension_map():
                skipped.append({"path": str(candidate), "reason": "unsupported"})
                continue
            analysis = self.analyze_file(str(candidate))
            if analysis["status"] != "ok":
                skipped.append({"path": str(candidate), "reason": "; ".join(analysis.get("errors", []))})
                continue
            rel = self._relative(candidate)
            language_counts[analysis["language"]] += 1
            files.append({
                "path": rel,
                "language": analysis["language"],
                "file_type": analysis["file_type"],
                "symbols": analysis["detected_symbols"],
                "entrypoints": analysis["entrypoints"],
                "risks": analysis["risks"],
            })
            if analysis["entrypoints"] or candidate.name in {"main.py", "__main__.py", "package.json"}:
                entrypoints.append(rel)
            if analysis["file_type"] == "configuration":
                configs.append(rel)
            if analysis["file_type"] == "documentation":
                docs.append(rel)
            if "test" in rel.casefold() or candidate.name.startswith("test_"):
                tests.append(rel)
            risks.extend(f"{rel}: {risk}" for risk in analysis["risks"])
        result.update({
            "status": "ok",
            "language": language_counts.most_common(1)[0][0] if language_counts else "unknown",
            "file_type": "project",
            "project_map": {
                "total_files_analyzed": len(files),
                "skipped_files": skipped[:50],
                "languages": dict(language_counts),
                "important_entrypoints": sorted(set(entrypoints)),
                "test_folders_or_files": sorted(set(tests)),
                "configuration_files": sorted(set(configs)),
                "documentation_files": sorted(set(docs)),
                "central_modules": self._central_modules(files),
                "possible_build_or_start_commands": self._start_commands(files, configs),
                "architecture_summary": self._architecture_summary(language_counts, entrypoints, tests, configs, docs),
            },
            "detected_symbols": {},
            "imports": [],
            "dependencies": [],
            "entrypoints": sorted(set(entrypoints)),
            "summary": f"Projektkarte: {len(files)} Dateien analysiert, Hauptsprache {language_counts.most_common(1)[0][0] if language_counts else 'unbekannt'}.",
            "risks": risks[:50],
            "memory_write_performed": False,
        })
        return self._finish(result)

    def _base_result(self, path: str) -> dict[str, Any]:
        return {
            "status": "pending",
            "source_path": str(path or ""),
            "language": "",
            "file_type": "",
            "detected_symbols": {},
            "imports": [],
            "dependencies": [],
            "entrypoints": [],
            "summary": "",
            "risks": [],
            "warnings": [],
            "errors": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_name": "CodeAgent",
            "read_only": True,
            "export_path": "",
        }

    def _finish(self, result: dict[str, Any]) -> dict[str, Any]:
        if result.get("errors"):
            self._last_errors.append("; ".join(result["errors"]))
        if result.get("status") == "ok":
            export_path = self.output_dir / f"code_analysis_{uuid.uuid4().hex}.json"
            result["export_path"] = str(export_path)
            export_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self._last_result = result
        self._log(result)
        return result

    def _error_result(self, result: dict[str, Any], error: str) -> dict[str, Any]:
        result["status"] = "error"
        result["errors"].append(error)
        return result

    def _resolve_path(self, value: str | Path) -> Path:
        raw = str(value or "").strip().strip('"')
        if not raw:
            raise ValueError("Kein Codepfad angegeben.")
        path = Path(raw)
        if not path.is_absolute():
            path = self.root / path
        resolved = path.resolve()
        if not any(self._is_relative_to(resolved, root) for root in self._allowed_roots()):
            raise ValueError(f"Pfad ist nicht freigegeben: {resolved}")
        return resolved

    def _allowed_roots(self) -> list[Path]:
        roots = []
        for item in self.config.get("allowed_roots", ["."]):
            item_path = Path(str(item))
            roots.append(item_path.resolve() if item_path.is_absolute() else (self.root / item_path).resolve())
        return roots or [self.root]

    @staticmethod
    def _is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def _extension_map(self) -> dict[str, str]:
        mapping = {}
        for language, spec in self.language_registry.items():
            for extension in spec.get("extensions", []):
                mapping[extension] = language
        return mapping

    def _suffix(self, path: Path) -> str:
        name = path.name.casefold()
        if name.endswith(".env.example"):
            return ".env.example"
        return path.suffix.casefold()

    @staticmethod
    def _file_type(language: str) -> str:
        if language in {"json", "yaml", "toml", "ini", "env_example"}:
            return "configuration"
        if language == "markdown":
            return "documentation"
        return "source"

    @staticmethod
    def _collect_patterns(content: str, patterns: list[str]) -> list[str]:
        found = []
        for pattern in patterns:
            for match in re.findall(pattern, content, flags=re.M):
                if isinstance(match, tuple):
                    found.extend(item for item in match if item)
                elif match:
                    found.append(match)
        return [str(item).strip() for item in found if str(item).strip()]

    def _risks(self, path: str, content: str) -> list[str]:
        language = self.detect_language(path, content)["language"]
        spec = self.language_registry.get(language, {})
        risks = []
        for marker in spec.get("known_risks", []):
            if marker.casefold() in content.casefold():
                risks.append(f"Risikomarker erkannt: {marker}")
        if re.search(r"(?i)(password|secret|token)\s*[:=]\s*['\"][^'\"]+", content):
            risks.append("Möglicher hartkodierter geheimer Wert.")
        return risks[:25]

    def _iter_project_files(self, root: Path):
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
        for candidate in root.rglob("*"):
            if any(part in skip_dirs for part in candidate.parts):
                continue
            if candidate.is_file():
                yield candidate

    def _relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    @staticmethod
    def _central_modules(files: list[dict[str, Any]]) -> list[str]:
        scored = sorted(files, key=lambda item: len(item.get("symbols", {}).get("functions", [])) + len(item.get("symbols", {}).get("classes", [])) + len(item.get("entrypoints", [])), reverse=True)
        return [item["path"] for item in scored[:10]]

    @staticmethod
    def _start_commands(files: list[dict[str, Any]], configs: list[str]) -> list[str]:
        commands = []
        paths = {item["path"] for item in files}
        if "package.json" in {Path(item).name for item in configs}:
            commands.append("npm test / npm run dev prüfen")
        if any(Path(item).name == "pyproject.toml" for item in configs):
            commands.append("python -m pytest prüfen")
        if any(Path(item).name in {"main.py", "__main__.py"} for item in paths):
            commands.append("python <entrypoint>.py")
        return commands

    @staticmethod
    def _architecture_summary(languages: Counter[str], entrypoints: list[str], tests: list[str], configs: list[str], docs: list[str]) -> str:
        main = languages.most_common(1)[0][0] if languages else "unbekannt"
        return (
            f"Hauptsprache: {main}. Einstiegspunkte: {len(set(entrypoints))}. "
            f"Tests: {len(set(tests))}. Konfigurationen: {len(set(configs))}. Dokumente: {len(set(docs))}."
        )

    @staticmethod
    def _extract_path(text: str) -> str:
        quoted = re.search(r'"([^"]+)"|\'([^\']+)\'', text or "")
        if quoted:
            return quoted.group(1) or quoted.group(2)
        windows_path = re.search(r"(?i)\b[a-z]:[\\/][^\s\"']+", text or "")
        if windows_path:
            return windows_path.group(0).rstrip(".,;:!?)]}")
        match = re.search(r"(?:analysiere code|analysiere projekt|erkläre code|erklaere code|finde einstiegspunkte|erstelle projektkarte|welche sprache ist|codeagent)\s+(.+)$", text or "", flags=re.I)
        if match:
            return match.group(1).strip()
        return (text or "").split()[-1] if (text or "").split() else ""

    def _log(self, result: dict[str, Any]) -> None:
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": result.get("status"),
            "source_path": result.get("source_path"),
            "language": result.get("language"),
            "file_type": result.get("file_type"),
            "errors": result.get("errors", []),
            "export_path": result.get("export_path", ""),
            "read_only": True,
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    @staticmethod
    def format_file(result: dict[str, Any]) -> str:
        if result.get("status") != "ok":
            return "\n".join([
                "CodeAgent: Codeanalyse nicht durchgeführt.",
                f"- Pfad: {result.get('source_path') or '-'}",
                f"- Fehler: {'; '.join(result.get('errors') or ['unbekannt'])}",
                "- read-only: ja",
            ])
        symbols = result.get("detected_symbols", {})
        return "\n".join([
            "CodeAgent: Datei analysiert.",
            f"- Datei: {result.get('source_path')}",
            f"- Sprache: {result.get('language')}",
            f"- Dateityp: {result.get('file_type')}",
            f"- Funktionen: {len(symbols.get('functions', []))}",
            f"- Klassen: {len(symbols.get('classes', []))}",
            f"- Imports/Dependencies: {len(result.get('imports', []))}",
            f"- Einstiegspunkte: {len(result.get('entrypoints', []))}",
            f"- Risiken: {len(result.get('risks', []))}",
            f"- JSON-Export: {result.get('export_path') or '-'}",
            f"- Zusammenfassung: {result.get('summary')}",
            "- read-only: ja",
        ])

    @staticmethod
    def format_project(result: dict[str, Any]) -> str:
        if result.get("status") != "ok":
            return CodeAgentService.format_file(result)
        project = result.get("project_map", {})
        return "\n".join([
            "CodeAgent: Projektkarte erstellt.",
            f"- Pfad: {result.get('source_path')}",
            f"- Hauptsprache: {result.get('language')}",
            f"- analysierte Dateien: {project.get('total_files_analyzed', 0)}",
            "- Sprachen: " + json.dumps(project.get("languages", {}), ensure_ascii=False, sort_keys=True),
            f"- Einstiegspunkte: {len(project.get('important_entrypoints', []))}",
            f"- Testdateien/-ordner: {len(project.get('test_folders_or_files', []))}",
            f"- Konfigurationen: {len(project.get('configuration_files', []))}",
            f"- Risiken: {len(result.get('risks', []))}",
            f"- JSON-Export: {result.get('export_path') or '-'}",
            f"- Architektur: {project.get('architecture_summary', '-')}",
            "- read-only: ja",
        ])

    @staticmethod
    def format_entrypoints(result: dict[str, Any]) -> str:
        if result.get("status") != "ok":
            return CodeAgentService.format_file(result)
        entrypoints = result.get("project_map", {}).get("important_entrypoints", result.get("entrypoints", []))
        lines = ["CodeAgent: Einstiegspunkte erkannt:"]
        lines.extend(f"- {item}" for item in entrypoints[:20])
        if len(lines) == 1:
            lines.append("- keine eindeutigen Einstiegspunkte erkannt")
        lines.append("- read-only: ja")
        return "\n".join(lines)
