from __future__ import annotations

import json
import hashlib
import sqlite3
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from .contracts import StoredRecord


class Storage:
    TABLES = (
        "memories",
        "knowledge_items",
        "learning_tasks",
        "graph_nodes",
        "graph_edges",
        "events",
        "sources",
        "questions",
        "chronicle_entries",
        "audit_events",
        "self_state",
        "self_state_events",
        "self_explanations",
        "self_boundaries",
        "self_change_log",
        "chronicle_integrity",
        "foundation_principles",
        "foundation_knowledge",
        "foundation_memory",
        "foundation_reasoning",
        "continuity_nodes",
        "continuity_snapshots",
        "continuity_events",
        "moral_assessments",
        "foundation_decisions",
        "strategic_goals",
        "self_questions",
        "meaning_nodes",
        "meaning_edges",
        "meaning_paths",
        "motivation_scores",
        "motivation_reports",
        "motivation_explanations",
        "motivation_evidence",
        "motivation_paths",
        "relevance_assessments",
        "relevance_reports",
        "knowledge_evaluations",
        "source_ratings",
        "knowledge_conflicts",
        "evaluation_history",
    )
    KNOWLEDGE_SEARCH_TABLES = (
        "memories",
        "knowledge_items",
        "learning_tasks",
        "graph_nodes",
        "graph_edges",
        "sources",
        "questions",
        "chronicle_entries",
        "foundation_principles",
        "foundation_knowledge",
        "foundation_memory",
        "foundation_reasoning",
        "strategic_goals",
        "self_questions",
        "meaning_nodes",
        "meaning_edges",
        "meaning_paths",
        "motivation_scores",
        "motivation_reports",
        "motivation_explanations",
        "motivation_evidence",
        "motivation_paths",
        "relevance_assessments",
        "relevance_reports",
        "knowledge_evaluations",
        "source_ratings",
        "knowledge_conflicts",
        "evaluation_history",
    )

    def __init__(self, database: str | Path):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        db = self.connect()
        try:
            for table in self.TABLES:
                db.execute(
                    f"""CREATE TABLE IF NOT EXISTS {table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        kind TEXT NOT NULL DEFAULT '',
                        content TEXT NOT NULL DEFAULT '',
                        metadata TEXT NOT NULL DEFAULT '{{}}',
                        created_at TEXT NOT NULL
                    )"""
                )
            db.execute(
                """CREATE INDEX IF NOT EXISTS idx_memories_content
                   ON memories(content)"""
            )
            for table in self.TABLES:
                db.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_kind ON {table}(kind)")
                db.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_created_at ON {table}(created_at)")
                db.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_kind_created ON {table}(kind, created_at)")
            db.execute(
                """CREATE TABLE IF NOT EXISTS file_search_documents (
                    path TEXT PRIMARY KEY,
                    area TEXT NOT NULL,
                    content TEXT NOT NULL,
                    modified_ns INTEGER NOT NULL,
                    archive INTEGER NOT NULL DEFAULT 0
                )"""
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_file_search_area_archive ON file_search_documents(area, archive)")
            try:
                db.execute(
                    """CREATE VIRTUAL TABLE IF NOT EXISTS file_search_fts
                       USING fts5(path UNINDEXED, area UNINDEXED, content, archive UNINDEXED)"""
                )
            except sqlite3.OperationalError:
                pass
            db.execute(
                """CREATE TRIGGER IF NOT EXISTS protect_chronicle_update
                   BEFORE UPDATE ON chronicle_entries
                   BEGIN
                     SELECT RAISE(ABORT, 'chronicle_entries is append-only');
                   END"""
            )
            db.execute(
                """CREATE TRIGGER IF NOT EXISTS protect_chronicle_delete
                   BEFORE DELETE ON chronicle_entries
                   BEGIN
                     SELECT RAISE(ABORT, 'chronicle_entries is append-only');
                   END"""
            )
            for table in (
                "foundation_principles",
                "foundation_knowledge",
                "foundation_memory",
                "foundation_reasoning",
                "continuity_snapshots",
                "foundation_decisions",
                "meaning_edges",
                "meaning_paths",
                "motivation_scores",
                "motivation_reports",
                "motivation_explanations",
                "motivation_evidence",
                "motivation_paths",
                "relevance_assessments",
                "relevance_reports",
                "knowledge_evaluations",
                "source_ratings",
                "knowledge_conflicts",
                "evaluation_history",
            ):
                db.execute(
                    f"""CREATE TRIGGER IF NOT EXISTS protect_{table}_update
                        BEFORE UPDATE ON {table}
                        BEGIN
                          SELECT RAISE(ABORT, '{table} is append-only');
                        END"""
                )
                db.execute(
                    f"""CREATE TRIGGER IF NOT EXISTS protect_{table}_delete
                        BEFORE DELETE ON {table}
                        BEGIN
                          SELECT RAISE(ABORT, '{table} is append-only');
                        END"""
                )
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def add(self, table: str, kind: str, content: str, metadata: dict | None = None) -> int:
        record = StoredRecord(table, kind, content, metadata or {})
        record.validate(self.TABLES)
        db = self.connect()
        try:
            cursor = db.execute(
                f"INSERT INTO {table}(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                (record.kind, record.content, json.dumps(record.metadata, ensure_ascii=False), self._now()),
            )
            row_id = int(cursor.lastrowid)
            if table == "chronicle_entries":
                self._sign_chronicle_entry(db, row_id, record.kind, record.content, record.metadata)
            db.commit()
            return row_id
        finally:
            db.close()

    def _sign_chronicle_entry(self, db, row_id: int, kind: str, content: str, metadata: dict) -> None:
        previous = db.execute("SELECT metadata FROM chronicle_integrity ORDER BY id DESC LIMIT 1").fetchone()
        previous_hash = json.loads(previous["metadata"]).get("entry_hash", "") if previous else ""
        payload = json.dumps(
            {"chronicle_id": row_id, "kind": kind, "content": content, "metadata": metadata},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        entry_hash = hashlib.sha256(f"{previous_hash}|{payload}".encode("utf-8")).hexdigest()
        integrity = {
            "chronicle_id": row_id,
            "previous_hash": previous_hash,
            "entry_hash": entry_hash,
            "algorithm": "sha256-chain",
        }
        db.execute(
            "INSERT INTO chronicle_integrity(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
            ("chronicle.integrity", str(row_id), json.dumps(integrity, ensure_ascii=False), self._now()),
        )

    def protect_existing_chronicle(self) -> int:
        added = 0
        with self.connect() as db:
            signed = {
                int(row["content"])
                for row in db.execute("SELECT content FROM chronicle_integrity").fetchall()
                if str(row["content"]).isdigit()
            }
            rows = db.execute("SELECT id, kind, content, metadata FROM chronicle_entries ORDER BY id").fetchall()
            for row in rows:
                if int(row["id"]) in signed:
                    continue
                try:
                    metadata = json.loads(row["metadata"])
                except (TypeError, ValueError):
                    metadata = {}
                self._sign_chronicle_entry(db, int(row["id"]), row["kind"], row["content"], metadata)
                added += 1
            db.commit()
        return added

    def verify_chronicle_integrity(self) -> dict:
        with self.connect() as db:
            entries = {
                int(row["id"]): row
                for row in db.execute("SELECT id, kind, content, metadata FROM chronicle_entries").fetchall()
            }
            ledger = db.execute("SELECT content, metadata FROM chronicle_integrity ORDER BY id").fetchall()
        previous_hash = ""
        issues = []
        signed_ids = set()
        for row in ledger:
            data = json.loads(row["metadata"])
            chronicle_id = int(data.get("chronicle_id", row["content"]))
            signed_ids.add(chronicle_id)
            entry = entries.get(chronicle_id)
            if not entry:
                issues.append({"chronicle_id": chronicle_id, "reason": "signierter Chronikeintrag fehlt"})
                previous_hash = data.get("entry_hash", "")
                continue
            try:
                metadata = json.loads(entry["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            payload = json.dumps(
                {"chronicle_id": chronicle_id, "kind": entry["kind"], "content": entry["content"], "metadata": metadata},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            expected = hashlib.sha256(f"{previous_hash}|{payload}".encode("utf-8")).hexdigest()
            if data.get("previous_hash", "") != previous_hash or data.get("entry_hash") != expected:
                issues.append({"chronicle_id": chronicle_id, "reason": "Hash-Kette oder Inhalt verändert"})
            previous_hash = data.get("entry_hash", "")
        for chronicle_id in sorted(set(entries) - signed_ids):
            issues.append({"chronicle_id": chronicle_id, "reason": "Chronikeintrag ist nicht signiert"})
        return {"ok": not issues, "entries": len(entries), "signed": len(signed_ids), "issues": issues}

    def add_memory(self, kind: str, content: str, metadata: dict | None = None) -> int:
        if kind == "research.web":
            raise ValueError("Research content must not be stored as memory; store a source reference instead.")
        return self.add("memories", kind, content, metadata)

    def add_source(self, url: str, metadata: dict | None = None) -> int:
        return self.add("sources", "research.source", url, metadata)

    def ensure_learning_task(self, subject: str, topics: list[str], origin: str) -> int:
        db = self.connect()
        try:
            row = db.execute(
                "SELECT id, metadata FROM learning_tasks WHERE kind = 'continuous.task' AND content = ? LIMIT 1",
                (subject,),
            ).fetchone()
            if row:
                try:
                    metadata = json.loads(row["metadata"])
                except (TypeError, ValueError):
                    metadata = {}
                if topics and not metadata.get("topics"):
                    metadata["topics"] = topics
                    db.execute(
                        "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                        (json.dumps(metadata, ensure_ascii=False), row["id"]),
                    )
                    db.commit()
                return int(row["id"])
            cursor = db.execute(
                "INSERT INTO learning_tasks(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                (
                    "continuous.task",
                    subject,
                    json.dumps(
                        {"subject": subject, "topics": topics, "origin": origin, "cycles": 0, "references_found": 0},
                        ensure_ascii=False,
                    ),
                    self._now(),
                ),
            )
            db.commit()
            return int(cursor.lastrowid)
        finally:
            db.close()

    def next_learning_task(self) -> dict | None:
        tasks = self.all_learning_tasks()
        active = [task for task in tasks if task["metadata"].get("active", True)]
        return min(active, key=lambda task: (task["cycles"], task["id"])) if active else None

    def all_learning_tasks(self) -> list[dict]:
        db = self.connect()
        try:
            rows = db.execute(
                "SELECT id, content, metadata FROM learning_tasks WHERE kind = 'continuous.task' ORDER BY id"
            ).fetchall()
        finally:
            db.close()
        tasks = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            tasks.append(
                {
                    "id": int(row["id"]),
                    "subject": metadata.get("subject") or row["content"],
                    "topics": metadata.get("topics", []),
                    "cycles": int(metadata.get("cycles", 0)),
                    "metadata": metadata,
                }
            )
        return tasks

    def list_learning_tasks(self, active_only: bool = True, limit: int | None = None, offset: int = 0) -> list[dict]:
        tasks = self.all_learning_tasks()
        if active_only:
            tasks = [task for task in tasks if task["metadata"].get("active", True)]
        start = max(0, offset)
        return tasks[start:] if limit is None else tasks[start : start + max(1, limit)]

    def deactivate_learning_task(self, subject: str, reason: str) -> bool:
        db = self.connect()
        try:
            row = db.execute(
                "SELECT id, metadata FROM learning_tasks WHERE kind = 'continuous.task' AND content = ? LIMIT 1",
                (subject,),
            ).fetchone()
            if not row:
                return False
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            metadata["active"] = False
            metadata["inactive_reason"] = reason
            metadata["deactivated_at"] = self._now()
            db.execute(
                "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), row["id"]),
            )
            db.commit()
            return True
        finally:
            db.close()

    def ensure_learning_reference(self, locator: str, metadata: dict) -> bool:
        db = self.connect()
        try:
            row = db.execute(
                """SELECT id FROM sources
                   WHERE kind = 'learning.reference' AND content = ?
                     AND json_extract(metadata, '$.subject') = ? LIMIT 1""",
                (locator, metadata.get("subject", "")),
            ).fetchone()
            if row:
                return False
            db.execute(
                "INSERT INTO sources(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                ("learning.reference", locator, json.dumps(metadata, ensure_ascii=False), self._now()),
            )
            db.commit()
            return True
        finally:
            db.close()

    def existing_learning_projects(self) -> list[dict]:
        db = self.connect()
        try:
            rows = db.execute(
                "SELECT content, metadata FROM memories WHERE kind IN ('learning.project', 'autonomous.project') ORDER BY id"
            ).fetchall()
        finally:
            db.close()
        projects = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            subject = metadata.get("subject") or row["content"].split(":", 1)[-1].strip()
            if subject:
                projects.append({"subject": subject, "topics": metadata.get("topics", [])})
        return projects

    def mark_learning_cycle(self, task_id: int, references_added: int, reason: str, assessment: dict | None = None) -> None:
        db = self.connect()
        try:
            row = db.execute("SELECT metadata FROM learning_tasks WHERE id = ?", (task_id,)).fetchone()
            metadata = json.loads(row["metadata"]) if row else {}
            metadata["cycles"] = int(metadata.get("cycles", 0)) + 1
            metadata["references_found"] = int(metadata.get("references_found", 0)) + references_added
            metadata["last_cycle_at"] = self._now()
            metadata["last_reason"] = reason
            if assessment:
                metadata["meta_learning"] = assessment
            db.execute(
                "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), task_id),
            )
            db.execute(
                "INSERT INTO events(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                (
                    "continuous_learning.cycle",
                    metadata.get("subject", ""),
                    json.dumps(
                        {"task_id": task_id, "references_added": references_added, "reason": reason, "assessment": assessment or {}},
                        ensure_ascii=False,
                    ),
                    self._now(),
                ),
            )
            db.commit()
        finally:
            db.close()

    def learning_references_for_subject(self, subject: str) -> list[dict]:
        db = self.connect()
        try:
            rows = db.execute(
                """SELECT content, metadata, created_at FROM sources
                   WHERE kind = 'learning.reference'
                     AND json_extract(metadata, '$.subject') = ?
                   ORDER BY id""",
                (subject,),
            ).fetchall()
        finally:
            db.close()
        references = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            references.append({"locator": row["content"], "metadata": metadata, "created_at": row["created_at"]})
        return references

    def deactivate_invalid_learning_tasks(self, validator) -> int:
        db = self.connect()
        changed = 0
        try:
            rows = db.execute("SELECT id, content, metadata FROM learning_tasks WHERE kind = 'continuous.task'").fetchall()
            for row in rows:
                if validator(row["content"]):
                    continue
                try:
                    metadata = json.loads(row["metadata"])
                except (TypeError, ValueError):
                    metadata = {}
                if metadata.get("active") is False:
                    continue
                metadata["active"] = False
                metadata["inactive_reason"] = "Kein geeignetes, klar abgegrenztes Lernziel."
                db.execute(
                    "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                    (json.dumps(metadata, ensure_ascii=False), row["id"]),
                )
                changed += 1
            db.commit()
        finally:
            db.close()
        return changed

    def learning_task_assessments(self, limit: int = 20) -> list[dict]:
        db = self.connect()
        try:
            rows = db.execute(
                "SELECT content, metadata FROM learning_tasks WHERE kind = 'continuous.task' ORDER BY id LIMIT ?",
                (max(1, limit),),
            ).fetchall()
        finally:
            db.close()
        result = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            result.append(
                {
                    "subject": row["content"],
                    "active": metadata.get("active", True),
                    "phase": metadata.get("meta_learning", {}).get("phase_name", "Bewusste Inkompetenz"),
                    "strategy": metadata.get("meta_learning", {}).get("strategy", "Lernlücke erfassen."),
                    "open_gaps": metadata.get("meta_learning", {}).get("open_gaps", []),
                }
            )
        return result

    def update_learning_assessment(self, task_id: int, assessment: dict) -> None:
        db = self.connect()
        try:
            row = db.execute("SELECT metadata FROM learning_tasks WHERE id = ?", (task_id,)).fetchone()
            if not row:
                return
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            metadata["meta_learning"] = assessment
            db.execute(
                "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), task_id),
            )
            db.commit()
        finally:
            db.close()

    def record_learning_application(self, subject: str, successful: bool, detail: str = "") -> bool:
        db = self.connect()
        try:
            row = db.execute(
                "SELECT id, metadata FROM learning_tasks WHERE kind = 'continuous.task' AND content = ? LIMIT 1",
                (subject,),
            ).fetchone()
            if not row:
                return False
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            key = "successful_applications" if successful else "failed_applications"
            metadata[key] = int(metadata.get(key, 0)) + 1
            if detail:
                metadata["last_application_detail"] = detail[:300]
            metadata["last_application_successful"] = bool(successful)
            metadata["last_application_at"] = self._now()
            db.execute(
                "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), row["id"]),
            )
            db.execute(
                "INSERT INTO events(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                (
                    "meta_learning.application",
                    subject,
                    json.dumps({"successful": bool(successful), "detail": detail[:300]}, ensure_ascii=False),
                    self._now(),
                ),
            )
            db.commit()
            return True
        finally:
            db.close()

    def count_learning_records(self) -> dict:
        db = self.connect()
        try:
            return {
                "tasks": int(
                    db.execute(
                        """SELECT COUNT(*) FROM learning_tasks
                           WHERE kind = 'continuous.task'
                             AND COALESCE(json_extract(metadata, '$.active'), 1) != 0"""
                    ).fetchone()[0]
                ),
                "inactive_tasks": int(
                    db.execute(
                        """SELECT COUNT(*) FROM learning_tasks
                           WHERE kind = 'continuous.task'
                             AND COALESCE(json_extract(metadata, '$.active'), 1) = 0"""
                    ).fetchone()[0]
                ),
                "references": int(db.execute("SELECT COUNT(*) FROM sources WHERE kind = 'learning.reference'").fetchone()[0]),
                "cycles": int(db.execute("SELECT COUNT(*) FROM events WHERE kind = 'continuous_learning.cycle'").fetchone()[0]),
            }
        finally:
            db.close()

    def add_edge(self, source: str, relation: str, target: str, metadata: dict | None = None) -> int:
        payload = {"source": source, "relation": relation, "target": target, **(metadata or {})}
        return self.add("graph_edges", relation, f"{source} -> {target}", payload)

    def search(self, term: str, limit: int = 20) -> list[dict]:
        pattern = f"%{term}%"
        hits: list[dict] = []
        db = self.connect()
        try:
            for table in self.KNOWLEDGE_SEARCH_TABLES:
                rows = db.execute(
                    f"SELECT kind, content, metadata, created_at FROM {table} "
                    "WHERE content LIKE ? OR kind LIKE ? ORDER BY id DESC LIMIT ?",
                    (pattern, pattern, max(1, limit - len(hits))),
                ).fetchall()
                hits.extend({"table": table, **dict(row)} for row in rows)
                if len(hits) >= limit:
                    break
        finally:
            db.close()
        return hits[:limit]

    def index_file(self, path: str, area: str, content: str, modified_ns: int, archive: bool = False) -> None:
        db = self.connect()
        try:
            current = db.execute("SELECT modified_ns FROM file_search_documents WHERE path = ?", (path,)).fetchone()
            if current and int(current["modified_ns"]) == int(modified_ns):
                return
            db.execute(
                """INSERT INTO file_search_documents(path, area, content, modified_ns, archive)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(path) DO UPDATE SET area=excluded.area, content=excluded.content,
                   modified_ns=excluded.modified_ns, archive=excluded.archive""",
                (path, area, content, int(modified_ns), int(bool(archive))),
            )
            try:
                db.execute("DELETE FROM file_search_fts WHERE path = ?", (path,))
                db.execute(
                    "INSERT INTO file_search_fts(path, area, content, archive) VALUES (?, ?, ?, ?)",
                    (path, area, content, str(int(bool(archive)))),
                )
            except sqlite3.OperationalError:
                pass
            db.commit()
        finally:
            db.close()

    def search_files(self, term: str, limit: int = 20, include_archive: bool = False) -> list[dict]:
        db = self.connect()
        try:
            archive_filter = "" if include_archive else "AND archive = '0'"
            try:
                rows = db.execute(
                    f"""SELECT path, area, snippet(file_search_fts, 2, '', '', ' ... ', 24) AS snippet,
                               CAST(archive AS INTEGER) AS archive
                        FROM file_search_fts WHERE file_search_fts MATCH ? {archive_filter} LIMIT ?""",
                    (term, max(1, limit)),
                ).fetchall()
            except sqlite3.OperationalError:
                pattern = f"%{term}%"
                rows = db.execute(
                    """SELECT path, area, substr(content, 1, 260) AS snippet, archive
                       FROM file_search_documents
                       WHERE (content LIKE ? OR path LIKE ?) AND (? OR archive = 0) LIMIT ?""",
                    (pattern, pattern, int(bool(include_archive)), max(1, limit)),
                ).fetchall()
            return [dict(row) for row in rows]
        finally:
            db.close()

    def user_inputs_for_local_date(self, target_date: date | None = None) -> list[dict]:
        local_timezone = datetime.now().astimezone().tzinfo or timezone.utc
        selected_date = target_date or datetime.now(local_timezone).date()
        start_local = datetime.combine(selected_date, time.min, tzinfo=local_timezone)
        end_local = start_local + timedelta(days=1)
        start_utc = start_local.astimezone(timezone.utc).isoformat()
        end_utc = end_local.astimezone(timezone.utc).isoformat()

        db = self.connect()
        try:
            current_rows = db.execute(
                """SELECT kind, content, metadata, created_at FROM events
                   WHERE kind = 'conversation.turn'
                     AND json_extract(metadata, '$.role') = 'user'
                     AND created_at >= ? AND created_at < ?
                   ORDER BY created_at, id""",
                (start_utc, end_utc),
            ).fetchall()

            event_start = current_rows[0]["created_at"] if current_rows else end_utc
            central_legacy_rows = db.execute(
                """SELECT kind, content, metadata, created_at FROM memories
                   WHERE kind = 'user.input' AND created_at >= ? AND created_at < ?
                   ORDER BY created_at, id""",
                (start_utc, event_start),
            ).fetchall()

            # Before central input logging existed, these agents stored exact prompts.
            central_legacy_start = central_legacy_rows[0]["created_at"] if central_legacy_rows else event_start
            legacy_rows = db.execute(
                """SELECT kind, content, metadata, created_at FROM memories
                   WHERE kind IN ('dialog.user', 'knowledge.query', 'planner.task',
                                  'reflection.task', 'tool.winget')
                     AND created_at >= ? AND created_at < ?
                   ORDER BY created_at, id""",
                (start_utc, central_legacy_start),
            ).fetchall()
        finally:
            db.close()

        return [dict(row) for row in (*legacy_rows, *central_legacy_rows, *current_rows)]

    def recent_conversation_turns(self, session_id: str, limit: int = 8) -> list[dict]:
        db = self.connect()
        try:
            rows = db.execute(
                """SELECT content, metadata, created_at FROM events
                   WHERE kind = 'conversation.turn'
                     AND json_extract(metadata, '$.session_id') = ?
                   ORDER BY id DESC LIMIT ?""",
                (session_id, max(1, limit)),
            ).fetchall()
        finally:
            db.close()

        turns = []
        for row in reversed(rows):
            try:
                metadata = json.loads(row["metadata"])
            except (TypeError, ValueError):
                metadata = {}
            turns.append(
                {
                    "role": metadata.get("role", ""),
                    "content": row["content"],
                    "intent": metadata.get("intent", ""),
                    "agent": metadata.get("agent", ""),
                    "created_at": row["created_at"],
                }
            )
        return turns

    def counts(self) -> dict[str, int]:
        db = self.connect()
        try:
            return {table: int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in self.TABLES}
        finally:
            db.close()
