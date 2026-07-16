# Canonical Architecture Map (CAMap) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: kanonische Architekturkarte
Gueltig ab: 2026-07-09

## Zweck

CAMap 1.0 dokumentiert Beziehungen zentraler Architekturkomponenten. Es beschreibt Abhaengigkeiten, bereitgestellte Leistungen, Nutzung, Governance-Zuordnung, Layer und Status. CAMap ist keine Runtime-Komponente.

Normativer Hinweis: Seit CMIBF 1.0 ist das Canonical Master Implementation Blueprint Framework die alleinige Architekturverfassung und normative Architekturquelle. CAMap ist eine Architekturkarte und besitzt keine eigenstaendige Architekturautoritaet. Abweichungen zwischen CAMap und CMIBF sind zugunsten des CMIBF aufzuloesen.

## Hauptbeziehungen

~~~mermaid
flowchart TD
  CMIBF --> AFP
  AFP --> CAWP
  CAWP --> CAC
  CMIBF --> CAC
  CMIBF --> AGF
  CMIBF --> Foundation
  AFP --> AGF
  AFP --> CDG
  CAC --> CAMap
  Foundation --> AGF
  Foundation --> CanonicalLayer[Canonical Layer]
  AGF --> CDG
  AGF --> CCPPolicy[CCP-Policy]
  CanonicalLayer --> CAM
  CanonicalLayer --> CLMSF
  CAM --> ALP
  CAM --> CADP
  Governance --> ReleaseIntegrity[Release Integrity]
  CG --> CKS
  CKS --> CAMap
  CKS --> CDI
  CKS --> CHI
  CLU --> CCPCognitive[CCP-Cognitive]
  CRE --> ExecutionPlanner[Execution Planner]
  ExecutionPlanner --> OrchestratorCore[Orchestrator Core]
  RuntimeSchema[Runtime Schema] --> ExecutionPlanner
  RuntimeSchema --> OrchestratorCore
  CanonicalMemory[Canonical Memory] --> CCPCognitive
~~~

## Komponenten

### Foundation

Depends On: CMIBF, Creator Identity, Foundation Rules
Provides: Principles, Compatibility boundaries
Used By: AGF, CDG, Governance, Canonical Memory
Governed By: CMIBF, Foundation
Layer: Foundation
Status: Canonical

### CMIBF

Depends On: freigegebene Architekturentscheidungen, kanonische Projektprinzipien, dokumentierte Governance-Regeln
Provides: Architekturverfassung, normative Architekturquelle, Architecture First Principle, CAC-Quellmodell
Used By: AFP, CAC, AGF, CDG, CAMap, Foundation, alle abgeleiteten Artefakte
Governed By: menschliche Freigabe und CMIBF-Governance
Layer: Normative Meta-Architecture
Status: Canonical

### AFP

Depends On: CMIBF
Provides: verbindliche Reihenfolge von Idee bis kontrollierter Evolution
Used By: CAWP, CDG, CDF, AGF, CAC, Release Integrity, Codex-Arbeitsregeln
Governed By: CMIBF
Layer: Normative Meta-Architecture / Governance
Status: Canonical

### CAWP

Depends On: CMIBF, AFP, CG, CDF, CDG, CKS
Provides: verbindliches Arbeitsverhalten fuer KI-Systeme, Kommunikationsregeln, Architekturdisziplin, Traceability, KI-Qualitaets-Gates
Used By: Codex, ChatGPT, lokale Modelle, Agentensysteme, zukuenftige KI-Systeme, Review- und Governance-Prozesse
Governed By: CMIBF, AFP
Layer: Governance / AI Working Protocol
Status: Canonical

### CAC

Depends On: CMIBF, AFP, CAWP, freigegebene Architekturdefinitionen
Provides: Syntaxanalyse, semantische Analyse, Regelvalidierung, Inkonsistenzpruefung, deterministische Ableitungen, Compliance- und Buildberichte
Used By: CAMap, Registries, Dependency Graphs, kanonische Artefakte, Release Integrity
Governed By: CMIBF, AFP, CAWP
Layer: Compilation / Governance
Status: Specified

### Canonical Layer

Depends On: CMIBF, Foundation
Provides: Canonical contracts, Registries, Policies
Used By: Operational Layer, Learning Layer, CAM, Release Integrity
Governed By: CMIBF, AFP, AGF, CDG
Layer: Canonical
Status: Canonical

### CLMSF

