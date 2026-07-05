# Architecture Baseline Pre Runtime Migration 34.1

Datum: 2026-07-05
Status: Vor Runtime-Migration, nach Execution Planner 1.0 und Orchestrator Core 1.0
Zweck: Offizieller Vorher-/Nachher-Vergleich fuer die kontrollierte Runtime-Migration.

## 1. Vorhandene Core-Komponenten

Aktiv vorhanden und durch Manifest/Tests belegt:

- Foundation: `01_system/kontinuum/core/foundation_2_2.py`, `foundation_2_1.py`, Foundation Decision, Foundation Memory, Foundation Query, Foundation Reasoning.
- Canonical Layer: `canonical_architecture.py`, `canonical_database.py`, `canonical_api_registry.py`, `canonical_artifacts.py`, Canonical Governance Baseline.
- Capability Resolution: `01_system/kontinuum/core/capability_resolution_engine.py`, `24_config/capability_registry_34_1.json`.
- Execution Planning: `01_system/kontinuum/core/execution_planner.py`, `24_config/execution_plan_schema_34_1.json`.
- Execution Runtime: `01_system/kontinuum/core/orchestrator_core.py`, `24_config/orchestrator_runtime_schema_34_1.json`.
- Operational Agents: Agenten aus `01_system/kontinuum/agents`, inklusive FileAgent, WebAgent, Knowledge/Memory-bezogene Agenten und neue Spezialagenten.
- Governance/Review/Canonical Memory: Continuous Governance, Continuous Canonical Engine, Canonical Memory Manager, Identity Manager, Release Integrity.

## 2. Aktuelle Architektur

Der aktuelle Stand bildet die neue Architektur bereits als getrennte Komponenten ab. Die Runtime-Migration ist jedoch noch nicht vollzogen.

Aktueller aktiver Pfad:

1. `KontinuumSystem.ask()` startet Foundation Decision und Schutzpruefung.
2. `PromptOrchestrator.handle()` klassifiziert den Intent und ruft den Request Router auf.
3. `CapabilityResolutionEngine.resolve()` wird optional ausgefuehrt und speichert die letzte Resolution.
4. `ExecutionPlanner.plan_from_resolutions()` wird optional ausgefuehrt und speichert den letzten Execution Plan.
5. Die tatsaechliche Ausfuehrung laeuft weiter ueber den bestehenden Direktpfad im `PromptOrchestrator`:
   - CommandService
   - RequestRouter-Auswahl
   - FileAgent/WebAgent/Knowledge/Memory/AgentRouter
   - lokale Knowledge-, Search- und Research-Pfade
6. `ResponseRecorder.finish()` schreibt Antwort, Quellen, Memory- und Audit-Kontext.

Noch nicht aktiver Zielpfad:

`Prompt -> Request Router -> Capability Resolution Engine -> Execution Planner -> Orchestrator Core -> Governance -> Agent -> Review -> Canonical Memory Manager`

## 3. Vollstaendige Ablaufkette vor Migration

Vor Migration ist `OrchestratorCore` initialisiert und im Systemstatus sichtbar, aber nicht der produktive Ausfuehrungspfad fuer normale Prompts. `PromptOrchestrator.handle()` erzeugt bereits Plaene, nutzt das Planergebnis aber nur als Quelle/Diagnose und faellt danach in den bisherigen Direktpfad zurueck.

Die erste spaetere Umstellstelle ist daher `01_system/kontinuum/core/application_services.py`, Methode `PromptOrchestrator.handle()`, direkt nach `plan = planner.plan_from_resolutions([resolution])` und vor dem bestehenden `_handle_routed`/Agent-Direktpfad.

## 4. Bekannte Altpfade

- `PromptOrchestrator` bleibt aktuell die produktive Ausfuehrungs- und Antwortschicht.
- Historische Starter und Statuspfade existieren weiter, insbesondere 23, 32.3, 32.4, 33.0 und 34.0 in `16_installation` und `13_tools`.
- Historische Projektstatus-, Einstiegspunkt- und Release-Dateien liegen aktiv in `14_documents` und `22_project_chronicle`.
- Versionierte Lernagenten liegen aktiv in `12_agents`; kanonisch dokumentiert sind aktuell `learning_agent_1_2.py` und `continuous_learning_governance_1_1.py`, aeltere Versionen sind historische Parallelstaende.
- `32_data` enthaelt flach abgelegte historische Spiegeldateien (`_version_*`, `_02_versions_*`, `_legacy_versions_*`) direkt im aktiven Datenordner.

## 5. Risiken

- Automatische Archivierung kann Tests brechen, weil mehrere historische Dateien direkt von Tests per `spec_from_file_location` geladen werden.
- 34.0-Start- und Statusdateien sind durch historische Status-/Chronikdokumente referenziert; vor Archivierung muessen Referenzen bewusst als historische Dokumentation oder aktive Abhaengigkeit klassifiziert werden.
- Release Integrity erlaubt einzelne Legacy-Pfade ausdruecklich; diese Ausnahmen muessen vor Bereinigung mit CAM und Release Integrity abgeglichen werden.
- `32_data` enthaelt sehr viele historische Datenartefakte; unkontrollierte Verschiebung kann Datenprovenienz, Tests oder historische Rekonstruktion stoeren.
- Ohne Feature-Flag waere die Runtime-Migration schwer kontrolliert rueckschaltbar.

## 6. Migrationsstrategie

Empfohlene Reihenfolge:

1. Artefakt-Lifecycle-Verstoesse klassifizieren und nach Freigabe archivieren.
2. Feature-Flag `orchestrator_runtime_enabled` einfuehren oder dokumentiert aktivieren.
3. `PromptOrchestrator.handle()` erweitert den bestehenden Planerpfad:
   - Plan erzeugen.
   - Wenn `plan.status == "ready"` und Feature-Flag aktiv ist: `OrchestratorCore.run(plan)`.
   - Bei blockiertem/ungueltigem Plan oder Runtime-Fehler: bestehender Direktpfad bleibt Fallback.
4. Regressionstests fuer Dialog, FileAgent, WebAgent, Knowledge, Memory, Status und Governance ausfuehren.
5. Erst nach stabilen Regressionen ueber Entfernung des alten Direktpfads entscheiden.

## 7. Feature-Flag

Gepruefter Stand: `orchestrator_runtime_enabled` wurde in den aktiven Kern-, Config-, Test- und Dokumentationspfaden nicht gefunden.

Empfehlung: Vor produktiver Runtime-Migration als explizites Konfigurationsflag einfuehren, bevorzugt in einer kanonischen Runtime-/Systemkonfiguration und mit defensivem Default `false`.

## 8. Rueckfallstrategie

Der alte Direktpfad im `PromptOrchestrator` bleibt vollstaendig erhalten. Der neue Runtime-Pfad darf nur bei `plan.status == "ready"` und aktivem Feature-Flag ausfuehren. Bei jeder Abweichung bleibt der bestehende Direktpfad die Rueckfallebene.

## 9. Ausgangszustand

- Execution Planner 1.0: implementiert und getestet.
- Orchestrator Core 1.0: implementiert und getestet.
- Runtime-Schema: vorhanden.
- PromptOrchestrator: erzeugt bereits Execution Plans, nutzt Orchestrator Core aber noch nicht produktiv.
- Feature-Flag: nicht vorhanden.
- Artefakt-Lifecycle: aktive Verstoesse vorhanden; vor Migration zu klaeren.
