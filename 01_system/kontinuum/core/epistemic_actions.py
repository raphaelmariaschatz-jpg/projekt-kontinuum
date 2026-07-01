from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse


class EpistemicActionService:
    DEFAULT_CONFIG = {
        "enabled": True,
        "automatic": False,
        "automatic_interval_seconds": 300,
        "automatic_startup_delay_seconds": 20,
        "max_automatic_cycles_per_run": 1,
        "max_sources_per_cycle": 3,
        "max_attempts_per_task": 3,
        "minimum_snippet_characters": 30,
        "protected_markers": ["schöpfer", "schoepfer", "passwort", "sicherheit", "identität", "identitaet", "superadmin"],
    }

    def __init__(self, path_tools, storage, search_engine, web, classifier, intelligence, platform):
        self.storage = storage
        self.search_engine = search_engine
        self.web = web
        self.classifier = classifier
        self.intelligence = intelligence
        self.platform = platform
        self.config_path = path_tools.paths()["config"] / "epistemic_action.json"
        self.config = self._load_config()
        self._last_result: dict = {}
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self.foundation_decision = None

    def bind_foundation(self, foundation_decision) -> None:
        self.foundation_decision = foundation_decision

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        override = os.getenv("KONTINUUM_EPISTEMIC_AUTOMATIC")
        if override is not None:
            config["automatic"] = override.casefold() not in {"0", "false", "no", "off"}
        return config

    def start(self) -> bool:
        if not self.config["enabled"] or not self.config["automatic"] or self.is_running():
            return False
        self._stop.clear()
        self._wake.clear()
        self._thread = threading.Thread(target=self._worker, name="KontinuumEpistemicAutomation", daemon=True)
        self._thread.start()
        return True

    def stop(self, timeout: float = 3.0) -> bool:
        self._stop.set()
        self._wake.set()
        thread = self._thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=timeout)
        return not self.is_running()

    def wake(self) -> None:
        self._wake.set()

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def status(self) -> dict:
        with self.storage.connect() as database:
            active = int(database.execute(
                "SELECT COUNT(*) FROM learning_tasks WHERE kind = 'epistemic.review' AND COALESCE(json_extract(metadata, '$.active'), 1) != 0"
            ).fetchone()[0])
            completed = int(database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'epistemic.action.cycle' AND json_extract(metadata, '$.resolved') = 1"
            ).fetchone()[0])
            cycles = int(database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'epistemic.action.cycle'"
            ).fetchone()[0])
        return {
            "enabled": bool(self.config["enabled"]),
            "automatic": bool(self.config["automatic"]),
            "running": self.is_running(),
            "interval_seconds": int(self.config["automatic_interval_seconds"]),
            "active_review_tasks": active,
            "cycles": cycles,
            "resolved_cycles": completed,
            "last_result": dict(self._last_result),
        }

    def run_cycle(self, task_id: int | None = None) -> dict:
        if not self.config["enabled"]:
            return {"ok": False, "message": "Epistemische Aktionsschicht ist deaktiviert."}
        with self._lock:
            task = self._select_task(task_id)
            if not task:
                return {"ok": False, "message": "Kein aktiver epistemischer Prüfauftrag verfügbar."}
            metadata = task["metadata"]
            attempts = int(metadata.get("action_attempts", 0))
            if attempts >= int(self.config["max_attempts_per_task"]):
                return self._finish(task, [], "max_attempts", False, "Maximale Prüfversuche erreicht.", terminal=True)
            knowledge = self._knowledge(int(metadata["knowledge_id"]))
            if not knowledge:
                return self._finish(task, [], "missing_knowledge", False, "Zugehöriges Wissen nicht gefunden.", terminal=True)
            if self._protected(knowledge["content"]):
                return self._finish(task, [], "protected", False, "Geschütztes Identitäts- oder Sicherheitswissen wird nicht automatisch recherchiert.", terminal=True)
            before = knowledge["metadata"].get("epistemic", {}).get("state", "unbewertet")
            result = self.search_engine.search(self._query(knowledge["content"]), limit=int(self.config["max_sources_per_cycle"]))
            accepted = self._evaluate_results(knowledge["content"], result.get("results", []))
            source_ids = []
            for row in accepted:
                source_ids.append(self.storage.add_source(row["url"], {
                    "title": row.get("title", ""),
                    "snippet": row.get("snippet", ""),
                    "page_title": row.get("page_title", ""),
                    "page_excerpt": row.get("page_excerpt", ""),
                    "provider": row.get("provider", ""),
                    "quality": row["quality"],
                    "source_class": row["quality"]["class"],
                    "quality_weight": row["quality"]["weight"],
                    "epistemic_review_task_id": task["id"],
                    "knowledge_id": knowledge["id"],
                    "status": "accepted_evidence",
                }))
            if source_ids:
                knowledge_metadata = dict(knowledge["metadata"])
                existing = list(knowledge_metadata.get("source_record_ids") or [])
                knowledge_metadata["source_record_ids"] = list(dict.fromkeys([*existing, *source_ids]))
                knowledge_metadata["source_record_id"] = knowledge_metadata["source_record_ids"][0]
                self._update_knowledge(knowledge["id"], knowledge_metadata)
            self.intelligence.refresh()
            after_row = self._knowledge(knowledge["id"])
            after = after_row["metadata"].get("epistemic", {}).get("state", "unbewertet")
            resolved = after == "knowledge"
            message = (
                f"Prüfzyklus für Wissen {knowledge['id']}: {len(source_ids)} akzeptierte Quellen. "
                f"Zustand {before} -> {after}."
            )
            return self._finish(task, source_ids, "completed", resolved, message, before, after)

    def run_automatic_cycle(self) -> dict:
        if self.foundation_decision:
            return self.foundation_decision.run_internal(
                "Automatischen epistemischen Prüfzyklus ausführen",
                self._run_automatic_cycle,
                {"service": "epistemic_actions"},
            )
        return self._run_automatic_cycle()

    def _run_automatic_cycle(self) -> dict:
        if not self.config["automatic"]:
            return {"ok": False, "message": "Epistemische Automatik ist deaktiviert."}
        results = []
        for _ in range(max(1, int(self.config["max_automatic_cycles_per_run"]))):
            result = self.run_cycle()
            results.append(result)
            if not result.get("ok") or result.get("resolved"):
                break
        summary = {
            "ok": any(result.get("ok") for result in results),
            "automatic": True,
            "cycles": len(results),
            "results": results,
            "message": results[-1]["message"] if results else "Kein automatischer Prüfzyklus ausgeführt.",
        }
        self._last_result = summary
        self.storage.add("events", "epistemic.automation.run", summary["message"], {
            "cycles": len(results), "resolved": sum(bool(row.get("resolved")) for row in results)
        })
        return summary

    def _worker(self) -> None:
        if self._stop.wait(max(0, int(self.config["automatic_startup_delay_seconds"]))):
            return
        while not self._stop.is_set():
            try:
                self.run_automatic_cycle()
            except Exception as exc:
                self._last_result = {"ok": False, "automatic": True, "message": f"Automatischer Prüfzyklusfehler: {exc}"}
            self._wake.clear()
            self._wake.wait(max(10, int(self.config["automatic_interval_seconds"])))

    def _select_task(self, task_id: int | None) -> dict | None:
        with self.storage.connect() as database:
            if task_id is not None:
                row = database.execute(
                    "SELECT id, content, metadata FROM learning_tasks WHERE id = ? AND kind = 'epistemic.review'",
                    (task_id,),
                ).fetchone()
            else:
                row = database.execute(
                    """SELECT id, content, metadata FROM learning_tasks
                       WHERE kind = 'epistemic.review' AND COALESCE(json_extract(metadata, '$.active'), 1) != 0
                         AND COALESCE(json_extract(metadata, '$.action_attempts'), 0) < ?
                       ORDER BY CASE json_extract(metadata, '$.priority') WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END DESC,
                                COALESCE(json_extract(metadata, '$.action_attempts'), 0), id LIMIT 1"""
                    , (int(self.config["max_attempts_per_task"]),)
                ).fetchone()
        if not row:
            return None
        return {"id": int(row["id"]), "content": row["content"], "metadata": self._metadata(row["metadata"])}

    def _knowledge(self, knowledge_id: int) -> dict | None:
        with self.storage.connect() as database:
            row = database.execute(
                "SELECT id, content, metadata FROM knowledge_items WHERE id = ? AND kind = 'knowledge.integrated'",
                (knowledge_id,),
            ).fetchone()
        return {"id": int(row["id"]), "content": row["content"], "metadata": self._metadata(row["metadata"])} if row else None

    def _evaluate_results(self, content: str, rows: list[dict]) -> list[dict]:
        keywords = {word for word in re.findall(r"\w{4,}", content.casefold())}
        accepted = []
        domains = set()
        for row in rows:
            domain = urlparse(row.get("url", "")).netloc.casefold().removeprefix("www.")
            snippet = " ".join(str(row.get("snippet", "")).split())
            if not domain or domain in domains or len(snippet) < int(self.config["minimum_snippet_characters"]):
                continue
            page = self.web.fetch_text(row["url"], timeout=int(self.config.get("page_timeout_seconds", 6))) if self.web else {}
            page_text = " ".join(str(page.get("text", "")).split())
            if page.get("error") or len(page_text) < int(self.config.get("minimum_page_characters", 120)):
                continue
            overlap = sum(
                word in snippet.casefold()
                or word in str(row.get("title", "")).casefold()
                or word in page_text[:6000].casefold()
                for word in keywords
            )
            if overlap < 1:
                continue
            domains.add(domain)
            classification = self.classifier.classify(row["url"], page.get("title", row.get("title", "")), page_text)
            accepted.append({
                **row,
                "page_title": page.get("title", ""),
                "page_excerpt": page_text[:1200],
                "quality": {**classification, "keyword_overlap": overlap, "page_verified": True, "accepted": True},
            })
        return accepted[: int(self.config["max_sources_per_cycle"])]

    def _finish(
        self,
        task: dict,
        source_ids: list[int],
        outcome: str,
        resolved: bool,
        message: str,
        before: str = "",
        after: str = "",
        terminal: bool = False,
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        metadata = dict(task["metadata"])
        metadata["action_attempts"] = int(metadata.get("action_attempts", 0)) + 1
        metadata["last_action_at"] = now
        metadata["last_action_outcome"] = outcome
        metadata["last_source_ids"] = source_ids
        if resolved or terminal:
            metadata["active"] = False
            metadata["resolved_at"] = now
        if terminal:
            metadata["terminal"] = True
            metadata["terminal_outcome"] = outcome
        with self.storage.connect() as database:
            database.execute(
                "UPDATE learning_tasks SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), task["id"]),
            )
            database.commit()
        event_metadata = {
            "task_id": task["id"],
            "knowledge_id": metadata.get("knowledge_id"),
            "source_ids": source_ids,
            "outcome": outcome,
            "resolved": resolved,
            "before": before,
            "after": after,
        }
        self.storage.add("events", "epistemic.action.cycle", message, event_metadata)
        self.storage.add("chronicle_entries", "epistemic.action.cycle", message, event_metadata)
        result = {"ok": outcome == "completed", "task_id": task["id"], "sources": len(source_ids), "resolved": resolved, "message": message}
        self._last_result = result
        return result

    def _update_knowledge(self, knowledge_id: int, metadata: dict) -> None:
        with self.storage.connect() as database:
            database.execute(
                "UPDATE knowledge_items SET metadata = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), knowledge_id),
            )
            database.commit()

    def _protected(self, content: str) -> bool:
        lower = content.casefold()
        return any(marker in lower for marker in self.config["protected_markers"])

    @staticmethod
    def _query(content: str) -> str:
        return " ".join(content.split())[:240]

    @staticmethod
    def _metadata(value: str) -> dict:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
