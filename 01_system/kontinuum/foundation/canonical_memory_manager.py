# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path


class MemoryValidationError(ValueError):
    pass


class CanonicalMemoryManager:
    VERSION = "1.0"
    FILE_NAME = "canonical_memory_config.json"
    VALID_CLASSES = {
        "identity",
        "user_preferences",
        "project",
        "knowledge",
        "conversation",
        "system",
        "governance",
        "learning",
        "agent_state",
        "temporary",
    }
    VALID_STATUSES = {"active", "archived", "deleted", "merged"}
    REQUIRED_FIELDS = {
        "id",
        "class",
        "title",
        "content",
        "source",
        "created_at",
        "updated_at",
        "confidence",
        "importance",
        "status",
        "version",
        "hash",
    }

    DEFAULT_DATA = {
        "schema_version": "1.0",
        "memory_classes": sorted(VALID_CLASSES),
        "entries": [],
        "last_updated": "",
        "hash": "",
    }

    def __init__(self, path_tools, storage=None, identity_manager=None):
        self.path_tools = path_tools
        self.storage = storage
        self.identity_manager = identity_manager
        self.logger = logging.getLogger("MemoryManager")
        self.config_dir = path_tools.paths()["config"]
        self.path = self.config_dir / self.FILE_NAME
        self.history_dir = self.config_dir / "history" / "canonical_memory_history"
        self.data = self.load_memory()

    def load_memory(self) -> dict:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8-sig"))
                self.validate_memory(data)
                self._notify("load", "Canonical Memory geladen.", {"path": str(self.path), "hash": data.get("hash", "")})
                return data
            except (OSError, ValueError, MemoryValidationError) as exc:
                self.logger.error("Canonical Memory ungueltig: %s", exc)
                raise
        data = json.loads(json.dumps(self.DEFAULT_DATA, ensure_ascii=False))
        data["last_updated"] = self._now()
        data["hash"] = self._file_hash(data)
        self.validate_memory(data)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self._write_history_event({"timestamp": self._now(), "action": "initialize", "memory_id": "", "actor": "system", "old_version": "", "new_version": "", "hash": data["hash"], "result": "created"})
        self._notify("initialize", "Canonical Memory initialisiert.", {"path": str(self.path), "hash": data["hash"]})
        return data

    def save_memory(self, entry: dict | str, memory_class: str = "project", title: str = "", source: str = "", actor: str = "system") -> dict:
        payload = self._entry_from_payload(entry, memory_class, title, source)
        memory_id = payload.get("id") or self._next_id()
        now = self._now()
        record = {
            "id": memory_id,
            "class": payload.get("class", memory_class),
            "title": payload.get("title", title),
            "content": payload.get("content", str(entry)),
            "source": payload.get("source", source),
            "created_at": payload.get("created_at", now),
            "updated_at": now,
            "confidence": float(payload.get("confidence", 1.0)),
            "importance": payload.get("importance", "medium"),
            "status": payload.get("status", "active"),
            "version": int(payload.get("version", 1)),
            "hash": "",
        }
        record["hash"] = self.entry_hash(record)
        data = self._copy_data()
        if any(item["id"] == record["id"] for item in data["entries"]):
            raise MemoryValidationError(f"Memory-ID bereits vorhanden: {record['id']}")
        data["entries"].append(record)
        return self._commit(data, "save", record["id"], actor, "", record["version"])

    def update_memory(self, memory_id: str, updates: dict, actor: str = "system") -> dict:
        data = self._copy_data()
        entry = self._find_required(data, memory_id)
        old_version = int(entry["version"])
        for key, value in updates.items():
            if key in {"id", "created_at", "hash"}:
                continue
            entry[key] = value
        entry["version"] = old_version + 1
        entry["updated_at"] = self._now()
        entry["hash"] = self.entry_hash(entry)
        return self._commit(data, "update", memory_id, actor, old_version, entry["version"])

    def delete_memory(self, memory_id: str, actor: str = "system") -> dict:
        return self.update_memory(memory_id, {"status": "deleted"}, actor=actor)

    def merge_memory(self, source_id: str, target_id: str, actor: str = "system") -> dict:
        data = self._copy_data()
        source = self._find_required(data, source_id)
        target = self._find_required(data, target_id)
        old_version = int(target["version"])
        if source["content"] and source["content"] not in target["content"]:
            target["content"] = f"{target['content']}\n\n{source['content']}".strip()
        target["version"] = old_version + 1
        target["updated_at"] = self._now()
        target["hash"] = self.entry_hash(target)
        source["status"] = "merged"
        source["updated_at"] = self._now()
        source["version"] = int(source["version"]) + 1
        source["hash"] = self.entry_hash(source)
        return self._commit(data, "merge", f"{source_id}->{target_id}", actor, old_version, target["version"])

    def find_memory(self, memory_id: str) -> dict | None:
        return next((dict(entry) for entry in self.data.get("entries", []) if entry.get("id") == memory_id), None)

    def search_memory(self, query: str, memory_class: str | None = None, active_only: bool = True) -> list[dict]:
        needle = (query or "").casefold()
        rows = []
        for entry in self.data.get("entries", []):
            if active_only and entry.get("status") != "active":
                continue
            if memory_class and entry.get("class") != memory_class:
                continue
            haystack = f"{entry.get('id', '')} {entry.get('class', '')} {entry.get('title', '')} {entry.get('content', '')}".casefold()
            if needle in haystack:
                rows.append(dict(entry))
        return rows

    def list_memory(self, memory_class: str | None = None, status: str | None = None) -> list[dict]:
        rows = []
        for entry in self.data.get("entries", []):
            if memory_class and entry.get("class") != memory_class:
                continue
            if status and entry.get("status") != status:
                continue
            rows.append(dict(entry))
        return rows

    def validate_memory(self, data: dict | None = None) -> bool:
        value = data or self.data
        if not isinstance(value, dict):
            raise MemoryValidationError("Canonical Memory muss ein JSON-Objekt sein.")
        if value.get("schema_version") != "1.0":
            raise MemoryValidationError("schema_version 1.0 fehlt.")
        entries = value.get("entries")
        if not isinstance(entries, list):
            raise MemoryValidationError("entries muss eine Liste sein.")
        ids = []
        for entry in entries:
            missing = self.REQUIRED_FIELDS - set(entry)
            if missing:
                raise MemoryValidationError(f"Pflichtfelder fehlen: {', '.join(sorted(missing))}")
            if entry["class"] not in self.VALID_CLASSES:
                raise MemoryValidationError(f"Ungueltige Memory-Klasse: {entry['class']}")
            if entry["status"] not in self.VALID_STATUSES:
                raise MemoryValidationError(f"Ungueltiger Memory-Status: {entry['status']}")
            ids.append(entry["id"])
            if entry.get("hash") != self.entry_hash(entry):
                raise MemoryValidationError(f"Hash ungueltig fuer {entry['id']}")
        active_ids = [entry["id"] for entry in entries if entry.get("status") == "active"]
        if len(active_ids) != len(set(active_ids)):
            raise MemoryValidationError("Doppelte aktive Memory-IDs erkannt.")
        if len(ids) != len(set(ids)):
            raise MemoryValidationError("Doppelte Memory-IDs erkannt.")
        expected_hash = self._file_hash({**value, "hash": ""})
        if value.get("hash") and value.get("hash") != expected_hash:
            raise MemoryValidationError("Datei-Hash ungueltig.")
        return True

    def backup_memory(self) -> Path | None:
        if not self.path.exists():
            return None
        self.history_dir.mkdir(parents=True, exist_ok=True)
        backup = self.history_dir / f"canonical_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup.write_text(self.path.read_text(encoding="utf-8-sig"), encoding="utf-8")
        return backup

    def get_statistics(self) -> dict:
        entries = self.data.get("entries", [])
        active = [entry for entry in entries if entry.get("status") == "active"]
        archived = [entry for entry in entries if entry.get("status") == "archived"]
        merged = [entry for entry in entries if entry.get("status") == "merged"]
        classes: dict[str, int] = {}
        for entry in entries:
            classes[entry["class"]] = classes.get(entry["class"], 0) + 1
        average_confidence = sum(float(entry.get("confidence", 0)) for entry in entries) / len(entries) if entries else 0.0
        return {
            "total": len(entries),
            "active": len(active),
            "archived": len(archived),
            "merged": len(merged),
            "average_confidence": round(average_confidence, 3),
            "classes": classes,
            "largest_classes": sorted(classes.items(), key=lambda item: item[1], reverse=True)[:5],
            "integrity": self.integrity_status(),
        }

    def status(self) -> dict:
        stats = self.get_statistics()
        backups = list(self.history_dir.glob("canonical_memory_*.json")) if self.history_dir.exists() else []
        return {
            "schema_version": self.data.get("schema_version", ""),
            "memory_count": stats["total"],
            "classes": stats["classes"],
            "last_updated": self.data.get("last_updated", ""),
            "path": str(self.path),
            "backups": len(backups),
            "integrity": stats["integrity"],
        }

    def format_status(self) -> str:
        status = self.status()
        return "\n".join([
            "Canonical Memory Manager 1.0 Status:",
            f"- Anzahl Erinnerungen: {status['memory_count']}",
            f"- Klassenverteilung: {status['classes']}",
            f"- letzte Änderung: {status['last_updated']}",
            f"- Speicherpfad: {status['path']}",
            f"- Anzahl Backups: {status['backups']}",
            f"- Integritätsstatus: {status['integrity']}",
            f"- Schema-Version: {status['schema_version']}",
        ])

    def format_statistics(self) -> str:
        stats = self.get_statistics()
        return "\n".join([
            "Canonical Memory Manager 1.0 Statistik:",
            f"- aktive Erinnerungen: {stats['active']}",
            f"- archivierte Erinnerungen: {stats['archived']}",
            f"- zusammengeführte Erinnerungen: {stats['merged']}",
            f"- durchschnittliche Confidence: {stats['average_confidence']}",
            f"- größte Klassen: {stats['largest_classes']}",
            f"- Integritätsstatus: {stats['integrity']}",
        ])

    def classify_memory(self, content: str, explicit_class: str | None = None) -> str:
        if explicit_class in self.VALID_CLASSES:
            return explicit_class
        text = (content or "").casefold()
        if any(marker in text for marker in ("identity", "identität", "creator", "schöpfer", "schoepfer")):
            return "identity"
        if any(marker in text for marker in ("bevorzuge", "bevorzugt", "präferenz", "praeferenz", "preferred")):
            return "user_preferences"
        if any(marker in text for marker in ("version", "projekt", "offen", "bug", "todo")):
            return "project"
        if any(marker in text for marker in ("governance", "audit", "freigabe")):
            return "governance"
        if any(marker in text for marker in ("learning", "lernen", "proposal")):
            return "learning"
        return "knowledge"

    def integrity_status(self) -> str:
        try:
            self.validate_memory(self.data)
            return "ok"
        except MemoryValidationError as exc:
            return f"fehler: {exc}"

    @staticmethod
    def entry_hash(entry: dict) -> str:
        payload = dict(entry)
        payload["hash"] = ""
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _commit(self, data: dict, action: str, memory_id: str, actor: str, old_version, new_version) -> dict:
        self.validate_memory({**data, "hash": ""})
        backup = self.backup_memory()
        data["last_updated"] = self._now()
        data["hash"] = self._file_hash({**data, "hash": ""})
        self.validate_memory(data)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.data = data
        event = {
            "timestamp": self._now(),
            "action": action,
            "memory_id": memory_id,
            "actor": actor,
            "old_version": old_version,
            "new_version": new_version,
            "hash": data["hash"],
            "result": "stored",
            "backup": str(backup) if backup else "",
        }
        self._write_history_event(event)
        self._record_governance(event)
        self._notify(action, "Canonical Memory geaendert.", event)
        return {"ok": True, "action": action, "memory_id": memory_id, "backup": str(backup) if backup else "", "hash": data["hash"]}

    def _copy_data(self) -> dict:
        return json.loads(json.dumps(self.data, ensure_ascii=False))

    def _entry_from_payload(self, entry: dict | str, memory_class: str, title: str, source: str) -> dict:
        if isinstance(entry, dict):
            payload = dict(entry)
            content = str(payload.get("content", ""))
        else:
            content = str(entry)
            payload = {"content": content, "title": title, "source": source}
        payload["class"] = self.classify_memory(content, payload.get("class") or memory_class)
        return payload

    def _find_required(self, data: dict, memory_id: str) -> dict:
        for entry in data.get("entries", []):
            if entry.get("id") == memory_id:
                return entry
        raise MemoryValidationError(f"Memory-ID nicht gefunden: {memory_id}")

    def _next_id(self) -> str:
        numbers = []
        for entry in self.data.get("entries", []):
            match = re.match(r"memory_(\d+)$", entry.get("id", ""))
            if match:
                numbers.append(int(match.group(1)))
        return f"memory_{(max(numbers) if numbers else 0) + 1:06d}"

    def _file_hash(self, data: dict) -> str:
        payload = dict(data)
        payload["hash"] = ""
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _write_history_event(self, event: dict) -> None:
        self.history_dir.mkdir(parents=True, exist_ok=True)
        with (self.history_dir / "canonical_memory_governance.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def _record_governance(self, event: dict) -> None:
        if self.storage:
            self.storage.add("audit_events", "canonical_memory.change", event.get("action", ""), event)

    def _notify(self, kind: str, content: str, metadata: dict) -> None:
        if self.storage:
            self.storage.add("foundation_memory", f"canonical_memory.{kind}", content, {"cmm": self.VERSION, **metadata})

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
