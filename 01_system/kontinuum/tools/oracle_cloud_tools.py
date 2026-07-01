from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


class OracleCloudTools:
    """Controlled bridge to Oracle Cloud Infrastructure CLI."""

    DEFAULT_CONFIG = {
        "enabled": True,
        "allow_changes": False,
        "require_superadmin_for_changes": True,
        "require_cost_confirmation": True,
        "profile": "DEFAULT",
        "oci_config_file": "",
        "executable": "",
        "compartment_ocid": "",
        "tenancy_ocid": "",
        "region": "",
        "timeout_seconds": 90,
        "max_output_characters": 20000,
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "24_config" / "oracle_cloud.json"
        self.audit_path = self.project_root / "27_logs" / "oracle_cloud_audit.log"
        self.workspace = self.project_root / "13_tools" / "oracle_cloud_workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

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
        found = shutil.which("oci")
        if found:
            return found
        candidates = [
            Path(os.environ.get("USERPROFILE", "")) / "bin" / "oci.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Oracle" / "oci.exe",
            Path("C:/Program Files (x86)/Oracle/oci_cli/oci.exe"),
            Path("C:/Program Files/Oracle/oci_cli/oci.exe"),
        ]
        return next((str(path) for path in candidates if path.is_file()), None)

    def _oci_config_file(self) -> Path:
        configured = str(self.config.get("oci_config_file") or "").strip()
        return Path(configured).expanduser() if configured else Path.home() / ".oci" / "config"

    def status(self) -> dict:
        executable = self._resolved_command()
        config_file = self._oci_config_file()
        enabled = bool(self.config.get("enabled"))
        configured = bool(
            config_file.is_file()
            and str(self.config.get("compartment_ocid") or "").startswith("ocid1.compartment.")
        )
        version = ""
        if executable:
            result = self._run_raw([executable, "--version"], timeout=15)
            version = result.get("output", "")
        message = (
            f"Oracle Cloud Integration: {'aktiv' if enabled else 'deaktiviert'}. "
            f"OCI CLI: {version if executable else 'nicht installiert'}. "
            f"OCI-Profil: {self.config.get('profile', 'DEFAULT')}. "
            f"Konfiguration: {'bereit' if configured else 'noch nicht eingerichtet'}. "
            f"Aenderungen: {'freigeschaltet' if self.config.get('allow_changes') else 'gesperrt'}."
        )
        return {
            "available": enabled and bool(executable),
            "enabled": enabled,
            "configured": configured,
            "executable": executable,
            "version": version,
            "profile": self.config.get("profile", "DEFAULT"),
            "config_file_exists": config_file.is_file(),
            "compartment_configured": bool(self.config.get("compartment_ocid")),
            "allow_changes": bool(self.config.get("allow_changes")),
            "require_cost_confirmation": bool(self.config.get("require_cost_confirmation")),
            "message": message,
        }

    def list_instances(self) -> dict:
        compartment = self._required_ocid("compartment_ocid", "Compartment-OCID")
        if not compartment["ok"]:
            return compartment
        return self._run(
            ["compute", "instance", "list", "--compartment-id", compartment["value"], "--all"],
            "instances.list",
        )

    def list_buckets(self) -> dict:
        compartment = self._required_ocid("compartment_ocid", "Compartment-OCID")
        if not compartment["ok"]:
            return compartment
        namespace = self._run(["os", "ns", "get"], "object_storage.namespace")
        if not namespace.get("ok"):
            return namespace
        try:
            namespace_value = json.loads(namespace["output"]).get("data")
        except (TypeError, ValueError, AttributeError):
            return {"ok": False, "message": "Object-Storage-Namespace konnte nicht gelesen werden."}
        return self._run(
            ["os", "bucket", "list", "--compartment-id", compartment["value"], "--namespace-name", namespace_value, "--all"],
            "buckets.list",
        )

    def limits(self) -> dict:
        tenancy = self._required_ocid("tenancy_ocid", "Tenancy-OCID")
        if not tenancy["ok"]:
            return tenancy
        return self._run(
            ["limits", "value", "list", "--compartment-id", tenancy["value"], "--all"],
            "limits.list",
        )

    def free_tier_status(self) -> dict:
        status = self.status()
        return {
            "ok": True,
            "message": (
                "Oracle Cloud Free-Tier-Schutzstatus:\n"
                f"- OCI CLI: {'bereit' if status['available'] else 'nicht bereit'}\n"
                f"- Konto-Konfiguration: {'bereit' if status['configured'] else 'nicht eingerichtet'}\n"
                f"- schreibende Aktionen: {'freigeschaltet' if status['allow_changes'] else 'gesperrt'}\n"
                f"- erneute Passwortbestätigung vor Kostenaktionen: {'aktiv' if status['require_cost_confirmation'] else 'deaktiviert'}\n"
                "- Kontinuum erzeugt keine kostenpflichtigen Ressourcen automatisch.\n"
                "- Oracle-Free-Tier-Kontingente und reale Kosten muessen im OCI-Kostenmanagement geprueft werden."
            ),
        }

    def change_instance_state(
        self,
        action: str,
        instance_ocid: str,
        user: dict | None = None,
        confirmation_handler=None,
    ) -> dict:
        authorization = self._authorize_change(user)
        if not authorization["ok"]:
            return authorization
        instance_ocid = (instance_ocid or "").strip()
        if not instance_ocid.startswith("ocid1.instance."):
            return {"ok": False, "message": "Ungültige Compute-Instance-OCID."}
        actions = {"start": "START", "stop": "STOP", "softstop": "SOFTSTOP", "reset": "RESET"}
        normalized = actions.get(action.casefold())
        if not normalized:
            return {"ok": False, "message": f"Nicht erlaubte Oracle-Instanzaktion: {action}"}
        if self.config.get("require_cost_confirmation"):
            if not callable(confirmation_handler):
                return {"ok": False, "message": "Kostenrelevante Oracle-Aktion benötigt eine erneute Superadminbestätigung mit Passwort."}
            try:
                confirmed = bool(confirmation_handler(f"Oracle-Instanz {action.casefold()}", instance_ocid))
            except Exception:
                confirmed = False
            if not confirmed:
                self._audit(f"instance.{action.casefold()}.cost_confirmation", False, user or {}, instance_ocid)
                return {"ok": False, "message": "Kostenrelevante Oracle-Aktion wurde nicht bestätigt."}
        result = self._run(
            ["compute", "instance", "action", "--instance-id", instance_ocid, "--action", normalized],
            f"instance.{action.casefold()}",
        )
        self._audit(f"instance.{action.casefold()}", bool(result.get("ok")), user or {}, instance_ocid)
        return result

    def _authorize_change(self, user: dict | None) -> dict:
        user = user or {}
        if not self.config.get("allow_changes"):
            return {"ok": False, "message": "Oracle-Cloud-Änderungen sind in der Konfiguration gesperrt."}
        if not self.config.get("require_superadmin_for_changes"):
            return {"ok": True}
        allowed = (
            bool(user.get("authenticated"))
            and bool(user.get("is_superadmin"))
            and str(user.get("role", "")).upper() == "SUPERADMIN"
            and bool((user.get("permissions") or {}).get("can_execute_admin_commands"))
        )
        if not allowed:
            return {"ok": False, "message": "Oracle-Cloud-Änderungen erfordern einen verifiziert angemeldeten SUPERADMIN."}
        return {"ok": True}

    def _required_ocid(self, key: str, label: str) -> dict:
        value = str(self.config.get(key) or "").strip()
        if not value.startswith("ocid1."):
            return {"ok": False, "message": f"{label} fehlt in 24_config\\oracle_cloud.json."}
        return {"ok": True, "value": value}

    def _run(self, arguments: list[str], event: str) -> dict:
        status = self.status()
        if not status["enabled"]:
            return {"ok": False, "message": "Oracle Cloud Integration ist deaktiviert."}
        executable = status.get("executable")
        if not executable:
            return {"ok": False, "message": "OCI CLI ist nicht installiert oder nicht konfiguriert."}
        config_file = self._oci_config_file()
        if not config_file.is_file():
            return {"ok": False, "message": "OCI-Konfigurationsdatei fehlt. Erwartet wird ~/.oci/config oder der konfigurierte Pfad."}
        command = [
            executable,
            "--config-file",
            str(config_file),
            "--profile",
            str(self.config.get("profile", "DEFAULT")),
        ]
        region = str(self.config.get("region") or "").strip()
        if region:
            command.extend(["--region", region])
        command.extend([*arguments, "--output", "json"])
        result = self._run_raw(command)
        self._audit(event, bool(result.get("ok")), {}, "")
        return result

    def _run_raw(self, command: list[str], timeout: int | None = None) -> dict:
        try:
            result = subprocess.run(
                command,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=timeout or int(self.config["timeout_seconds"]),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "OCI-Aufruf hat das Zeitlimit überschritten."}
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "message": f"OCI-Aufruf fehlgeschlagen: {exc}"}
        output = ((result.stdout or "") + ("\n" + result.stderr if result.stderr else "")).strip()
        limit = int(self.config["max_output_characters"])
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "output": output[:limit] + ("\n... Ausgabe gekürzt ..." if len(output) > limit else ""),
        }

    def _audit(self, event: str, success: bool, user: dict, resource: str) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        safe_resource = resource[:160].replace("\n", " ").replace("\r", " ")
        line = (
            f"{datetime.now().astimezone().isoformat()} | {event} | success={success} | "
            f"user={user.get('username', '')} | resource={safe_resource}\n"
        )
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
