from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryDecision:
    action: str
    layer: str
    subject: str
    key: str
    value: str
    confidence: float
    reason: str
    structured: dict


class MemoryReviewer:
    TRANSIENT = ("heute", "gerade", "momentan", "vorhin", "morgen", "gestern")
    UNCERTAIN = ("vielleicht", "vermutlich", "wahrscheinlich", "möglicherweise", "moeglicherweise", "scheint")

    def review(self, text: str, explicit: bool = False, owner: str = "") -> MemoryDecision:
        clean = " ".join((text or "").split()).strip(" .")
        lower = clean.casefold()
        uncertain = any(marker in lower for marker in self.UNCERTAIN)
        if lower.startswith("notebook-quelle ") or re.search(r"https?://", clean):
            locator = re.search(r"https?://\S+", clean)
            value = locator.group(0) if locator else clean
            return MemoryDecision("store", "sources", "Kontinuum", f"source:{self._slug(value)}", value, 0.95, "Quellenbezug erkannt.", {"typ": "quelle"})
        version = re.search(r"\b(?:kontinuum\s+)?version\s+(\d+(?:\.\d+)*)\s+(?:ist\s+)?(.+)", clean, re.I)
        if version:
            number, status_text = version.groups()
            status = self._status(status_text)
            structured = {
                "projekt": "Kontinuum",
                "version": number,
                "status": status,
                "tests": "bestanden" if "test" in lower and "bestanden" in lower else "",
                "offen": self._open_detail(clean),
            }
            return MemoryDecision(
                "mark_uncertain" if uncertain else "store",
                "project",
                "Kontinuum",
                f"version:{number}",
                status,
                0.65 if uncertain else 0.98,
                "Strukturierte Versionsaussage erkannt.",
                structured,
            )
        preference = re.search(r"\b(?:ich|raphael)\s+(?:bevorzuge|bevorzugt|mag|möchte|moechte)\s+(.+)", clean, re.I)
        if preference:
            value = preference.group(1).strip()
            return MemoryDecision("store", "facts", owner or "Raphael", f"preference:{self._slug(value)}", value, 0.9, "Dauerhafte Präferenz erkannt.", {"typ": "präferenz"})
        creator = re.search(r"\b(?:mein|der)\s+schöpfer\s+(?:ist|heißt|heisst)\s+(.+)", clean, re.I)
        if creator:
            value = creator.group(1).strip()
            return MemoryDecision("store", "facts", "Kontinuum", "creator", value, 0.99, "Stabile Identitätsaussage erkannt.", {"typ": "identität"})
        if any(marker in lower for marker in ("offener punkt", "offene punkte", "offener bug", "noch offen", "todo")):
            return MemoryDecision("store", "project", "Kontinuum", f"open:{self._slug(clean)}", clean, 0.9, "Offener Projektpunkt erkannt.", {"status": "offen"})
        if any(marker in lower for marker in self.TRANSIENT):
            return MemoryDecision("store" if explicit else "discard", "episodic", owner or "Sitzung", f"event:{self._slug(clean)}", clean, 0.55, "Zeitgebundenes Ereignis erkannt.", {"dauerhaft": False})
        if explicit:
            return MemoryDecision("mark_uncertain" if uncertain else "store", "facts", owner or "Kontinuum", f"fact:{self._slug(clean)}", clean, 0.6 if uncertain else 0.8, "Explizite Erinnerung.", {})
        return MemoryDecision("discard", "short_term", owner or "Sitzung", "", clean, 0.2, "Keine hinreichende Langzeitrelevanz erkannt.", {})

    @staticmethod
    def _status(text: str) -> str:
        lower = text.casefold()
        for status in ("umgesetzt", "fertig", "abgeschlossen", "geplant", "offen", "getestet", "veröffentlicht"):
            if status in lower:
                return status
        return "unbestätigt"

    @staticmethod
    def _open_detail(text: str) -> str:
        match = re.search(r"\boffen\s*[:\-]?\s*(.+)", text, re.I)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _slug(text: str) -> str:
        value = unicodedata.normalize("NFKD", text.casefold())
        value = "".join(character for character in value if not unicodedata.combining(character))
        return "-".join(re.findall(r"[a-z0-9]+", value)[:10]) or "memory"


