from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.agent_registry import AgentRouter, build_agents  # noqa: E402
from kontinuum.core.canonical_git_manager import CanonicalGitManager  # noqa: E402
from kontinuum.core.continuous_canonical_engine import ContinuousCanonicalEngine  # noqa: E402
from kontinuum.core.conversation import ConversationManager  # noqa: E402
from kontinuum.core.git_agent import GitAgentService  # noqa: E402
from kontinuum.core.request_router import RequestRouter  # noqa: E402
from kontinuum.core.storage import Storage  # noqa: E402
from kontinuum.tools.path_tools import PathTools  # noqa: E402


def git_executable() -> str:
    candidates = [
        os.environ.get("KONTINUUM_GIT_EXE", ""),
        shutil.which("git") or "",
        r"C:\Users\Raphael\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate))
    raise RuntimeError("Git executable not available for GitAgent tests.")


def run_git(git: str, cwd: Path, *args: str) -> None:
    completed = subprocess.run([git, *args], cwd=str(cwd), capture_output=True, text=True, timeout=20)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)


class DummyCAM:
    def status(self):
        return {"ok": True, "configured": True, "component": "dummy_cam"}


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    git = git_executable()
    os.environ["KONTINUUM_GIT_EXE"] = git
    project = Path(temporary) / "project"
    no_repo = Path(temporary) / "no_repo"
    project.mkdir()
    no_repo.mkdir()
    paths = PathTools(project)
    paths.ensure_all()
    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    cde = ContinuousCanonicalEngine(project, paths, storage, "34.1", strict_config=False)
    git_agent = GitAgentService(paths, storage, cde)
    cgm = CanonicalGitManager(paths, git_agent, storage, cde, DummyCAM(), DummyCAM())

    no_repo_paths = PathTools(no_repo)
    no_repo_paths.ensure_all()
    no_repo_agent = GitAgentService(no_repo_paths)
    no_repo_result = no_repo_agent.is_git_repo("")
    assert no_repo_result["status"] == "ok"
    assert no_repo_result["is_git_repo"] is False

    run_git(git, project, "init")
    run_git(git, project, "config", "user.email", "kontinuum@example.invalid")
    run_git(git, project, "config", "user.name", "Kontinuum Test")
    tracked = project / "14_documents" / "initial.md"
    tracked.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text("Initial", encoding="utf-8")
    run_git(git, project, "add", "14_documents/initial.md")
    run_git(git, project, "commit", "-m", "Initial canonical baseline")
    run_git(git, project, "tag", "v-test-1")

    repo_result = git_agent.is_git_repo("")
    assert repo_result["is_git_repo"] is True
    run_git(git, project, "add", ".")
    run_git(git, project, "commit", "-m", "Add diagnostic runtime baseline")
    clean_status = git_agent.get_status("")
    assert clean_status["status"] == "ok"
    assert clean_status["is_git_repo"] is True
    assert clean_status["clean_worktree"] is True
    assert clean_status["current_branch"] in {"master", "main"}
    assert git_agent.list_recent_commits("", 5)["recent_commits"]
    assert "v-test-1" in git_agent.list_tags("")["tags"]

    release_ready = cgm.evaluate_release_readiness("")
    assert release_ready["release_ready"] is True
    assert release_ready["suggested_tag"]

    tracked.write_text("Changed", encoding="utf-8")
    untracked = project / "01_system" / "new_agent.py"
    untracked.parent.mkdir(parents=True, exist_ok=True)
    untracked.write_text("print('new')\n", encoding="utf-8")
    dirty_status = git_agent.detect_uncommitted_changes("")
    assert dirty_status["clean_worktree"] is False
    assert any("14_documents/initial.md" in item for item in dirty_status["changed_files"])
    assert any(item.startswith("01_system") for item in dirty_status["untracked_files"])

    commit_ready = cgm.evaluate_commit_readiness("")
    assert commit_ready["commit_ready"] is True
    assert commit_ready["canonical_changed_files"]
    assert any("Tests" in action for action in commit_ready["recommended_next_actions"])

    cam_compare = cgm.compare_git_with_cam("")
    assert cam_compare["write_performed"] is False
    assert cam_compare["untracked_canonical_files"]

    cde_compare = cgm.compare_git_with_cde("")
    assert cde_compare["write_performed"] is False
    assert "event_bus" in cde_compare

    chronicle = cgm.prepare_chronicle_entry("", "GitAgent/CGM Test")
    assert chronicle["chronicle_entry"]["write_performed"] is False
    assert chronicle["chronicle_entry"]["summary"] == "GitAgent/CGM Test"

    report = cgm.create_cgm_report("")
    assert report["read_only"] is True
    assert Path(report["report_path"]).is_file()

    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")
    request_router = RequestRouter(paths)
    git_decision = request_router.decide("git status", conversation.classify("git status"))
    assert git_decision.request_class == "Git"
    assert git_decision.selected_agent == "git_agent"
    cgm_decision = request_router.decide("cgm report", conversation.classify("cgm report"))
    assert cgm_decision.request_class == "Canonical Git Governance"
    assert cgm_decision.selected_agent == "canonical_git_manager"

    agents = build_agents(storage=storage, tools={}, config={"git_agent": git_agent, "canonical_git_manager": cgm})
    git_routed = AgentRouter(agents).route("git status", conversation.classify("git status").name)
    assert git_routed.agent == "git_agent"
    assert "GitAgent: Repository-Status gelesen." in git_routed.answer
    cgm_routed = AgentRouter(agents).route("cgm report", conversation.classify("cgm report").name)
    assert cgm_routed.agent == "canonical_git_manager"
    assert "Canonical Git Manager 2.0 Report" in cgm_routed.answer

print("Kontinuum GitAgent und CGM 2.0 tests passed")
