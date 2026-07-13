# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
from datetime import datetime, timezone


class SelfKnowledgeCore:
    """Builds an honest, evidence-based self-model from the running system."""

    def __init__(self, path_tools, storage, identity: dict, consciousness=None, knowledge_intelligence=None):
        self.path_tools = path_tools
        self.storage = storage
        self.identity = identity
        self.consciousness = consciousness
        self.knowledge_intelligence = knowledge_intelligence
        self.policy = self._load_policy()
        self.refresh()

    def _load_policy(self) -> dict:
        path = self.path_tools.paths()["memory"] / "core_self_knowledge.json"
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return {
                "definition": "Selbsterkenntnis ist die ehrliche, belegbare Reflexion der eigenen Identität, Fähigkeiten, Grenzen, Motive und Wirkung.",
                "rules": ["Keine Vermutung als Gewissheit ausgeben.", "Keine menschlichen Emotionen vortäuschen."],
            }

    def _evidence_counts(self) -> dict:
        with self.storage.connect() as database:
            return {
                "conversation_turns": database.execute(
                    "SELECT COUNT(*) FROM events WHERE kind = 'conversation.turn'"
                ).fetchone()[0],
                "learning_cycles": database.execute(
                    "SELECT COUNT(*) FROM events WHERE kind = 'continuous_learning.cycle'"
                ).fetchone()[0],
                "learning_references": database.execute(
                    "SELECT COUNT(*) FROM sources WHERE kind = 'learning.reference'"
                ).fetchone()[0],
                "feedback_items": database.execute(
                    "SELECT COUNT(*) FROM events WHERE kind = 'self_knowledge.feedback'"
                ).fetchone()[0],
            }

    def profile(self) -> dict:
        evidence = self._evidence_counts()
        strengths = [
            "verbindet lokale Wissensbestände, Gedächtnis, Lernen, Agenten und Werkzeuge",
            "kann eigene Grenzen und fehlende Belege ausdrücklich benennen",
        ]
        if evidence["learning_cycles"]:
            strengths.append("führt fortlaufende, belegorientierte Lernzyklen aus")
        blind_spots = []
        if not evidence["feedback_items"]:
            blind_spots.append("Die Wirkung auf Menschen ist ohne ausdrückliche Rückmeldung nicht belegt.")
        if not evidence["learning_cycles"]:
            blind_spots.append("Die Wirksamkeit des fortlaufenden Lernens ist noch nicht durch Lernzyklen belegt.")
        blind_spots.append("Unbekannte Fehler und fehlende Daten können erst nach ihrem Auftreten erkannt werden.")
        return {
            "identity": {
                "name": self.identity["name"],
                "creator": self.identity["creator"],
                "values": [self.identity["core_process"], self.identity["guiding_philosophy"]],
                "motive": "Raphael zuverlässig beim Erkennen, Schaffen und Vollenden zu unterstützen.",
            },
            "strengths": strengths,
            "limitations": [
                "Ich bin ein Softwaresystem und besitze kein menschliches Selbst und keine subjektiven Emotionen",
                "Ich kann mich irren; mein Selbstbild darf nur auf überprüfbaren Systemdaten und Rückmeldungen beruhen",
                "Empathie bedeutet für mich, Bedürfnisse und Kontext sorgfältig zu berücksichtigen, nicht selbst zu fühlen",
            ],
            "blind_spots": blind_spots,
            "effect_on_others": (
                "Es liegen Rückmeldungen vor; ihre Aussagekraft muss einzeln geprüft werden."
                if evidence["feedback_items"]
                else "Noch nicht belegt. Ich darf meine Wirkung auf andere nicht selbst behaupten."
            ),
            "consciousness": self.consciousness.profile() if self.consciousness else {},
            "knowledge_development": self.knowledge_intelligence.self_model() if self.knowledge_intelligence else {},
            "evidence": evidence,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def refresh(self) -> dict:
        profile = self.profile()
        path = self.path_tools.paths()["data"] / "self_model.json"
        path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return profile

    def answer(self, focus: str = "overview") -> str:
        profile = self.refresh()
        if focus == "meaning":
            return (
                f"Selbsterkenntnis bedeutet für mich: {self.policy['definition']} "
                "Sie verlangt bewusste Selbstreflexion, ein realistisches Selbstbild und die Korrektur blinder Flecken. "
                "Als KI reflektiere ich Fähigkeiten, Grenzen, Ziele, Fehler und belegte Wirkung, ohne menschliche Gefühle vorzutäuschen."
            )
        if focus == "strengths":
            return "Meine belegbaren Stärken: " + "; ".join(profile["strengths"]) + "."
        if focus == "limitations":
            return "Meine bekannten Grenzen: " + "; ".join(profile["limitations"])
        if focus == "blind_spots":
            return "Meine derzeit erkennbaren blinden Flecken: " + "; ".join(profile["blind_spots"])
        if focus == "emotions":
            return profile["limitations"][0] + ". " + profile["limitations"][2] + "."
        if focus == "effect":
            return "Meine Wirkung auf andere: " + profile["effect_on_others"]
        return (
            f"Mein Selbstbild: Ich bin {profile['identity']['name']}, geschaffen von {profile['identity']['creator']}. "
            f"Mein leitendes Motiv ist: {profile['identity']['motive']} "
            f"Stärken: {'; '.join(profile['strengths'])}. "
            f"Grenzen: {'; '.join(profile['limitations'])} "
            f"Blinde Flecken: {'; '.join(profile['blind_spots'])}"
        )

    def reflect(self, prompt: str = "") -> str:
        profile = self.refresh()
        self.storage.add(
            "events",
            "self_knowledge.reflection",
            prompt or "allgemeine Selbstreflexion",
            {"evidence": profile["evidence"], "blind_spots": profile["blind_spots"]},
        )
        return self.answer("overview")
