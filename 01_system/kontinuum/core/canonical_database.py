from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class CanonicalDatabaseManager:
    """Read-only verifier for Kontinuum's canonical SQLite contract."""

    VERSION = "1.2"

    def __init__(
        self,
        project_root: str | Path,
        storage=None,
        release_version: str = "34.1",
        strict_config: bool = True,
    ):
        self.root = Path(project_root).resolve()
        self.storage = storage
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.config_path = self.root / "24_config" / f"canonical_database_{token}.json"
        self.strict_config = strict_config
        self.config = self._load_config()

    def _load_config(self) -> dict:
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            if not self.strict_config:
                return {"version": self.release_version, "configured": False}
            raise RuntimeError(f"CDM-Konfiguration fehlt oder ist ungueltig: {self.config_path}") from exc
        if value.get("version") != self.release_version:
            raise RuntimeError("CDM-Konfiguration gehoert nicht zur aktiven Version.")
        return value

    def _database_path(self) -> Path:
        if self.storage is not None:
            return Path(self.storage.database)
        return self.root / self.config.get("database", "32_data/kontinuum.db")

    @staticmethod
    def _objects(connection: sqlite3.Connection, object_type: str) -> dict[str, str]:
        return {
            str(row[0]): str(row[1] or "")
            for row in connection.execute(
                """SELECT name, sql FROM sqlite_master
                   WHERE type = ? AND name NOT LIKE 'sqlite_%' ORDER BY name""",
                (object_type,),
            )
        }

    @staticmethod
    def _columns(connection: sqlite3.Connection, table: str) -> dict[str, dict]:
        return {
            str(row[1]): {
                "type": str(row[2] or "").upper(),
                "not_null": bool(row[3]),
                "default": row[4],
                "primary_key": bool(row[5]),
            }
            for row in connection.execute(f'PRAGMA table_info("{table}")')
        }

    def status(self) -> dict:
        if not self.config.get("configured", True):
            return {
                "version": self.VERSION,
                "active": False,
                "ok": False,
                "configured": False,
                "mutation_policy": "read_only_verification; controlled_migration_only",
            }
        database = self._database_path()
        if not database.is_file():
            return {
                "version": self.VERSION,
                "active": True,
                "ok": False,
                "database": str(database),
                "error": "Kanonische Datenbank fehlt.",
                "mutation_policy": "read_only_verification; controlled_migration_only",
            }
        try:
            with sqlite3.connect(f"file:{database.resolve().as_posix()}?mode=ro", uri=True) as connection:
                integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
                foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
                tables = self._objects(connection, "table")
                indexes = self._objects(connection, "index")
                triggers = self._objects(connection, "trigger")
                views = self._objects(connection, "view")

                required_tables = self.config.get("required_tables", [])
                missing_tables = [name for name in required_tables if name not in tables]

                column_issues: dict[str, dict] = {}
                for table, expected_columns in self.config.get("table_contracts", {}).items():
                    if table not in tables:
                        continue
                    actual = self._columns(connection, table)
                    missing = [name for name in expected_columns if name not in actual]
                    mismatched = {
                        name: {"expected": expected, "actual": actual.get(name)}
                        for name, expected in expected_columns.items()
                        if name in actual
                        and any(actual[name].get(key) != value for key, value in expected.items())
                    }
                    if missing or mismatched:
                        column_issues[table] = {"missing": missing, "mismatched": mismatched}

                required_indexes = self.config.get("required_indexes", [])
                missing_indexes = [name for name in required_indexes if name not in indexes]
                required_triggers = self.config.get("required_triggers", [])
                missing_triggers = [name for name in required_triggers if name not in triggers]

                fts = {}
                for name in self.config.get("required_fts", []):
                    sql = tables.get(name, "")
                    fts[name] = {
                        "present": name in tables,
                        "fts5": "USING fts5" in sql or "using fts5" in sql.casefold(),
                    }
                fts_ok = all(item["present"] and item["fts5"] for item in fts.values())

                domains = {}
                for domain, domain_tables in self.config.get("data_domains", {}).items():
                    missing = [name for name in domain_tables if name not in tables]
                    domains[domain] = {
                        "ok": not missing,
                        "tables": domain_tables,
                        "missing": missing,
                    }
        except sqlite3.Error as exc:
            return {
                "version": self.VERSION,
                "active": True,
                "ok": False,
                "database": str(database),
                "error": str(exc),
                "mutation_policy": "read_only_verification; controlled_migration_only",
            }

        checks = {
            "integrity": integrity == "ok",
            "tables": not missing_tables,
            "columns": not column_issues,
            "indexes": not missing_indexes,
            "triggers": not missing_triggers,
            "fts": fts_ok,
            "data_domains": all(item["ok"] for item in domains.values()),
        }
        return {
            "version": self.VERSION,
            "active": True,
            "configured": True,
            "ok": all(checks.values()),
            "database": str(database),
            "checks": checks,
            "integrity_check": integrity,
            "foreign_keys_enabled": bool(foreign_keys),
            "object_counts": {
                "tables": len(tables),
                "indexes": len(indexes),
                "triggers": len(triggers),
                "views": len(views),
            },
            "missing_tables": missing_tables,
            "column_issues": column_issues,
            "missing_indexes": missing_indexes,
            "missing_triggers": missing_triggers,
            "fts": fts,
            "data_domains": domains,
            "unmanaged_tables": sorted(
                name
                for name in tables
                if name not in set(required_tables)
                and not any(name.startswith(f"{fts_name}_") for fts_name in self.config.get("required_fts", []))
            ),
            "mutation_policy": "read_only_verification; controlled_migration_only",
        }

    def format_status(self) -> str:
        status = self.status()
        if not status.get("configured", True):
            return "Canonical Database Manager 1.2: nicht konfiguriert."
        counts = status.get("object_counts", {})
        return (
            f"Canonical Database Manager {self.VERSION}: "
            f"{'VERIFIZIERT' if status.get('ok') else 'NICHT VERIFIZIERT'}.\n"
            f"- SQLite-Integritaet={status.get('checks', {}).get('integrity', False)}, "
            f"Tabellen={counts.get('tables', 0)}, Indizes={counts.get('indexes', 0)}, "
            f"Trigger={counts.get('triggers', 0)}.\n"
            f"- Tabellenvertrag={status.get('checks', {}).get('tables', False)}, "
            f"Spaltenvertrag={status.get('checks', {}).get('columns', False)}, "
            f"FTS={status.get('checks', {}).get('fts', False)}.\n"
            "- Pruefung ist read-only; Schemaaenderungen erfordern eine kontrollierte Migration."
        )
