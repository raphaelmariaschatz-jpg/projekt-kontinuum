# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


class SafetyBlock(NotImplementedError):
    """Raised when a mutating CDM operation is requested in read-only mode."""


class CanonicalDataManager:
    """Read-only resolver and verifier for Kontinuum canonical data paths."""

    VERSION = "1.0"
    VALID_CATEGORIES = {
        "canonical_master_data",
        "runtime_data",
        "logs",
        "historical_version_data",
        "exports",
        "temporary_data",
        "unclear_review_required",
    }

    def __init__(
        self,
        project_root: str | Path,
        registry_path: str | Path | None = None,
        strict_config: bool = True,
    ):
        self.root = Path(project_root).resolve()
        self.registry_path = (
            Path(registry_path).resolve()
            if registry_path is not None
            else self.root / "24_config" / "canonical_data_registry_1_0.json"
        )
        self.strict_config = strict_config
        self.registry = self.load_registry()
        self._by_id = {
            item.get("logical_id", ""): item
            for item in self.registry.get("data_objects", [])
            if item.get("logical_id")
        }
        self._by_path = {
            self._normalize_relative(item.get("current_path", "")): item
            for item in self.registry.get("data_objects", [])
            if item.get("current_path")
        }

    def load_registry(self) -> dict:
        try:
            value = json.loads(self.registry_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            if not self.strict_config:
                return {"version": self.VERSION, "configured": False, "data_objects": []}
            raise RuntimeError(f"Canonical Data Registry fehlt oder ist ungueltig: {self.registry_path}") from exc
        if value.get("version") != self.VERSION:
            raise RuntimeError("Canonical Data Registry gehoert nicht zu CDM 1.0.")
        return value

    @staticmethod
    def _normalize_relative(path: str | Path) -> str:
        return Path(str(path).replace("\\", "/")).as_posix().lstrip("./")

    def _absolute(self, relative_path: str | Path) -> Path:
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return self.root / self._normalize_relative(relative_path)

    def resolve(self, logical_id: str) -> Path:
        item = self._by_id.get(logical_id)
        if item is None:
            raise KeyError(f"Unbekannte logische Daten-ID: {logical_id}")
        return self._absolute(item["current_path"])

    def classify(self, path: str | Path) -> str:
        path_obj = Path(path)
        relative = (
            path_obj.resolve().relative_to(self.root).as_posix()
            if path_obj.is_absolute()
            else self._normalize_relative(path)
        )
        item = self._by_path.get(relative)
        if item is not None:
            return item.get("category", "unclear_review_required")

        lowered = relative.casefold()
        name = Path(relative).name.casefold()
        if "32_data/02_versions/" in lowered or name.startswith("_version_"):
            return "historical_version_data"
        if name.startswith("_legacy_") or name.startswith("_02_versions_") or "legacy_versions" in lowered:
            return "historical_version_data"
        if "32_data/17_tests/" in lowered or "_migration_" in lowered or "backup" in lowered:
            return "temporary_data"
        if "internet_learning_queue" in lowered or "internet_learning_review" in lowered or "export" in lowered:
            return "exports"
        if any(token in name for token in ("log", "audit", "report", "chronicle")):
            return "logs"
        return "unclear_review_required"

    def exists(self, logical_id: str) -> bool:
        return self.resolve(logical_id).exists()

    def validate_registry(self) -> dict:
        objects = self.registry.get("data_objects", [])
        logical_ids = [item.get("logical_id", "") for item in objects]
        duplicate_ids = sorted(item for item, count in Counter(logical_ids).items() if item and count > 1)
        invalid_categories = sorted(
            {
                item.get("category", "")
                for item in objects
                if item.get("category") not in self.VALID_CATEGORIES
            }
        )
        write_enabled = sorted(
            item.get("logical_id", "")
            for item in objects
            if not item.get("read_only", True) or item.get("migration_approved", False)
        )
        missing_paths = sorted(
            item.get("logical_id", "")
            for item in objects
            if item.get("current_path") and not self._absolute(item["current_path"]).exists()
        )
        issues = []
        if duplicate_ids:
            issues.append("duplicate_logical_ids")
        if invalid_categories:
            issues.append("invalid_categories")
        if write_enabled:
            issues.append("write_or_migration_enabled")
        if missing_paths:
            issues.append("missing_current_paths")
        return {
            "ok": not issues,
            "version": self.VERSION,
            "object_count": len(objects),
            "duplicate_logical_ids": duplicate_ids,
            "invalid_categories": invalid_categories,
            "write_or_migration_enabled": write_enabled,
            "missing_current_paths": missing_paths,
            "issues": issues,
            "mutation_policy": self.registry.get("mutation_policy", "read_only_no_migration"),
        }

    def _list_by_category(self, *categories: str) -> list[dict]:
        allowed = set(categories)
        return [
            item
            for item in self.registry.get("data_objects", [])
            if item.get("category") in allowed
        ]

    def list_active_data(self) -> list[dict]:
        return self._list_by_category("canonical_master_data", "runtime_data", "logs")

    def list_historical_data(self) -> list[dict]:
        return self._list_by_category("historical_version_data")

    def list_runtime_data(self) -> list[dict]:
        return self._list_by_category("runtime_data")

    def list_unclear_data(self) -> list[dict]:
        return self._list_by_category("unclear_review_required")

    def generate_status_report(self) -> dict:
        objects = self.registry.get("data_objects", [])
        categories = Counter(item.get("category", "unclear_review_required") for item in objects)
        validation = self.validate_registry()
        risks = Counter(item.get("risk", "unknown") for item in objects)
        return {
            "version": self.VERSION,
            "ok": validation["ok"],
            "read_only": True,
            "migration_performed": False,
            "object_count": len(objects),
            "active_or_canonical_count": len(self.list_active_data()),
            "historical_count": categories.get("historical_version_data", 0),
            "runtime_count": categories.get("runtime_data", 0),
            "unclear_count": categories.get("unclear_review_required", 0),
            "category_counts": dict(sorted(categories.items())),
            "risk_counts": dict(sorted(risks.items())),
            "validation": validation,
            "registry_path": str(self.registry_path),
            "mutation_policy": self.registry.get("mutation_policy", "read_only_no_migration"),
        }

    def format_status_report(self) -> str:
        status = self.generate_status_report()
        return (
            f"Canonical Data Manager {self.VERSION}: "
            f"{'VALIDIERT' if status['ok'] else 'MANUAL REVIEW REQUIRED'}.\n"
            f"- Datenobjekte={status['object_count']}, "
            f"aktiv/kanonisch={status['active_or_canonical_count']}, "
            f"historisch={status['historical_count']}, "
            f"runtime={status['runtime_count']}, unklar={status['unclear_count']}.\n"
            "- Modus: read-only; keine Migration, keine Verschiebung, keine Loeschung."
        )

    def migrate(self, *args, **kwargs):
        raise SafetyBlock("CDM 1.0 ist read-only; Migration ist blockiert.")

    def move(self, *args, **kwargs):
        raise SafetyBlock("CDM 1.0 ist read-only; Verschieben ist blockiert.")

    def delete(self, *args, **kwargs):
        raise SafetyBlock("CDM 1.0 ist read-only; Loeschen ist blockiert.")

    def rewrite_reference(self, *args, **kwargs):
        raise SafetyBlock("CDM 1.0 ist read-only; Referenzumschreibung ist blockiert.")
