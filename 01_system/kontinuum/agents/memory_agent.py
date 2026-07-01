from __future__ import annotations
import re
import unicodedata

from .base_agent import BaseAgent, AgentResult


class MemoryAgent(BaseAgent):
    name = "memory"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        normalized = "".join(
            character for character in unicodedata.normalize("NFKD", lower)
            if not unicodedata.combining(character)
        )
        return (
            normalized.startswith(("merke ", "merke dir ", "speichere ", "was weisst du uber ",
                                   "aktualisiere erinnerung ", "vergiss ", "verknupfe erinnerungen "))
            or normalized in {"zeige projekterinnerungen", "zeige offene punkte", "prufe widerspruche", "gedachtnisstatus"}
        )

    def handle(self, prompt: str) -> AgentResult:
        core = self.config.get("memory_core")
        if not core:
            return AgentResult(self.name, True, "Memory-Core ist nicht angebunden.")
        text = prompt.strip()
        lower = text.casefold()
        owner = self.config.get("conversation", {}).get("user", {}).get("full_name", "") or "Raphael"
        if lower.startswith(("merke dir ", "merke ", "speichere ")):
            content = re.sub(r"^(?:merke\s+dir|merke|speichere)\s+", "", text, flags=re.I)
            result = core.remember(content, owner=owner, explicit=True)
            platform = self.config.get("knowledge_platform")
            if platform and result.get("id"):
                platform.integrate_memory(result)
            answer = self._decision_answer(result)
        elif lower.startswith(("was weißt du über ", "was weisst du über ", "was weisst du uber ")):
            term = re.sub(r"^was\s+wei(?:ß|ss)t\s+du\s+(?:über|uber)\s+", "", text, flags=re.I).strip(" .?!")
            platform = self.config.get("knowledge_platform")
            explanation = platform.explain(term) if platform else ""
            answer = (
                explanation
                if explanation and "noch kein integrierter Wissensweg" not in explanation
                else self._format(core.recall(term), f"Erinnerungen zu „{term}“")
            )
        elif lower == "zeige projekterinnerungen":
            answer = self._format(core.recall(layer="project"), "Projekterinnerungen")
        elif lower == "zeige offene punkte":
            rows = [row for row in core.recall(layer="project") if row["metadata"].get("structured", {}).get("status") == "offen" or row["metadata"].get("key", "").startswith("open:")]
            answer = self._format(rows, "Offene Punkte")
        elif lower.startswith("aktualisiere erinnerung "):
            match = re.match(r"aktualisiere erinnerung\s+(\d+)\s*[:\-]?\s*(.+)", text, re.I)
            answer = self._decision_answer(core.update(int(match.group(1)), match.group(2), owner)) if match else "Format: aktualisiere erinnerung <ID>: <neuer Inhalt>"
        elif lower.startswith("vergiss "):
            answer = f"Vergessene Erinnerungen: {core.forget(text[8:].strip())}."
        elif lower.startswith("verknüpfe erinnerungen "):
            ids = [int(value) for value in re.findall(r"\d+", text)]
            answer = "Erinnerungen verknüpft." if len(ids) >= 2 and core.link(ids[0], ids[1]) else "Zwei gültige Erinnerungs-IDs erforderlich."
        elif lower in {"prüfe widersprüche", "pruefe widersprueche"}:
            conflicts = core.contradictions()
            answer = f"Widerspruchsprüfung: {len(conflicts)} Schlüssel mit abweichenden Aussagen."
            for conflict in conflicts[:10]:
                answer += f"\n- {conflict['subject']} / {conflict['key']}: " + ", ".join(str(row["metadata"].get("value", "")) for row in conflict["entries"])
        else:
            status = core.status()
            answer = f"Kontinuum Memory-Core 1.0: {status['total']} Erinnerungen, {status['contradictions']} Widerspruchsschlüssel.\nSchichten: {status['layers']}"
        return AgentResult(self.name, True, answer)

    @staticmethod
    def _decision_answer(result: dict) -> str:
        action = result.get("action")
        if action == "discard":
            return f"Erinnerung verworfen: {result.get('reason', '')}"
        if action == "error":
            return result.get("reason", "Memory-Core-Fehler.")
        return (
            f"Erinnerung {action}: ID {result.get('id')} | Schicht {result.get('layer')} | "
            f"{result.get('subject')} / {result.get('key')} = {result.get('value')} "
            f"| Status {result.get('status')}."
        )

    @staticmethod
    def _format(rows: list[dict], title: str) -> str:
        if not rows:
            return f"{title}: keine Einträge."
        lines = [f"{title} ({len(rows)}):"]
        for row in rows:
            metadata = row["metadata"]
            lines.append(f"- [{row['id']}] {metadata.get('subject')} / {metadata.get('key')}: {metadata.get('value')} ({metadata.get('status')})")
        return "\n".join(lines)
