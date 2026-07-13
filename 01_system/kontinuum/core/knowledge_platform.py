# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone


class KnowledgePlatform:
    """Connects knowledge, notebook sources, memories, graph, and chronicle."""

    def __init__(self, storage, memory_core, version: str, intelligence=None):
        self.storage = storage
        self.memory_core = memory_core
        self.version = version
        self.intelligence = intelligence

    def integrate_notebook_source(
        self,
        notebook_source_id: int,
        source_record_id: int,
        title: str,
        locator: str,
        summary: str,
    ) -> dict:
        return self.integrate(
            summary,
            origin="notebook",
            title=title,
            locator=locator,
            source_record_ids=[source_record_id],
            notebook_source_id=notebook_source_id,
        )

    def integrate(
        self,
        content: str,
        origin: str | dict,
        title: str = "",
        locator: str = "",
        source_record_ids: list[int] | None = None,
        notebook_source_id: int | None = None,
        existing_memory_id: int | None = None,
        extra: dict | None = None,
    ) -> dict:
        if isinstance(origin, dict):
            legacy_metadata = dict(origin)
            origin = legacy_metadata.pop("origin", "legacy")
            title = title or legacy_metadata.pop("title", legacy_metadata.pop("source_title", ""))
            locator = locator or legacy_metadata.pop("locator", legacy_metadata.pop("source_locator", ""))
            source_record_ids = source_record_ids or legacy_metadata.pop("source_record_ids", None)
            notebook_source_id = notebook_source_id or legacy_metadata.pop("notebook_source_id", None)
            extra = {**legacy_metadata, **(extra or {})}
        clean = " ".join((content or "").split()).strip()
        if not clean:
            return {"ok": False, "reason": "Kein integrierbarer Inhalt."}
        foundation_guard = getattr(self, "foundation_guard", None)
        foundation_integrity = getattr(self, "foundation_integrity", None)
        if foundation_guard and foundation_integrity:
            decision = foundation_integrity.integration_decision(clean, str(origin), foundation_guard)
            if not decision["allowed"]:
                return {"ok": False, **decision}
        elif foundation_guard and foundation_guard.is_foundation(clean):
            decision = {
                "allowed": False,
                "classification": "foundation_knowledge",
                "reason": "Fundamentwissen darf nur über die geschützte Fundamentschicht verwaltet werden.",
            }
            if not decision["allowed"]:
                return {"ok": False, **decision}
        contamination_guard = getattr(self, "contamination_guard", None)
        if contamination_guard and not contamination_guard.should_integrate(clean, origin=origin, title=title):
            return {
                "ok": False,
                "reason": "Knowledge Contamination Guard: System-/Statusausgabe wurde nicht als Fachwissen integriert.",
                "classification": "report",
            }
        if origin in {"dialogue", "learning"}:
            existing = self._existing_integrated(clean, origin)
            if existing:
                return {"action": "existing", "knowledge_id": existing["id"], "origin": origin}
        learned_at = datetime.now(timezone.utc).isoformat()
        source_ids = [int(value) for value in (source_record_ids or []) if value]
        provenance = {
            "origin": origin,
            "knowledge_class": "learned.knowledge",
            "memory_layer": "learned_knowledge",
            "classification_version": "3.0",
            "source_record_ids": source_ids,
            "source_record_id": source_ids[0] if source_ids else None,
            "notebook_source_id": notebook_source_id,
            "source_locator": locator,
            "source_title": title or origin,
            "introduced_version": self.version,
            "learned_at": learned_at,
            **(extra or {}),
        }
        knowledge_id = self.storage.add(
            "knowledge_items",
            "knowledge.integrated",
            clean,
            provenance,
        )
        if existing_memory_id:
            memory_id = existing_memory_id
        else:
            memory = self.memory_core.remember(
                clean,
                owner="Kontinuum",
                explicit=True,
                source=f"knowledge_platform:{origin}",
                provenance={**provenance, "knowledge_id": knowledge_id},
            )
            memory_id = memory.get("id")
        provenance["memory_id"] = memory_id
        self._update_metadata("knowledge_items", knowledge_id, provenance)
        chronicle_id = self.storage.add(
            "chronicle_entries",
            "knowledge.integrated",
            self._compact_chronicle_event(origin, title, provenance),
            {**provenance, "knowledge_id": knowledge_id, "memory_id": memory_id},
        )
        provenance["chronicle_id"] = chronicle_id
        self._update_metadata("knowledge_items", knowledge_id, provenance)

        nodes = {
            "knowledge": f"knowledge:{knowledge_id}",
            "memory": f"memory:{memory_id}",
            "version": f"version:{self.version}",
            "chronicle": f"chronicle:{chronicle_id}",
        }
        if notebook_source_id:
            nodes["notebook"] = f"notebook:{notebook_source_id}"
        for source_id in source_ids:
            nodes[f"source_{source_id}"] = f"source:{source_id}"
        for node_type, node in nodes.items():
            self.storage.add(
                "graph_nodes",
                node_type.split("_", 1)[0],
                node,
                {"label": title if node_type.startswith(("source", "notebook")) else node, **provenance},
            )
        edge_metadata = {"knowledge_platform": True, "origin": origin, "introduced_version": self.version}
        for source_id in source_ids:
            source_node = nodes[f"source_{source_id}"]
            target = nodes.get("notebook", nodes["knowledge"])
            self.storage.add_edge(source_node, "importiert in" if notebook_source_id else "stützt Wissen", target, edge_metadata)
        if notebook_source_id:
            self.storage.add_edge(nodes["notebook"], "erzeugt Wissen", nodes["knowledge"], edge_metadata)
        if memory_id:
            self.storage.add_edge(nodes["knowledge"], "verankert als Erinnerung", nodes["memory"], edge_metadata)
            self.storage.add_edge(nodes["memory"], "dokumentiert in", nodes["chronicle"], edge_metadata)
        else:
            self.storage.add_edge(nodes["knowledge"], "dokumentiert in", nodes["chronicle"], edge_metadata)
        self.storage.add_edge(nodes["version"], "führte Wissen ein", nodes["knowledge"], edge_metadata)
        if self.intelligence:
            self.intelligence.refresh()
        return {
            "knowledge_id": knowledge_id,
            "memory_id": memory_id,
            "chronicle_id": chronicle_id,
            "version": self.version,
            "learned_at": learned_at,
            "origin": origin,
        }

    def integrate_memory(self, memory: dict, title: str = "Manuelle Erinnerung") -> dict:
        memory_id = memory.get("id")
        if not memory_id:
            return {"ok": False, "reason": "Keine gespeicherte Erinnerung."}
        return self.integrate(
            memory.get("value") or memory.get("content") or title,
            origin="memory",
            title=title,
            existing_memory_id=int(memory_id),
            extra={"memory_layer": memory.get("layer", "")},
        )

    def backfill(self, limit: int = 1000) -> dict:
        linked = {table: 0 for table in ("sources", "memories", "knowledge_items", "chronicle_entries")}
        with self.storage.connect() as database:
            for table in linked:
                rows = database.execute(
                    f"SELECT id, kind, content, metadata, created_at FROM {table} ORDER BY id LIMIT ?",
                    (max(1, limit),),
                ).fetchall()
                for row in rows:
                    node = f"{self._node_type(table)}:{row['id']}"
                    if self._node_exists(database, node):
                        continue
                    metadata = self._metadata(row["metadata"])
                    version = metadata.get("introduced_version") or metadata.get("version") or "legacy"
                    payload = {
                        "label": row["content"][:160],
                        "legacy_backfill": True,
                        "original_kind": row["kind"],
                        "original_created_at": row["created_at"],
                        "introduced_version": version,
                    }
                    database.execute(
                        "INSERT INTO graph_nodes(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                        (self._node_type(table), node, json.dumps(payload, ensure_ascii=False), datetime.now(timezone.utc).isoformat()),
                    )
                    linked[table] += 1
            database.commit()
        for table, count in linked.items():
            if count:
                self.storage.add_edge(
                    f"version:{self.version}",
                    "verknüpfte Altbestand",
                    f"legacy:{table}",
                    {"knowledge_platform": True, "legacy_backfill": True, "records": count},
                )
        return {"linked": linked, "total": sum(linked.values())}

    def explain(self, term: str) -> str:
        needle = (term or "").strip()
        if not needle:
            return "Bitte einen Begriff angeben: wissensweg <Begriff>."
        pattern = f"%{needle}%"
        with self.storage.connect() as database:
            rows = database.execute(
                """SELECT id, content, metadata, created_at
                   FROM knowledge_items
                   WHERE kind = 'knowledge.integrated'
                     AND (content LIKE ? OR metadata LIKE ?)
                   ORDER BY id DESC LIMIT 10""",
                (pattern, pattern),
            ).fetchall()
        if not rows:
            return f"Für „{needle}“ ist noch kein integrierter Wissensweg dokumentiert."
        lines = [f"Wissensweg für „{needle}“ ({len(rows)}):"]
        for row in rows:
            metadata = self._metadata(row["metadata"])
            trust = metadata.get("trust", {})
            epistemic = metadata.get("epistemic", {})
            lines.extend(
                [
                    f"- Wissen [{row['id']}]: {row['content']}",
                    f"  Ursprung: {metadata.get('origin', '')}",
                    f"  Quelle: {metadata.get('source_title', '')} | {metadata.get('source_locator', '')}",
                    f"  Stützende Quellen: {self._sources(metadata)}",
                    f"  Notebook: [{metadata.get('notebook_source_id') or ''}]",
                    f"  Gelernt: {metadata.get('learned_at', row['created_at'])}",
                    f"  Eingeführt mit Version: {metadata.get('introduced_version', '')}",
                    f"  Verbundene Erinnerung: [{metadata.get('memory_id', self._memory_id(row['id']))}]",
                    f"  Projektchronik: [{metadata.get('chronicle_id', '')}]",
                    f"  Vertrauen: {trust.get('level', 'unbewertet')} ({trust.get('score', 0):.2f})",
                    f"  Bestätigende Quellen: {trust.get('confirming_sources', 0)} | Bestätigungen: {trust.get('confirming_knowledge', 0)}",
                    f"  Quellenklassen: {trust.get('source_classes', {})} | Qualitätsgewicht: {trust.get('source_quality_weight', 0):.2f}",
                    f"  Widersprüche: {trust.get('contradictions', 0)} | Letzte Bestätigung: {trust.get('last_confirmation', '')}",
                    f"  Wissenszustand: {epistemic.get('state', 'unbewertet')} | Überprüfung: {epistemic.get('review_priority', 'none')}",
                    f"  Zustandsgrund: {epistemic.get('reason', '')}",
                ]
            )
        return "\n".join(lines)

    def status(self) -> dict:
        with self.storage.connect() as database:
            integrated = int(
                database.execute(
                    "SELECT COUNT(*) FROM knowledge_items WHERE kind = 'knowledge.integrated'"
                ).fetchone()[0]
            )
            paths = int(
                database.execute(
                    "SELECT COUNT(*) FROM graph_edges WHERE json_extract(metadata, '$.knowledge_platform') = 1"
                ).fetchone()[0]
            )
            chronicle = int(
                database.execute(
                    "SELECT COUNT(*) FROM chronicle_entries WHERE kind = 'knowledge.integrated'"
                ).fetchone()[0]
            )
            origins = {
                row["origin"]: int(row["count"])
                for row in database.execute(
                    """SELECT COALESCE(json_extract(metadata, '$.origin'), 'legacy') AS origin, COUNT(*) AS count
                       FROM knowledge_items WHERE kind = 'knowledge.integrated' GROUP BY origin"""
                ).fetchall()
            }
        return {
            "version": self.version,
            "integrated_knowledge": integrated,
            "graph_edges": paths,
            "chronicle_entries": chronicle,
            "origins": origins,
            "conflicts": len(self.intelligence.conflicts()) if self.intelligence else 0,
            "epistemic_states": self.intelligence.self_model().get("epistemic_states", {}) if self.intelligence else {},
            "knowledge_gaps": len(self.intelligence.knowledge_gaps()) if self.intelligence else 0,
        }

    def _memory_id(self, knowledge_id: int) -> str:
        with self.storage.connect() as database:
            row = database.execute(
                """SELECT id FROM memories
                   WHERE kind = 'memory.core'
                     AND json_extract(metadata, '$.provenance.knowledge_id') = ?
                   ORDER BY id DESC LIMIT 1""",
                (knowledge_id,),
            ).fetchone()
        return str(row["id"]) if row else ""

    def _existing_integrated(self, content: str, origin: str) -> dict | None:
        with self.storage.connect() as database:
            row = database.execute(
                """SELECT id, metadata FROM knowledge_items
                   WHERE kind = 'knowledge.integrated' AND content = ?
                     AND json_extract(metadata, '$.origin') = ?
                   ORDER BY id DESC LIMIT 1""",
                (content, origin),
            ).fetchone()
        return {"id": int(row["id"]), "metadata": self._metadata(row["metadata"])} if row else None

    @staticmethod
    def _compact_chronicle_event(origin: str, title: str, provenance: dict) -> str:
        """Create a short event record without copying source or dialogue text."""
        labels = {
            "dialogue": "Geprüftes Dialogwissen integriert",
            "learning": "Geprüftes Lernwissen integriert",
            "memory": "Erinnerung als Wissen integriert",
            "notebook": "Notebook-Wissen integriert",
            "research": "Geprüftes Recherchewissen integriert",
        }
        event = labels.get(origin, "Wissenseinheit integriert")
        subject = " ".join((title or provenance.get("source_title") or origin).split()).strip()
        if subject.casefold().startswith("dialogantwort"):
            subject = "lokaler Fachdialog"
        locator = " ".join(str(provenance.get("source_locator") or "").split()).strip()
        if locator and origin in {"notebook", "research"}:
            subject = f"{subject} ({locator})"
        return f"{event}: {subject}"[:220]

    def _sources(self, metadata: dict) -> str:
        source_ids = metadata.get("source_record_ids") or []
        if not source_ids and metadata.get("source_record_id"):
            source_ids = [metadata["source_record_id"]]
        if not source_ids:
            return metadata.get("source_locator", "") or "keine externe Quelle"
        placeholders = ",".join("?" for _ in source_ids)
        with self.storage.connect() as database:
            rows = database.execute(
                f"SELECT id, content, metadata FROM sources WHERE id IN ({placeholders}) ORDER BY id",
                tuple(source_ids),
            ).fetchall()
        values = []
        for row in rows:
            source_metadata = self._metadata(row["metadata"])
            values.append(f"[{row['id']}] {source_metadata.get('title') or row['content']}")
        return "; ".join(values) or metadata.get("source_locator", "") or "keine externe Quelle"

    def _update_metadata(self, table: str, record_id: int, metadata: dict) -> None:
        with self.storage.connect() as database:
            database.execute(
                f"UPDATE {table} SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), record_id),
            )
            database.commit()

    @staticmethod
    def _node_type(table: str) -> str:
        return {
            "sources": "source",
            "memories": "memory",
            "knowledge_items": "knowledge",
            "chronicle_entries": "chronicle",
        }[table]

    @staticmethod
    def _node_exists(database, node: str) -> bool:
        return bool(database.execute("SELECT 1 FROM graph_nodes WHERE content = ? LIMIT 1", (node,)).fetchone())

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
