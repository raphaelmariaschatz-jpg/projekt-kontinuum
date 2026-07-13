# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations
import re

from kontinuum.version import APP_VERSION

from .base_agent import BaseAgent, AgentResult


class KnowledgeAgent(BaseAgent):
    name = "knowledge"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        return (
            lower.startswith(("suche ", "definition ", "definiere ", "wissensweg ", "woher weißt du ", "woher weisst du ",
                              "wissensplattform altbestand ", "vertrauen ", "wie sicher ist "))
            or lower.startswith(("prüfauftrag ", "pruefauftrag "))
            or lower.startswith(("warum ist ", "warum sind "))
            or lower in {
                "wissensplattformstatus",
                "welche informationen widersprechen sich",
                "wissenskonflikte",
                "was habe ich im letzten monat gelernt",
                "welche themen beschäftigen mich besonders",
                "welche themen beschaeftigen mich besonders",
                "welche wissensgebiete wachsen am stärksten",
                "welche wissensgebiete wachsen am staerksten",
                "selbstmodellstatus",
                "wissensselbstmodellstatus",
                "was hat sich geändert",
                "was hat sich geaendert",
                "warum hat sich das geändert",
                "warum hat sich das geaendert",
                "zeige zustandsverlauf",
                "zeige offene innere konflikte",
                "chronikschutzstatus",
                "was vermute ich",
                "welche aussagen sind unsicher",
                "welche informationen sollten überprüft werden",
                "welche informationen sollten ueberprueft werden",
                "welche wissenslücken habe ich",
                "welche wissensluecken habe ich",
                "überprüfungsaufträge",
                "ueberpruefungsauftraege",
                "epistemischer status",
                "aktionsschichtstatus",
                "prüfzyklus",
                "pruefzyklus",
            }
        )

    def handle(self, prompt: str) -> AgentResult:
        search = self.tools.get("search_tools")
        platform = self.config.get("knowledge_platform")
        intelligence = self.config.get("knowledge_intelligence")
        actions = self.config.get("epistemic_actions")
        persistent_self_model = self.config.get("persistent_self_model")
        lower = prompt.casefold().strip()
        if lower == "wissensplattformstatus":
            status = platform.status() if platform else {}
            answer = (
                f"Kontinuum Knowledge Platform {status.get('version', '')}: "
                f"{status.get('integrated_knowledge', 0)} integrierte Wissenseinheiten, "
                f"{status.get('graph_edges', 0)} Wissensweg-Kanten, "
                f"{status.get('chronicle_entries', 0)} Chronikeinträge."
                f"\nUrsprünge: {status.get('origins', {})}"
                f"\nWissenskonflikte: {status.get('conflicts', 0)}"
                f"\nEpistemische Zustände: {status.get('epistemic_states', {})}"
                f"\nWissenslücken: {status.get('knowledge_gaps', 0)}"
            )
        elif lower in {"welche informationen widersprechen sich", "wissenskonflikte"}:
            intelligence.refresh()
            answer = intelligence.format_conflicts()
        elif lower == "was habe ich im letzten monat gelernt":
            answer = intelligence.format_self_model("learned")
        elif lower in {"welche themen beschäftigen mich besonders", "welche themen beschaeftigen mich besonders"}:
            answer = intelligence.format_self_model("topics")
        elif lower in {"welche wissensgebiete wachsen am stärksten", "welche wissensgebiete wachsen am staerksten"}:
            answer = intelligence.format_self_model("growth")
        elif lower == "wissensselbstmodellstatus":
            answer = intelligence.format_self_model()
        elif lower == "selbstmodellstatus":
            answer = persistent_self_model.format_status()
        elif lower in {"was hat sich geändert", "was hat sich geaendert", "zeige zustandsverlauf"}:
            answer = persistent_self_model.format_changes()
        elif lower in {"warum hat sich das geändert", "warum hat sich das geaendert"}:
            answer = persistent_self_model.format_explanations()
        elif lower == "zeige offene innere konflikte":
            answer = persistent_self_model.format_conflicts()
        elif lower == "chronikschutzstatus":
            status = persistent_self_model.chronicle_status()
            answer = (
                f"Chronikschutz {APP_VERSION}: {'intakt' if status['ok'] else 'Integritätsverletzung erkannt'}, "
                f"{status['signed']} von {status['entries']} Einträgen signiert, "
                f"{len(status['issues'])} Auffälligkeiten."
            )
        elif lower == "was vermute ich":
            intelligence.refresh()
            answer = intelligence.format_epistemic("hypotheses")
        elif lower == "welche aussagen sind unsicher":
            intelligence.refresh()
            answer = intelligence.format_epistemic("uncertain")
        elif lower in {
            "welche informationen sollten überprüft werden",
            "welche informationen sollten ueberprueft werden",
            "überprüfungsaufträge",
            "ueberpruefungsauftraege",
        }:
            intelligence.refresh()
            answer = intelligence.format_epistemic("review")
        elif lower in {"welche wissenslücken habe ich", "welche wissensluecken habe ich"}:
            intelligence.refresh()
            answer = intelligence.format_gaps()
        elif lower == "epistemischer status":
            intelligence.refresh()
            answer = (
                "Epistemischer Status:\n"
                + intelligence.format_epistemic("hypotheses") + "\n\n"
                + intelligence.format_epistemic("uncertain") + "\n\n"
                + intelligence.format_gaps()
            )
        elif lower == "aktionsschichtstatus":
            status = actions.status()
            answer = (
                f"Epistemische Aktionsschicht {APP_VERSION}: {status['active_review_tasks']} aktive Prüfaufträge, "
                f"{status['cycles']} Zyklen, {status['resolved_cycles']} abgeschlossene Zyklen. "
                f"Automatik: {status['automatic']}, Hintergrund läuft: {status['running']}."
            )
        elif lower in {"prüfzyklus", "pruefzyklus"}:
            result = actions.run_cycle()
            answer = result["message"]
        elif lower.startswith(("prüfauftrag ", "pruefauftrag ")):
            match = re.search(r"\d+", lower)
            result = actions.run_cycle(int(match.group(0))) if match else {"message": "Format: prüfauftrag <ID>"}
            answer = result["message"]
        elif lower.startswith(("warum ist ", "warum sind ")) and "unsicher" in lower:
            term = re.sub(r"^warum\s+(?:ist|sind)\s+", "", prompt.strip(), flags=re.I)
            term = re.sub(r"\s+unsicher\s*[?!.]*$", "", term, flags=re.I).strip()
            intelligence.refresh()
            answer = intelligence.explain_uncertainty(term)
        elif lower == "wissensplattform altbestand verknüpfen":
            result = platform.backfill() if platform else {"linked": {}, "total": 0}
            answer = f"Altbestand verknüpft: {result['total']} neue Graphknoten. Details: {result['linked']}"
        elif lower.startswith(("wissensweg ", "woher weißt du ", "woher weisst du ")):
            term = re.sub(r"^(?:wissensweg|woher\s+wei(?:ß|ss)t\s+du)\s+", "", prompt.strip(), flags=re.I)
            answer = platform.explain(term) if platform else "Knowledge Platform ist nicht angebunden."
        elif lower.startswith(("vertrauen ", "wie sicher ist ")):
            term = re.sub(r"^(?:vertrauen|wie\s+sicher\s+ist)\s+", "", prompt.strip(), flags=re.I).strip(" .?!")
            intelligence.refresh()
            answer = platform.explain(term) if platform else "Knowledge Platform ist nicht angebunden."
        elif search and lower.startswith("suche "):
            term = prompt[6:].strip()
            result = search.search_all(term)
            answer = result.get("answer", "Keine Treffer.")
        else:
            answer = (
                f"Wissensagent {APP_VERSION}: Ich suche künftig zuerst in 04_knowledge, "
                "dann in 03_memory, 06_learning, 32_data, Chronicle und zuletzt Legacy."
            )
        if not lower.startswith("wissensplattform"):
            self.remember("knowledge.query", prompt, {"agent": self.name})
        return AgentResult(self.name, True, answer)
