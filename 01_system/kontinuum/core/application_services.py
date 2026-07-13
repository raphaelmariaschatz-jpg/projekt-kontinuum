# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import re
from datetime import datetime

from kontinuum.agents.agent_registry import AgentRouter
from kontinuum.tools.formula_engine import FormulaEngine

from .conversation import Intent, normalize
from .request_router import RequestRouter
from .response_policy import ResponsePolicyManager


class ResponseRecorder:
    def __init__(self, system):
        self.system = system
        self.conversation = system.conversation
        self.response_policy = ResponsePolicyManager(system)

    def finish(self, answer: str, agent: str, intent: Intent) -> str:
        policy_result = self.response_policy.apply(answer, agent, intent)
        answer = policy_result.answer
        raw_answer = answer
        answer = self._with_source_footer(answer, agent)
        decision_id = getattr(self.system._foundation_context, "decision_id", None)
        if decision_id:
            self.system.foundation_decision.mark_created(decision_id, agent, answer)
        self.conversation.log_turn("assistant", answer, intent, agent)
        if (
            intent.input_type in {"question", "thought"}
            and agent not in {"knowledge", "memory", "identity_router", "session", "system", "foundation"}
            and len(" ".join(raw_answer.split())) >= 30
            and self.system.knowledge_contamination_guard.should_integrate(raw_answer, origin="dialogue", title=f"Dialogantwort ({agent})")
        ):
            self.system.knowledge_platform.integrate(
                raw_answer,
                origin="dialogue",
                title=f"Dialogantwort ({agent})",
                locator=f"conversation:{self.conversation.session_id}",
                extra={"agent": agent, "intent": intent.name},
            )
        if decision_id:
            self.system.foundation_decision.complete(decision_id, agent, answer)
            self.system._foundation_context.decision_id = None
        return answer

    def _with_source_footer(self, answer: str, agent: str) -> str:
        if "Quellen:" in (answer or "") and "- Suchmodus:" in (answer or ""):
            return answer
        mode = getattr(self.system, "search_mode", "Automatisch")
        if "Quellen:" in (answer or ""):
            return f"{answer}\n- Suchmodus: {mode}"
        local_agents = {
            "archive_search",
            "foundation",
            "identity_manager",
            "identity_router",
            "local_knowledge",
            "local_math",
            "local_truth",
            "memory",
            "search",
            "session",
            "system",
        }
        if agent == "web_agent":
            report = "\n".join([
                "Quellen:",
                "- lokale Datenbank: nein",
                "- Memory: nein",
                "- Internet: ja",
                "- Web-Ergebnisse: 1",
                f"- Suchmodus: {mode}",
            ])
            return f"{answer}\n\n{report}"
        if agent == "file_agent":
            report = "\n".join([
                "Quellen:",
                "- lokale Datei: ja",
                "- lokale Datenbank: nein",
                "- Memory: nein",
                "- Internet: nein",
                "- Web-Ergebnisse: 0",
                f"- Suchmodus: {mode}",
            ])
            return f"{answer}\n\n{report}"
        if agent == "vision_agent":
            report = "\n".join([
                "Quellen:",
                "- lokale Bilddatei: ja",
                "- lokale Datenbank: nein",
                "- Memory: nein",
                "- Internet: nein",
                "- Web-Ergebnisse: 0",
                "- Analysemodus: Metadatenanalyse, read-only",
                f"- Suchmodus: {mode}",
            ])
            return f"{answer}\n\n{report}"
        if agent in {"git_agent", "canonical_git_manager"}:
            report = "\n".join([
                "Quellen:",
                "- lokales Git-Repository: ja",
                "- lokale Datenbank: nein",
                "- Memory: nein",
                "- Internet: nein",
                "- Web-Ergebnisse: 0",
                "- Analysemodus: Git/Governance read-only",
                f"- Suchmodus: {mode}",
            ])
            return f"{answer}\n\n{report}"
        if agent == "code_agent":
            report = "\n".join([
                "Quellen:",
                "- lokaler Quellcode: ja",
                "- lokale Datenbank: nein",
                "- Memory: nein",
                "- Internet: nein",
                "- Web-Ergebnisse: 0",
                "- Analysemodus: Codeanalyse read-only",
                f"- Suchmodus: {mode}",
            ])
            return f"{answer}\n\n{report}"
        local_used = agent in local_agents
        memory_used = agent in {"archive_search", "foundation", "identity_manager", "identity_router", "local_knowledge", "local_truth", "memory", "search", "session"}
        if agent == "identity_manager":
            report = "\n".join([
                "Quellen:",
                "- lokale Datei: ja",
                "- lokale Datenbank: nein",
                "- Memory: ja",
                "- Internet: nein",
                "- Web-Ergebnisse: 0",
                f"- Suchmodus: {mode}",
            ])
            return f"{answer}\n\n{report}"
        report = "\n".join([
            "Quellen:",
            f"- lokale Datenbank: {'ja' if local_used else 'nein'}",
            f"- Memory: {'ja' if memory_used else 'nein'}",
            "- Internet: nein",
            "- Web-Ergebnisse: 0",
            f"- Suchmodus: {mode}",
        ])
        return f"{answer}\n\n{report}"


