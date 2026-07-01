from __future__ import annotations
import re
from .base_agent import BaseAgent, AgentResult


class LearningAgent(BaseAgent):
    name = "learning"

    SUBJECTS = {
        "mathematik": ["Arithmetik", "Algebra", "Geometrie", "Analysis", "Statistik"],
        "physik": ["Mechanik", "Thermodynamik", "Elektromagnetismus", "Optik", "Quantenphysik"],
        "chemie": ["Atombau", "Periodensystem", "Bindungen", "Reaktionen", "Organische Chemie"],
        "biologie": ["Zellbiologie", "Genetik", "Evolution", "Ökologie"],
        "informatik": ["Algorithmen", "Datenstrukturen", "Datenbanken", "KI", "IT-Sicherheit"],
        "bewusstsein": ["Selbstmodell", "Gedächtnis", "Qualia", "Intentionalität", "KI-Bewusstsein"],
    }

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").lower().strip()
        return lower.startswith(("lerne ", "lernen ", "studiere ", "trainiere ")) or "lernstatus" in lower

    def handle(self, prompt: str) -> AgentResult:
        lower = prompt.lower().strip()
        if "lernstatus" in lower:
            answer = "Lernsystem 23.0 aktiv. Lernprojekte werden in 06_learning und 32_data/kontinuum.db geführt."
            return AgentResult(self.name, True, answer)

        subject = re.sub(r"^(lerne|lernen|studiere|trainiere)\s+", "", prompt.strip(), flags=re.I).strip(" .!?")
        canonical = subject[:1].upper() + subject[1:] if subject else "Allgemeines Wissen"
        topics = self.SUBJECTS.get(subject.lower(), ["Grundlagen", "Begriffe", "Kernkonzepte", "Methoden", "Anwendungen"])
        self.remember("learning.project", f"Lernprojekt: {canonical}", {"subject": canonical, "topics": topics, "version": "23.0"})
        for topic in topics:
            self.add_edge(f"Lernprojekt: {canonical}", "enthält Lerngebiet", topic)
        answer = f"Lernprojekt angelegt: {canonical}\nTeilgebiete: {', '.join(topics)}."
        return AgentResult(self.name, True, answer)
