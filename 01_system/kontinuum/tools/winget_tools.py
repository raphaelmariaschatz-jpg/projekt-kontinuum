from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path


class WingetTools:
    DEFAULT_CONFIG = {
        "enabled": False,
        "allow_changes": False,
        "timeout_seconds": 60,
        "max_output_characters": 16000,
        "executable": "",
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "24_config" / "winget.json"
        self.config = self._load_config()
        self.confirmation_handler = None
        self._status_cache: tuple[float, dict] | None = None

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    def _resolved_command(self) -> str | None:
        configured = Path(str(self.config.get("executable") or ""))
        if configured.is_file():
            return str(configured)
        found = shutil.which("winget")
        if found:
            return found
        alias = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "winget.exe"
        if alias.is_file():
            return str(alias)
        windows_apps = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "WindowsApps"
        try:
            candidates = sorted(
                windows_apps.glob("Microsoft.DesktopAppInstaller_*_x64__8wekyb3d8bbwe/winget.exe"),
                reverse=True,
            )
            return str(candidates[0]) if candidates else None
        except OSError:
            return None

    def status(self) -> dict:
        if self._status_cache and time.monotonic() - self._status_cache[0] < 15:
            return dict(self._status_cache[1])
        if not self.config["enabled"]:
            return {"available": False, "enabled": False, "message": "winget ist in Kontinuum deaktiviert."}
        executable = self._resolved_command()
        if not executable:
            return {"available": False, "enabled": True, "message": "winget wurde nicht gefunden."}
        result = self._run(["--version"], timeout=10)
        version = result.get("output", "").strip()
        status = {
            "available": bool(result.get("ok")),
            "enabled": True,
            "executable": executable,
            "version": version,
            "allow_changes": bool(self.config["allow_changes"]),
            "message": (
                f"winget direkt integriert: {version}. "
                f"Systemaenderungen sind {'freigeschaltet' if self.config['allow_changes'] else 'standardmaessig gesperrt'}."
            ),
        }
        self._status_cache = (time.monotonic(), status)
        return dict(status)

    def search(self, query: str) -> dict:
        return self._run(["search", "--query", query, "--accept-source-agreements", "--disable-interactivity"])

    def show(self, package_id: str) -> dict:
        return self._run(["show", "--id", package_id, "--exact", "--accept-source-agreements", "--disable-interactivity"])

    def list_installed(self) -> dict:
        return self._run(["list", "--disable-interactivity"])

    def list_upgrades(self) -> dict:
        return self._run(["upgrade", "--accept-source-agreements", "--disable-interactivity"])

    def change(self, action: str, package_id: str) -> dict:
        if not self.config["allow_changes"]:
            return {
                "available": True,
                "ok": False,
                "message": (
                    f"winget-{action} ist aus Sicherheitsgruenden gesperrt. "
                    "Systemaenderungen erfordern eine ausdrueckliche Freigabe."
                ),
            }
        if not callable(self.confirmation_handler) or not self.confirmation_handler(f"winget-{action}", package_id):
            return {
                "available": True,
                "ok": False,
                "message": "winget-Systemaenderung abgebrochen: Superadmin-Bestaetigung erforderlich.",
            }
        commands = {
            "installieren": "install",
            "aktualisieren": "upgrade",
            "deinstallieren": "uninstall",
        }
        command = commands.get(action)
        if not command:
            return {"available": True, "ok": False, "message": f"Unbekannte winget-Aktion: {action}"}
        return self._run(
            [
                command,
                "--id",
                package_id,
                "--exact",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            timeout=600,
        )

    def _run(self, arguments: list[str], timeout: int | None = None) -> dict:
        executable = self._resolved_command()
        if not executable:
            return {"available": False, "ok": False, "message": "winget wurde nicht gefunden."}
        try:
            result = subprocess.run(
                [executable, *arguments],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=timeout or int(self.config["timeout_seconds"]),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"available": True, "ok": False, "message": "winget-Aufruf hat das Zeitlimit ueberschritten."}
        except (OSError, subprocess.SubprocessError) as exc:
            return {"available": False, "ok": False, "message": f"winget-Aufruf fehlgeschlagen: {exc}"}
        output = ((result.stdout or "") + ("\n" + result.stderr if result.stderr else "")).strip()
        limit = int(self.config["max_output_characters"])
        if len(output) > limit:
            output = output[:limit] + "\n... Ausgabe gekuerzt ..."
        return {
            "available": True,
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "output": output or "(keine Ausgabe)",
        }
