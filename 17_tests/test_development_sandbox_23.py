from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.tools.development_tools import DevelopmentTools
from kontinuum.agents.development_agent import DevelopmentAgent


with tempfile.TemporaryDirectory() as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config" / "development_sandbox.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"workspace": "sandbox"}), encoding="utf-8")
    tool = DevelopmentTools(root)
    assert tool.workspace == (root / "sandbox").resolve()
    assert tool.status()["promotion"] == "superadmin-controlled"
    assert not tool.test()["ok"]
    (tool.workspace / "test_example.py").write_text(
        "import unittest\n\nclass ExampleTest(unittest.TestCase):\n"
        "    def test_ok(self):\n        self.assertEqual(2 + 2, 4)\n",
        encoding="utf-8",
    )
    assert tool.test()["ok"]
    assert tool.initialize_git()["ok"]
    assert tool.git_snapshot("Initial sandbox test")["ok"]
    assert tool.git_status()["ok"]
    assert not tool._authorize_self_extension({"role": "USER"})["ok"]
    assert not tool._authorize_self_extension({"role": "SUPERADMIN", "is_superadmin": True})["ok"]
    assert tool._authorize_self_extension(
        {
            "authenticated": True,
            "role": "SUPERADMIN",
            "is_superadmin": True,
            "permissions": {"can_execute_admin_commands": True},
        }
    )["ok"]

    candidate = tool.workspace / "candidate"
    (candidate / "01_system" / "kontinuum").mkdir(parents=True)
    (candidate / "17_tests").mkdir(parents=True)
    changed_code = candidate / "01_system" / "kontinuum" / "feature.py"
    changed_test = candidate / "17_tests" / "test_feature_23.py"
    changed_code.write_text("VALUE = 23\n", encoding="utf-8")
    changed_test.write_text("print('feature test passed')\n", encoding="utf-8")
    checks = tool._preflight_candidate(
        candidate,
        ["01_system/kontinuum/feature.py", "17_tests/test_feature_23.py"],
    )
    assert checks["ok"]
    assert not tool._preflight_candidate(candidate, ["01_system/kontinuum/feature.py"])["ok"]
    assert not tool._preflight_candidate(
        candidate,
        ["01_system/kontinuum/feature.py", "17_tests/test_feature_23.py"],
        {"17_tests/test_feature_23.py": "existing"},
    )["ok"]
    changed_code.write_text("import subprocess\n", encoding="utf-8")
    assert not tool._preflight_candidate(
        candidate,
        ["01_system/kontinuum/feature.py", "17_tests/test_feature_23.py"],
    )["ok"]
    changed_code.write_text("VALUE = 23\n", encoding="utf-8")

    active_code = root / "01_system" / "kontinuum" / "feature.py"
    active_code.parent.mkdir(parents=True)
    active_code.write_text("VALUE = 1\n", encoding="utf-8")
    tool._run_full_project_tests = lambda: {"ok": False, "message": "erzwungener Testfehler"}
    rollback = tool._promote_with_rollback(
        candidate,
        ["01_system/kontinuum/feature.py", "17_tests/test_feature_23.py"],
    )
    assert not rollback["ok"]
    assert active_code.read_text(encoding="utf-8") == "VALUE = 1\n"
    assert not (root / "17_tests" / "test_feature_23.py").exists()

    class FakeDevelopmentTool:
        def self_extend(self, task, user):
            return {"ok": False, "message": f"{user.get('role')}:{task}"}

    agent = DevelopmentAgent(
        tools={"development_tools": FakeDevelopmentTool()},
        config={"conversation": {"user": {"role": "USER", "is_superadmin": False}}},
    )
    assert agent.can_handle("programmiere: Test")
    assert agent.handle("programmiere: Test").answer == "USER:Test"

print("Kontinuum development sandbox tests passed")
