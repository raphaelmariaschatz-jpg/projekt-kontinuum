# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import hashlib
from datetime import datetime
from pathlib import Path


class DevelopmentTools:
    """Controlled programming, testing, and Git workspace for Kontinuum."""

    DEFAULT_CONFIG = {
        "enabled": True,
        "workspace": "13_tools/development_sandbox",
        "codex_sandbox": "workspace-write",
        "codex_timeout_seconds": 900,
        "test_timeout_seconds": 120,
        "max_output_characters": 20000,
        "allow_git_snapshots": True,
        "allow_self_extension": True,
        "full_test_timeout_seconds": 600,
        "max_changed_files": 100,
        "max_changed_file_bytes": 1000000,
        "promotion_roots": [
            "01_system/kontinuum",
            "11_gui",
            "14_documents",
            "17_tests",
            "22_project_chronicle",
        ],
        "promotion_extensions": [".py", ".md", ".txt"],
        "require_test_changes": True,
        "require_new_test_file": True,
        "protected_paths": [
            "01_system/kontinuum/core/auth.py",
            "01_system/kontinuum/tools/development_tools.py",
            "01_system/kontinuum/agents/development_agent.py",
            "24_config/development_sandbox.json",
        ],
        "forbidden_python_tokens": [
            "import os",
            "from os",
            "import subprocess",
            "from subprocess",
            "import shutil",
            "from shutil",
            "import socket",
            "from socket",
            "import ctypes",
            "from ctypes",
            "import winreg",
            "from winreg",
            "import urllib",
            "from urllib",
            "import requests",
            "from requests",
            "__import__(",
            "eval(",
            "exec(",
            "open(",
        ],
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()
        self.config_path = self.project_root / "24_config" / "development_sandbox.json"
        self.config = self._load_config()
        self.workspace = (self.project_root / str(self.config["workspace"])).resolve()
        if self.project_root not in self.workspace.parents:
            raise ValueError("Die Entwicklungssandbox muss innerhalb der Projektwurzel liegen.")
        self.workspace.mkdir(parents=True, exist_ok=True)
        self._ensure_workspace_files()

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    def _ensure_workspace_files(self) -> None:
        readme = self.workspace / "README.md"
        if not readme.exists():
            readme.write_text(
                "# Kontinuum Development Sandbox\n\n"
                "Dieser Bereich ist Kontinuums isolierter Programmier- und Testarbeitsplatz.\n"
                "Aenderungen werden nicht automatisch in den aktiven Projektkern uebernommen.\n",
                encoding="utf-8",
            )
        gitignore = self.workspace / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("__pycache__/\n*.pyc\n.coverage\n.pytest_cache/\n", encoding="utf-8")

    def _git_command(self) -> str | None:
        candidates = [
            shutil.which("git"),
            os.environ.get("KONTINUUM_GIT_COMMAND"),
            str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Git" / "cmd" / "git.exe"),
            "C:/Program Files/Git/cmd/git.exe",
        ]
        return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)

    def _codex_command(self) -> str | None:
        integrated = self.project_root / "13_tools" / "codex_cli" / "codex.exe"
        return str(integrated) if integrated.is_file() else shutil.which("codex")

    def _run(
        self,
        command: list[str],
        timeout: int,
        cwd: Path | None = None,
        extra_environment: dict[str, str] | None = None,
    ) -> dict:
        environment = os.environ.copy()
        git = self._git_command()
        if git:
            git_cmd = str(Path(git).parent)
            git_bin = str(Path(git).parent.parent / "bin")
            environment["PATH"] = os.pathsep.join([git_cmd, git_bin, environment.get("PATH", "")])
        environment.update(extra_environment or {})
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.workspace,
                capture_output=True,
                text=True,
                errors="replace",
                env=environment,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": f"Ausfuehrung nach {timeout} Sekunden beendet."}
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "message": f"Ausfuehrung fehlgeschlagen: {exc}"}
        output = ((result.stdout or "") + ("\n" + result.stderr if result.stderr else "")).strip()
        limit = int(self.config["max_output_characters"])
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "output": output[:limit] + ("\n... Ausgabe gekuerzt ..." if len(output) > limit else ""),
        }

    def initialize_git(self) -> dict:
        git = self._git_command()
        if not git:
            return {"ok": False, "message": "Git wurde nicht gefunden."}
        if not (self.workspace / ".git").is_dir():
            initialized = self._run(self._git_args(git, "init", "-b", "main"), 30)
            if not initialized["ok"]:
                return initialized
        self._run(self._git_args(git, "config", "user.name", "Kontinuum"), 10)
        self._run(self._git_args(git, "config", "user.email", "kontinuum@local"), 10)
        return {"ok": True, "git": git, "workspace": str(self.workspace)}

    def status(self) -> dict:
        git = self.initialize_git()
        codex = self._codex_command()
        return {
            "available": bool(self.config["enabled"]),
            "workspace": str(self.workspace),
            "codex_available": bool(codex),
            "codex_sandbox": self.config["codex_sandbox"],
            "git_available": bool(git.get("ok")),
            "git": git.get("git"),
            "promotion": "superadmin-controlled",
            "message": (
                f"Entwicklungssandbox: {self.workspace}. "
                f"Codex: {'bereit' if codex else 'nicht verfuegbar'} ({self.config['codex_sandbox']}). "
                f"Git: {'bereit' if git.get('ok') else 'nicht verfuegbar'}. "
                "Self-Extension in den aktiven Kern ist nur nach Superadmin-Autorisierung und Pflichtpruefungen moeglich."
            ),
        }

    def develop(self, task: str) -> dict:
        if not self.config["enabled"]:
            return {"ok": False, "message": "Entwicklungssandbox ist deaktiviert."}
        task = (task or "").strip()
        if not task:
            return {"ok": False, "message": "Kein Entwicklungsauftrag angegeben."}
        codex = self._codex_command()
        if not codex:
            return {"ok": False, "message": "Codex-CLI wurde nicht gefunden."}
        self.initialize_git()
        prompt = (
            "Arbeite ausschliesslich in der aktuellen Entwicklungssandbox. "
            "Programmiere die angeforderte Loesung, fuehre passende Tests aus und dokumentiere das Ergebnis. "
            "Greife nicht auf den aktiven Kontinuum-Kern ausserhalb dieses Arbeitsbereichs schreibend zu. "
            f"Auftrag: {task}"
        )
        result = self._run(
            [codex, "exec", "--sandbox", str(self.config["codex_sandbox"]), "-C", str(self.workspace), prompt],
            int(self.config["codex_timeout_seconds"]),
        )
        tests = self.test()
        result["tests"] = tests
        test_output = tests.get("output") or tests.get("message") or "Kein Testergebnis."
        result["output"] = f"{result.get('output', '').strip()}\n\n--- Kontrollierter Sandbox-Test ---\n{test_output}".strip()
        result["ok"] = bool(result.get("ok")) and bool(tests.get("ok"))
        result["workspace"] = str(self.workspace)
        return result

    def self_extend(self, task: str, user: dict | None = None) -> dict:
        authorization = self._authorize_self_extension(user)
        if not authorization["ok"]:
            return authorization
        task = (task or "").strip()
        if not task:
            return {"ok": False, "message": "Kein Programmierauftrag angegeben."}

        candidate = self.workspace / "self_extension_candidate"
        if candidate.exists():
            shutil.rmtree(candidate)
        self._copy_candidate(candidate)
        before = self._manifest(candidate)
        candidate_git = self._initialize_candidate_git(candidate)
        if not candidate_git.get("ok"):
            return {"ok": False, "message": "Kandidaten-Git konnte nicht initialisiert werden.", "git": candidate_git}
        codex = self._codex_command()
        if not codex:
            return {"ok": False, "message": "Codex-CLI wurde nicht gefunden."}
        prompt = (
            "Du erweiterst Projekt Kontinuum als geprueften Kandidaten. Arbeite ausschliesslich im aktuellen "
            "Kandidatenordner. Aendere nur vorhandene freigegebene Projektpfade. Ergaenze fuer jede "
            "Verhaltensaenderung passende Tests. Veraendere keine Authentifizierung, Sicherheitsdaten, Datenbanken "
            "oder Sicherungen. Fuehre geeignete Tests aus. Auftrag: "
            f"{task}"
        )
        development = self._run(
            [codex, "exec", "--sandbox", str(self.config["codex_sandbox"]), "-C", str(candidate), prompt],
            int(self.config["codex_timeout_seconds"]),
            cwd=candidate,
        )
        after = self._manifest(candidate)
        changes = self._changed_files(before, after)
        checks = self._preflight_candidate(candidate, changes, before)
        if not development.get("ok") or not checks.get("ok"):
            return {
                "ok": False,
                "message": "Self-Extension nicht freigegeben: Entwicklung oder Vorpruefung fehlgeschlagen.",
                "development": development,
                "checks": checks,
                "changes": changes,
            }

        snapshot = self._candidate_snapshot(candidate, f"Self-extension candidate: {task[:80]}")
        promotion = self._promote_with_rollback(candidate, changes)
        self._audit_self_extension(user or {}, task, promotion)
        promotion.update({"development": development, "checks": checks, "candidate_snapshot": snapshot})
        return promotion

    def _authorize_self_extension(self, user: dict | None) -> dict:
        user = user or {}
        allowed = (
            bool(self.config.get("allow_self_extension"))
            and bool(user.get("authenticated"))
            and bool(user.get("is_superadmin"))
            and str(user.get("role", "")).upper() == "SUPERADMIN"
            and bool((user.get("permissions") or {}).get("can_execute_admin_commands"))
        )
        if allowed:
            return {"ok": True}
        return {
            "ok": False,
            "message": (
                "Self-Extension ist ausschließlich für einen verifiziert angemeldeten SUPERADMIN "
                "mit Admin-Ausführungsberechtigung erlaubt."
            ),
        }

    def _copy_candidate(self, candidate: Path) -> None:
        candidate.mkdir(parents=True, exist_ok=True)
        for relative in self.config["promotion_roots"]:
            source = self.project_root / relative
            destination = candidate / relative
            if source.is_dir():
                shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"), dirs_exist_ok=True)

    def _initialize_candidate_git(self, candidate: Path) -> dict:
        git = self._git_command()
        if not git:
            return {"ok": False, "message": "Git wurde nicht gefunden."}
        initialized = self._run(self._git_args(git, "init", "-b", "main"), 30, cwd=candidate)
        if not initialized.get("ok"):
            return initialized
        self._run(self._git_args(git, "config", "user.name", "Kontinuum"), 10, cwd=candidate)
        self._run(self._git_args(git, "config", "user.email", "kontinuum@local"), 10, cwd=candidate)
        self._run(self._git_args(git, "add", "--all"), 60, cwd=candidate)
        return self._run(self._git_args(git, "commit", "-m", "Self-extension candidate baseline"), 120, cwd=candidate)

    def _candidate_snapshot(self, candidate: Path, message: str) -> dict:
        git = self._git_command()
        if not git:
            return {"ok": False, "message": "Git wurde nicht gefunden."}
        staged = self._run(self._git_args(git, "add", "--all"), 60, cwd=candidate)
        if not staged.get("ok"):
            return staged
        return self._run(self._git_args(git, "commit", "-m", message), 120, cwd=candidate)

    def _git_args(self, git: str, *arguments: str) -> list[str]:
        disabled_hooks = self.project_root / "13_tools" / "git_hooks_disabled"
        disabled_hooks.mkdir(parents=True, exist_ok=True)
        return [git, "-c", f"core.hooksPath={disabled_hooks}", *arguments]

    @staticmethod
    def _hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
        return digest.hexdigest()

    def _manifest(self, root: Path) -> dict[str, str]:
        return {
            path.relative_to(root).as_posix(): self._hash(path)
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and ".git" not in path.parts
        }

    @staticmethod
    def _changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
        return sorted(path for path, digest in after.items() if before.get(path) != digest)

    def _preflight_candidate(
        self,
        candidate: Path,
        changes: list[str],
        baseline: dict[str, str] | None = None,
    ) -> dict:
        if not changes:
            return {"ok": False, "message": "Der Programmierauftrag hat keine Dateien geändert."}
        if len(changes) > int(self.config["max_changed_files"]):
            return {"ok": False, "message": "Zu viele geänderte Dateien.", "changes": changes}
        roots = tuple(str(root).replace("\\", "/").rstrip("/") + "/" for root in self.config["promotion_roots"])
        extensions = {str(value).casefold() for value in self.config["promotion_extensions"]}
        protected = {str(value).replace("\\", "/") for value in self.config["protected_paths"]}
        problems = []
        if self.config.get("require_test_changes") and not any(path.startswith("17_tests/") for path in changes):
            problems.append("Jede Self-Extension muss mindestens eine geänderte Testdatei enthalten.")
        if self.config.get("require_new_test_file"):
            baseline = baseline or {}
            changed_tests = [path for path in changes if path.startswith("17_tests/")]
            if not any(path not in baseline for path in changed_tests):
                problems.append("Jede Self-Extension muss mindestens eine neue Testdatei ergänzen.")
            modified_tests = [path for path in changed_tests if path in baseline]
            if modified_tests:
                problems.append("Bestehende Tests dürfen durch automatische Self-Extension nicht verändert werden.")
        for relative in changes:
            path = candidate / relative
            if relative in protected:
                problems.append(f"Geschützter Self-Extension-Pfad: {relative}")
            if not relative.startswith(roots):
                problems.append(f"Nicht freigegebener Pfad: {relative}")
            if path.suffix.casefold() not in extensions:
                problems.append(f"Nicht freigegebener Dateityp: {relative}")
            if path.stat().st_size > int(self.config["max_changed_file_bytes"]):
                problems.append(f"Datei zu groß: {relative}")
            if path.is_symlink():
                problems.append(f"Symbolischer Link nicht erlaubt: {relative}")
            if any(part.casefold() in {"10_security", "32_data", "09_backups", ".git"} for part in Path(relative).parts):
                problems.append(f"Sicherheitskritischer Pfad: {relative}")
            if path.suffix.casefold() == ".py":
                try:
                    source = path.read_text(encoding="utf-8").casefold()
                except (OSError, UnicodeError):
                    problems.append(f"Python-Datei nicht sicher lesbar: {relative}")
                    continue
                for token in self.config["forbidden_python_tokens"]:
                    if str(token).casefold() in source:
                        problems.append(f"Automatisch nicht erlaubtes Python-Merkmal `{token}` in: {relative}")
        if problems:
            return {"ok": False, "message": "\n".join(problems), "changes": changes}

        python_files = [str(candidate / path) for path in changes if path.casefold().endswith(".py")]
        syntax = {"ok": True, "output": "Keine geänderten Python-Dateien."}
        if python_files:
            syntax = self._run([sys.executable, "-m", "py_compile", *python_files], 120, cwd=candidate)
        candidate_tests = self._run_candidate_tests(candidate)
        return {
            "ok": bool(syntax.get("ok")) and bool(candidate_tests.get("ok")),
            "syntax": syntax,
            "candidate_tests": candidate_tests,
            "changes": changes,
        }

    def _run_candidate_tests(self, candidate: Path) -> dict:
        test_files = sorted((candidate / "17_tests").glob("test_*_23.py"))
        if not test_files:
            return {"ok": False, "message": "Keine Kandidatentests gefunden."}
        outputs = []
        environment = {"KONTINUUM_ROOT": str(candidate), "PYTHONPATH": str(candidate / "01_system")}
        for test_file in test_files:
            result = self._run(
                [sys.executable, str(test_file)],
                int(self.config["test_timeout_seconds"]),
                cwd=candidate,
                extra_environment=environment,
            )
            outputs.append(f"=== {test_file.name} ===\n{result.get('output') or result.get('message', '')}")
            if not result.get("ok"):
                return {"ok": False, "output": "\n".join(outputs)}
        return {"ok": True, "output": "\n".join(outputs)}

    def _promote_with_rollback(self, candidate: Path, changes: list[str]) -> dict:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.project_root / "09_backups" / f"self_extension_{stamp}"
        backup.mkdir(parents=True, exist_ok=True)
        existing = []
        created = []
        full_tests = {}
        try:
            for relative in changes:
                target = self.project_root / relative
                source = candidate / relative
                if target.exists():
                    destination = backup / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, destination)
                    existing.append(relative)
                else:
                    created.append(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            full_tests = self._run_full_project_tests()
            if not full_tests.get("ok"):
                raise RuntimeError("Vollständige Testsuite fehlgeschlagen.")
        except Exception as exc:
            for relative in existing:
                shutil.copy2(backup / relative, self.project_root / relative)
            for relative in created:
                target = self.project_root / relative
                if target.exists():
                    target.unlink()
            return {
                "ok": False,
                "message": f"Self-Extension zurückgerollt: {exc}",
                "backup": str(backup),
                "changes": changes,
                "full_tests": full_tests,
            }
        return {
            "ok": True,
            "message": "Self-Extension geprüft, übernommen und durch die vollständige Testsuite bestätigt.",
            "backup": str(backup),
            "changes": changes,
            "full_tests": full_tests,
        }

    def _run_full_project_tests(self) -> dict:
        runner = self.project_root / "16_installation" / "TEST_KONTINUUM_32_3.bat"
        return self._run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(runner)],
            int(self.config["full_test_timeout_seconds"]),
            cwd=self.project_root,
            extra_environment={"KONTINUUM_ROOT": str(self.project_root), "PYTHONPATH": str(self.project_root / "01_system")},
        )

    def _audit_self_extension(self, user: dict, task: str, result: dict) -> None:
        audit = self.project_root / "27_logs" / "self_extension_audit.log"
        audit.parent.mkdir(parents=True, exist_ok=True)
        line = (
            f"{datetime.now().astimezone().isoformat()} | success={bool(result.get('ok'))} | "
            f"user={user.get('username', '')} | changes={len(result.get('changes', []))} | "
            f"task={' '.join(task.split())[:200]}\n"
        )
        with audit.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def test(self) -> dict:
        result = self._run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(self.workspace), "-p", "test_*.py", "-v"],
            int(self.config["test_timeout_seconds"]),
        )
        if result.get("ok") and "Ran 0 tests" in result.get("output", ""):
            result["ok"] = False
            result["message"] = "Keine Sandbox-Tests gefunden. Entwicklungsauftraege muessen passende Tests enthalten."
        result["workspace"] = str(self.workspace)
        return result

    def git_status(self) -> dict:
        initialized = self.initialize_git()
        if not initialized.get("ok"):
            return initialized
        return self._run(self._git_args(initialized["git"], "status", "--short", "--branch"), 30)

    def git_snapshot(self, message: str = "") -> dict:
        if not self.config["allow_git_snapshots"]:
            return {"ok": False, "message": "Git-Snapshots sind deaktiviert."}
        initialized = self.initialize_git()
        if not initialized.get("ok"):
            return initialized
        git = initialized["git"]
        staged = self._run(self._git_args(git, "add", "--all"), 30)
        if not staged["ok"]:
            return staged
        status = self._run(self._git_args(git, "status", "--porcelain"), 30)
        if not status.get("output"):
            return {"ok": True, "message": "Keine Aenderungen fuer einen Git-Snapshot vorhanden."}
        label = (message or "").strip() or f"Kontinuum snapshot {datetime.now().isoformat(timespec='seconds')}"
        return self._run(self._git_args(git, "commit", "-m", label), 60)
