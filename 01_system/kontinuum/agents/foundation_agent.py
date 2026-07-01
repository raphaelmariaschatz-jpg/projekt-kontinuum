from __future__ import annotations

import re

from kontinuum.version import APP_VERSION

from .base_agent import AgentResult, BaseAgent


class FoundationAgent(BaseAgent):
    name = "foundation"

    def can_handle(self, prompt: str) -> bool:
        lower = (prompt or "").casefold().strip()
        supported = lower in {
            "kontinuitätsstatus",
            "kontinuitaetsstatus",
            "fundamentstatus",
            "fundamentale prinzipien",
            "moralstatus",
            "fundamentschichtstatus",
            "fundamentintegritätsstatus",
            "fundamentintegritaetsstatus",
            "fundamentaudit",
            "foundationmemorystatus",
            "foundation memory status",
            "langfristige ziele",
            "zielstatus",
            "selbstfragen",
            "stelle dir eine frage",
            "bedeutungsstatus",
            "meaningstatus",
            "motivationsstatus",
            "motivationstatus",
            "motivationsprioritäten",
            "motivationsprioritaeten",
            "motivationserklärungsstatus",
            "motivationserklaerungsstatus",
            "relevanzstatus",
            "zeitrelevanzstatus",
            "bedeutungsinflation",
            "chronikprägung",
            "chronikpraegung",
            "wissenslückenpriorität",
            "wissenslueckenprioritaet",
            "benutzerstatus",
            "sessionstatus",
            "wer ist angemeldet",
            "rollenstatus",
            "offene fundamentzyklen",
            "fundamentzyklus reparieren",
            "fundamentzyklenstatus",
            "foundationstatus",
            "foundation2status",
            "foundation 2.1 status",
            "foundationregeln",
            "foundation registry",
            "foundationapi status",
            "foundation rule engine status",
            "architekturstatus",
            "canonical architecture status",
            "cam status",
            "canonical database status",
            "cdm status",
        } or lower.startswith(("moralbewertung ", "bewerte handlung ", "zielkonflikt "))
        return supported or lower.startswith((
            "foundationregel ",
            "wissensklasse ",
            "bedeutungspfad", "meaningpfad", "bedeutung ",
            "motivationsprioritäten ", "motivationsprioritaeten ", "motivation ",
            "motivationserklärung ", "motivationserklaerung ", "warum score ",
            "erkläre priorität ", "erklaere prioritaet ", "wichtige einflüsse ", "wichtige einfluesse ",
        ))

    def handle(self, prompt: str) -> AgentResult:
        continuity = self.config.get("continuity_core")
        moral = self.config.get("moral_core")
        foundation = self.config.get("foundation_decision")
        foundation_integrity = self.config.get("foundation_integrity")
        foundation_memory = self.config.get("foundation_memory")
        foundation_api = self.config.get("foundation_api")
        foundation_status_center = self.config.get("foundation_status_center")
        canonical_architecture = self.config.get("canonical_architecture")
        canonical_database = self.config.get("canonical_database")
        meaning = self.config.get("meaning_core")
        motivation = self.config.get("motivation_core")
        motivation_explanation = self.config.get("motivation_explanation")
        temporal_relevance = self.config.get("temporal_relevance")
        meaning_presentation = self.config.get("meaning_presentation")
        session_context = self.config.get("session_context")
        foundation_cycle_recovery = self.config.get("foundation_cycle_recovery")
        foundation_context = self.config.get("foundation_context")
        lower = prompt.casefold().strip()
        if lower in {"kontinuitätsstatus", "kontinuitaetsstatus", "fundamentstatus"}:
            answer = continuity.format_status()
        elif lower == "fundamentale prinzipien":
            answer = continuity.format_principles()
        elif lower == "moralstatus":
            status = moral.status()
            answer = (
                f"Moral Core {APP_VERSION}: {status['rules']} Regeln, {status['assessments']} Bewertungen. "
                f"Entscheidungen: {status['decisions']}."
            )
        elif lower == "fundamentschichtstatus":
            status = foundation.status()
            completed = status["completed_cycles"]
            decisions = status["decisions"]
            current_id = getattr(foundation_context, "decision_id", None)
            if current_id and foundation_cycle_recovery and int(current_id) in foundation_cycle_recovery.open_cycles():
                completed = min(decisions, completed + 1)
            answer = (
                f"Foundation Decision Layer {APP_VERSION}: {completed}/{decisions} "
                f"Entscheidungszyklen vollständig, {status['active_goals']} aktive Langzeitziele, "
                f"{status['open_self_questions']} offene kontrollierte Selbstfragen. "
                "Verbindlicher Ablauf: Erkennen → Schaffen → Vollenden."
            )
        elif lower in {"fundamentintegritätsstatus", "fundamentintegritaetsstatus"}:
            status = foundation_integrity.status()
            answer = (
                f"Foundation Knowledge Protection {status['version']}: "
                f"{'intakt' if status['ok'] else 'verletzt'}, "
                f"{status['verified_records']}/{status['protected_records']} geschützte Datensätze verifiziert, "
                f"{len(status['contamination'])} aktive Kontaminationsbefunde. "
                "Fundamentwissen ist von Fachwissen, Lernen, Berichten, Diagnosen und Wissenslücken getrennt."
            )
        elif lower == "fundamentaudit":
            answer = foundation_integrity.audit_report()
        elif lower in {"foundationmemorystatus", "foundation memory status"}:
            answer = foundation_memory.format_status()
        elif lower.startswith("wissensklasse "):
            content = prompt[len("wissensklasse "):].strip()
            answer = foundation_memory.explain_classification(content, self.config.get("foundation_knowledge_guard"))
        elif lower in {"langfristige ziele", "zielstatus"}:
            answer = foundation.format_goals()
        elif lower == "selbstfragen":
            answer = foundation.format_questions()
        elif lower == "stelle dir eine frage":
            result = foundation.generate_self_question("user_requested_controlled_reflection")
            answer = f"Kontrollierte Selbstfrage: {result['question']} | Grundlage: {result['basis']}"
        elif lower in {"bedeutungsstatus", "meaningstatus"}:
            answer = meaning.format_status()
        elif lower.startswith(("bedeutungspfad", "meaningpfad", "bedeutung ")):
            term = re.sub(r"^(?:bedeutungspfad|meaningpfad|bedeutung)\s*", "", prompt, flags=re.I).strip()
            debug = " debug" in lower or lower.endswith("debug")
            term = re.sub(r"\s+debug$", "", term, flags=re.I).strip()
            answer = meaning_presentation.explain(term, debug=debug) if meaning_presentation else meaning.explain_path(term)
        elif lower in {"motivationsstatus", "motivationstatus"}:
            answer = motivation.format_status()
        elif lower in {"motivationsprioritäten", "motivationsprioritaeten"}:
            answer = motivation.format_priorities()
        elif lower in {"motivationserklärungsstatus", "motivationserklaerungsstatus"}:
            answer = motivation_explanation.format_status()
        elif lower in {"benutzerstatus", "sessionstatus", "wer ist angemeldet", "rollenstatus"}:
            answer = session_context.format_status()
        elif lower in {"offene fundamentzyklen", "fundamentzyklenstatus"}:
            answer = foundation_cycle_recovery.format_status()
        elif lower == "fundamentzyklus reparieren":
            result = foundation_cycle_recovery.recover("user.requested")
            answer = f"Foundation-Zyklus-Recovery: {result['recovered']} Zyklen geschlossen, offen danach: {result['open_after']}."
        elif lower in {"foundationstatus", "foundation2status", "foundation 2.1 status"}:
            answer = foundation_status_center.format_status() if foundation_status_center else "Foundation Status Center ist nicht angebunden."
        elif lower in {"foundationregeln", "foundation registry"}:
            answer = foundation_status_center.format_rules() if foundation_status_center else "Foundation Registry ist nicht angebunden."
        elif lower == "foundationapi status":
            status = foundation_api.get_status() if foundation_api else {}
            answer = (
                f"Foundation API {status.get('version', '')}: "
                f"{'aktiv' if status.get('active') else 'nicht aktiv'}, "
                f"Operationen: {', '.join(status.get('allowed_operations', []))}. "
                f"Schreiben: {status.get('write_operations', 'unbekannt')}."
            )
        elif lower == "foundation rule engine status":
            status = foundation_api.get_status().get("rule_engine", {}) if foundation_api else {}
            answer = (
                f"Foundation Rule Engine {status.get('version', '')}: "
                f"{'aktiv' if status.get('active') else 'nicht aktiv'}, "
                f"{status.get('block_patterns', 0)} Schutzmuster, "
                f"Query-Routen: {', '.join(status.get('query_routes', []))}."
            )
        elif lower in {"architekturstatus", "canonical architecture status", "cam status"}:
            answer = (
                canonical_architecture.format_status()
                if canonical_architecture and canonical_architecture.status().get("active")
                else "Canonical Architecture Manager ist in dieser Laufzeit nicht konfiguriert."
            )
        elif lower in {"canonical database status", "cdm status"}:
            answer = (
                canonical_database.format_status()
                if canonical_database and canonical_database.status().get("active")
                else "Canonical Database Manager ist in dieser Laufzeit nicht konfiguriert."
            )
        elif lower.startswith("foundationregel "):
            rule_id = prompt.split(None, 1)[1].strip().upper()
            rule = foundation_api.get_rule(rule_id) if foundation_api else None
            answer = (
                f"{rule['rule_id']} [{rule['foundation_class']}]: {rule['content']}"
                if rule else f"Keine Foundation-Regel mit ID {rule_id} gefunden."
            )
        elif lower in {"relevanzstatus", "zeitrelevanzstatus"}:
            answer = temporal_relevance.format_status()
        elif lower == "bedeutungsinflation":
            answer = temporal_relevance.format_inflation_risk()
        elif lower in {"chronikprägung", "chronikpraegung"}:
            answer = temporal_relevance.format_chronicle_importance()
        elif lower in {"wissenslückenpriorität", "wissenslueckenprioritaet"}:
            answer = temporal_relevance.format_gap_priorities()
        elif lower.startswith(("motivationserklärung ", "motivationserklaerung ", "warum score ", "erkläre priorität ", "erklaere prioritaet ")):
            term = re.sub(
                r"^(?:motivationserklärung|motivationserklaerung|warum\s+score|erkläre\s+priorität|erklaere\s+prioritaet)\s+",
                "",
                prompt,
                flags=re.I,
            ).strip()
            answer = motivation_explanation.explain(term)
        elif lower.startswith(("wichtige einflüsse ", "wichtige einfluesse ")):
            term = re.sub(r"^(?:wichtige\s+einflüsse|wichtige\s+einfluesse)\s+", "", prompt, flags=re.I).strip()
            if "ident" in term.casefold():
                answer = motivation_explanation.format_identity_influences()
            else:
                answer = motivation_explanation.format_influences(term)
        elif lower.startswith(("motivationsprioritäten ", "motivationsprioritaeten ", "motivation ")):
            category = re.sub(r"^(?:motivationsprioritäten|motivationsprioritaeten|motivation)\s+", "", prompt, flags=re.I).strip()
            answer = motivation.format_priorities(category)
        elif lower.startswith(("moralbewertung ", "bewerte handlung ")):
            action = re.sub(r"^(?:moralbewertung|bewerte\s+handlung)\s+", "", prompt, flags=re.I).strip()
            answer = moral.format_assessment(action)
        elif lower.startswith("zielkonflikt "):
            goals = re.split(r"\s+(?:oder|vs\.?|gegen)\s+", prompt[len("zielkonflikt "):], maxsplit=1, flags=re.I)
            if len(goals) != 2:
                answer = "Format: zielkonflikt <Ziel A> oder <Ziel B>"
            else:
                result = moral.resolve_goal_conflict(goals[0].strip(), goals[1].strip())
                answer = (
                    f"Moralischer Zielkonflikt: {result['decision']}. "
                    f"Bevorzugtes Ziel: {result['preferred'] or 'keines ohne weitere Prüfung'}. "
                    f"Grund: {result['reason']}"
                )
        else:
            answer = f"Temporal Relevance Core {APP_VERSION}, Motivation Explanation Core, Motivation Core, Meaning Core und Foundation Decision Layer sind aktiv."
        return AgentResult(self.name, True, answer)
