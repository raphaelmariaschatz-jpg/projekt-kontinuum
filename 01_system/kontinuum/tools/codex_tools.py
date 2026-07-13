# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class CodexTools:
    """Controlled bridge to a separately executable OpenAI Codex CLI."""

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
        self.command = os.environ.get("KONTINUUM_CODEX_COMMAND", "codex")
        self.sandbox = os.environ.get("KONTINUUM_CODEX_SANDBOX", "read-only")
        self.timeout = int(os.environ.get("KONTINUUM_CODEX_TIMEOUT", "600"))

    def _resolved_command(self) -> str | None:
        configured = Path(self.command)
        if configured.is_file():
            return str(configured)
        integrated = self.root / "13_tools" / "codex_cli" / "codex.exe"
        if integrated.is_file():
            return str(integrated)
        return shutil.which(self.command)

    def status(self) -> dict:
        executable = self._resolved_command()
        if not executable:
            return {
                "available": False,
                "message": "Codex-CLI nicht ausführbar. KONTINUUM_CODEX_COMMAND auf eine separat installierte Codex-CLI setzen.",
            }
        try:
            result = subprocess.run(
                [executable, "--version"],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {"available": False, "command": executable, "message": f"Codex-CLI nicht startbar: {exc}"}
        output = (result.stdout or result.stderr).strip()
        return {
            "available": result.returncode == 0,
            "command": executable,
            "sandbox": self.sandbox,
            "version": output,
            "message": output or f"Codex-CLI beendete sich mit Code {result.returncode}.",
        }

    def execute(self, prompt: str) -> dict:
        executable = self._resolved_command()
        if not executable:
            return self.status()
        command = [
            executable,
            "exec",
            "--sandbox",
            self.sandbox,
            "--skip-git-repo-check",
            "-C",
            str(self.root),
            prompt,
        ]
        try:
            result = subprocess.run(
                command,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {"available": False, "message": f"Codex-Aufruf fehlgeschlagen: {exc}"}
        return {
            "available": result.returncode == 0,
            "returncode": result.returncode,
            "answer": (result.stdout or result.stderr).strip(),
            "sandbox": self.sandbox,
        }
