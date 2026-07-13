# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from .path_tools import PathTools
from .json_tools import JsonTools
from .file_tools import FileTools
from .search_tools import SearchTools
from .web_tools import WebTools
from .backup_tools import BackupTools
from .import_tools import ImportTools
from .export_tools import ExportTools
from .codex_tools import CodexTools
from .language_model_tools import LanguageModelTools
from .python_tools import PythonTools
from .winget_tools import WingetTools
from .search_engine_tools import SearchEngineTools
from .development_tools import DevelopmentTools
from .oracle_cloud_tools import OracleCloudTools
from .notebook_tools import NotebookTools
from .maintenance_tools import MaintenanceTools


def build_tools(root=None):
    path_tools = PathTools(root)
    tools = {
        "path_tools": path_tools,
        "json_tools": JsonTools(),
        "file_tools": FileTools(),
        "search_tools": SearchTools(path_tools),
        "web_tools": WebTools(),
        "backup_tools": BackupTools(),
        "import_tools": ImportTools(),
        "export_tools": ExportTools(),
        "codex_tools": CodexTools(path_tools.project_root()),
        "language_model_tools": LanguageModelTools(path_tools.project_root()),
        "python_tools": PythonTools(path_tools.project_root()),
        "winget_tools": WingetTools(path_tools.project_root()),
        "search_engine_tools": SearchEngineTools(path_tools.project_root()),
        "development_tools": DevelopmentTools(path_tools.project_root()),
        "oracle_cloud_tools": OracleCloudTools(path_tools.project_root()),
        "notebook_tools": NotebookTools(path_tools.project_root()),
        "maintenance_tools": MaintenanceTools(path_tools.project_root()),
    }
    return tools
