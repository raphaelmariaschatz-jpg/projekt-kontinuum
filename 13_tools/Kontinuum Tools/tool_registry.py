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
    }
    return tools