class CommandService:
    def __init__(self, system):
        self.system = system

    def handle(self, text: str, intent: Intent) -> tuple[str, str] | None:
        lower = normalize(text).strip(" .!?")
        if intent.name == "history.today_inputs":
            return self._format_todays_inputs(), "conversation"
        if lower == "webagentstatus":
            web_agent = getattr(self.system, "web_agent", None)
            return (web_agent.format_status() if web_agent else "WebAgent ist nicht angebunden."), "web_agent"
        if lower == "fileagentstatus":
            file_agent = getattr(self.system, "file_agent", None)
            return (file_agent.format_status() if file_agent else "FileAgent ist nicht angebunden."), "file_agent"
        if lower == "changeagentstatus":
            change_agent = getattr(self.system, "change_agent", None)
            return (change_agent.format_status() if change_agent else "ChangeAgent ist nicht angebunden."), "change_agent"
        if lower == "visionagentstatus":
            vision_agent = getattr(self.system, "vision_agent", None)
            return (vision_agent.format_status() if vision_agent else "VisionAgent ist nicht angebunden."), "vision_agent"
        if lower in {"gitagentstatus", "gitstatus"}:
            git_agent = getattr(self.system, "git_agent", None)
            return (git_agent.format_status() if git_agent else "GitAgent ist nicht angebunden."), "git_agent"
        if lower == "cgmstatus":
            manager = getattr(self.system, "canonical_git_manager", None)
            return (manager.format_status() if manager else "Canonical Git Manager 2.0 ist nicht angebunden."), "canonical_git_manager"
        if lower == "codeagentstatus":
            code_agent = getattr(self.system, "code_agent", None)
            return (code_agent.format_status() if code_agent else "CodeAgent ist nicht angebunden."), "code_agent"
        if lower in {"canonicalenginestatus", "cestatus", "continuouscanonicalstatus"}:
            engine = getattr(self.system, "continuous_canonical_engine", None)
            return (
                engine.format_status() if engine else "Continuous Canonical Engine ist nicht angebunden."
            ), "continuous_canonical_engine"
        if lower in {"identity status", "identitystatus", "identitätsstatus", "identitaetsstatus"}:
            manager = getattr(self.system, "identity_manager", None)
            return (manager.format_status() if manager else "IdentityManager ist nicht angebunden."), "identity_manager"
        if lower in {"memory status", "memorystatus", "cmm status", "cmmstatus"}:
            manager = getattr(self.system, "canonical_memory_manager", None)
            return (manager.format_status() if manager else "Canonical Memory Manager ist nicht angebunden."), "memory"
        if lower in {"orchestratorstatus", "orchestrator core status", "runtime status"}:
            orchestrator = getattr(self.system, "orchestrator_core", None)
            return (orchestrator.format_status() if orchestrator else "Orchestrator Core ist nicht angebunden."), "orchestrator_core"
        if lower in {"executionplanstatus", "execution planner status", "plannerstatus"}:
            planner = getattr(self.system, "execution_planner", None)
            return (planner.format_status() if planner else "Execution Planner ist nicht angebunden."), "execution_planner"
        if lower in {"crestatus", "cre status", "capabilitystatus", "capability resolution status"}:
            engine = getattr(self.system, "capability_resolution_engine", None)
            return (engine.format_status() if engine else "Capability Resolution Engine ist nicht angebunden."), "capability_resolution_engine"
        if lower in {"agent integration status", "caim status", "agent registry status", "caimstatus"}:
            manager = getattr(self.system, "canonical_agent_integration_manager", None)
            return (
                manager.format_status() if manager else "Canonical Agent Integration Manager ist nicht angebunden."
            ), "canonical_agent_integration_manager"
        if lower in {"memory statistics", "memorystatistics", "memory statistik", "memorystatistik", "cmm statistics", "cmmstatistics"}:
            manager = getattr(self.system, "canonical_memory_manager", None)
            return (manager.format_statistics() if manager else "Canonical Memory Manager ist nicht angebunden."), "memory"
        if lower.startswith("archivsuche "):
            result = self.system.search_router.search_archive(text[12:].strip())
            return self.system.search_router.format(result), "archive_search"
        if lower.startswith("suche "):
            result = self.system.search_router.search(text[6:].strip())
            return self.system.search_router.format(result), "search"
        if lower in {"agenten", "agentenstatus"}:
            return "Aktive Agenten: " + ", ".join(self.system.modules.list_active()), "system"
        if lower == "routingstatus":
            diagnosis = self.system.agent_router.diagnose("pythonstatus", "command")
            return f"Explizites Agentenrouting aktiv. Beispielroute: {diagnosis}", "system"
        if lower == "foundationreasoningstatus":
            return self.system.foundation_reasoning.format_status(), "foundation"
        if lower == "diagnostikstatus":
            return self.system.autonomous_diagnostics.status()["message"], "internal_diagnostic"
        if lower in {"diagnostik", "diagnose", "diagnostik starten"}:
            return self.system.autonomous_diagnostics.run("user.requested")["message"], "internal_diagnostic"
        if lower in {"benutzerstatus", "sessionstatus", "wer ist angemeldet", "rollenstatus"}:
            return self.system.session_context.format_status(), "session"
        if lower in {"offene fundamentzyklen", "fundamentzyklenstatus"}:
            current_id = getattr(self.system._foundation_context, "decision_id", None)
            exclude_ids = {int(current_id)} if current_id else set()
            return self.system.foundation_cycle_recovery.format_status(exclude_ids=exclude_ids), "foundation"
        if lower == "fundamentzyklus reparieren":
            current_id = getattr(self.system._foundation_context, "decision_id", None)
            exclude_ids = {int(current_id)} if current_id else set()
            result = self.system.foundation_cycle_recovery.recover("user.requested", exclude_ids=exclude_ids)
            return f"Foundation-Zyklus-Recovery: {result['recovered']} Zyklen geschlossen, offen danach: {result['open_after']}.", "foundation"
        if lower == "versionen":
            versions = sorted(
                path.name for path in self.system.path_tools.paths()["versions"].glob("version_*") if path.is_dir()
            )
            return f"Version {self.system.version} aktiv. Erkannte Versionsordner: {len(versions)}.", "system"
        return None

    def _format_todays_inputs(self) -> str:
        rows = self.system.storage.user_inputs_for_local_date()
        local_timezone = datetime.now().astimezone().tzinfo
        today = datetime.now().astimezone().strftime("%d.%m.%Y")
        if not rows:
            return f"Für heute, den {today}, sind keine Eingaben gespeichert."
        lines = [f"Gespeicherte Eingaben von heute, {today} ({len(rows)}):"]
        for row in rows:
            timestamp = datetime.fromisoformat(row["created_at"]).astimezone(local_timezone).strftime("%H:%M:%S")
            lines.append(f"- {timestamp} | {' '.join(str(row['content']).split())}")
        return "\n".join(lines)


