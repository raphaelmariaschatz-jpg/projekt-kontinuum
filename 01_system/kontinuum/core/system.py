# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import threading
from pathlib import Path

from kontinuum.agents.agent_registry import AgentRouter, build_agents
from kontinuum.tools.tool_registry import build_tools
from kontinuum.version import APP_VERSION

from .application_services import PromptOrchestrator
from .capability_resolution_engine import CapabilityResolutionEngine
from .execution_planner import ExecutionPlanner
from .orchestrator_core import OrchestratorCore
from .search_router import SearchRouter
from .conversation import ConversationManager, Intent, normalize
from .continuous_learning import ContinuousLearningService
from .internet_learning import InternetLearningService
from .web_agent import WebAgentService
from .file_agent import FileAgentService
from .continuous_canonical_engine import ContinuousCanonicalEngine
from .change_agent import ChangeAgentService
from .vision_agent import VisionAgentService
from .git_agent import GitAgentService
from .canonical_git_manager import CanonicalGitManager
from .code_agent import CodeAgentService
from .consciousness import ConsciousnessCore
from .canonical_reflective_layer import CanonicalReflectiveLayer
from .meta_reasoning import MetaReasoningEngine
from .ai_competency_framework import CanonicalAICompetencyFramework
from .api_learning_connector import APILearningConnector
from .cognitive_pipeline import CanonicalCognitivePipeline
from .intelligence_framework import CanonicalIntelligenceFramework
from .project_vision import CanonicalProjectVisionFramework
from .media_learning import CanonicalMediaLearningFramework
from .enterprise_framework import CanonicalEnterpriseFramework
from .human_interface import CanonicalHumanInterfaceFramework
from .self_knowledge import SelfKnowledgeCore
from .memory_core import MemoryCore
from .knowledge_platform import KnowledgePlatform
from .knowledge_intelligence import KnowledgeIntelligence
from .epistemic_actions import EpistemicActionService
from .source_quality import SourceQualityClassifier
from .persistent_self_model import PersistentSelfModelCore
from .continuity import ContinuityCore
from .moral_core import MoralCore
from .foundation_decision import FoundationDecisionLayer
from .meaning_core import MeaningCore
from .motivation_core import MotivationCore
from .motivation_explanation import MotivationExplanationCore
from .temporal_relevance import TemporalRelevanceCore
from .session_context import SessionContext
from .identity_router import IdentityRouter
from .identity_manager import IdentityManager
from kontinuum.foundation.canonical_memory_manager import CanonicalMemoryManager
from kontinuum.foundation.canonical_agent_integration_manager import CanonicalAgentIntegrationManager
from .knowledge_contamination_guard import KnowledgeContaminationGuard
from .foundation_knowledge_guard import FoundationKnowledgeGuard
from .foundation_integrity import FoundationIntegrityCore
from .foundation_memory import FoundationMemoryLayer
from .foundation_query import FoundationQueryLayer
from .foundation_reasoning import FoundationReasoningLayer
from .foundation_2_2 import (
    FoundationAPI,
    FoundationMigrationManager,
    FoundationRegistry,
    FoundationRuleEngine,
    FoundationStatusCenter,
    ImprovementFoundation,
)
from .meaning_presentation import MeaningPresentationLayer
from .foundation_cycle_recovery import FoundationCycleRecovery
from .autonomous_diagnostics import AutonomousDiagnosticsCore
from .canonical_architecture import CanonicalArchitectureManager
from .canonical_database import CanonicalDatabaseManager
from .canonical_api_registry import CanonicalAPIRegistryManager
from .canonical_artifacts import CanonicalArtifactManager
from .storage import Storage
from .structure import validate_structure


class ModuleView:
    def __init__(self, agents):
        self.agents = agents

    def list_active(self) -> list[str]:
        return [agent.name for agent in self.agents]


