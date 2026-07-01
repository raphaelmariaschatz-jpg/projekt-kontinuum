from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from .meta_learning import MetaLearningEngine


class ContinuousLearningService:
    DEFAULT_CONFIG = {
        "enabled": True,
        "interval_seconds": 60,
        "startup_delay_seconds": 5,
        "max_references_per_cycle": 3,
        "max_files_scanned_per_cycle": 1500,
        "max_characters_read_per_file": 200000,
        "allowed_suffixes": [".json", ".md", ".txt", ".py"],
        "policy": "references_only",
        "default_subjects": ["Mathematik", "Physik", "Chemie", "Biologie", "Informatik", "Geschichte", "Philosophie"],
    }

    def __init__(self, path_tools, storage):
        self.path_tools = path_tools
        self.storage = storage
        self.config_path = path_tools.paths()["config"] / "continuous_learning.json"
        self.config = self._load_config()
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._last_result: dict = {}
        self.meta_learning = MetaLearningEngine()
        self.foundation_decision = None
        self.foundation_guard = None
        self.foundation_memory = None

    def bind_foundation(self, foundation_decision) -> None:
        self.foundation_decision = foundation_decision

    def bind_foundation_guard(self, foundation_guard) -> None:
        self.foundation_guard = foundation_guard

    def bind_foundation_memory(self, foundation_memory) -> None:
        self.foundation_memory = foundation_memory

    def _is_foundation_subject(self, subject: str) -> bool:
        if self.foundation_guard and self.foundation_guard.is_foundation(subject):
            return True
        return bool(
            self.foundation_memory
            and self.foundation_memory.classify(subject, self.foundation_guard).get("is_foundation")
        )

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        override = os.getenv("KONTINUUM_CONTINUOUS_LEARNING")
        if override is not None:
            config["enabled"] = override.casefold() not in {"0", "false", "no", "off"}
        return config

    def start(self) -> bool:
        if not self.config["enabled"] or self.is_running():
            return False
        self._stop.clear()
        self._wake.clear()
        self._thread = threading.Thread(target=self._worker, name="KontinuumContinuousLearning", daemon=True)
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
        counts = self.storage.count_learning_records()
        assessments = self.meta_status(200)
        phase_counts: dict[str, int] = {}
        for assessment in assessments:
            phase = assessment["phase"] if assessment["active"] else "deaktiviert"
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        return {
            "enabled": bool(self.config["enabled"]),
            "running": self.is_running(),
            "policy": self.config["policy"],
            "interval_seconds": int(self.config["interval_seconds"]),
            "tasks": counts["tasks"],
            "inactive_tasks": counts["inactive_tasks"],
            "references": counts["references"],
            "cycles": counts["cycles"],
            "phase_counts": phase_counts,
            "last_result": dict(self._last_result),
        }

    def add_task(self, subject: str, topics: list[str] | None = None, origin: str = "user") -> int:
        if self._is_foundation_subject(subject):
            self.storage.add("audit_events", "foundation.learning_task.blocked", subject, {
                "origin": origin,
                "knowledge_class": "foundation_knowledge",
                "reason": "Fundamentwissen darf nicht als Lernauftrag oder Wissenslücke geführt werden.",
            })
            raise ValueError("Fundamentwissen darf nicht als Lernauftrag oder Wissenslücke angelegt werden.")
        task_id = self.storage.ensure_learning_task(subject, topics or [], origin)
        self.wake()
        return task_id

    def meta_status(self, limit: int = 12) -> list[dict]:
        return self.storage.learning_task_assessments(limit)

    def record_application(self, subject: str, successful: bool, detail: str = "") -> bool:
        recorded = self.storage.record_learning_application(subject, successful, detail)
        if recorded:
            self.wake()
        return recorded

    def seed_default_tasks(self) -> int:
        self.storage.deactivate_invalid_learning_tasks(self.meta_learning.is_valid_subject)
        created = 0
        configured = [{"subject": subject, "topics": []} for subject in self.config["default_subjects"]]
        projects = [*configured, *self.storage.existing_learning_projects()]
        for project in projects:
            if not self.meta_learning.is_valid_subject(str(project["subject"])):
                continue
            if self._is_foundation_subject(str(project["subject"])):
                continue
            before = self.storage.count_learning_records()["tasks"]
            self.storage.ensure_learning_task(str(project["subject"]), list(project.get("topics", [])), "continuous_seed")
            created += int(self.storage.count_learning_records()["tasks"] > before)
        self.refresh_meta_assessments()
        return created

    def refresh_meta_assessments(self) -> int:
        updated = 0
        for task in self.storage.all_learning_tasks():
            if not task["metadata"].get("active", True):
                continue
            references = self.storage.learning_references_for_subject(task["subject"])
            assessment = self.meta_learning.assess(task, references)
            self.storage.update_learning_assessment(task["id"], assessment.as_dict())
            updated += 1
        return updated

    def run_cycle(self, reason: str = "background") -> dict:
        if self.foundation_decision and reason == "background":
            return self.foundation_decision.run_internal(
                "Kontinuierlichen autonomen Lernzyklus ausführen",
                lambda: self._run_cycle(reason),
                {"service": "continuous_learning"},
            )
        return self._run_cycle(reason)

    def _run_cycle(self, reason: str = "background") -> dict:
        if not self.config["enabled"]:
            return {"ok": False, "message": "Kontinuierliches Lernen ist deaktiviert."}
        with self._lock:
            task = self.storage.next_learning_task()
            if not task:
                result = {"ok": True, "task": "", "references_added": 0, "message": "Kein Lernauftrag vorhanden."}
            else:
                references = self._discover_references(task["subject"], task.get("topics", []))
                added = 0
                for reference in references:
                    added += int(self.storage.ensure_learning_reference(reference["locator"], reference["metadata"]))
                all_references = self.storage.learning_references_for_subject(task["subject"])
                assessment_task = dict(task)
                assessment_task["metadata"] = dict(task.get("metadata", {}))
                assessment_task["metadata"]["cycles"] = int(assessment_task["metadata"].get("cycles", 0)) + 1
                assessment = self.meta_learning.assess(assessment_task, all_references)
                self.storage.mark_learning_cycle(task["id"], added, reason, assessment.as_dict())
                result = {
                    "ok": True,
                    "task": task["subject"],
                    "references_added": added,
                    "references_considered": len(references),
                    "phase": assessment.phase_name,
                    "strategy": assessment.strategy,
                    "open_gaps": assessment.open_gaps,
                    "message": (
                        f"Lernzyklus für {task['subject']}: {added} neue Fundstellen indexiert. "
                        f"Phase: {assessment.phase_name}."
                    ),
                }
            self._last_result = result
            return result

    def _worker(self) -> None:
        if self._stop.wait(max(0, int(self.config["startup_delay_seconds"]))):
            return
        while not self._stop.is_set():
            try:
                self.run_cycle()
            except Exception as exc:
                self._last_result = {"ok": False, "message": f"Lernzyklusfehler: {exc}"}
            self._wake.clear()
            self._wake.wait(max(1, int(self.config["interval_seconds"])))

    def _discover_references(self, subject: str, topics: list[str]) -> list[dict]:
        needles = [subject.casefold(), *(str(topic).casefold() for topic in topics[:8])]
        roots = [
            ("04_knowledge", self.path_tools.paths()["knowledge"]),
            ("06_learning", self.path_tools.paths()["learning"]),
            ("03_memory", self.path_tools.paths()["memory"]),
            ("22_project_chronicle", self.path_tools.paths()["chronicle"]),
        ]
        allowed = {str(value).casefold() for value in self.config["allowed_suffixes"]}
        max_scan = max(1, int(self.config["max_files_scanned_per_cycle"]))
        max_refs = max(1, int(self.config["max_references_per_cycle"]))
        max_characters = max(1000, int(self.config["max_characters_read_per_file"]))
        scanned = 0
        references: list[dict] = []
        for area, root in roots:
            if not root.exists():
                continue
            for file in root.rglob("*"):
                if scanned >= max_scan or len(references) >= max_refs:
                    return references
                if not file.is_file() or file.suffix.casefold() not in allowed:
                    continue
                scanned += 1
                name_match = any(needle in file.name.casefold() for needle in needles)
                content_match = False
                if not name_match:
                    try:
                        with file.open("r", encoding="utf-8-sig", errors="replace") as handle:
                            text = handle.read(max_characters)
                        content_match = any(needle in text.casefold() for needle in needles)
                    except OSError:
                        continue
                if name_match or content_match:
                    references.append(
                        {
                            "locator": str(file),
                            "metadata": {
                                "subject": subject,
                                "topics": topics[:8],
                                "source_type": "local_file",
                                "area": area,
                                "policy": "references_only",
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            },
                        }
                    )
        return references
