# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone

from kontinuum.version import APP_VERSION


class MeaningCore:
    """Builds semantic links between principles, goals, actions, memories, chronicle, and identity."""

    VERSION = "1.0"
    PATH = ("principle", "goal", "action", "memory", "chronicle", "identity")

    def __init__(self, storage, identity: dict):
        self.storage = storage
        self.identity = identity
        self.rebuild()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def rebuild(self) -> dict:
        self._seed_identity()
        counts = {
            "principles": self._link_principles_to_identity(),
            "goals": self._link_goals_to_principles(),
            "actions": self._link_actions_to_goals(),
            "memories": self._link_memories_to_actions(),
            "chronicle": self._link_chronicle_to_memories(),
        }
        path_id = self._ensure_path(counts)
        return {"path_id": path_id, "counts": counts, "total_links": sum(counts.values())}

    def status(self) -> dict:
        with self.storage.connect() as db:
            nodes = int(db.execute("SELECT COUNT(*) FROM meaning_nodes WHERE json_extract(metadata, '$.meaning_core') = 1").fetchone()[0])
            edges = int(db.execute("SELECT COUNT(*) FROM meaning_edges WHERE json_extract(metadata, '$.meaning_core') = 1").fetchone()[0])
            paths = int(db.execute("SELECT COUNT(*) FROM meaning_paths WHERE json_extract(metadata, '$.meaning_core') = 1").fetchone()[0])
            by_kind = {
                row["kind"]: int(row["count"])
                for row in db.execute(
                    """SELECT kind, COUNT(*) AS count FROM meaning_nodes
                       WHERE json_extract(metadata, '$.meaning_core') = 1 GROUP BY kind"""
                ).fetchall()
            }
        return {
            "version": self.VERSION,
            "nodes": nodes,
            "edges": edges,
            "paths": paths,
            "path": list(self.PATH),
            "node_kinds": by_kind,
        }

    def format_status(self) -> str:
        status = self.status()
        return (
            f"Meaning Core {APP_VERSION}:\n"
            f"- Bedeutungsknoten: {status['nodes']}\n"
            f"- Bedeutungsbeziehungen: {status['edges']}\n"
            f"- Bedeutungspfade: {status['paths']}\n"
            "- kanonischer Pfad: Prinzip -> Ziel -> Handlung -> Erinnerung -> Chronik -> Identität\n"
            f"- Knotentypen: {status['node_kinds']}"
        )

    def explain_path(self, term: str = "") -> str:
        rows = self._recent_edges(term, limit=18)
        if not rows:
            return "Noch kein passender Bedeutungspfad gefunden."
        lines = ["Bedeutungspfad:"]
        for row in rows:
            metadata = self._metadata(row["metadata"])
            lines.append(
                f"- {metadata.get('source_label', metadata.get('source'))} "
                f"--{row['kind']}--> {metadata.get('target_label', metadata.get('target'))}"
            )
        lines.append("Lesart: Prinzipien begründen Ziele; Ziele rahmen Handlungen; Handlungen erzeugen Erinnerungen und Chronik; Chronik stabilisiert Identität.")
        return "\n".join(lines)

    def _seed_identity(self) -> None:
        self._ensure_node(
            "identity",
            "identity:kontinuum",
            {
                "label": f"{self.identity.get('name', 'Kontinuum')} mit Schöpfer {self.identity.get('creator', 'Raphael Schatz')}",
                "protected": True,
                "identity": True,
            },
        )

    def _link_principles_to_identity(self) -> int:
        rows = self._rows("foundation_principles", "foundation.principle")
        count = 0
        for row in rows:
            metadata = self._metadata(row["metadata"])
            source = f"principle:{row['content']}"
            self._ensure_node("principle", source, {"label": metadata.get("text", row["content"]), "protected": True})
            count += self._ensure_edge(source, "prägt Identität", "identity:kontinuum", "principle_to_identity")
        return count

    def _link_goals_to_principles(self) -> int:
        principles = self._rows("foundation_principles", "foundation.principle")
        goals = self._rows("strategic_goals", "strategic.goal")
        count = 0
        for goal in goals:
            goal_meta = self._metadata(goal["metadata"])
            goal_node = f"goal:{goal['content']}"
            self._ensure_node("goal", goal_node, {"label": goal_meta.get("goal", goal["content"]), "priority": goal_meta.get("priority")})
            for principle in principles:
                principle_meta = self._metadata(principle["metadata"])
                if self._related(goal["content"], goal_meta.get("goal", ""), principle["content"], principle_meta.get("text", "")):
                    count += self._ensure_edge(f"principle:{principle['content']}", "begründet Ziel", goal_node, "principle_to_goal")
        return count

    def _link_actions_to_goals(self) -> int:
        goals = self._rows("strategic_goals", "strategic.goal")
        actions = self._rows("foundation_decisions", "foundation.decision", limit=200)
        count = 0
        for action in actions:
            action_meta = self._metadata(action["metadata"])
            action_node = f"action:{action['id']}"
            self._ensure_node("action", action_node, {
                "label": action_meta.get("action", action["content"])[:220],
                "decision": action_meta.get("decision"),
            })
            for goal in goals:
                goal_meta = self._metadata(goal["metadata"])
                if self._related(action["content"], action_meta.get("action", ""), goal["content"], goal_meta.get("goal", "")):
                    count += self._ensure_edge(f"goal:{goal['content']}", "rahmt Handlung", action_node, "goal_to_action")
        return count

    def _link_memories_to_actions(self) -> int:
        actions = self._rows("foundation_decisions", "foundation.decision", limit=200)
        memories = self._rows("memories", "", limit=300)
        count = 0
        for memory in memories:
            memory_node = f"memory:{memory['id']}"
            self._ensure_node("memory", memory_node, {"label": memory["content"][:220], "kind": memory["kind"]})
            for action in actions:
                if self._related(memory["content"], memory["kind"], action["content"], self._metadata(action["metadata"]).get("action", "")):
                    count += self._ensure_edge(f"action:{action['id']}", "erzeugt oder prägt Erinnerung", memory_node, "action_to_memory")
                    break
        return count

    def _link_chronicle_to_memories(self) -> int:
        memories = self._rows("memories", "", limit=300)
        chronicle = self._rows("chronicle_entries", "", limit=200)
        count = 0
        for entry in chronicle:
            chronicle_node = f"chronicle:{entry['id']}"
            self._ensure_node("chronicle", chronicle_node, {"label": entry["content"][:220], "kind": entry["kind"]})
            count += self._ensure_edge(chronicle_node, "stabilisiert Identität", "identity:kontinuum", "chronicle_to_identity")
            for memory in memories:
                if self._related(entry["content"], entry["kind"], memory["content"], memory["kind"]):
                    count += self._ensure_edge(f"memory:{memory['id']}", "dokumentiert in Chronik", chronicle_node, "memory_to_chronicle")
                    break
        return count

    def _ensure_node(self, kind: str, content: str, metadata: dict) -> int:
        with self.storage.connect() as db:
            existing = db.execute(
                "SELECT id FROM meaning_nodes WHERE kind = ? AND content = ? LIMIT 1", (kind, content)
            ).fetchone()
        if existing:
            return int(existing["id"])
        return self.storage.add("meaning_nodes", kind, content, {"meaning_core": True, **metadata})

    def _ensure_edge(self, source: str, relation: str, target: str, kind: str) -> int:
        content = f"{source} -> {target}"
        with self.storage.connect() as db:
            existing = db.execute(
                "SELECT id FROM meaning_edges WHERE kind = ? AND content = ? LIMIT 1", (kind, content)
            ).fetchone()
        if existing:
            return 0
        return int(bool(self.storage.add(
            "meaning_edges",
            kind,
            content,
            {
                "meaning_core": True,
                "source": source,
                "target": target,
                "relation": relation,
                "source_label": self._label_for(source),
                "target_label": self._label_for(target),
            },
        )))

    def _ensure_path(self, counts: dict) -> int:
        content = "Prinzip -> Ziel -> Handlung -> Erinnerung -> Chronik -> Identität"
        with self.storage.connect() as db:
            existing = db.execute(
                "SELECT id FROM meaning_paths WHERE kind = 'meaning.path' AND content = ? LIMIT 1",
                (content,),
            ).fetchone()
        if existing:
            return int(existing["id"])
        return self.storage.add(
            "meaning_paths",
            "meaning.path",
            content,
            {
                "meaning_core": True,
                "version": self.VERSION,
                "path": list(self.PATH),
                "counts": counts,
                "created_at": self._now(),
            },
        )

    def _label_for(self, node: str) -> str:
        table, _, key = node.partition(":")
        if table in {"principle", "goal"}:
            lookup_table = "foundation_principles" if table == "principle" else "strategic_goals"
            with self.storage.connect() as db:
                row = db.execute("SELECT metadata FROM " + lookup_table + " WHERE content = ? LIMIT 1", (key,)).fetchone()
            if row:
                metadata = self._metadata(row["metadata"])
                return metadata.get("text") or metadata.get("goal") or node
        return node

    def _recent_edges(self, term: str, limit: int) -> list:
        pattern = f"%{term.strip()}%" if term.strip() else "%"
        with self.storage.connect() as db:
            return db.execute(
                """SELECT kind, content, metadata FROM meaning_edges
                   WHERE json_extract(metadata, '$.meaning_core') = 1
                     AND (content LIKE ? OR metadata LIKE ?)
                   ORDER BY id DESC LIMIT ?""",
                (pattern, pattern, max(1, limit)),
            ).fetchall()

    def _rows(self, table: str, kind: str, limit: int = 1000) -> list[dict]:
        where = "WHERE kind = ?" if kind else ""
        params: tuple = (kind, max(1, limit)) if kind else (max(1, limit),)
        with self.storage.connect() as db:
            rows = db.execute(
                f"SELECT id, kind, content, metadata, created_at FROM {table} {where} ORDER BY id DESC LIMIT ?",
                params,
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value or "{}")
        except (TypeError, ValueError):
            return {}

    @staticmethod
    def _tokens(*values: str) -> set[str]:
        stop = {"und", "oder", "der", "die", "das", "ein", "eine", "mit", "von", "zu", "als", "ist", "soll"}
        tokens = set()
        for value in values:
            current = "".join(char.casefold() if char.isalnum() else " " for char in str(value))
            tokens.update(token for token in current.split() if len(token) >= 5 and token not in stop)
        return tokens

    def _related(self, *values: str) -> bool:
        left = self._tokens(*values[:2])
        right = self._tokens(*values[2:])
        if left & right:
            return True
        combined = " ".join(str(value).casefold() for value in values)
        semantic_markers = (
            ("kontinuit", "identit"),
            ("wissen", "quelle"),
            ("moral", "verantwort"),
            ("selbst", "frage"),
            ("chronik", "erinner"),
            ("schaffen", "vollenden"),
        )
        return any(all(marker in combined for marker in pair) for pair in semantic_markers)