class MemoryCore:
    LAYERS = ("short_term", "episodic", "facts", "project", "sources", "relationships")

    def __init__(self, storage):
        self.storage = storage
        self.reviewer = MemoryReviewer()
        self.session_id = ""

    def remember(
        self,
        text: str,
        owner: str = "",
        explicit: bool = True,
        source: str = "conversation",
        provenance: dict | None = None,
    ) -> dict:
        decision = self.reviewer.review(text, explicit=explicit, owner=owner)
        if decision.action == "discard":
            return {"action": "discard", "reason": decision.reason}
        existing = self._active_by_key(decision.subject, decision.key)
        if existing and existing["metadata"].get("value", "").casefold() == decision.value.casefold():
            return {"action": "discard", "reason": "Erinnerung ist bereits aktiv und unverändert.", "id": existing["id"]}
        action = "store"
        replaces = None
        contradiction = False
        if existing:
            action = "replace"
            replaces = existing["id"]
            contradiction = True
            self._set_status(existing["id"], "superseded", {"replaced_by_pending": True})
        metadata = {
            "layer": decision.layer,
            "subject": decision.subject,
            "key": decision.key,
            "value": decision.value,
            "status": "uncertain" if decision.action == "mark_uncertain" else "active",
            "confidence": decision.confidence,
            "review_reason": decision.reason,
            "source": source,
            "structured": decision.structured,
            "replaces": replaces,
            "contradiction": contradiction,
            "provenance": provenance or {},
        }
        memory_id = self.storage.add_memory("memory.core", text, metadata)
        if replaces:
            self._set_status(replaces, "superseded", {"replaced_by": memory_id})
            self.storage.add_edge(f"memory:{memory_id}", "ersetzt", f"memory:{replaces}", {"reason": "Widerspruch/Update"})
        self.storage.add_edge(decision.subject, "hat Erinnerung", f"memory:{memory_id}", {"layer": decision.layer, "key": decision.key})
        return {"action": action, "id": memory_id, **metadata}

    def observe(self, text: str, owner: str = "") -> dict:
        return self.remember(text, owner=owner, explicit=False, source="automatic_reviewer")

    def recall(self, term: str = "", layer: str | None = None, active_only: bool = True, limit: int = 30) -> list[dict]:
        rows = self._rows()
        result = []
        needle = term.casefold().strip()
        for row in reversed(rows):
            metadata = row["metadata"]
            if active_only and metadata.get("status") not in {"active", "uncertain"}:
                continue
            if layer and metadata.get("layer") != layer:
                continue
            searchable = f"{row['content']} {metadata.get('subject', '')} {metadata.get('key', '')} {metadata.get('value', '')}".casefold()
            if needle and needle not in searchable:
                continue
            result.append(row)
            if len(result) >= limit:
                break
        return result

    def update(self, memory_id: int, text: str, owner: str = "") -> dict:
        current = self._by_id(memory_id)
        if not current:
            return {"action": "error", "reason": f"Erinnerung {memory_id} nicht gefunden."}
        self._set_status(memory_id, "superseded", {"update_requested": True})
        result = self.remember(text, owner=owner or current["metadata"].get("subject", ""), explicit=True, source="manual_update")
        if result.get("id"):
            self.storage.add_edge(f"memory:{result['id']}", "aktualisiert", f"memory:{memory_id}")
        return result

    def forget(self, selector: str) -> int:
        rows = [self._by_id(int(selector))] if selector.isdigit() else self.recall(selector, active_only=True, limit=100)
        changed = 0
        for row in rows:
            if row:
                self._set_status(row["id"], "forgotten", {"forgotten": True})
                changed += 1
        return changed

    def link(self, first_id: int, second_id: int, relation: str = "verknüpft mit") -> bool:
        if not self._by_id(first_id) or not self._by_id(second_id):
            return False
        self.storage.add_edge(f"memory:{first_id}", relation, f"memory:{second_id}", {"memory_core": True})
        return True

    def contradictions(self) -> list[dict]:
        grouped: dict[tuple[str, str], list[dict]] = {}
        for row in self._rows():
            metadata = row["metadata"]
            grouped.setdefault((metadata.get("subject", ""), metadata.get("key", "")), []).append(row)
        return [
            {"subject": subject, "key": key, "entries": rows}
            for (subject, key), rows in grouped.items()
            if key and len({row["metadata"].get("value", "").casefold() for row in rows}) > 1
        ]

    def status(self) -> dict:
        rows = self._rows()
        layers = {layer: 0 for layer in self.LAYERS}
        for row in rows:
            layer = row["metadata"].get("layer", "facts")
            layers[layer] = layers.get(layer, 0) + 1
        with self.storage.connect() as database:
            layers["episodic"] = int(
                database.execute("SELECT COUNT(*) FROM events WHERE kind = 'conversation.turn'").fetchone()[0]
            )
            layers["short_term"] = int(
                database.execute(
                    """SELECT COUNT(*) FROM events WHERE kind = 'conversation.turn'
                       AND json_extract(metadata, '$.session_id') = ?""",
                    (self.session_id,),
                ).fetchone()[0]
            ) if self.session_id else 0
            layers["relationships"] = int(
                database.execute(
                    "SELECT COUNT(*) FROM graph_edges WHERE content LIKE 'memory:%' OR content LIKE '% -> memory:%'"
                ).fetchone()[0]
            )
        return {"total": len(rows), "layers": layers, "contradictions": len(self.contradictions())}

    def _rows(self) -> list[dict]:
        with self.storage.connect() as database:
            rows = database.execute("SELECT id, content, metadata, created_at FROM memories WHERE kind = 'memory.core' ORDER BY id").fetchall()
        result = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            result.append({"id": int(row["id"]), "content": row["content"], "metadata": metadata, "created_at": row["created_at"]})
        return result

    def _by_id(self, memory_id: int) -> dict | None:
        return next((row for row in self._rows() if row["id"] == memory_id), None)

    def _active_by_key(self, subject: str, key: str) -> dict | None:
        return next(
            (
                row for row in reversed(self._rows())
                if row["metadata"].get("subject") == subject
                and row["metadata"].get("key") == key
                and row["metadata"].get("status") in {"active", "uncertain"}
            ),
            None,
        )

    def _set_status(self, memory_id: int, status: str, extra: dict | None = None) -> None:
        row = self._by_id(memory_id)
        if not row:
            return
        metadata = dict(row["metadata"])
        metadata["status"] = status
        metadata.update(extra or {})
        with self.storage.connect() as database:
            database.execute("UPDATE memories SET metadata = ? WHERE id = ?", (json.dumps(metadata, ensure_ascii=False), memory_id))
            database.commit()