class LocalKnowledgeService:
    CORE_DEFINITIONS = {
        "quantendynamik": (
            "Quantendynamik beschreibt, wie sich Quantensysteme zeitlich entwickeln. "
            "Im Zentrum stehen Zustände, Operatoren und die Schrödinger-Gleichung; je nach System geht es um "
            "Teilchen, Felder, Übergänge, Messprozesse und Wechselwirkungen. Kurz: Sie ist die Dynamik der "
            "Quantenmechanik, also nicht nur welche Zustände möglich sind, sondern wie sie sich verändern."
        ),
        "quantenmechanik": (
            "Quantenmechanik ist die physikalische Theorie mikroskopischer Systeme. Sie beschreibt Materie und "
            "Strahlung über Zustände, Wahrscheinlichkeiten, Operatoren, Superposition und Messungen statt über "
            "klassische Bahnen."
        ),
        "dna": (
            "DNA ist der Träger genetischer Information. Sie besteht aus Nukleotiden mit den Basen A, T, G und C; "
            "deren Reihenfolge codiert Bau- und Regulationsinformationen für Zellen."
        ),
        "python": (
            "Python ist eine gut lesbare, dynamische Programmiersprache. Sie wird für Automatisierung, Datenanalyse, "
            "Webentwicklung, wissenschaftliches Rechnen, KI und viele allgemeine Softwareaufgaben genutzt."
        ),
    }

    def answer(self, text: str) -> tuple[str, str] | None:
        lower = text.casefold()
        normalized = normalize(text)
        if "ich bin raphael" in normalized and ("schopfer" in normalized or "schoepfer" in normalized):
            return "Hallo Raphael. Ich erkenne dich gemaess meiner Kernidentitaet als meinen Schoepfer.", "local_truth"
        if "google suche" in normalized and any(word in normalized for word in ("benutze", "verwende", "nutze")):
            return (
                "Ich habe derzeit keinen eigenen Google-Suchconnector. Für Webrecherche kann ich direkte URLs "
                "abrufen und Fundstellen speichern. Eine Suchmaschinenintegration muss separat konfiguriert werden.",
                "system",
            )
        if "hooksche" in lower or "hookesche" in lower:
            return (
                "Das Hookesche Gesetz beschreibt im elastischen Bereich F = -k · x: "
                "Die Rückstellkraft ist proportional zur Auslenkung.",
                "local_knowledge",
            )
        if "binomisch" in normalized and "formel" in normalized:
            return (
                "Die drei binomischen Formeln lauten:\n"
                "1. (a + b)² = a² + 2ab + b²\n"
                "2. (a - b)² = a² - 2ab + b²\n"
                "3. (a + b)(a - b) = a² - b²",
                "local_math",
            )
        if "umfang der erde" in normalized:
            return (
                "Der Erdumfang beträgt am Äquator ungefähr 40.075 Kilometer; "
                "entlang eines Meridians sind es ungefähr 40.008 Kilometer.",
                "local_knowledge",
            )
        for key, answer in self.CORE_DEFINITIONS.items():
            if key in normalized:
                return answer, "knowledge"
        arithmetic = re.fullmatch(r".*?(\d+)\s*[x×*]\s*(\d+).*?", lower)
        if arithmetic:
            return (
                f"{arithmetic.group(1)} × {arithmetic.group(2)} = "
                f"{int(arithmetic.group(1)) * int(arithmetic.group(2))}.",
                "local_math",
            )
        return None


