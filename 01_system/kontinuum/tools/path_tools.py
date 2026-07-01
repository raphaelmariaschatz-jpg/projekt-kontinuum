from __future__ import annotations
import os
from pathlib import Path


class PathTools:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))

    def project_root(self) -> Path:
        return self.root

    def paths(self) -> dict[str, Path]:
        r = self.root
        return {
            "system": r / "01_system",
            "versions": r / "02_versions",
            "memory": r / "03_memory",
            "knowledge": r / "04_knowledge",
            "connectors": r / "05_connectors",
            "learning": r / "06_learning",
            "models": r / "07_models",
            "workspace_index": r / "08_workspace_index",
            "backups": r / "09_backups",
            "security": r / "10_security",
            "gui": r / "11_gui",
            "agents": r / "12_agents",
            "tools": r / "13_tools",
            "documents": r / "14_documents",
            "exports": r / "15_exports",
            "installation": r / "16_installation",
            "tests": r / "17_tests",
            "autonomous_learning": r / "18_autonomous_learning",
            "university_sources": r / "19_university_sources",
            "library_sources": r / "20_library_sources",
            "internet_sources": r / "21_internet_sources",
            "chronicle": r / "22_project_chronicle",
            "recovery": r / "23_recovery",
            "config": r / "24_config",
            "voice": r / "25_voice",
            "research": r / "26_research",
            "logs": r / "27_logs",
            "import": r / "30_import",
            "reports": r / "31_reports",
            "data": r / "32_data",
        }

    def ensure_all(self) -> None:
        for path in self.paths().values():
            path.mkdir(parents=True, exist_ok=True)

    def map_legacy_path(self, value: str) -> str:
        return value.replace("E:\\Projekt Kontinuum", str(self.root)).replace("29_memory", "03_memory")

