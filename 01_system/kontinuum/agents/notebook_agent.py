from __future__ import annotations

import re

from kontinuum.version import APP_VERSION
from .base_agent import AgentResult, BaseAgent


class NotebookAgent(BaseAgent):
    name = "knowledge_notebook"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return lower in {"notizbuchstatus", "projektquellenstatus"} or lower.startswith(("notizbuch ", "wissensnotizbuch "))

    def handle(self, prompt: str) -> AgentResult:
        tool = self.tools.get("notebook_tools")
        lower = prompt.casefold().strip()
        if not tool:
            return AgentResult(self.name, True, "Wissensnotizbuch ist nicht angebunden.")
        command = re.sub(r"^(?:wissensnotizbuch|notizbuch)\s*", "", prompt.strip(), flags=re.I).strip()
        if lower == "notizbuchstatus" or command.casefold() in {"", "status", "quellen"}:
            sources = tool.list_sources()
            answer = f"Wissensnotizbuch {APP_VERSION}: {len(sources)} manuell importierte Quellen."
            if sources:
                answer += "\n" + "\n".join(f"[{row['id']}] {row.get('title', '')}" for row in sources[:20])
        elif lower == "projektquellenstatus":
            answer = self._project_sources_status()
        elif command.casefold().startswith("import "):
            result = tool.import_source(command[7:].strip())
            answer = (
                f"Quelle importiert [{result['id']}]: {result['title']} ({result['characters']} Zeichen)\n"
                f"Zusammenfassung: {result['summary']}\n"
                f"Wissensweg: Quelle -> Notebook -> Memory-Core -> Wissensgraph -> Projektchronik."
                if result.get("ok") else f"Import fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}"
            )
        elif command.casefold().startswith(("frage ", "frage:")):
            answer = tool.answer(command.split(" ", 1)[1].lstrip(":").strip())
        elif command.casefold().startswith("lernen"):
            answer = tool.learn(command[6:].strip() or "Wissensnotizbuch")
        elif command.casefold().startswith("zusammenfassung"):
            match = re.search(r"\d+", command)
            answer = tool.summarize(int(match.group(0)) if match else None)
        else:
            answer = "Befehle: notizbuch import <Pfad|URL>, notizbuch zusammenfassung, notizbuch frage <Frage>, notizbuch lernen <Thema>."
        return AgentResult(self.name, True, answer)

    def _project_sources_status(self) -> str:
        path_tools = self.tools.get("path_tools")
        if not path_tools:
            return "Projektquellenstatus: Pfadwerkzeug nicht angebunden."
        root = path_tools.project_root()
        patterns = [
            ("Architekturberichte", root / "14_documents", "PROJEKTSTRUKTUR_*.md"),
            ("Projektstatus", root / "14_documents" / "projektstatus", "*.md"),
            ("Chronik", root / "22_project_chronicle", "*.md"),
            ("README", root, "README.md"),
        ]
        lines = [f"Projektquellenstatus {APP_VERSION}:"]
        for label, folder, pattern in patterns:
            count = len(list(folder.glob(pattern))) if folder.exists() else 0
            lines.append(f"- {label}: {count}")
        lines.append("Notizbuchquellen bleiben manuell importierte Quellen; Projektquellen sind Architektur, Chronik, Status und README.")
        return "\n".join(lines)
