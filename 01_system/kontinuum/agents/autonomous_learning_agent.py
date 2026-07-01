from __future__ import annotations

from kontinuum.version import APP_VERSION

from .base_agent import BaseAgent, AgentResult


class AutonomousLearningAgent(BaseAgent):
    name = "autonomous_learning"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower().strip()
        return lower in {"autostatus", "autonomiestatus", "autonom lernen"} or lower.startswith(("lerne selbständig", "lerne selbstaendig", "erweitere alle wissensgebiete"))

    def handle(self, prompt: str) -> AgentResult:
        lower = prompt.lower().strip()
        service = self.config.get("continuous_learning")
        if lower in {"autostatus", "autonomiestatus"}:
            status = service.status() if service else {}
            answer = (
                f"Kontinuierliches Lernen {APP_VERSION}:\n"
                f"- aktiviert: {status.get('enabled', False)}\n"
                f"- Hintergrund läuft: {status.get('running', False)}\n"
                f"- Lernaufträge: {status.get('tasks', 0)}\n"
                f"- deaktivierte Lernziele: {status.get('inactive_tasks', 0)}\n"
                f"- Fundstellen: {status.get('references', 0)}\n"
                f"- Lernzyklen: {status.get('cycles', 0)}\n"
                f"- Kompetenzphasen: {status.get('phase_counts', {})}\n"
                "- Speicherprinzip: Fundstellen statt Volltexte."
            )
        else:
            subjects = ["Mathematik", "Physik", "Chemie", "Biologie", "Informatik"]
            for s in subjects:
                self.remember("autonomous.project", f"Autonomes Lernprojekt: {s}", {"subject": s, "version": APP_VERSION})
                if service:
                    service.add_task(s, origin="autonomous_learning_agent")
            result = service.run_cycle(reason="user_command") if service else {}
            answer = "Dauerhafte Lernaufträge aktiv für: " + ", ".join(subjects) + "\n" + result.get("message", "")
        return AgentResult(self.name, True, answer)
