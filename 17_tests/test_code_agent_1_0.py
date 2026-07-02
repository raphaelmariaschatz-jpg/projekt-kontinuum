from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.agent_registry import AgentRouter, build_agents  # noqa: E402
from kontinuum.core.code_agent import CodeAgentService  # noqa: E402
from kontinuum.core.conversation import ConversationManager  # noqa: E402
from kontinuum.core.request_router import RequestRouter  # noqa: E402
from kontinuum.core.storage import Storage  # noqa: E402
from kontinuum.tools.path_tools import PathTools  # noqa: E402


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary) / "project"
    outside = Path(temporary) / "outside.py"
    paths = PathTools(root)
    paths.ensure_all()
    source = root / "30_import" / "sample_project"
    source.mkdir(parents=True, exist_ok=True)
    py_file = source / "main.py"
    js_file = source / "app.js"
    unsupported = source / "image.bin"
    large_file = source / "large.py"
    missing = source / "missing.py"
    test_file = source / "test_main.py"
    package = source / "package.json"

    py_file.write_text(
        "import os\n"
        "from pathlib import Path\n\n"
        "class Runner:\n"
        "    def run(self):\n"
        "        return Path.cwd()\n\n"
        "def main():\n"
        "    # TODO: add tests\n"
        "    return Runner().run()\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        encoding="utf-8",
    )
    js_file.write_text(
        "const fs = require('fs');\n"
        "class App {}\n"
        "function start() { return fs.existsSync('.'); }\n"
        "module.exports = { start };\n",
        encoding="utf-8",
    )
    test_file.write_text("def test_main():\n    assert True\n", encoding="utf-8")
    package.write_text('{"scripts": {"test": "node app.js"}}', encoding="utf-8")
    unsupported.write_bytes(b"\x00\x01")
    large_file.write_text("x = 1\n" * 400, encoding="utf-8")
    outside.write_text("print('outside')\n", encoding="utf-8")

    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    code_agent = CodeAgentService(paths, storage=storage)
    code_agent.config["max_file_size_bytes"] = 1000

    py_result = code_agent.analyze_file(str(py_file))
    assert py_result["status"] == "ok"
    assert py_result["language"] == "python"
    assert "main" in py_result["detected_symbols"]["functions"]
    assert "Runner" in py_result["detected_symbols"]["classes"]
    assert "os" in py_result["imports"]
    assert py_result["entrypoints"]
    assert py_result["read_only"] is True
    assert py_result["memory_write_performed"] is False

    js_result = code_agent.analyze_file(str(js_file))
    assert js_result["status"] == "ok"
    assert js_result["language"] == "javascript"
    assert "start" in js_result["detected_symbols"]["functions"]
    assert "App" in js_result["detected_symbols"]["classes"]
    assert "fs" in js_result["imports"]

    project = code_agent.analyze_project(str(source))
    assert project["status"] == "ok"
    assert project["file_type"] == "project"
    assert project["project_map"]["total_files_analyzed"] >= 4
    assert project["project_map"]["important_entrypoints"]
    assert project["project_map"]["test_folders_or_files"]
    assert project["project_map"]["configuration_files"]

    missing_result = code_agent.analyze_file(str(missing))
    assert missing_result["status"] == "error"
    assert "nicht gefunden" in missing_result["errors"][0]

    unsupported_result = code_agent.analyze_file(str(unsupported))
    assert unsupported_result["status"] == "error"
    assert "Nicht unterstützter Dateityp" in unsupported_result["errors"][0]

    blocked_result = code_agent.analyze_file(str(outside))
    assert blocked_result["status"] == "error"
    assert "nicht freigegeben" in blocked_result["errors"][0]

    large_result = code_agent.analyze_file(str(large_file))
    assert large_result["status"] == "error"
    assert "zu groß" in large_result["errors"][0]

    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")
    request_router = RequestRouter(paths)
    file_prompt = f"analysiere code {py_file}"
    file_decision = request_router.decide(file_prompt, conversation.classify(file_prompt))
    assert file_decision.request_class == "Codeanalyse"
    assert file_decision.selected_agent == "code_agent"
    project_prompt = f"analysiere projekt {source}"
    project_decision = request_router.decide(project_prompt, conversation.classify(project_prompt))
    assert project_decision.request_class == "Codeanalyse"
    assert project_decision.selected_agent == "code_agent"

    agents = build_agents(storage=storage, tools={}, config={"code_agent": code_agent})
    routed_file = AgentRouter(agents).route(file_prompt, conversation.classify(file_prompt).name)
    assert routed_file.agent == "code_agent"
    assert "CodeAgent: Datei analysiert." in routed_file.answer
    routed_project = AgentRouter(agents).route(project_prompt, conversation.classify(project_prompt).name)
    assert routed_project.agent == "code_agent"
    assert "CodeAgent: Projektkarte erstellt." in routed_project.answer

    status = code_agent.format_status()
    assert "CodeAgent aktiv: ja" in status
    assert "python" in status

print("Kontinuum CodeAgent 1.0 tests passed")