Depends On: CMIBF, AFP, CAWP, CPI, CAC, AGF, CDG, CDF, CCP-Policy, CAM, ALP, CADP, CIPL, Release Integrity; optionally consumes CAF identity and assurance references
Provides: Canonical licence identities, licence registry architecture, licence lifecycle, validation model, policy model, audit model, security and compliance model, export rules, extension points
Used By: Future Licence Manager, future Licence Validation Service, Governance, Release Integrity, CAM, Compliance reviews
Governed By: CMIBF, AFP, AGF, CDG, CCP-Policy
Layer: Canonical
Status: Canonical concept, architecture approved; implementation later

### Operational Layer

Depends On: Canonical Layer, Runtime Schema
Provides: Agents, Tools, GUI, Connectors
Used By: Orchestrator Core, Runtime
Governed By: Governance, Release Integrity
Layer: Operational
Status: Canonical

### Learning Layer

Depends On: Canonical Layer, Canonical Memory
Provides: Learning evidence, Reflection data, Chronicle references
Used By: CCP-Cognitive, Governance
Governed By: Governance, Foundation
Layer: Learning
Status: Canonical

### AGF

Depends On: CMIBF, AFP, Foundation
Provides: Architecture governance rules under CMIBF
Used By: CDG, CCP-Policy, Release Integrity
Governed By: CMIBF, Foundation
Layer: Governance
Status: Canonical

### CDG

Depends On: CMIBF, AFP, AGF, CIPL
Provides: Development rules
Used By: Future Codex orders, Governance
Governed By: CMIBF, AGF
Layer: Governance
Status: Canonical

### CAM

Depends On: ALP, CADP
Provides: Artifact classification, Storage governance
Used By: Release Integrity, Governance, CIPL
Governed By: AGF, CDG
Layer: Canonical
Status: Canonical, partially operationalized

### CADP

Depends On: CAM, ALP
Provides: Active directory purity rules
Used By: CAM, Release Integrity
Governed By: CCP-Policy, AGF
Layer: Governance
Status: Canonical

### ALP

Depends On: CAM
Provides: Artifact lifecycle rules
Used By: CADP, Release Integrity, CIPL
Governed By: AGF
Layer: Governance
Status: Canonical

### CIPL

Depends On: CDG, Creator Identity
Provides: IP and origin ledger
Used By: CG, CKS, Governance
Governed By: AGF, CDG
Layer: Governance
Status: Canonical

### CCP-Policy

Depends On: AGF, CDG
Provides: Controlled change policy
Used By: CADP, Governance, Release Integrity
Governed By: AGF
Layer: Governance
Status: Canonical

### CCP-Cognitive

Depends On: CLU, CRE, Execution Planner, Canonical Memory
Provides: Cognitive processing model
Used By: Phase 2 planning
Governed By: Governance, Foundation
Layer: Cognitive / Learning
Status: Canonical concept

### CLU

Depends On: Transformer-basierte Tokenisierung, CG
Provides: Language understanding concept
Used By: CCP-Cognitive, Execution Planner
Governed By: Governance
Layer: Cognitive
Status: Canonical concept

### CRE

Depends On: Capability Registry, Governance
Provides: Capability candidate resolution
Used By: Execution Planner, CCP-Cognitive
Governed By: Governance, Runtime Schema
Layer: Operational / Cognitive
Status: Canonical, implemented

### Execution Planner

Depends On: CRE, Runtime Schema
Provides: Validated execution plans
Used By: Orchestrator Core, CCP-Cognitive
Governed By: Governance, Release Integrity
Layer: Operational
Status: Canonical, implemented

### Orchestrator Core

Depends On: Execution Planner, Runtime Schema
Provides: Controlled execution
Used By: Operational runtime
Governed By: Release Integrity, Governance
Layer: Operational
Status: Canonical, implemented behind feature flag

### Runtime Schema

Depends On: Canonical Layer
Provides: Runtime contracts
Used By: Execution Planner, Orchestrator Core
Governed By: Release Integrity
Layer: Canonical / Operational
Status: Canonical, implemented

### Canonical Memory

Depends On: Foundation, Learning Layer
Provides: Continuity and memory evidence
Used By: CCP-Cognitive, Governance, CHI
Governed By: Foundation, Governance
Layer: Learning
Status: Canonical

### Release Integrity

Depends On: AGF, CAM, ALP, Runtime Schema
Provides: Release gates, Evidence checks
Used By: Governance, Phase transitions
Governed By: AGF
Layer: Governance
Status: Canonical, implemented

### CKS

Depends On: CG, CAMap, CDI, CHI
Provides: Knowledge Governance Layer, Canonical architecture knowledge structure
Used By: Governance, Phase 2 onboarding
Governed By: CDG, AGF
Layer: Knowledge Governance
Status: Canonical
