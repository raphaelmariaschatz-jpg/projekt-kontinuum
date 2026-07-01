from __future__ import annotations

from .base_agent import AgentResult, BaseAgent


class CanonicalGitAgent(BaseAgent):
    name = "canonical_git_manager"

    def can_handle(self, prompt: str) -> bool:
        manager = self.config.get("canonical_git_manager")
        return bool(manager and manager.looks_like_cgm_command(prompt))

    def handle(self, prompt: str) -> AgentResult:
        manager = self.config.get("canonical_git_manager")
        if not manager:
            return AgentResult(self.name, True, "Canonical Git Manager 2.0 ist nicht angebunden.")
        result = manager.handle_command(prompt)
        return AgentResult(self.name, True, result.get("message", "CGM 2.0 konnte den Auftrag nicht verarbeiten."), result)
