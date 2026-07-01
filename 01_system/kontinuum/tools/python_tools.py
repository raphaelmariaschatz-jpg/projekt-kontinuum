from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


class PythonTools:
    DEFAULT_CONFIG = {
        "enabled": True,
        "timeout_seconds": 15,
        "max_output_characters": 12000,
        "isolated_mode": True,
        "workspace": "13_tools/python_workspace",
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "24_config" / "python_runtime.json"
        self.config = self._load_config()
        self.workspace = self.project_root / str(self.config["workspace"])
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        config["enabled"] = os.getenv("KONTINUUM_PYTHON_ENABLED", str(config["enabled"])).casefold() not in {
            "0",
            "false",
            "no",
            "off",
        }
        return config

    def status(self) -> dict:
        executable = Path(sys.executable)
        if not self.config["enabled"]:
            return {"available": False, "enabled": False, "message": "Python-Ausfuehrung ist deaktiviert."}
        if not executable.is_file():
            return {"available": False, "enabled": True, "message": "Python-Laufzeit wurde nicht gefunden."}
        try:
            result = subprocess.run(
                [str(executable), "--version"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {"available": False, "enabled": True, "message": f"Python ist nicht startbar: {exc}"}
        version = (result.stdout or result.stderr).strip()
        return {
            "available": result.returncode == 0,
            "enabled": True,
            "executable": str(executable),
            "version": version,
            "workspace": str(self.workspace),
            "isolated_mode": bool(self.config["isolated_mode"]),
            "message": f"Python direkt integriert: {version}. Arbeitsordner: {self.workspace}",
        }

    def execute(self, code: str) -> dict:
        if not self.config["enabled"]:
            return self.status()
        code = (code or "").strip()
        if not code:
            return {"available": True, "ok": False, "message": "Kein Python-Code angegeben."}

        command = [sys.executable]
        if self.config["isolated_mode"]:
            command.append("-I")
        command.extend(["-c", code])
        try:
            result = subprocess.run(
                command,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=int(self.config["timeout_seconds"]),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "available": True,
                "ok": False,
                "message": f"Python-Ausfuehrung nach {self.config['timeout_seconds']} Sekunden beendet.",
            }
        except (OSError, subprocess.SubprocessError) as exc:
            return {"available": False, "ok": False, "message": f"Python-Ausfuehrung fehlgeschlagen: {exc}"}

        output = (result.stdout or "").rstrip()
        error = (result.stderr or "").rstrip()
        combined = output
        if error:
            combined = f"{combined}\n{error}".strip()
        limit = int(self.config["max_output_characters"])
        truncated = len(combined) > limit
        if truncated:
            combined = combined[:limit] + "\n... Ausgabe gekuerzt ..."
        return {
            "available": True,
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "output": combined or "(keine Ausgabe)",
            "truncated": truncated,
            "workspace": str(self.workspace),
        }