class PromptOrchestrator:
    CURRENT_INFORMATION_MARKERS = (
        "heute",
        "aktuell",
        "aktuelle",
        "aktuellen",
        "neueste",
        "neuesten",
        "preise",
        "preis",
        "wetter",
        "nachrichten",
        "versionen",
        "gesetze",
        "produkte",
        "produkt",
        "sport",
        "börse",
        "boerse",
    )

    def __init__(self, system):
        self.system = system
        self.commands = CommandService(system)
        self.local_knowledge = LocalKnowledgeService()
        self.formula_engine = FormulaEngine()
        self.request_router = RequestRouter(system.path_tools)
        self.recorder = ResponseRecorder(system)
        self.agent_router = AgentRouter(system.agents)

    def handle(self, text: str) -> str:
        intent = self.system.conversation.classify(text)
        decision = self.request_router.decide(text, intent)
        plan = None
        capability_engine = getattr(self.system, "capability_resolution_engine", None)
        if capability_engine:
            resolution = capability_engine.resolve(text, intent, decision)
            self.system.last_capability_resolution = resolution
            capability = resolution.get("required_capability", "")
            if capability and capability != "unknown":
                decision.sources.append(f"CRE:{capability}")
            planner = getattr(self.system, "execution_planner", None)
            if planner:
                plan = planner.plan_from_resolutions([resolution])
                self.system.last_execution_plan = plan
                decision.sources.append(f"ExecutionPlanner:{plan.get('status', '')}")
        self.system.conversation.log_turn("user", text, intent)
        self.system.agent_config["conversation"] = self.system.conversation.context_for_agents()
        if intent.name not in {"command", "memory.store"}:
            user = self.system.conversation.user
            owner = user.get("full_name") or user.get("username") or "Raphael"
            self.system.memory_core.observe(text, owner=owner)
        runtime_result = self._handle_orchestrator_runtime(text, intent, decision, plan)
        if runtime_result:
            answer, agent = runtime_result
            self.request_router.record(text, decision, answer, agent)
            return self.recorder.finish(answer, agent, intent)
        routed = self._handle_routed(text, intent, decision)
        if routed:
            answer, agent = routed
            self.request_router.record(text, decision, answer, agent)
            return self.recorder.finish(answer, agent, intent)
        web_agent = getattr(self.system, "web_agent", None)
        if web_agent and web_agent.urls_in(text):
            result = web_agent.handle_command(text)
            return self.recorder.finish(result.get("message", "WebAgent konnte den Auftrag nicht verarbeiten."), "web_agent", intent)
        file_agent = getattr(self.system, "file_agent", None)
        if file_agent and file_agent.looks_like_file_command(text):
            result = file_agent.handle_command(text)
            file_answer = result.get("message", "FileAgent konnte den Auftrag nicht verarbeiten.")
            if result.get("ok") and self._wants_function_test_report(text):
                file_answer = self._combine_file_and_diagnostic(file_answer, self._build_function_test_report())
            return self.recorder.finish(file_answer, "file_agent", intent)
        source_command = self._source_command(text)
        selected_mode = self._selected_mode()
        if not source_command and selected_mode != "Automatisch":
            source_command = {
                "Lokal": "local_only",
                "Internet": "internet_only",
                "Hybrid": "internet_and_local",
            }.get(selected_mode, "")
        if source_command == "last":
            report = getattr(self.system, "last_source_report", "")
            answer = report or self._source_report(False, False, False, 0, "Noch keine Suchroute in dieser Sitzung protokolliert.", selected_mode)
            return self.recorder.finish(answer, "system", intent)
        foundation_query = self.system.foundation_query.answer(
            text,
            getattr(self.system._foundation_context, "decision_id", None),
        )
        if foundation_query:
            return self.recorder.finish(foundation_query["answer"], "foundation", intent)
        if text.casefold().startswith("wissensklasse "):
            content = text[len("wissensklasse "):].strip()
            answer = self.system.foundation_memory.explain_classification(
                content, self.system.foundation_knowledge_guard
            )
            return self.recorder.finish(answer, "foundation", intent)
        identity_answer = self.system.identity_router.answer(text)
        if identity_answer:
            return self.recorder.finish(identity_answer, "identity_router", intent)
        command = self.commands.handle(text, intent)
        if command:
            return self.recorder.finish(command[0], command[1], intent)
        if source_command == "local_only":
            answer = self._answer_local_only(text)
            return self.recorder.finish(answer, "local_knowledge", intent)
        if source_command == "internet_and_local":
            answer = self._answer_with_search_engine(text, "prefer_internet", include_local=True)
            return self.recorder.finish(answer, "research", intent)
        if source_command == "internet_only":
            answer = self._answer_with_search_engine(text, "internet_only", include_local=False)
            return self.recorder.finish(answer, "research", intent)
        local = self.local_knowledge.answer(text) if intent.input_type != "command" else None
        if local:
            return self.recorder.finish(local[0], local[1], intent)
        local_truth = self.system.conversation.local_truth_answer(intent)
        if local_truth:
            return self.recorder.finish(local_truth, "local_truth", intent)
        local_agent_result = self.agent_router.route(text, intent.name)
        if local_agent_result and local_agent_result.agent not in {"dialogue", "research"}:
            return self.recorder.finish(local_agent_result.answer, local_agent_result.agent, intent)
        if local_agent_result and local_agent_result.agent == "research" and intent.input_type == "command":
            return self.recorder.finish(local_agent_result.answer, local_agent_result.agent, intent)
        normalized = normalize(text)
        project_term = next(
            (term for term in ("projektchronik", "forschung") if term in normalized),
            "",
        )
        if project_term:
            local_result = self.system.search_router.search(project_term, limit=10)
            return self.recorder.finish(self.system.search_router.format(local_result), "local_knowledge", intent)
        if self._needs_current_information(text, intent):
            answer = self._answer_with_search_engine(text, "prefer_internet", include_local=True)
            return self.recorder.finish(answer, "research", intent)
        if self.system._should_auto_research(text, intent):
            local_result = self.system.search_router.search(text, limit=5)
            if local_result["hits"]:
                report = self._source_report(True, True, False, 0, search_mode=self._selected_mode())
                self.system.last_source_report = report
                return self.recorder.finish(self.system.search_router.format(local_result) + "\n\n" + report, "local_knowledge", intent)
        routed_text = f"recherchiere {text}" if self.system._should_auto_research(text, intent) else text
        result = self.agent_router.route(routed_text, intent.name)
        answer = result.answer if result else "Keine passende Verarbeitung gefunden."
        agent = result.agent if result else "system"
        self.request_router.record(text, decision, answer, agent)
        return self.recorder.finish(answer, agent, intent)

    def _orchestrator_runtime_enabled(self) -> bool:
        config = getattr(self.system, "agent_config", {}) or {}
        return bool(getattr(self.system, "orchestrator_runtime_enabled", False) or config.get("orchestrator_runtime_enabled", False))

    def _handle_orchestrator_runtime(self, text: str, intent: Intent, decision, plan) -> tuple[str, str] | None:
        if not self._orchestrator_runtime_enabled():
            return None
        if not plan:
            self._record_orchestrator_runtime_fallback(decision, "plan_missing")
            return None
        if plan.get("status") != "ready":
            self._record_orchestrator_runtime_fallback(decision, "plan_not_ready", run={"plan_status": plan.get("status", "")})
            return None
        orchestrator = getattr(self.system, "orchestrator_core", None)
        if not orchestrator:
            self._record_orchestrator_runtime_fallback(decision, "orchestrator_missing")
            return None
        try:
            run = orchestrator.run(
                plan,
                payload={
                    "text": text,
                    "intent": getattr(intent, "name", ""),
                    "request_class": getattr(decision, "request_class", ""),
                    "selected_agent": getattr(decision, "selected_agent", ""),
                },
            )
        except Exception as exc:
            self._record_orchestrator_runtime_fallback(decision, "runtime_error", error=exc)
            return None
        self.system.last_orchestrator_run = run
        if run.get("status") != "completed":
            self._record_orchestrator_runtime_fallback(decision, "run_not_completed", run=run)
            return None
        answer, agent = self._orchestrator_answer(run)
        if not answer:
            self._record_orchestrator_runtime_fallback(decision, "empty_runtime_answer", run=run)
            return None
        decision.sources.append(f"OrchestratorCore:{run.get('status', '')}")
        return answer, agent or "orchestrator_core"

    def _orchestrator_answer(self, run: dict) -> tuple[str, str]:
        results = run.get("results", []) if isinstance(run, dict) else []
        for result in results:
            if result.get("handled") and result.get("answer"):
                return str(result.get("answer", "")), str(result.get("actual_agent") or result.get("expected_agent") or "orchestrator_core")
        for result in results:
            if result.get("answer"):
                return str(result.get("answer", "")), str(result.get("actual_agent") or result.get("expected_agent") or "orchestrator_core")
        return "", "orchestrator_core"

    def _record_orchestrator_runtime_fallback(self, decision, reason: str, error: Exception | str | None = None, run: dict | None = None) -> None:
        event = {"reason": reason}
        if error:
            event["error"] = str(error)
        if run:
            event["run_status"] = str(run.get("status") or run.get("plan_status") or "")
            if run.get("errors"):
                event["errors"] = run.get("errors")
        self.system.last_orchestrator_runtime_fallback = event
        history = getattr(self.system, "orchestrator_runtime_fallbacks", [])
        if not isinstance(history, list):
            history = []
        history.append(event)
        self.system.orchestrator_runtime_fallbacks = history[-20:]
        if hasattr(decision, "sources"):
            decision.sources.append(f"OrchestratorCore:fallback:{reason}")

    def _handle_routed(self, text: str, intent: Intent, decision) -> tuple[str, str] | None:
        selected = decision.selected_agent
        if selected.startswith("capability:"):
            capability = selected.split(":", 1)[1]
            result = self._handle_capability(capability, text)
            if result:
                decision.sources.append(f"CAIM:{capability}")
                return result.answer, result.agent
            return self._routing_diagnosis(decision, selected), "router"
        if selected == "status_agent":
            if normalize(text).strip() == "routingstatus":
                return self.request_router.format_status(), "router"
            command = self.commands.handle(text, intent)
            if command:
                return command[0], "status_agent"
        if selected == "canonical_engine":
            command = self.commands.handle(text, intent)
            if command:
                return command[0], "canonical_engine"
        if selected == "change_agent":
            result = self._handle_named_agent("change_agent", text)
            if result:
                decision.sources.append("ChangeAgent")
                return result.answer, "change_agent"
        if selected == "vision_agent":
            result = self._handle_named_agent("vision_agent", text)
            if result:
                decision.sources.append("VisionAgent")
                return result.answer, "vision_agent"
        if selected == "canonical_git_manager":
            result = self._handle_named_agent("canonical_git_manager", text)
            if result:
                decision.sources.append("CGM 2.0")
                return result.answer, "canonical_git_manager"
        if selected == "git_agent":
            result = self._handle_named_agent("git_agent", text)
            if result:
                decision.sources.append("GitAgent")
                return result.answer, "git_agent"
        if selected == "code_agent":
            result = self._handle_named_agent("code_agent", text)
            if result:
                decision.sources.append("CodeAgent")
                return result.answer, "code_agent"
        if selected == "math_agent":
            answer = self.formula_engine.answer(text)
            if answer:
                decision.sources.append("FormulaEngine")
                return answer, "math_agent"
            decision.sources.append("FormulaEngine:unresolved")
            return "Die Rechenaufgabe wurde erkannt, aber die Formel-Engine konnte sie noch nicht lösen.", "math_agent"
        if selected == "file_agent":
            file_agent = getattr(self.system, "file_agent", None)
            if file_agent:
                result = file_agent.handle_command(text)
                decision.sources.append(result.get("path") or result.get("file_name") or "FileAgent")
                file_answer = result.get("message", "Datei konnte nicht gelesen werden: unbekannter Grund.")
                if result.get("ok") and self._wants_function_test_report(text):
                    decision.sources.append("interne Diagnostik")
                    file_answer = self._combine_file_and_diagnostic(file_answer, self._build_function_test_report())
                return file_answer, "file_agent"
        if selected == "web_agent":
            web_agent = getattr(self.system, "web_agent", None)
            if web_agent:
                result = web_agent.handle_command(text)
                decision.sources.append(result.get("start_url") or "WebAgent")
                return result.get("message", "WebAgent konnte den Auftrag nicht verarbeiten."), "web_agent"
        if selected == "learning_agent":
            result = self._handle_named_agent("learning", text)
            if result:
                decision.sources.append("LearningAgent")
                return result.answer, "learning_agent"
        if selected == "identity_manager":
            result = self._handle_identity_manager(text)
            if result:
                decision.sources.append("IdentityManager")
                return result, "identity_manager"
            result = self._handle_named_agent("memory", f"speichere {text}")
            if result:
                decision.sources.append("MemoryAgent")
                return result.answer, "memory"
        if selected in {"memory_agent", "config_fallback"}:
            if selected == "config_fallback":
                identity_result = self._handle_identity_manager(text)
                if identity_result:
                    decision.sources.append("IdentityManager")
                    return identity_result, "identity_manager"
            result = self._handle_named_agent("memory", text)
            if not result:
                result = self._handle_named_agent("memory", f"speichere {text}")
            if result:
                decision.sources.append("MemoryAgent")
                return result.answer, "memory"
        if selected == "knowledge_agent":
            answer = self._answer_knowledge(text, intent, decision)
            if answer:
                return answer, "knowledge_agent"
        if selected:
            return self._routing_diagnosis(decision, selected), "router"
        return None

    def _handle_named_agent(self, name: str, text: str):
        agent = next((candidate for candidate in self.system.agents if candidate.name == name), None)
        if not agent:
            return None
        result = agent.handle(text)
        return result if result and result.handled else None

    def _handle_capability(self, capability: str, text: str):
        manager = getattr(self.system, "canonical_agent_integration_manager", None)
        if not manager:
            return None
        candidates = manager.find_by_capability(capability)
        for candidate in candidates:
            if not manager.can_execute(candidate.get("id", "")):
                continue
            agent = next((item for item in self.system.agents if item.name == candidate.get("name")), None)
            if not agent:
                continue
            result = agent.handle(text)
            if result and result.handled:
                return result
        return None

    def _handle_identity_manager(self, text: str) -> str | None:
        manager = getattr(self.system, "identity_manager", None)
        if not manager or not manager.can_handle(text):
            return None
        result = manager.save_from_text(text)
        if not result.get("ok"):
            return None
        identity = result["identity"]
        creator = identity.get("creator", {}).get("name", "Raphael Schatz")
        address = identity.get("user", {}).get("preferred_address", "Raphael")
        assistant = identity.get("assistant", {}).get("name", "Kontinuum")
        short_name = identity.get("assistant", {}).get("short_name", "K")
        return (
            f"Ich habe die kanonische Identität gespeichert: Creator {creator}, "
            f"bevorzugte Anrede {address}, Systemname {assistant}/{short_name}."
        )

    def _wants_function_test_report(self, text: str) -> bool:
        normalized = normalize(text)
        triggers = (
            "vollstandiger funktionstest",
            "vollstaendiger funktionstest",
            "vollständiger funktionstest",
            "funktionen prufen",
            "funktionen pruefen",
            "funktionen prüfen",
            "selftest",
            "diagnostikbericht",
            "gefundene fehler",
            "schwachstellen",
            "gewunschte erweiterungen",
            "gewünschte erweiterungen",
        )
        return any(trigger in normalized for trigger in triggers)

    def _build_function_test_report(self) -> str:
        diagnostics = self._run_available_diagnostics()
        status_checks = self._collect_function_test_statuses()
        findings = diagnostics.get("findings", []) if isinstance(diagnostics, dict) else []
        errors = self._diagnostic_errors(findings)
        weaknesses = self._diagnostic_weaknesses(diagnostics, status_checks)
        extensions = self._diagnostic_extensions(status_checks)
        return "\n".join([
            "[DIAGNOSTIKBERICHT]",
            "Ein vollständiger automatischer Funktionstest ist noch nicht vollständig angebunden. Ausgeführt wurden verfügbare interne Checks.",
            "",
            "Ausgeführte Checks:",
            *[f"- {item}" for item in status_checks],
            "",
            "1. Gefundene Fehler:",
            *[f"- {item}" for item in errors],
            "2. Gefundene Schwachstellen:",
            *[f"- {item}" for item in weaknesses],
            "3. Gewünschte Erweiterungen:",
            *[f"- {item}" for item in extensions],
        ])

    def _run_available_diagnostics(self) -> dict:
        diagnostics = getattr(self.system, "autonomous_diagnostics", None)
        if not diagnostics:
            return {"ok": False, "findings": [], "message": "Autonomous Diagnostics ist nicht angebunden."}
        try:
            return diagnostics.run("user.function_test_report")
        except Exception as exc:
            return {
                "ok": False,
                "findings": [{
                    "title": "Autonomous Diagnostics konnte nicht ausgeführt werden",
                    "severity": "HIGH",
                    "area": "diagnostics",
                    "impact": "Der interne Diagnosecheck brach ab.",
                    "cause": str(exc),
                }],
                "message": f"Autonomous Diagnostics fehlgeschlagen: {exc}",
            }

    def _collect_function_test_statuses(self) -> list[str]:
        checks: list[tuple[str, object, tuple[str, ...]]] = [
            ("Systemstatus", self.system, ("status",)),
            ("CAIM-Status", getattr(self.system, "canonical_agent_integration_manager", None), ("format_status", "status")),
            ("CMM/Memory-Status", getattr(self.system, "canonical_memory_manager", None), ("format_status", "status")),
            ("CIM/Identity-Status", getattr(self.system, "identity_manager", None), ("format_status", "status")),
            ("Routingstatus", self.request_router, ("format_status", "status")),
            ("CodeAgent-Status", getattr(self.system, "code_agent", None), ("format_status", "status")),
        ]
        results = []
        for label, target, method_names in checks:
            method_name = next((name for name in method_names if target and hasattr(target, name)), "")
            if not target or not method_name:
                results.append(f"{label}: nicht angebunden")
                continue
            try:
                value = getattr(target, method_name)()
                results.append(f"{label}: verfügbar ({self._brief_status(value)})")
            except Exception as exc:
                results.append(f"{label}: Fehler beim Abruf ({type(exc).__name__}: {exc})")
        return results

    @staticmethod
    def _brief_status(value) -> str:
        if isinstance(value, dict):
            if "ok" in value:
                return "ok" if value.get("ok") else "prüfen"
            if "active" in value:
                return "aktiv" if value.get("active") else "inaktiv"
            return f"{len(value)} Statusfelder"
        text = " ".join(str(value).split())
        return text[:120] + ("..." if len(text) > 120 else "")

    @staticmethod
    def _diagnostic_errors(findings: list[dict]) -> list[str]:
        if not findings:
            return ["Keine kritischen Fehler in den verfügbaren internen Checks gemeldet."]
        errors = []
        for item in findings[:8]:
            title = item.get("title") or item.get("code") or "Diagnosefund"
            severity = item.get("severity") or item.get("severity_label") or "unbewertet"
            area = item.get("area") or "unbekannter Bereich"
            evidence = item.get("evidence") or item.get("cause") or ""
            suffix = f" Evidenz: {evidence}" if evidence else ""
            errors.append(f"{title} ({area}, Schweregrad: {severity}).{suffix}")
        return errors

    @staticmethod
    def _diagnostic_weaknesses(diagnostics: dict, status_checks: list[str]) -> list[str]:
        weaknesses = []
        if diagnostics and diagnostics.get("message"):
            weaknesses.append(str(diagnostics["message"]))
        unavailable = [item for item in status_checks if "nicht angebunden" in item or "Fehler beim Abruf" in item]
        weaknesses.extend(unavailable)
        if not weaknesses:
            weaknesses.append("Keine zusätzlichen Schwachstellen aus den verfügbaren Statuschecks abgeleitet.")
        return weaknesses

    @staticmethod
    def _diagnostic_extensions(status_checks: list[str]) -> list[str]:
        extensions = [
            "Vollständigen TestAgent anbinden, der Funktions-, Integrations- und Regressionstests koordiniert.",
            "Diagnostikbericht um konkrete Testskript-Ergebnisse und priorisierte Reparaturvorschläge erweitern.",
        ]
        if any(item.startswith("CodeAgent-Status: nicht angebunden") for item in status_checks):
            extensions.append("CodeAgent-Status in den Funktionstestbericht integrieren, sobald der Agent angebunden ist.")
        return extensions

    @staticmethod
    def _combine_file_and_diagnostic(file_answer: str, diagnostic_report: str) -> str:
        return f"{file_answer.rstrip()}\n\n{diagnostic_report.strip()}"

    @staticmethod
    def _routing_diagnosis(decision, expected_agent: str) -> str:
        return "\n".join([
            "Der Router hat den Auftrag erkannt, aber es wurde keine ausführende Agentenantwort erzeugt.",
            f"- erkannter Intent: {decision.request_class}",
            f"- erwarteter Agent: {expected_agent}",
            "- Grund: Für diese Route wurde kein angebundener Agent oder Fallback mit `handled=True` gefunden.",
            "- empfohlene Reparatur: Agent im System registrieren oder Route auf IdentityManager/MemoryAgent/ConfigFallback abbilden.",
        ])

    def _answer_knowledge(self, text: str, intent: Intent, decision) -> str | None:
        local = self.local_knowledge.answer(text)
        if local:
            decision.sources.append("Kernwissen")
            return local[0]
        local_truth = self.system.conversation.local_truth_answer(intent)
        if local_truth:
            decision.sources.append("Kernidentität")
            return local_truth
        result = self._handle_named_agent("knowledge", text)
        if result and result.answer and "Ich suche künftig" not in result.answer:
            decision.sources.append("KnowledgeAgent")
            return result.answer
        search_result = self.system.search_router.search(text, limit=5)
        hits = [hit for hit in search_result.get("hits", []) if not self._is_echo_hit(hit, text)]
        if hits:
            search_result = {**search_result, "hits": hits}
            decision.sources.append("lokale Wissensdatenbank")
            return self.system.search_router.format(search_result)
        if self._needs_current_information(text, intent) or self._automatic_internet_enabled():
            decision.sources.append("automatische Internetrecherche")
            return self._answer_with_search_engine(text, "prefer_internet", include_local=True)
        model = self.system.tools.get("language_model_tools")
        if model and hasattr(model, "generate"):
            context = self.system.conversation.context_for_agents()
            generated = model.generate(
                text,
                context=context.get("turns", []),
                local_truths=context.get("local_truths", {}),
                user=context.get("user", {}),
            )
            if isinstance(generated, dict) and generated.get("ok") and generated.get("answer"):
                decision.sources.append("lokales Sprachmodell")
                return generated["answer"]
        term = re.sub(r"^(was\s+ist|was\s+sind|erkläre|erklaere|definiere)\s+", "", text.strip(), flags=re.I).strip(" ?!.")
        return (
            f"{term or 'Dieses Thema'} ist als Wissensfrage erkannt. Im vorhandenen Kernwissen und in den lokalen "
            "Lernquellen finde ich dazu noch keine belastbare ausführliche Antwort. Automatische Internetrecherche "
            "war nicht verfügbar; bitte prüfe den Suchconnector, wenn ich online ergänzen soll."
        )

    def _automatic_internet_enabled(self) -> bool:
        search_engine = self.system.tools.get("search_engine_tools")
        config = getattr(search_engine, "config", {}) if search_engine else {}
        return bool(config.get("enabled") and config.get("auto_research_questions", True))

    @staticmethod
    def _is_echo_hit(hit: dict, text: str) -> bool:
        needle = " ".join((text or "").split()).casefold()
        if not needle:
            return False

        def values(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from values(child)
            elif isinstance(value, list):
                for child in value:
                    yield from values(child)
            elif isinstance(value, str):
                yield " ".join(value.split()).casefold()

        return any(candidate == needle for candidate in values(hit))

    def _source_command(self, text: str) -> str:
        normalized = normalize(text)
        if "zeige mir, wo du gesucht hast" in normalized or "wo hast du gesucht" in normalized:
            return "last"
        if "nutze nur die lokale datenbank" in normalized or "nur die lokale datenbank" in normalized or "nur lokale datenbank" in normalized:
            return "local_only"
        if "internet und lokale datenbank" in normalized or "lokale datenbank und internet" in normalized:
            return "internet_and_local"
        if "suche im internet" in normalized or "nutze internet" in normalized or "internetsuche" in normalized or "websuche" in normalized:
            return "internet_only"
        return ""

    def _selected_mode(self) -> str:
        value = getattr(self.system, "search_mode", "Automatisch")
        return value if value in {"Automatisch", "Lokal", "Internet", "Hybrid"} else "Automatisch"

    def _needs_current_information(self, text: str, intent: Intent) -> bool:
        if intent.name not in {"dialog.question", "dialog.follow_up"}:
            return False
        normalized = normalize(text)
        return any(marker in normalized for marker in self.CURRENT_INFORMATION_MARKERS)

    def _answer_local_only(self, text: str) -> str:
        result = self.system.search_router.search(text, limit=8)
        report = self._source_report(True, True, False, 0, search_mode=self._selected_mode())
        self.system.last_source_report = report
        return self.system.search_router.format(result) + "\n\n" + report

    def _answer_with_search_engine(self, text: str, mode: str, include_local: bool) -> str:
        parts = []
        local_used = False
        memory_used = False
        if include_local:
            local_result = self.system.search_router.search(text, limit=5)
            local_used = True
            memory_used = True
            if local_result.get("hits"):
                parts.append("Lokale Suche:\n" + self.system.search_router.format(local_result))
        search_engine = self.system.tools.get("search_engine_tools")
        if not search_engine or not getattr(search_engine, "config", {}).get("enabled", False):
            report = self._source_report(
                local_used,
                memory_used,
                False,
                0,
                "Internet-Recherche nicht verfügbar oder ohne verwertbare Treffer.",
                self._selected_mode(),
            )
            self.system.last_source_report = report
            parts.append(report)
            return "\n\n".join(parts)
        try:
            result = search_engine.search(text, mode=mode)
        except TypeError:
            result = search_engine.search(text)
        web_count = sum(
            1
            for row in result.get("results", [])
            if row.get("provider") not in {"local_knowledge", "notebook_knowledge"}
        )
        internet_used = mode != "local_only"
        if result.get("ok"):
            parts.append(search_engine.format_results(result))
        else:
            parts.append("Internet-Recherche nicht verfügbar oder ohne verwertbare Treffer.\n" + result.get("error", "Unbekannter Fehler"))
        report = self._source_report(local_used, memory_used, internet_used, web_count, search_mode=self._selected_mode())
        self.system.last_source_report = report
        parts.append(report)
        return "\n\n".join(parts)

    @staticmethod
    def _source_report(
        local_database: bool,
        memory: bool,
        internet: bool,
        web_results: int,
        note: str = "",
        search_mode: str = "Automatisch",
    ) -> str:
        lines = [
            "Quellen:",
            f"- lokale Datenbank: {'ja' if local_database else 'nein'}",
            f"- Memory: {'ja' if memory else 'nein'}",
            f"- Internet: {'ja' if internet else 'nein'}",
            f"- Web-Ergebnisse: {web_results}",
            f"- Suchmodus: {search_mode}",
        ]
        if note:
            lines.append(note)
        return "\n".join(lines)
