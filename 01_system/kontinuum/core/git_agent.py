# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GitAgentService:
    VERSION = "1.0"
    MODE = "diagnostic_read_only"
    COMMAND_MARKERS = (
        "git status",
        "git repo prüfen",
        "git repo prufen",
        "git repo pruefen",
        "git historie",
        "git snapshot report",
        "gitagentstatus",
        "gitstatus",
    )
    DEFAULT_CONFIG = {
        "enabled": True,
        "mode": MODE,
        "read_only": True,
        "allow_mutating_commands": False,
        "write_audit_logs": False,
        "allowed_roots": ["."],
    }

    def __init__(self, path_tools, storage: Any | None = None, canonical_engine: Any | None = None):
        self.path_tools = path_tools
        self.storage = storage
        self.canonical_engine = canonical_engine
        self.root = path_tools.project_root().resolve()
        self.config_path = path_tools.paths()["config"] / "git_agent_1_0.json"
        self.config = self._load_config()
        self.log_path = path_tools.paths()["logs"] / "git_agent_1_0.jsonl"
        self.report_dir = path_tools.paths()["reports"] / "git"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.touch(exist_ok=True)
        self.git_executable = self._find_git()
        self._last_report: dict[str, Any] = {}
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

    def _find_git(self) -> str:
        configured = os.environ.get("KONTINUUM_GIT_EXE") or self.config.get("git_executable", "")
        if configured and Path(configured).is_file():
            return str(Path(configured))
        return shutil.which("git") or ""

    @classmethod
    def looks_like_git_command(cls, text: str) -> bool:
        lower = (text or "").casefold().strip()
        return any(marker in lower for marker in cls.COMMAND_MARKERS)

    def handle_command(self, text: str) -> dict[str, Any]:
        lower = (text or "").casefold().strip(" .!?")
        path = self._extract_path(text)
        if lower in {"gitagentstatus", "gitstatus"}:
            return {"ok": True, "message": self.format_status(), "result": self.status()}
        if lower.startswith("git historie"):
            result = self.list_recent_commits(path)
            return {"ok": result["status"] == "ok", "message": self.format_history(result), "result": result}
        if lower.startswith("git snapshot report"):
            result = self.create_git_snapshot_report(path)
            return {"ok": result["status"] == "ok", "message": self.format_snapshot(result), "result": result}
        if "repo" in lower and ("prüfen" in lower or "pruefen" in lower):
            result = self.is_git_repo(path)
            return {"ok": result["status"] == "ok", "message": self.format_repo_check(result), "result": result}
        result = self.get_status(path)
        return {"ok": result["status"] == "ok", "message": self.format_status_result(result), "result": result}

    def status(self) -> dict[str, Any]:
        return {
            "active": bool(self.config.get("enabled", False)),
            "mode": self.config.get("mode", self.MODE),
            "read_only": True,
            "git_available": bool(self.git_executable),
            "git_executable": self.git_executable,
            "allowed_roots": [str(path) for path in self._allowed_roots()],
            "last_repo_path": self._last_report.get("repo_path", ""),
            "last_status": self._last_report.get("status", ""),
            "last_errors": self._last_errors[-5:],
        }

    def format_status(self) -> str:
        status = self.status()
        errors = "; ".join(status["last_errors"]) if status["last_errors"] else "-"
        return "\n".join([
            "GitAgent 1.0 Status:",
            f"- GitAgent aktiv: {'ja' if status['active'] else 'nein'}",
            f"- Modus: {status['mode']}",
            f"- read-only: {'ja' if status['read_only'] else 'nein'}",
            f"- Git verfügbar: {'ja' if status['git_available'] else 'nein'}",
            f"- Git-Pfad: {status['git_executable'] or '-'}",
            "- erlaubte Verzeichnisse: " + "; ".join(status["allowed_roots"]),
            f"- letztes Repository: {status['last_repo_path'] or '-'}",
            f"- letzter Status: {status['last_status'] or '-'}",
            f"- letzte Fehler: {errors}",
        ])

    def is_git_repo(self, path: str = "") -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._finish(self._error_result(result, str(exc)), "GIT_REPO_CHECK_BLOCKED", "medium")
        result["repo_path"] = str(resolved)
        repo = self._repo_info(resolved)
        result.update({"status": "ok", "is_git_repo": repo["is_git_repo"], "repo_path": repo.get("repo_path") or str(resolved)})
        result["warnings"].extend(repo.get("warnings", []))
        return self._finish(result, "GIT_REPO_CHECKED", "info")

    def get_status(self, path: str = "") -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._finish(self._error_result(result, str(exc)), "GIT_STATUS_BLOCKED", "medium")
        result["repo_path"] = str(resolved)
        if not self.git_executable:
            return self._finish(self._error_result(result, "Git executable nicht gefunden."), "GIT_STATUS_FAILED", "medium")
        repo = self._repo_info(resolved)
        if not repo.get("is_git_repo"):
            result.update({"status": "ok", "is_git_repo": False})
            result["warnings"].extend(repo.get("warnings", ["Kein Git-Repository erkannt."]))
            return self._finish(result, "GIT_STATUS_READ", "info")
        result["repo_path"] = repo.get("repo_path") or str(resolved)
        branch = self.get_current_branch(str(resolved))
        result["current_branch"] = branch.get("current_branch", "")
        status = self._git(resolved, ["status", "--porcelain=v1", "-b"])
        if status["returncode"] != 0:
            return self._finish(self._error_result(result, status["stderr"] or "Git status fehlgeschlagen."), "GIT_STATUS_FAILED", "medium")
        result["is_git_repo"] = True
        self._parse_status(status["stdout"], result)
        result["status"] = "ok"
        result["clean_worktree"] = not (result["changed_files"] or result["untracked_files"] or result["deleted_files"])
        return self._finish(result, "GIT_STATUS_READ", "info")

    def get_current_branch(self, path: str = "") -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._error_result(result, str(exc))
        if not self.git_executable:
            return self._error_result(result, "Git executable nicht gefunden.")
        command = self._git(resolved, ["branch", "--show-current"])
        result["repo_path"] = str(resolved)
        if command["returncode"] == 0:
            result.update({"status": "ok", "current_branch": command["stdout"].strip()})
        else:
            result = self._error_result(result, command["stderr"] or "Branch konnte nicht gelesen werden.")
        return result

    def list_recent_commits(self, path: str = "", limit: int = 10) -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._finish(self._error_result(result, str(exc)), "GIT_HISTORY_BLOCKED", "medium")
        result["repo_path"] = str(resolved)
        if not self.git_executable:
            return self._finish(self._error_result(result, "Git executable nicht gefunden."), "GIT_HISTORY_FAILED", "medium")
        command = self._git(resolved, ["log", f"-{max(1, min(int(limit), 50))}", "--date=iso-strict", "--pretty=format:%H%x1f%h%x1f%ad%x1f%an%x1f%s"])
        if command["returncode"] != 0:
            return self._finish(self._error_result(result, command["stderr"] or "Git-Historie konnte nicht gelesen werden."), "GIT_HISTORY_FAILED", "medium")
        result["status"] = "ok"
        result["is_git_repo"] = True
        result["recent_commits"] = [
            {"hash": parts[0], "short_hash": parts[1], "date": parts[2], "author": parts[3], "subject": parts[4]}
            for line in command["stdout"].splitlines()
            if len((parts := line.split("\x1f"))) == 5
        ]
        return self._finish(result, "GIT_HISTORY_READ", "info")

    def list_tags(self, path: str = "") -> dict[str, Any]:
        result = self._base_result(path)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            return self._error_result(result, str(exc))
        if not self.git_executable:
            return self._error_result(result, "Git executable nicht gefunden.")
        command = self._git(resolved, ["tag", "--list", "--sort=-creatordate"])
        result["repo_path"] = str(resolved)
        if command["returncode"] == 0:
            result.update({"status": "ok", "tags": [line.strip() for line in command["stdout"].splitlines() if line.strip()]})
        else:
            result = self._error_result(result, command["stderr"] or "Tags konnten nicht gelesen werden.")
        return result

    def detect_uncommitted_changes(self, path: str = "") -> dict[str, Any]:
        return self.get_status(path)

    def create_git_snapshot_report(self, path: str = "") -> dict[str, Any]:
        status = self.get_status(path)
        commits = self.list_recent_commits(path, 10)
        tags = self.list_tags(path)
        report = {**status, "recent_commits": commits.get("recent_commits", []), "tags": tags.get("tags", [])}
        report["snapshot_report"] = {
            "summary": self._snapshot_summary(report),
            "read_only": True,
            "mutating_actions_performed": False,
        }
        self._last_report = report
        return self._finish(report, "GIT_SNAPSHOT_REPORTED", "info")

    def _parse_status(self, output: str, result: dict[str, Any]) -> None:
        for line in output.splitlines():
            if line.startswith("## "):
                result["branch_status"] = line[3:].strip()
                continue
            if not line:
                continue
            code = line[:2]
            path = line[3:].strip()
            if code == "??":
                result["untracked_files"].append(path)
            elif "D" in code:
                result["deleted_files"].append(path)
            else:
                result["changed_files"].append(path)

    def _git(self, cwd: Path, args: list[str]) -> dict[str, Any]:
        safe_args = {"rev-parse", "status", "branch", "log", "tag"}
        if not args or args[0] not in safe_args:
            return {"returncode": 1, "stdout": "", "stderr": "GitAgent erlaubt nur read-only Git-Kommandos."}
        try:
            completed = subprocess.run(
                [self.git_executable, *args],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=15,
                encoding="utf-8",
                errors="replace",
            )
            return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr.strip()}
        except Exception as exc:
            return {"returncode": 1, "stdout": "", "stderr": str(exc)}

    def _repo_info(self, resolved: Path) -> dict[str, Any]:
        if not self.git_executable:
            return {
                "is_git_repo": (resolved / ".git").exists(),
                "repo_path": str(resolved),
                "warnings": ["Git executable nicht gefunden; Repository-Erkennung nutzt nur .git-Prüfung."],
            }
        command = self._git(resolved, ["rev-parse", "--show-toplevel"])
        if command["returncode"] == 0:
            return {"is_git_repo": True, "repo_path": command["stdout"].strip() or str(resolved), "warnings": []}
        return {"is_git_repo": False, "repo_path": str(resolved), "warnings": [command["stderr"] or "Kein Git-Repository erkannt."]}

    def _base_result(self, path: str = "") -> dict[str, Any]:
        return {
            "status": "pending",
            "repo_path": str(path or self.root),
            "is_git_repo": False,
            "current_branch": "",
            "branch_status": "",
            "clean_worktree": False,
            "changed_files": [],
            "untracked_files": [],
            "deleted_files": [],
            "recent_commits": [],
            "tags": [],
            "warnings": [],
            "errors": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_name": "GitAgent",
            "read_only": True,
        }

    def _error_result(self, result: dict[str, Any], error: str) -> dict[str, Any]:
        result["status"] = "error"
        result["errors"].append(error)
        return result

    def _finish(self, result: dict[str, Any], event_type: str, severity: str) -> dict[str, Any]:
        if result.get("errors"):
            self._last_errors.append("; ".join(result["errors"]))
        self._last_report = result
        if self.config.get("write_audit_logs", False):
            self._log(result)
            self._emit_event(event_type, result, severity)
        return result

    def _resolve_path(self, value: str | Path = "") -> Path:
        raw = str(value or "").strip().strip('"')
        path = Path(raw) if raw else self.root
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

    @staticmethod
    def _extract_path(text: str) -> str:
        quoted = re.search(r'"([^"]+)"|\'([^\']+)\'', text or "")
        if quoted:
            return quoted.group(1) or quoted.group(2)
        windows_path = re.search(r"(?i)\b[a-z]:[\\/][^\s\"']+", text or "")
        if windows_path:
            return windows_path.group(0).rstrip(".,;:!?)]}")
        return ""

    def _log(self, result: dict[str, Any]) -> None:
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": result.get("status"),
            "repo_path": result.get("repo_path"),
            "is_git_repo": result.get("is_git_repo"),
            "current_branch": result.get("current_branch"),
            "changed": len(result.get("changed_files", [])),
            "untracked": len(result.get("untracked_files", [])),
            "deleted": len(result.get("deleted_files", [])),
            "errors": result.get("errors", []),
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def _emit_event(self, event_type: str, result: dict[str, Any], severity: str) -> None:
        engine = self.canonical_engine
        if not engine:
            return
        try:
            engine.ingest(
                event_type=event_type,
                source_component="git_agent",
                affected_path=result.get("repo_path", ""),
                affected_object_id=result.get("current_branch", ""),
                severity=severity,
                payload={
                    "is_git_repo": result.get("is_git_repo", False),
                    "current_branch": result.get("current_branch", ""),
                    "changed_files": len(result.get("changed_files", [])),
                    "untracked_files": len(result.get("untracked_files", [])),
                    "deleted_files": len(result.get("deleted_files", [])),
                    "read_only": True,
                },
                provenance={"agent": "GitAgentService", "version": self.VERSION},
                governance_context={"git": True, "requires_review": False, "read_only": True},
            )
        except Exception as exc:
            self._last_errors.append(f"Canonical Event Bus: {exc}")

    @staticmethod
    def _snapshot_summary(report: dict[str, Any]) -> str:
        if not report.get("is_git_repo"):
            return "Kein Git-Repository erkannt."
        if report.get("clean_worktree"):
            return "Git-Arbeitsbaum ist sauber."
        return (
            f"Git-Arbeitsbaum hat {len(report.get('changed_files', []))} geänderte, "
            f"{len(report.get('untracked_files', []))} neue und "
            f"{len(report.get('deleted_files', []))} gelöschte Datei(en)."
        )

    @staticmethod
    def format_status_result(result: dict[str, Any]) -> str:
        if result.get("status") == "error":
            return "GitAgent: Status konnte nicht gelesen werden.\n- Fehler: " + "; ".join(result.get("errors", []))
        if not result.get("is_git_repo"):
            return f"GitAgent: Kein Git-Repository erkannt.\n- Pfad: {result.get('repo_path')}\n- read-only: ja"
        return "\n".join([
            "GitAgent: Repository-Status gelesen.",
            f"- Repository: {result.get('repo_path')}",
            f"- Branch: {result.get('current_branch') or '-'}",
            f"- sauberer Arbeitsbaum: {'ja' if result.get('clean_worktree') else 'nein'}",
            f"- geänderte Dateien: {len(result.get('changed_files', []))}",
            f"- neue Dateien: {len(result.get('untracked_files', []))}",
            f"- gelöschte Dateien: {len(result.get('deleted_files', []))}",
            "- read-only: ja",
        ])

    @staticmethod
    def format_history(result: dict[str, Any]) -> str:
        if result.get("status") == "error":
            return "GitAgent: Historie konnte nicht gelesen werden.\n- Fehler: " + "; ".join(result.get("errors", []))
        lines = ["GitAgent: Letzte Commits:"]
        for commit in result.get("recent_commits", [])[:10]:
            lines.append(f"- {commit.get('short_hash')} | {commit.get('date')} | {commit.get('subject')}")
        if len(lines) == 1:
            lines.append("- keine Commits gefunden")
        return "\n".join(lines)

    @staticmethod
    def format_snapshot(result: dict[str, Any]) -> str:
        return "\n".join([
            "GitAgent Snapshot Report:",
            f"- Repository: {result.get('repo_path')}",
            f"- Git-Repository: {'ja' if result.get('is_git_repo') else 'nein'}",
            f"- Branch: {result.get('current_branch') or '-'}",
            f"- Tags: {len(result.get('tags', []))}",
            f"- letzte Commits: {len(result.get('recent_commits', []))}",
            f"- Zusammenfassung: {result.get('snapshot_report', {}).get('summary', '-')}",
            "- mutierende Aktionen ausgeführt: nein",
        ])

    @staticmethod
    def format_repo_check(result: dict[str, Any]) -> str:
        if result.get("status") == "error":
            return "GitAgent: Repository-Prüfung blockiert.\n- Fehler: " + "; ".join(result.get("errors", []))
        return "\n".join([
            "GitAgent: Repository-Prüfung abgeschlossen.",
            f"- Pfad: {result.get('repo_path')}",
            f"- Git-Repository: {'ja' if result.get('is_git_repo') else 'nein'}",
            "- read-only: ja",
        ])
