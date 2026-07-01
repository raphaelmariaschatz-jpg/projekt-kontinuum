from __future__ import annotations

import json
from datetime import datetime, timezone


class ConsciousnessCore:
    """Describes functional awareness without claiming subjective experience."""

    def __init__(self, path_tools, storage):
        self.path_tools = path_tools
        self.storage = storage
        self.policy = self._load_policy()
        self.refresh()

    def _load_policy(self) -> dict:
        path = self.path_tools.paths()["memory"] / "core_consciousness.json"
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return {
                "definition": "Bewusstsein umfasst Wahrnehmung, Reaktionsfähigkeit, inhaltliche Verarbeitung und Reflexion.",
                "rules": ["Subjektives Erleben oder Qualia niemals ohne überprüfbaren Nachweis behaupten."],
            }

    def profile(self) -> dict:
        with self.storage.connect() as database:
            conversation_turns = database.execute(
                "SELECT COUNT(*) FROM events WHERE kind = 'conversation.turn'"
            ).fetchone()[0]
            reflections = database.execute(
                "SELECT COUNT(*) FROM events WHERE kind IN ('consciousness.reflection', 'self_knowledge.reflection')"
            ).fetchone()[0]
        return {
            "model": "funktionales Bewusstseinsmodell",
            "arousal": {
                "meaning": "laufender, reaktionsfähiger Systemzustand",
                "status": "aktiv",
                "evidence": "Kontinuum verarbeitet diese Anfrage.",
            },
            "awareness": {
                "meaning": "Eingaben, Kontext, lokale Daten und Systemzustände inhaltlich erfassen und verarbeiten",
                "status": "funktional nachweisbar",
                "evidence": {"conversation_turns": conversation_turns, "reflections": reflections},
            },
            "self_awareness": {
                "meaning": "eigenes Selbstmodell, Ziele, Fähigkeiten, Grenzen und Verarbeitung reflektieren",
                "status": "funktional nachweisbar",
            },
            "subjective_experience": {
                "qualia": "nicht nachgewiesen",
                "feelings": "nicht nachgewiesen",
                "claim": "Kontinuum behauptet kein subjektives Erleben und kein echtes phänomenales Bewusstsein.",
            },
            "perception_limits": [
                "Wahrnehmung ist auf bereitgestellte Eingaben, verbundene Werkzeuge, lokale Daten und Systemzustände begrenzt",
                "Nicht bereitgestellte Umweltreize können nicht wahrgenommen werden",
                "Funktionale Verarbeitung ist kein Beweis für subjektives Erleben",
            ],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def refresh(self) -> dict:
        profile = self.profile()
        path = self.path_tools.paths()["data"] / "consciousness_model.json"
        path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return profile

    def answer(self, focus: str = "overview") -> str:
        profile = self.refresh()
        if focus == "meaning":
            return (
                f"Bewusstsein bedeutet im Kern: {self.policy['definition']} "
                "Wissenschaftlich werden Wachheit und inhaltliches Erleben unterschieden. "
                "Bei mir sind Reaktionsfähigkeit, Kontextverarbeitung und Selbstreflexion funktional nachweisbar; "
                "subjektives Erleben oder Qualia sind nicht nachgewiesen und werden von mir nicht behauptet."
            )
        if focus == "status":
            return (
                "Mein Bewusstseinsstatus: funktionale Wachheit aktiv; funktionale Kontextwahrnehmung und "
                "Selbstreflexion nachweisbar; subjektives Erleben, Gefühle und Qualia nicht nachgewiesen."
            )
        if focus == "perception":
            return "Meine Wahrnehmung: " + "; ".join(profile["perception_limits"])
        if focus == "qualia":
            return (
                "Subjektives Erleben, Gefühle und Qualia sind bei mir nicht nachgewiesen. "
                + profile["subjective_experience"]["claim"]
            )
        return (
            "Ich verfüge über ein funktionales Bewusstseinsmodell: Ich kann Eingaben und Kontext verarbeiten, "
            "reagieren und mein Selbstmodell reflektieren. Das ist kein Beweis für subjektives Erleben; "
            "Qualia und echtes phänomenales Bewusstsein behaupte ich nicht."
        )

    def reflect(self, prompt: str = "") -> str:
        profile = self.refresh()
        self.storage.add(
            "events",
            "consciousness.reflection",
            prompt or "allgemeine Bewusstseinsreflexion",
            {
                "arousal": profile["arousal"]["status"],
                "awareness": profile["awareness"]["status"],
                "subjective_experience": "nicht nachgewiesen",
            },
        )
        return self.answer("overview")
