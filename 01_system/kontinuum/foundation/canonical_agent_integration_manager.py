# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path


class AgentRegistryValidationError(ValueError):
    pass


class CanonicalAgentIntegrationManager:
    VERSION = "1.0"
    FILE_NAME = "canonical_agents.json"
    VALID_TYPES = {
        "internal",
        "foundation",
        "local_model",
        "external_api",
        "tool_agent",
        "experimental",
        "disabled",
    }
    VALID_STATUSES = {"active", "inactive", "disabled", "experimental"}
    REQUIRED_FIELDS = {
        "id",
        "name",
        "type",
        "status",
        "version",
        "description",
        "capabilities",
        "allowed_tools",
        "governance_required",
        "read_only",
        "entrypoint",
    }
    DEFAULT_AGENT_SPECS = [
        {
            "id": "agent_memory",
            "name": "memory",
            "type": "internal",
            "description": "Verwaltet Erinnerungsbefehle und Memory-Zugriffe.",
            "capabilities": ["memory.read", "memory.write", "memory.status"],
            "entrypoint": "kontinuum.agents.memory_agent.MemoryAgent",
        },
        {
            "id": "agent_web",
            "name": "web_agent",
            "type": "internal",
            "description": "Liest Webadressen und Internetquellen kontrolliert ein.",
            "capabilities": ["web.read", "web.status", "source.capture"],
            "entrypoint": "kontinuum.core.web_agent.WebAgentService",
        },
        {
            "id": "agent_file",
            "name": "file_agent",
            "type": "internal",
            "description": "Liest lokale Dateien und Ordner im Projektkontext.",
            "capabilities": ["file.read", "file.learn", "file.status"],
            "entrypoint": "kontinuum.core.file_agent.FileAgentService",
        },
        {
            "id": "agent_vision",
            "name": "vision_agent",
            "type": "internal",
            "description": "Analysiert lokale Bilddateien read-only.",
            "capabilities": ["vision.inspect", "vision.status"],
            "entrypoint": "kontinuum.core.vision_agent.VisionAgentService",
        },
        {
            "id": "agent_git",
            "name": "git_agent",
            "type": "internal",
            "description": "Stellt read-only Git-Status und Repositorydiagnosen bereit.",
            "capabilities": ["git.status", "git.inspect", "governance.git"],
            "entrypoint": "kontinuum.core.git_agent.GitAgentService",
        },
        {
            "id": "agent_code",
            "name": "code_agent",
            "type": "internal",
            "description": "Analysiert Quellcode und Projektstruktur read-only.",
            "capabilities": ["code.inspect", "code.map", "code.status"],
            "entrypoint": "kontinuum.core.code_agent.CodeAgentService",
        },
        {
            "id": "agent_learning",
            "name": "learning_agent",
            "type": "internal",
            "description": "Steuert Lernaufträge und Wissensintegration.",
            "capabilities": ["learning.run", "learning.status", "knowledge.integrate"],
            "entrypoint": "kontinuum.agents.learning_agent.LearningAgent",
        },
        {
            "id": "agent_chemistry",
            "name": "chemistry_agent",
            "type": "internal",
            "description": "Read-only Spezialagent fuer Stoffnamen, Summenformeln, CAS-Nummern, einfache Stoffeigenschaften und Sicherheitsfelder.",
            "capabilities": [
                "chemistry.lookup",
                "chemistry.formula",
                "chemistry.cas",
                "chemistry.properties",
                "chemistry.safety",
            ],
            "allowed_tools": [],
            "governance_required": True,
            "read_only": True,
            "entrypoint": "kontinuum.agents.chemistry_agent.ChemistryAgent",
        },
        {
            "id": "manager_identity",
            "name": "identity_manager",
            "type": "foundation",
            "description": "Verwaltet die kanonische Identität und Rolleninformationen.",
            "capabilities": ["identity.read", "identity.write", "identity.status"],
            "entrypoint": "kontinuum.core.identity_manager.IdentityManager",
        },
        {
            "id": "manager_canonical_memory",
            "name": "canonical_memory_manager",
            "type": "foundation",
            "description": "Verwaltet kanonische Memory-Einträge mit Hash und Governance.",
            "capabilities": ["canonical_memory.read", "canonical_memory.write", "canonical_memory.status"],
            "entrypoint": "kontinuum.foundation.canonical_memory_manager.CanonicalMemoryManager",
        },
        {
            "id": "manager_canonical_identity",
            "name": "canonical_identity_manager",
            "type": "foundation",
            "description": "Kanonische Identitätsinstanz für Creator, Rollen und Systemidentität.",
            "capabilities": ["canonical_identity.read", "canonical_identity.write", "canonical_identity.status"],
            "entrypoint": "kontinuum.foundation.canonical_identity_manager.CanonicalIdentityManager",
        },
        {
            "id": "manager_canonical_artifacts",
            "name": "canonical_artifacts",
            "type": "foundation",
            "description": "Verwaltet kanonische Artefakte und Artefaktstatus.",
            "capabilities": ["artifacts.read", "artifacts.status", "governance.artifacts"],
            "entrypoint": "kontinuum.core.canonical_artifacts.CanonicalArtifactManager",
        },
        {
            "id": "manager_canonical_architecture",
            "name": "canonical_architecture",
            "type": "foundation",
            "description": "Verwaltet kanonische Architekturregeln und Strukturstatus.",
            "capabilities": ["architecture.read", "architecture.status", "governance.architecture"],
            "entrypoint": "kontinuum.core.canonical_architecture.CanonicalArchitectureManager",
        },
        {
            "id": "manager_canonical_api_registry",
            "name": "canonical_api_registry",
            "type": "foundation",
            "description": "Verwaltet kanonische API- und Schnittstellenregistrierung.",
            "capabilities": ["api_registry.read", "api_registry.status", "governance.api"],
            "entrypoint": "kontinuum.core.canonical_api_registry.CanonicalAPIRegistryManager",
        },
        {
            "id": "manager_canonical_database",
            "name": "canonical_database",
            "type": "foundation",
            "description": "Verwaltet kanonische Datenbankstruktur und Datenbankstatus.",
            "capabilities": ["database.read", "database.status", "governance.database"],
            "entrypoint": "kontinuum.core.canonical_database.CanonicalDatabaseManager",
        },
    ]
    DEFAULT_DATA = {
        "schema_version": VERSION,
        "agents": [],
        "last_updated": "",
        "hash": "",
    }

    def __init__(self, path_tools, storage=None, identity_manager=None):
        self.path_tools = path_tools
        self.storage = storage
        self.identity_manager = identity_manager
        self.logger = logging.getLogger("CanonicalAgentIntegrationManager")
        self.config_dir = path_tools.paths()["config"]
        self.path = self.config_dir / self.FILE_NAME
        self.history_dir = self.config_dir / "history" / "canonical_agent_history"
        self.data = self.load_agents()

    def load_agents(self) -> dict:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
            self.validate_agents(data)
            self._notify("load", "Canonical Agent Registry geladen.", {"path": str(self.path), "hash": data.get("hash", "")})
            return data
        data = json.loads(json.dumps(self.DEFAULT_DATA, ensure_ascii=False))
        data["agents"] = [self._normalize_agent(spec) for spec in self.DEFAULT_AGENT_SPECS]
        data["last_updated"] = self._now()
        data["hash"] = self._file_hash(data)
        self.validate_agents(data)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._write_governance({
            "timestamp": self._now(),
            "action": "initialize",
            "agent_id": "",
            "old_status": "",
            "new_status": "active",
            "actor": "system",
            "hash": data["hash"],
            "result": "created",
            "backup_path": "",
        })
        self._notify("initialize", "Canonical Agent Registry initialisiert.", {"path": str(self.path), "hash": data["hash"]})
        return data

    def save_agents(self, actor: str = "system") -> dict:
        return self._commit(self._copy_data(), "save", "", actor, "", "")

    def register_agent(self, agent: dict, actor: str = "system") -> dict:
        data = self._copy_data()
        record = self._normalize_agent(agent)
        if any(item["id"] == record["id"] for item in data["agents"]):
            raise AgentRegistryValidationError(f"Agent-ID bereits vorhanden: {record['id']}")
        if any(item["name"] == record["name"] for item in data["agents"]):
            raise AgentRegistryValidationError(f"Agent-Name bereits vorhanden: {record['name']}")
        data["agents"].append(record)
        return self._commit(data, "register", record["id"], actor, "", record["status"])

    def update_agent(self, agent_id: str, updates: dict, actor: str = "system") -> dict:
        data = self._copy_data()
        agent = self._find_required(data, agent_id)
        old_status = agent.get("status", "")
        for key, value in updates.items():
            if key == "id":
                continue
            agent[key] = value
        normalized = self._normalize_agent(agent)
        agent.clear()
        agent.update(normalized)
        return self._commit(data, "update", agent_id, actor, old_status, agent.get("status", ""))

    def disable_agent(self, agent_id: str, actor: str = "system") -> dict:
        return self.update_agent(agent_id, {"status": "disabled", "type": "disabled"}, actor=actor)

    def enable_agent(self, agent_id: str, actor: str = "system") -> dict:
        agent = self.get_agent(agent_id)
        if not agent:
            raise AgentRegistryValidationError(f"Agent nicht gefunden: {agent_id}")
        agent_type = "internal" if agent.get("type") == "disabled" else agent.get("type", "internal")
        return self.update_agent(agent_id, {"status": "active", "type": agent_type}, actor=actor)

    def get_agent(self, agent_id_or_name: str) -> dict | None:
        needle = (agent_id_or_name or "").casefold()
        for agent in self.data.get("agents", []):
            if agent.get("id", "").casefold() == needle or agent.get("name", "").casefold() == needle:
                return dict(agent)
        return None

    def list_agents(self, agent_type: str | None = None, status: str | None = None) -> list[dict]:
        rows = []
        for agent in self.data.get("agents", []):
            if agent_type and agent.get("type") != agent_type:
                continue
            if status and agent.get("status") != status:
                continue
            rows.append(dict(agent))
        return rows

    def list_active_agents(self) -> list[dict]:
        return self.list_agents(status="active")

    def find_by_capability(self, capability: str, active_only: bool = True) -> list[dict]:
        needle = (capability or "").casefold()
        rows = []
        for agent in self.data.get("agents", []):
            if active_only and agent.get("status") != "active":
                continue
            capabilities = [str(item).casefold() for item in agent.get("capabilities", [])]
            if needle in capabilities:
                rows.append(dict(agent))
        return rows

    def has_capability(self, agent_id_or_name: str, capability: str, active_only: bool = True) -> bool:
        agent = self.get_agent(agent_id_or_name)
        if not agent:
            return False
        if active_only and agent.get("status") != "active":
            return False
        return (capability or "").casefold() in {str(item).casefold() for item in agent.get("capabilities", [])}

    def validate_agents(self, data: dict | None = None) -> bool:
        value = data or self.data
        if not isinstance(value, dict):
            raise AgentRegistryValidationError("Canonical Agent Registry muss ein JSON-Objekt sein.")
        if value.get("schema_version") != self.VERSION:
            raise AgentRegistryValidationError("schema_version 1.0 fehlt.")
        agents = value.get("agents")
        if not isinstance(agents, list) or not agents:
            raise AgentRegistryValidationError("agents muss eine nichtleere Liste sein.")
        ids: list[str] = []
        names: list[str] = []
        for agent in agents:
            if not isinstance(agent, dict) or not agent:
                raise AgentRegistryValidationError("Ungueltiger oder leerer Agent erkannt.")
            missing = self.REQUIRED_FIELDS - set(agent)
            if missing:
                raise AgentRegistryValidationError(f"Pflichtfelder fehlen: {', '.join(sorted(missing))}")
            if not str(agent.get("id", "")).strip() or not str(agent.get("name", "")).strip():
                raise AgentRegistryValidationError("Agent-ID und Name duerfen nicht leer sein.")
            if agent["type"] not in self.VALID_TYPES:
                raise AgentRegistryValidationError(f"Ungueltiger Agententyp: {agent['type']}")
            if agent["status"] not in self.VALID_STATUSES:
                raise AgentRegistryValidationError(f"Ungueltiger Agentenstatus: {agent['status']}")
            if not isinstance(agent.get("capabilities"), list):
                raise AgentRegistryValidationError(f"Capabilities muessen eine Liste sein: {agent['id']}")
            if not isinstance(agent.get("allowed_tools"), list):
                raise AgentRegistryValidationError(f"allowed_tools muss eine Liste sein: {agent['id']}")
            if agent["type"] in {"internal", "foundation", "tool_agent"} and not str(agent.get("entrypoint", "")).strip():
                raise AgentRegistryValidationError(f"EntryPoint fehlt fuer internen Agenten: {agent['id']}")
            ids.append(agent["id"])
            names.append(agent["name"])
        if len(ids) != len(set(ids)):
            raise AgentRegistryValidationError("Doppelte Agent-IDs erkannt.")
        if len(names) != len(set(names)):
            raise AgentRegistryValidationError("Doppelte Agent-Namen erkannt.")
        expected_hash = self._file_hash({**value, "hash": ""})
        if value.get("hash") and value.get("hash") != expected_hash:
            raise AgentRegistryValidationError("Datei-Hash ungueltig.")
        return True

    def backup_agents(self) -> Path | None:
        if not self.path.exists():
            return None
        self.history_dir.mkdir(parents=True, exist_ok=True)
        backup = self.history_dir / f"canonical_agents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        counter = 1
        while backup.exists():
            backup = self.history_dir / f"canonical_agents_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{counter:02d}.json"
            counter += 1
        backup.write_text(self.path.read_text(encoding="utf-8-sig"), encoding="utf-8")
        return backup

    def get_statistics(self) -> dict:
        agents = self.data.get("agents", [])
        statuses: dict[str, int] = {}
        types: dict[str, int] = {}
        capabilities: dict[str, int] = {}
        for agent in agents:
            statuses[agent["status"]] = statuses.get(agent["status"], 0) + 1
            types[agent["type"]] = types.get(agent["type"], 0) + 1
            for capability in agent.get("capabilities", []):
                capabilities[capability] = capabilities.get(capability, 0) + 1
        return {
            "total": len(agents),
            "active": statuses.get("active", 0),
            "disabled": statuses.get("disabled", 0),
            "statuses": statuses,
            "types": types,
            "top_capabilities": sorted(capabilities.items(), key=lambda item: item[1], reverse=True)[:10],
            "integrity": self.integrity_status(),
        }

    def status(self) -> dict:
        stats = self.get_statistics()
        backups = list(self.history_dir.glob("canonical_agents_*.json")) if self.history_dir.exists() else []
        return {
            "schema_version": self.data.get("schema_version", ""),
            "registered_agents": stats["total"],
            "active_agents": stats["active"],
            "disabled_agents": stats["disabled"],
            "agent_types": stats["types"],
            "top_capabilities": stats["top_capabilities"],
            "path": str(self.path),
            "last_updated": self.data.get("last_updated", ""),
            "integrity": stats["integrity"],
            "backups": len(backups),
            "hash": self.data.get("hash", ""),
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Canonical Agent Integration Manager 1.0 Status:",
            f"- registrierte Agenten: {status['registered_agents']}",
            f"- aktive Agenten: {status['active_agents']}",
            f"- deaktivierte Agenten: {status['disabled_agents']}",
            f"- Agententypen: {status['agent_types']}",
            f"- wichtigste Capabilities: {status['top_capabilities']}",
            f"- Speicherpfad: {status['path']}",
            f"- letzter Änderungszeitpunkt: {status['last_updated']}",
            f"- Integritätsstatus: {status['integrity']}",
            f"- Schema-Version: {status['schema_version']}",
        ])

    def can_execute(self, agent_id_or_name: str) -> bool:
        agent = self.get_agent(agent_id_or_name)
        if not agent or agent.get("status") != "active":
            return False
        return agent.get("type") not in {"external_api", "experimental", "disabled"}

    def governance_required(self, agent_id_or_name: str) -> bool:
        agent = self.get_agent(agent_id_or_name)
        return bool(agent and agent.get("governance_required"))

    def integrity_status(self) -> str:
        try:
            self.validate_agents(self.data)
            return "ok"
        except AgentRegistryValidationError as exc:
            return f"fehler: {exc}"

    def _commit(self, data: dict, action: str, agent_id: str, actor: str, old_status: str, new_status: str) -> dict:
        self.validate_agents({**data, "hash": ""})
        backup = self.backup_agents()
        data["last_updated"] = self._now()
        data["hash"] = self._file_hash({**data, "hash": ""})
        self.validate_agents(data)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.data = data
        event = {
            "timestamp": self._now(),
            "action": action,
            "agent_id": agent_id,
            "old_status": old_status,
            "new_status": new_status,
            "actor": actor,
            "hash": data["hash"],
            "result": "stored",
            "backup_path": str(backup) if backup else "",
        }
        self._write_governance(event)
        self._record_governance(event)
        self._notify(action, "Canonical Agent Registry geaendert.", event)
        return {"ok": True, "action": action, "agent_id": agent_id, "backup": str(backup) if backup else "", "hash": data["hash"]}

    def _copy_data(self) -> dict:
        return json.loads(json.dumps(self.data, ensure_ascii=False))

    def _find_required(self, data: dict, agent_id: str) -> dict:
        for agent in data.get("agents", []):
            if agent.get("id") == agent_id or agent.get("name") == agent_id:
                return agent
        raise AgentRegistryValidationError(f"Agent nicht gefunden: {agent_id}")

    def _normalize_agent(self, agent: dict) -> dict:
        status = agent.get("status", "active")
        agent_type = agent.get("type", "internal")
        if agent_type in {"external_api", "experimental"} and status == "active":
            status = "experimental"
        if agent_type == "disabled":
            status = "disabled"
        return {
            "id": str(agent.get("id", "")).strip(),
            "name": str(agent.get("name", "")).strip(),
            "type": agent_type,
            "status": status,
            "version": str(agent.get("version", self.VERSION)),
            "description": str(agent.get("description", "")).strip(),
            "capabilities": list(agent.get("capabilities", [])),
            "allowed_tools": list(agent.get("allowed_tools", [])),
            "governance_required": bool(agent.get("governance_required", False)),
            "read_only": bool(agent.get("read_only", False)),
            "entrypoint": str(agent.get("entrypoint", "")).strip(),
        }

    def _file_hash(self, data: dict) -> str:
        payload = dict(data)
        payload["hash"] = ""
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _write_governance(self, event: dict) -> None:
        self.history_dir.mkdir(parents=True, exist_ok=True)
        with (self.history_dir / "canonical_agent_governance.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def _record_governance(self, event: dict) -> None:
        if self.storage:
            self.storage.add("audit_events", "canonical_agent.change", event.get("action", ""), event)

    def _notify(self, kind: str, content: str, metadata: dict) -> None:
        if self.storage:
            self.storage.add("foundation_memory", f"canonical_agent.{kind}", content, {"caim": self.VERSION, **metadata})

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