class KontinuumSystem:
    version = APP_VERSION

    def __init__(self, root: str | Path | None = None):
        self.lifecycle_state = "initializing"
        self.tools = build_tools(root=root)
        self.search_mode = "Automatisch"
        self.orchestrator_runtime_enabled = False
        self.orchestrator_runtime_fallbacks = []
        self.path_tools = self.tools["path_tools"]
        self.path_tools.ensure_all()
        self.storage = Storage(self.path_tools.paths()["data"] / "kontinuum.db")
        self.memory_core = MemoryCore(self.storage)
        self.foundation_knowledge_guard = FoundationKnowledgeGuard()
        self.knowledge_intelligence = KnowledgeIntelligence(self.storage, self.foundation_knowledge_guard)
        self.knowledge_platform = KnowledgePlatform(
            self.storage, self.memory_core, self.version, self.knowledge_intelligence
        )
        self.tools["notebook_tools"].bind(self.storage)
        self.tools["notebook_tools"].web = self.tools["web_tools"]
        self.tools["notebook_tools"].memory_core = self.memory_core
        self.tools["notebook_tools"].knowledge_platform = self.knowledge_platform
        self.knowledge_intelligence.refresh()
        self.search_router = SearchRouter(self.path_tools, self.storage)
        self.tools["search_engine_tools"].bind_local_router(self.search_router)
        self.agent_config = {"version": self.version}
        self.agent_config["orchestrator_runtime_enabled"] = self.orchestrator_runtime_enabled
        self.agent_config["memory_core"] = self.memory_core
        self.agent_config["knowledge_platform"] = self.knowledge_platform
        self.agent_config["knowledge_intelligence"] = self.knowledge_intelligence
        self.agent_config["foundation_knowledge_guard"] = self.foundation_knowledge_guard
        self.source_quality = SourceQualityClassifier()
        self.epistemic_actions = EpistemicActionService(
            self.path_tools,
            self.storage,
            self.tools["search_engine_tools"],
            self.tools["web_tools"],
            self.source_quality,
            self.knowledge_intelligence,
            self.knowledge_platform,
        )
        self.agent_config["epistemic_actions"] = self.epistemic_actions
        self.identity_manager = IdentityManager(self.path_tools, self.storage)
        self.identity = self.identity_manager.to_legacy_identity()
        self.agent_config["identity_manager"] = self.identity_manager
        self.canonical_memory_manager = CanonicalMemoryManager(
            self.path_tools,
            self.storage,
            self.identity_manager,
        )
        self.agent_config["canonical_memory_manager"] = self.canonical_memory_manager
        self.canonical_agent_integration_manager = CanonicalAgentIntegrationManager(
            self.path_tools,
            self.storage,
            self.identity_manager,
        )
        self.agent_config["canonical_agent_integration_manager"] = self.canonical_agent_integration_manager
        self.capability_resolution_engine = CapabilityResolutionEngine(
            self.canonical_agent_integration_manager,
            path_tools=self.path_tools,
        )
        self.agent_config["capability_resolution_engine"] = self.capability_resolution_engine
        self.execution_planner = ExecutionPlanner(
            self.capability_resolution_engine,
            path_tools=self.path_tools,
        )
        self.agent_config["execution_planner"] = self.execution_planner
        self.session_context = SessionContext(self.identity)
        self.session_context.bind({})
        self.identity_router = IdentityRouter(self.session_context, self.identity)
        self.knowledge_contamination_guard = KnowledgeContaminationGuard()
        self.knowledge_platform.contamination_guard = self.knowledge_contamination_guard
        self.knowledge_platform.foundation_guard = self.foundation_knowledge_guard
        self.continuity_core = ContinuityCore(self.path_tools, self.storage, self.identity)
        self.moral_core = MoralCore(self.path_tools, self.storage)
        self.agent_config["continuity_core"] = self.continuity_core
        self.agent_config["moral_core"] = self.moral_core
        self.continuity_core.checkpoint("Systeminitialisierung begonnen.", self.version, {"lifecycle": self.lifecycle_state})
        self.continuous_learning = ContinuousLearningService(self.path_tools, self.storage)
        self.agent_config["continuous_learning"] = self.continuous_learning
        self.internet_learning = InternetLearningService(self.path_tools)
        self.agent_config["internet_learning"] = self.internet_learning
        self.web_agent = WebAgentService(self.path_tools, self.storage, self.continuous_learning)
        self.agent_config["web_agent"] = self.web_agent
        self.file_agent = FileAgentService(self.path_tools, self.storage, self.continuous_learning)
        self.agent_config["file_agent"] = self.file_agent
        self.continuous_canonical_engine = ContinuousCanonicalEngine(
            self.path_tools.project_root(),
            self.path_tools,
            self.storage,
            self.version,
            strict_config=False,
        )
        self.agent_config["continuous_canonical_engine"] = self.continuous_canonical_engine
        self.web_agent.canonical_engine = self.continuous_canonical_engine
        self.file_agent.canonical_engine = self.continuous_canonical_engine
        self.git_agent = GitAgentService(
            self.path_tools,
            self.storage,
            self.continuous_canonical_engine,
        )
        self.agent_config["git_agent"] = self.git_agent
        self.change_agent = ChangeAgentService(
            self.path_tools,
            self.continuous_canonical_engine,
            self.storage,
        )
        self.agent_config["change_agent"] = self.change_agent
        self.vision_agent = VisionAgentService(
            self.path_tools,
            self.storage,
            self.continuous_canonical_engine,
        )
        self.agent_config["vision_agent"] = self.vision_agent
        self.code_agent = CodeAgentService(
            self.path_tools,
            self.storage,
            self.continuous_canonical_engine,
        )
        self.agent_config["code_agent"] = self.code_agent
        self.consciousness = ConsciousnessCore(self.path_tools, self.storage)
        self.agent_config["consciousness"] = self.consciousness
        self.self_knowledge = SelfKnowledgeCore(
            self.path_tools, self.storage, self.identity, self.consciousness, self.knowledge_intelligence
        )
        self.agent_config["self_knowledge"] = self.self_knowledge
        self.canonical_reflective_layer = CanonicalReflectiveLayer(self.path_tools, self.storage)
        self.agent_config["canonical_reflective_layer"] = self.canonical_reflective_layer
        self.meta_reasoning = MetaReasoningEngine(self.storage)
        self.agent_config["meta_reasoning"] = self.meta_reasoning
        self.ai_competency_framework = CanonicalAICompetencyFramework(
            self.path_tools.project_root()
        )
        self.agent_config["ai_competency_framework"] = self.ai_competency_framework
        self.api_learning_connector = APILearningConnector()
        self.agent_config["api_learning_connector"] = self.api_learning_connector
        self.cognitive_pipeline = CanonicalCognitivePipeline(
            self.path_tools.project_root(), self.storage
        )
        self.agent_config["cognitive_pipeline"] = self.cognitive_pipeline
        self.intelligence_framework = CanonicalIntelligenceFramework(
            self.path_tools.project_root(), self.storage
        )
        self.agent_config["intelligence_framework"] = self.intelligence_framework
        self.project_vision_framework = CanonicalProjectVisionFramework(
            self.path_tools.project_root(), self.storage
        )
        self.agent_config["project_vision_framework"] = self.project_vision_framework
        self.media_learning_framework = CanonicalMediaLearningFramework(
            self.path_tools.project_root()
        )
        self.agent_config["media_learning_framework"] = self.media_learning_framework
        self.enterprise_framework = CanonicalEnterpriseFramework(
            self.path_tools.project_root()
        )
        self.agent_config["enterprise_framework"] = self.enterprise_framework
        self.human_interface_framework = CanonicalHumanInterfaceFramework(
            self.path_tools.project_root()
        )
        self.agent_config["human_interface_framework"] = self.human_interface_framework
        self.foundation_decision = FoundationDecisionLayer(
            self.storage, self.moral_core, self.continuity_core, self.knowledge_intelligence
        )
        self.foundation_integrity = FoundationIntegrityCore(
            self.storage,
            self.identity,
            self.continuity_core.foundation,
            self.foundation_decision,
        )
        self.foundation_memory = FoundationMemoryLayer(
            self.storage,
            self.identity,
            self.continuity_core.foundation,
            self.foundation_decision.goals(),
            self.version,
        )
        self.foundation_integrity.bind_memory_layer(self.foundation_memory)
        self.foundation_reasoning = FoundationReasoningLayer(self.storage, self.foundation_memory)
        self.foundation_decision.bind_reasoning(self.foundation_reasoning)
        self.foundation_query = FoundationQueryLayer(
            self.storage,
            self.foundation_memory,
            self.session_context,
            self.identity,
            self.foundation_reasoning,
        )
        self.foundation_registry = FoundationRegistry(self.storage, self.foundation_memory)
        self.foundation_rule_engine = FoundationRuleEngine(self.foundation_registry)
        self.improvement_foundation = ImprovementFoundation(self.storage, self.foundation_registry)
        self.foundation_migration_manager = FoundationMigrationManager(self.storage, self.foundation_registry)
        self.foundation_migration_manager.migrate()
        self.foundation_api = FoundationAPI(
            self.storage,
            self.foundation_registry,
            self.foundation_rule_engine,
            self.foundation_query,
        )
        self.foundation_status_center = FoundationStatusCenter(
            self.foundation_registry,
            self.foundation_rule_engine,
            self.foundation_api,
            self.improvement_foundation,
            self.foundation_migration_manager,
            self.foundation_decision,
            self.foundation_integrity,
            self.foundation_query,
            self.foundation_reasoning,
        )
        self.canonical_architecture = CanonicalArchitectureManager(
            self.path_tools.project_root(),
            self.storage,
            self.version,
            strict_config=False,
        )
        self.canonical_database = CanonicalDatabaseManager(
            self.path_tools.project_root(),
            self.storage,
            self.version,
            strict_config=False,
        )
        self.canonical_api_registry = CanonicalAPIRegistryManager(
            self.path_tools.project_root(),
            self.version,
            strict_config=False,
        )
        self.canonical_artifacts = CanonicalArtifactManager(
            self.path_tools.project_root(),
            self.version,
            strict_config=False,
        )
        self.canonical_git_manager = CanonicalGitManager(
            self.path_tools,
            self.git_agent,
            self.storage,
            self.continuous_canonical_engine,
            self.canonical_architecture,
            self.canonical_artifacts,
        )
        self.agent_config["canonical_git_manager"] = self.canonical_git_manager
        self.knowledge_platform.foundation_integrity = self.foundation_integrity
        self.continuous_learning.bind_foundation_guard(self.foundation_knowledge_guard)
        self.continuous_learning.bind_foundation_memory(self.foundation_memory)
        self.knowledge_intelligence.refresh()
        self.foundation_cycle_recovery = FoundationCycleRecovery(self.foundation_decision)
        self.foundation_cycle_recovery.recover("system.startup")
        self.agent_config["foundation_decision"] = self.foundation_decision
        self.agent_config["foundation_integrity"] = self.foundation_integrity
        self.agent_config["foundation_memory"] = self.foundation_memory
        self.agent_config["foundation_query"] = self.foundation_query
        self.agent_config["foundation_reasoning"] = self.foundation_reasoning
        self.agent_config["foundation_registry"] = self.foundation_registry
        self.agent_config["foundation_rule_engine"] = self.foundation_rule_engine
        self.agent_config["foundation_api"] = self.foundation_api
        self.agent_config["improvement_foundation"] = self.improvement_foundation
        self.agent_config["foundation_migration_manager"] = self.foundation_migration_manager
        self.agent_config["foundation_status_center"] = self.foundation_status_center
        self.agent_config["canonical_architecture"] = self.canonical_architecture
        self.agent_config["canonical_database"] = self.canonical_database
        self.agent_config["canonical_api_registry"] = self.canonical_api_registry
        self.agent_config["canonical_artifacts"] = self.canonical_artifacts
        self.meaning_core = MeaningCore(self.storage, self.identity)
        self.agent_config["meaning_core"] = self.meaning_core
        self.meaning_presentation = MeaningPresentationLayer(self.storage, self.identity)
        self.agent_config["meaning_presentation"] = self.meaning_presentation
        self.motivation_core = MotivationCore(
            self.storage, self.meaning_core, self.foundation_decision, self.knowledge_intelligence
        )
        self.foundation_reasoning.trace_motivation_scores()
        self.agent_config["motivation_core"] = self.motivation_core
        self.motivation_explanation = MotivationExplanationCore(
            self.storage, self.motivation_core, self.meaning_core, self.foundation_decision, self.foundation_reasoning
        )
        self.agent_config["motivation_explanation"] = self.motivation_explanation
        self.temporal_relevance = TemporalRelevanceCore(
            self.storage, self.meaning_core, self.motivation_core, self.knowledge_intelligence
        )
        self.agent_config["temporal_relevance"] = self.temporal_relevance
        self.agent_config["session_context"] = self.session_context
        self.agent_config["identity_router"] = self.identity_router
        self.agent_config["foundation_cycle_recovery"] = self.foundation_cycle_recovery
        self._foundation_context = threading.local()
        self.agent_config["foundation_context"] = self._foundation_context
        self.epistemic_actions.bind_foundation(self.foundation_decision)
        self.continuous_learning.bind_foundation(self.foundation_decision)
        self.persistent_self_model = PersistentSelfModelCore(
            self.storage,
            self.identity,
            {
                "version": lambda: self.version,
                "lifecycle": lambda: self.lifecycle_state,
                "research": lambda: self.tools["search_engine_tools"].status(),
                "epistemic_actions": lambda: self.epistemic_actions.status(),
                "continuous_learning": lambda: self.continuous_learning.status(),
                "web_agent": lambda: self.web_agent.status(),
                "file_agent": lambda: self.file_agent.status(),
                "git_agent": lambda: self.git_agent.status(),
                "change_agent": lambda: self.change_agent.format_status(),
                "vision_agent": lambda: self.vision_agent.status(),
                "code_agent": lambda: self.code_agent.status(),
                "canonical_git_manager": lambda: self.canonical_git_manager.status(),
                "canonical_agent_integration_manager": lambda: self.canonical_agent_integration_manager.status(),
                "capability_resolution_engine": lambda: self.capability_resolution_engine.status(),
                "orchestrator_core": lambda: self.orchestrator_core.status(),
                "knowledge_platform": lambda: self.knowledge_platform.status(),
                "continuity": lambda: self.continuity_core.status(),
                "moral": lambda: self.moral_core.status(),
                "foundation": lambda: self.foundation_decision.status(),
                "foundation_integrity": lambda: self.foundation_integrity.status(),
                "foundation_memory": lambda: self.foundation_memory.status(),
                "foundation_query": lambda: self.foundation_query.status(),
                "foundation_reasoning": lambda: self.foundation_reasoning.status(),
                "foundation_2_2": lambda: self.foundation_status_center.status(),
                "foundation_2_1": lambda: self.foundation_status_center.status(),
                "canonical_architecture": lambda: self.canonical_architecture.status(),
                "canonical_database": lambda: self.canonical_database.status(),
                "canonical_api_registry": lambda: self.canonical_api_registry.status(),
                "canonical_artifacts": lambda: self.canonical_artifacts.status(),
                "meaning": lambda: self.meaning_core.status(),
                "motivation": lambda: self.motivation_core.status(),
                "motivation_explanation": lambda: self.motivation_explanation.status(),
                "temporal_relevance": lambda: self.temporal_relevance.status(),
            },
        )
        self.persistent_self_model.resolve_conflict(
            "moral.foundation_decisions",
            "29.1 korrigiert den veränderlichen Entscheidungszähler von Moralwissen zu beobachtbarem Selbstwissen.",
        )
        self.persistent_self_model.observe("Systemstart und Initialisierung des persistenten Selbstmodells.", "system.startup")
        self.agent_config["persistent_self_model"] = self.persistent_self_model
        self.conversation = ConversationManager(
            self.storage, self.identity, self.version, self.self_knowledge, self.consciousness
        )
        self.conversation.bind_user(self.session_context.current())
        self.memory_core.session_id = self.conversation.session_id
        self.agents = build_agents(storage=self.storage, tools=self.tools, config=self.agent_config)
        self.orchestrator_core = OrchestratorCore(
            self.agents,
            schema_path=self.path_tools.paths()["config"] / OrchestratorCore.SCHEMA_FILE,
        )
        self.agent_config["orchestrator_core"] = self.orchestrator_core
        self.agent_router = AgentRouter(self.agents)
        self.modules = ModuleView(self.agents)
        self.prompt_orchestrator = PromptOrchestrator(self)
        self.request_router = self.prompt_orchestrator.request_router
        self.autonomous_diagnostics = AutonomousDiagnosticsCore(self)
        self.agent_config["autonomous_diagnostics"] = self.autonomous_diagnostics
        self.diagnostic_report = self.autonomous_diagnostics.run("automatic.startup")
        self.continuous_learning.seed_default_tasks()
        self.continuous_learning.start()
        self.internet_learning.start()
        self.epistemic_actions.start()
        self.lifecycle_state = "ready"
        self.foundation_decision.generate_self_question("system.ready")
        self.continuity_core.checkpoint("Systeminitialisierung vollständig abgeschlossen.", self.version, {"lifecycle": self.lifecycle_state})
        self.persistent_self_model.observe("Systeminitialisierung vollständig abgeschlossen.", "system.ready")

    def set_user_context(self, identity: dict | None) -> None:
        self.conversation.bind_user(self.session_context.bind(identity))

    def set_cost_confirmation_handler(self, handler) -> None:
        self.agent_config["cost_confirmation_handler"] = handler
        winget = self.tools.get("winget_tools")
        if winget:
            winget.confirmation_handler = handler

    def set_search_progress_handler(self, handler) -> None:
        self.search_router.set_progress_handler(handler)

    def set_search_mode(self, mode: str) -> None:
        value = (mode or "Automatisch").strip()
        self.search_mode = value if value in {"Automatisch", "Lokal", "Internet", "Hybrid"} else "Automatisch"

    def close(self) -> None:
        self.internet_learning.stop()
        self.epistemic_actions.stop()
        self.continuous_learning.stop()
        self.lifecycle_state = "stopped"
        self.continuity_core.checkpoint("Systemdienste kontrolliert beendet.", self.version, {"lifecycle": self.lifecycle_state})
        self.persistent_self_model.observe("Systemdienste kontrolliert beendet.", "system.shutdown")

    def _load_identity(self) -> dict:
        path = self.path_tools.paths()["memory"] / "core_identity.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            fixed = data.get("fixed_principles", {})
            return {
                "name": fixed.get("name", "Kontinuum"),
                "creator": fixed.get("creator", "Raphael Schatz"),
                "core_process": fixed.get("core_process", "Erkennen - Schaffen - Vollenden"),
                "guiding_philosophy": fixed.get("guiding_philosophy", "Der Weg ist das Ziel"),
                "address_user_as": fixed.get("address_user_as", "Raphael"),
            }
        except (OSError, ValueError):
            return {
                "name": "Kontinuum",
                "creator": "Raphael Schatz",
                "core_process": "Erkennen - Schaffen - Vollenden",
                "guiding_philosophy": "Der Weg ist das Ziel",
                "address_user_as": "Raphael",
            }

    def status(self) -> dict:
        structure = validate_structure(self.path_tools)
        model_status = self.tools["language_model_tools"].status()
        python_status = self.tools["python_tools"].status()
        winget_status = self.tools["winget_tools"].status()
        search_engine_status = self.tools["search_engine_tools"].status()
        oracle_cloud_status = self.tools["oracle_cloud_tools"].status()
        formula_agent = next((agent for agent in self.agents if agent.name == "formula"), None)
        return {
            "name": self.identity["name"],
            "version": self.version,
            "backend": f"KontinuumSystem {self.version}",
            "database": str(self.storage.database),
            "agents": len(self.agents),
            "structure_ok": structure["ok"],
            "language_model": model_status,
            "python": python_status,
            "winget": winget_status,
            "search_engine": search_engine_status,
            "oracle_cloud": oracle_cloud_status,
            "formula_engine": formula_agent.engine.status() if formula_agent else "Formel-Engine nicht verfügbar.",
            "continuous_learning": self.continuous_learning.status(),
            "internet_learning": self.internet_learning.status(),
            "web_agent": self.web_agent.status(),
            "file_agent": self.file_agent.status(),
            "git_agent": self.git_agent.status(),
            "change_agent": self.change_agent.format_status(),
            "vision_agent": self.vision_agent.status(),
            "code_agent": self.code_agent.status(),
            "canonical_git_manager": self.canonical_git_manager.status(),
            "canonical_agent_integration_manager": self.canonical_agent_integration_manager.status(),
            "capability_resolution_engine": self.capability_resolution_engine.status(),
            "orchestrator_runtime_enabled": self.orchestrator_runtime_enabled,
            "orchestrator_runtime_fallbacks": list(self.orchestrator_runtime_fallbacks[-5:]),
            "orchestrator_core": self.orchestrator_core.status(),
            "self_knowledge": self.self_knowledge.profile(),
            "consciousness": self.consciousness.profile(),
            "canonical_reflective_layer": self.canonical_reflective_layer.status(),
            "meta_reasoning": self.meta_reasoning.status(),
            "ai_competency_framework": self.ai_competency_framework.status(),
            "api_learning_connector": self.api_learning_connector.status(),
            "cognitive_pipeline": self.cognitive_pipeline.status(),
            "intelligence_framework": self.intelligence_framework.status(),
            "project_vision_framework": self.project_vision_framework.status(),
            "media_learning_framework": self.media_learning_framework.status(),
            "enterprise_framework": self.enterprise_framework.status(),
            "human_interface_framework": self.human_interface_framework.status(),
            "memory_core": self.memory_core.status(),
            "canonical_memory_manager": self.canonical_memory_manager.status(),
            "knowledge_platform": self.knowledge_platform.status(),
            "knowledge_self_model": self.knowledge_intelligence.self_model(),
            "epistemic_actions": self.epistemic_actions.status(),
            "persistent_self_model": self.persistent_self_model.status(),
            "continuity_core": self.continuity_core.status(),
            "moral_core": self.moral_core.status(),
            "foundation_decision": self.foundation_decision.status(),
            "foundation_integrity": self.foundation_integrity.status(),
            "foundation_memory": self.foundation_memory.status(),
            "foundation_query": self.foundation_query.status(),
            "foundation_reasoning": self.foundation_reasoning.status(),
            "canonical_identity_manager": self.identity_manager.status(),
            "foundation_2_2": self.foundation_status_center.status(),
            "foundation_2_1": self.foundation_status_center.status(),
            "canonical_architecture": self.canonical_architecture.status(),
            "canonical_database": self.canonical_database.status(),
            "canonical_api_registry": self.canonical_api_registry.status(),
            "canonical_artifacts": self.canonical_artifacts.status(),
            "meaning_core": self.meaning_core.status(),
            "motivation_core": self.motivation_core.status(),
            "motivation_explanation": self.motivation_explanation.status(),
            "temporal_relevance": self.temporal_relevance.status(),
            "session": self.session_context.current(),
            "foundation_cycles": {"open": len(self.foundation_cycle_recovery.open_cycles())},
            "maintenance": self.tools["maintenance_tools"].status(),
            "autonomous_diagnostics": self.autonomous_diagnostics.status(),
        }

    def ask(self, prompt: str) -> str:
        text = (prompt or "").strip()
        if not text:
            return f"Ich bin bereit, {self.identity['address_user_as']}."
        batch = self._command_batch(text)
        if batch:
            return "\n\n".join(self.ask(command) for command in batch)
        blocked = self.persistent_self_model.guard_input(text)
        assessment_only = text.casefold().startswith(("moralbewertung ", "bewerte handlung ", "zielkonflikt "))
        decision = self.foundation_decision.begin(text, {
            "interface": "ask",
            "assessment_only": assessment_only,
            "protection_blocked": bool(blocked),
            "protection_reason": blocked or "",
            "protection_source": "persistent_self_model" if blocked else "",
        })
        if decision["decision"] == "block":
            if blocked:
                self.persistent_self_model.observe("Schutzregel ausgelöst.", "self.protection")
            self.storage.add("audit_events", "foundation.action.blocked", text, decision)
            self.foundation_decision.complete_blocked(int(decision["decision_id"]), decision["reason"])
            return f"Handlung durch Fundament-Schicht blockiert. Grund: {decision['reason']}"
        self._foundation_context.decision_id = int(decision["decision_id"])
        try:
            answer = self.prompt_orchestrator.handle(text)
            self.persistent_self_model.observe("Abgeschlossene Systeminteraktion.", "system.ask")
            return answer
        except Exception as exc:
            self.foundation_decision.complete(
                int(decision["decision_id"]), "system", f"Interaktion fehlgeschlagen: {exc}"
            )
            raise
        finally:
            self._foundation_context.decision_id = None

    def ask_async(self, prompt: str, callback) -> threading.Thread:
        def worker():
            try:
                callback(self.ask(prompt), None)
            except Exception as exc:
                callback("", exc)

        thread = threading.Thread(target=worker, daemon=True, name="KontinuumAsyncRequest")
        thread.start()
        return thread

    def _command_batch(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) < 2:
            return []
        if any(line.casefold().startswith(("python", "codex", "winget")) for line in lines):
            return []
        return lines if all(self.conversation.classify(line).input_type == "command" for line in lines) else []

    def _should_auto_research(self, text: str, intent: Intent) -> bool:
        search_engine = self.tools.get("search_engine_tools")
        config = getattr(search_engine, "config", {}) if search_engine else {}
        if not config.get("enabled") or not config.get("auto_research_questions", True):
            return False
        if intent.name not in {"dialog.question", "dialog.follow_up"}:
            return False
        normalized = normalize(text)
        local_dialog_phrases = (
            "warum antwortest du nicht",
            "wie geht es dir",
            "was kannst du",
            "was denkst du",
        )
        return not any(phrase in normalized for phrase in local_dialog_phrases)
