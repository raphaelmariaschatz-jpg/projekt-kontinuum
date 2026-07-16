# Canonical Glossary (CG) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: kanonisches Architektur-Glossar
Gueltig ab: 2026-07-09
Geltungsbereich: kanonische Begriffsverwendung in Projekt Kontinuum

## Zweck

Canonical Glossary (CG) 1.0 definiert die verbindliche Verwendung zentraler Architekturbegriffe von Projekt Kontinuum. Es ist eine reine Dokumentations- und Governance-Komponente und veraendert keine Runtime, keine Imports, keine APIs, keine Datenbanken und keine Architekturimplementierung.

## Begriffsregeln

- Abkuerzungen duerfen nicht mehrdeutig verwendet werden.
- Jeder kanonische Frameworkname und jede Abkuerzung duerfen innerhalb der Architektur nur genau einer Bedeutung zugeordnet sein. Bereits reservierte Bezeichnungen duerfen nicht erneut verwendet werden; bei semantischen Kollisionen ist ein neuer kanonischer Name festzulegen.
- `CVF` bleibt dauerhaft fuer das Canonical Vision Framework im Sinn von Computer Vision, visueller Wahrnehmung, Interpretation und Bildverarbeitung reserviert.
- `CPVF` bezeichnet eindeutig das Canonical Project Vision Framework fuer Projektvision, Mission und langfristige Orientierung.
- 'CCP-Policy' bezeichnet Canonical Change Policy.
- 'CCP-Cognitive' oder 'CCP-Cog' bezeichnet Canonical Cognitive Pipeline.
- 'CADP' bezeichnet im aktuellen kanonischen Projektstand Canonical Active Directory Policy.
- Inkonsistenzen werden dokumentiert, aber nicht durch CG 1.0 automatisch geaendert.

## Begriffe

### AFP - Canonical Architecture First Principle

Name: Canonical Architecture First Principle
Abkuerzung: AFP
Vollstaendige Bezeichnung: Canonical Architecture First Principle
Definition: Verbindliches Architekturprinzip, nach dem Architektur jeder Implementierung vorausgeht und jede Implementierung eine definierte, gepruefte und freigegebene CMIBF-Grundlage benoetigt.
Zweck: Verhindert Architekturentstehung im Code, konkurrierende Architekturwahrheiten und Implementierungen ohne kanonische Grundlage.
Architekturphase: dauerhafte Architektur- und Entwicklungsregel
Status: Canonical

Verantwortlichkeit:
- Reihenfolge von Idee bis kontrollierter Evolution festlegen
- Implementierung vor Architekturfreigabe verhindern
- AFP-Verletzungen als Architekturverletzungen klassifizieren

Verwandte Komponenten:
- CMIBF
- CAWP
- CAC
- CDG
- AGF

### CAWP - Canonical AI Working Protocol

Name: Canonical AI Working Protocol
Abkuerzung: CAWP
Vollstaendige Bezeichnung: Canonical AI Working Protocol 1.0
Definition: Verbindliches Arbeitsprotokoll fuer alle KI-Systeme, die an Projekt Kontinuum mitwirken.
Zweck: Definiert Arbeitsverhalten, Kommunikationsregeln, Architekturdisziplin, Traceability, Qualitaets-Gates und Fehlerkultur von KI-Systemen.
Architekturphase: Governance unterhalb AFP, vor CAC und Implementierung
Status: Canonical

Verantwortlichkeit:
- KI-Arbeitsverhalten verbindlich regeln
- Transparenz, Nachvollziehbarkeit und Qualitaet von KI-Arbeit sichern
- KI-Systeme auf CMIBF, AFP und CAC verpflichten

Verwandte Komponenten:
- CMIBF
- AFP
- CPI
- CAC
- CDG
- CDF

### CAWP-Verstoss - CAWP Violation

Name: CAWP-Verstoss
Abkuerzung: keine
Vollstaendige Bezeichnung: Canonical AI Working Protocol Violation
Definition: Abweichung vom verbindlichen Arbeitsprotokoll fuer KI-Systeme.
Zweck: Macht fehlerhaftes KI-Arbeitsverhalten governance-faehig, pruefbar und berichtbar.
Architekturphase: Analyse, Umsetzung, Review, Abschlussbericht, Governance
Status: Canonical

Verwandte Komponenten:
- CAWP
- CPI
- AFP
- Governance

### CPI - Continuous Process Improvement

Name: Continuous Process Improvement
Abkuerzung: CPI
Vollstaendige Bezeichnung: Continuous Process Improvement 2.0
Definition: Kanonisches Governance-Framework zur kontinuierlichen Verbesserung saemtlicher Arbeitsprozesse in Projekt Kontinuum.
Zweck: Sichert Canonical Improvement Lifecycle, Root-Cause-Analyse, Verbesserungsklassen, Priorisierung, Standardisierung, Automatisierungspruefung, Dokumentationspflicht, Wirksamkeitspruefung, Verbesserungshistorie und reproduzierbare Prozessverbesserung.
Architekturphase: Governance unterhalb CAWP, vor CAC
Status: Canonical

Verantwortlichkeit:
- wiederkehrende Probleme dauerhaft analysieren und beseitigen
- wiederkehrende Taetigkeiten standardisieren
- sinnvolle Automatisierung pruefen
- Prozessverbesserungen dokumentieren und governance-konform freigeben lassen

Verwandte Komponenten:
- CMIBF
- AFP
- CAWP
- CAC
- CDG
- CDF

### CIL - Canonical Improvement Lifecycle

Name: Canonical Improvement Lifecycle
Abkuerzung: CIL
Vollstaendige Bezeichnung: Canonical Improvement Lifecycle
Definition: Verbindlicher zehnphasiger CPI-Lebenszyklus von Observation, Root Cause Analysis, Improvement Proposal, Governance Review, Approval, Implementation, Validation, Effectiveness Review, Standardisation bis Knowledge Integration.
Zweck: Stellt sicher, dass Verbesserungen beobachtet, ursachenbezogen analysiert, vorgeschlagen, geprueft, freigegeben, validiert, wirksamkeitsgeprueft, standardisiert und dauerhaft ins Projektwissen integriert werden.
Architekturphase: Governance, Prozessverbesserung, kontrollierte Evolution
Status: Canonical

Verwandte Komponenten:
- CPI
- CAWP
- CMIBF
- Governance

### CPI-Vorschlag - CPI Proposal

Name: CPI-Vorschlag
Abkuerzung: keine
Vollstaendige Bezeichnung: Continuous Process Improvement Proposal
Definition: Nicht verbindlicher Vorschlag zur Verbesserung eines wiederkehrenden Arbeits-, Governance-, Architektur-, Dokumentations-, Review-, Freigabe-, Implementierungs-, KI-, Entwickler-, Kommunikations-, Wissensmanagement-, Qualitaetssicherungs-, Release-, Archivierungs-, Versionsmanagement- oder Projektorganisationsprozesses.
Zweck: Trennt Verbesserungserkenntnis von verbindlicher Governance-Freigabe.
Architekturphase: Prozessverbesserung, Review, Governance
Status: Canonical

Verwandte Komponenten:
- CPI
- CAWP
- Governance

### CPI-Verstoss - CPI Violation

Name: CPI-Verstoss
Abkuerzung: keine
Vollstaendige Bezeichnung: Continuous Process Improvement Violation
Definition: Abweichung von CPI-Regeln, insbesondere implizite Prozessaenderung, fehlende Dokumentation, fehlende Ursachenanalyse oder nicht freigegebene neue Arbeitsregel.
Zweck: Macht fehlerhafte Prozessverbesserung sichtbar, pruefbar und governance-faehig.
Architekturphase: Prozessverbesserung, Governance, Review
Status: Canonical

Verwandte Komponenten:
- CPI
- Governance
- Traceability

### CPI-Metrik - CPI Metric

Name: CPI-Metrik
Abkuerzung: keine
Vollstaendige Bezeichnung: Continuous Process Improvement Metric
Definition: Optionale Kennzahl zur Bewertung von Prozessqualitaet und Verbesserungswirkung, ohne Architekturentscheidungen zu ersetzen.
Zweck: Macht langfristige Qualitaetsentwicklung beobachtbar, etwa Fehlerwiederholung, Automatisierungsgrad, Dokumentationsvollstaendigkeit, Governance-Konsistenz, Review-Qualitaet, Bearbeitungsdauer oder Freigabezeit.
Architekturphase: Prozessverbesserung, Governance, Wirksamkeitspruefung
Status: Canonical

Verwandte Komponenten:
- CPI
- CIL
- Governance

### Root-Cause-Analyse - Root Cause Analysis

Name: Root-Cause-Analyse
Abkuerzung: RCA
Vollstaendige Bezeichnung: Root Cause Analysis
Definition: Ursachenanalyse mit dem Ziel, wiederkehrende Probleme dauerhaft zu beseitigen statt Symptome nur kurzfristig zu korrigieren.
Zweck: Grundlage fuer dauerhafte CPI-Verbesserungen.
Architekturphase: Prozessverbesserung, Fehlerkultur, Governance
Status: Canonical

Verwandte Komponenten:
- CPI
- CAWP

### KI-System - AI System

Name: KI-System
Abkuerzung: keine
Vollstaendige Bezeichnung: Kuenstliches Analyse-, Assistenz-, Entwicklungs-, Pruef- oder Agentensystem
Definition: System, das an Projekt Kontinuum analysierend, planend, dokumentierend, pruefend, implementierend oder koordinierend mitwirkt.
Zweck: Definiert den Geltungsbereich von CAWP hersteller- und modellunabhaengig.
Architekturphase: alle Phasen, soweit KI-Arbeit beteiligt ist
Status: Canonical

Verwandte Komponenten:
- CAWP
- Codex-Integration
- Agentensysteme

### Architekturautoritaet - Architecture Authority

Name: Architekturautoritaet
Abkuerzung: keine
Vollstaendige Bezeichnung: Normative Architekturautoritaet
Definition: Befugnis, Architektur fuer Projekt Kontinuum normativ zu definieren, zu aendern oder freizugeben.
Zweck: Klaert, dass ausschliesslich das CMIBF normative Architekturautoritaet besitzt.
Architekturphase: dauerhaft
Status: Canonical

Verantwortlichkeit:
- normative Quelle von abgeleiteten Artefakten unterscheiden
- Code, Tests, Konfigurationen, Reports und Registries als nicht-normativ einordnen

Verwandte Komponenten:
- CMIBF
- AFP

### Architekturverletzung - Architecture Violation

Name: Architekturverletzung
Abkuerzung: keine
Vollstaendige Bezeichnung: Architecture Violation
Definition: Zustand oder Aenderung, die gegen CMIBF, AFP, Governance-Regeln, Freigaben oder CAC-Validierung verstoesst.
Zweck: Macht unzulaessige Architektur- und Implementierungszustaende blockierbar.
Architekturphase: Validierung, Build, Release, Evolution
Status: Canonical

Verantwortlichkeit:
- Implementierung ohne CMIBF-Grundlage blockieren
- direkte Aenderung abgeleiteter Artefakte markieren
- Release bei widerspruechlichem Architekturstand verhindern

Verwandte Komponenten:
- CAC
- Governance
- Release Integrity

### Architektur-Gate - Architecture Gate

Name: Architektur-Gate
Abkuerzung: keine
Vollstaendige Bezeichnung: Architecture Gate
Definition: Verbindlicher Pruefpunkt im AFP-Zyklus, der vor Fortsetzung zur naechsten Phase bestanden sein muss.
Zweck: Sichert CMIBF-Abdeckung, Architekturpruefung, Freigabe, CAC-Validierung, Implementierungsvalidierung, Release-Konformitaet und kontrollierte Evolution.
Architekturphase: gesamter AFP-Zyklus
Status: Canonical

Verwandte Komponenten:
- AFP
- CAC
- Release Integrity

### Architekturfreigabe - Architecture Approval

Name: Architekturfreigabe
Abkuerzung: keine
Vollstaendige Bezeichnung: Architecture Approval
Definition: Dokumentierte Freigabe einer CMIBF-definierten Architekturgrundlage vor CAC-Verarbeitung und Implementierung.
Zweck: Verhindert technische Umsetzung ohne gepruefte Architekturentscheidung.
Architekturphase: vor CAC und Implementierung
Status: Canonical

Verwandte Komponenten:
- CMIBF
- AFP
- Governance

### Architekturanalyse - Architecture Analysis

Name: Architekturanalyse
Abkuerzung: keine
Vollstaendige Bezeichnung: Architecture Analysis
Definition: Pruefung einer Idee, Anforderung, Betriebsbeobachtung oder Evolutionsabsicht auf notwendige CMIBF-Definition, Abhaengigkeiten, Regeln, Risiken und Freigabebedarf.
Zweck: Startpunkt jeder kontrollierten Architektur- und Entwicklungsarbeit.
Architekturphase: AFP-Phase vor CMIBF-Definition oder CMIBF-Erweiterung
Status: Canonical

Verwandte Komponenten:
- AFP
- CMIBF
- CDG

### CMIBF - Canonical Master Implementation Blueprint Framework

Name: Canonical Master Implementation Blueprint Framework
Abkuerzung: CMIBF
Vollstaendige Bezeichnung: Canonical Master Implementation Blueprint Framework 1.0
Definition: Einzige normative Architekturquelle und Architekturverfassung von Projekt Kontinuum.
Zweck: Definiert, aendert, erweitert und legitimiert Architektur ausschliesslich an einer kanonischen Stelle.
Architekturphase: dauerhaft
Status: Canonical

Verantwortlichkeit:
- Architektur definieren
- Architekturentscheidungen freigeben
- Grundlage fuer CAC-Ableitungen bereitstellen

Verwandte Komponenten:
- AFP
- CAC
- AGF
- CDG

### CAC - Canonical Architecture Compiler

Name: Canonical Architecture Compiler
Abkuerzung: CAC
Vollstaendige Bezeichnung: Canonical Architecture Compiler
Definition: Pruefender und deterministisch ableitender Compiler fuer das CMIBF-Quellmodell.
Zweck: Analysiert Syntax und Semantik, validiert Regeln, erkennt Inkonsistenzen und erzeugt ausschliesslich deterministische Ableitungen.
Architekturphase: nach Architekturfreigabe, vor Artefakten und Implementierung
Status: Specified

Verantwortlichkeit:
- CMIBF lesen und interpretieren
- AFP-Verletzungen erkennen
- ungueltige Architekturzustaende und Builds ablehnen

Verwandte Komponenten:
- CMIBF
- AFP
- Compliance

### Kanonisches Artefakt - Canonical Artifact

Name: Kanonisches Artefakt
Abkuerzung: keine
Vollstaendige Bezeichnung: Canonical Artifact
Definition: Eindeutig identifiziertes Artefakt mit kanonischem Zweck, Status, Herkunft und Governance-Kontext.
Zweck: Macht Dokumente, Modelle, Reports und Implementierungsbelege rueckverfolgbar.
Architekturphase: alle Phasen
Status: Canonical

Verwandte Komponenten:
- CAM
- ALP
- CMIBF

### Abgeleitetes Artefakt - Derived Artifact

Name: Abgeleitetes Artefakt
Abkuerzung: keine
Vollstaendige Bezeichnung: Derived Artifact
Definition: Aus dem CMIBF durch den CAC oder einen freigegebenen Ableitungsprozess erzeugtes Artefakt ohne eigenstaendige normative Architekturautoritaet.
Zweck: Trennt reproduzierbare Ableitungen von der editierbaren Architekturquelle.
Architekturphase: nach CAC-Verarbeitung
Status: Canonical

Verantwortlichkeit:
- nicht manuell als Architekturquelle bearbeiten
- Herkunft und CMIBF-Referenz bewahren

Verwandte Komponenten:
- CAC
- CMIBF
- Traceability

### Normative Architekturquelle - Normative Architecture Source

Name: Normative Architekturquelle
Abkuerzung: keine
Vollstaendige Bezeichnung: Normative Architecture Source
Definition: Quelle mit verbindlicher Autoritaet fuer Architekturdefinitionen. In Projekt Kontinuum ist dies ausschliesslich das CMIBF.
Zweck: Verhindert konkurrierende Architekturwahrheiten.
Architekturphase: dauerhaft
Status: Canonical

### Deterministische Ableitung - Deterministic Derivation

Name: Deterministische Ableitung
Abkuerzung: keine
Vollstaendige Bezeichnung: Deterministic Derivation
Definition: Reproduzierbare Erzeugung gleicher Artefakte aus gleicher freigegebener CMIBF-Quelle und gleicher Compiler-Version.
Zweck: Sichert Pruefbarkeit, Build-Stabilitaet und Auditierbarkeit.
Architekturphase: CAC, Build, Release
Status: Canonical

### Kontrollierte Evolution - Controlled Evolution

Name: Kontrollierte Evolution
Abkuerzung: keine
Vollstaendige Bezeichnung: Controlled Evolution
Definition: Weiterentwicklung, die erneut mit Architekturanalyse beginnt und den vollstaendigen AFP-Zyklus durchlaeuft.
Zweck: Verhindert direkte Codeaenderungen aus Betrieb, Monitoring oder Implementierungsdruck.
Architekturphase: Betrieb, Monitoring, Evolution
Status: Canonical

### Implementierungsautoritaet - Implementation Authority

Name: Implementierungsautoritaet
Abkuerzung: keine
Vollstaendige Bezeichnung: Implementation Authority
Definition: Befugnis, eine freigegebene Architektur technisch umzusetzen, ohne dabei Architektur normativ zu definieren oder zu veraendern.
Zweck: Trennt Ausfuehrung von Architekturautoritaet.
Architekturphase: Implementierung
Status: Canonical

### Traceability - Rueckverfolgbarkeit

Name: Traceability
Abkuerzung: keine
Vollstaendige Bezeichnung: Rueckverfolgbarkeit
Definition: Nachweisbare Kette von Idee, Architekturanalyse, CMIBF-Regel, Freigabe, CAC-Ableitung, Artefakt, Implementierung, Test, Release, Monitoring und Evolutionsentscheidung.
Zweck: Macht jede Implementierung auf eine freigegebene CMIBF-Grundlage zurueckfuehrbar.
Architekturphase: alle Phasen
Status: Canonical

### Compliance-Verweigerung - Compliance Refusal

Name: Compliance-Verweigerung
Abkuerzung: keine
Vollstaendige Bezeichnung: Compliance Refusal
Definition: Dokumentierte Ablehnung einer Validierung oder Zertifizierung wegen CMIBF-, AFP-, Regel-, Traceability- oder Konsistenzverstoss.
Zweck: Verhindert scheinbare Konformitaet bei ungueltigem Architekturstand.
Architekturphase: Validierung, Compliance, Release
Status: Canonical

### Build-Verweigerung - Build Refusal

Name: Build-Verweigerung
Abkuerzung: keine
Vollstaendige Bezeichnung: Build Refusal
Definition: Ablehnung eines Architektur-Builds oder einer Artefaktableitung durch den CAC bei fehlender CMIBF-Grundlage, fehlender Freigabe, Inkonsistenz, nicht deterministischer Ableitung oder AFP-Verstoss.
Zweck: Blockiert ungueltige Architekturzustaende vor Implementierung, Release oder Betrieb.
Architekturphase: CAC, Build, Release
Status: Canonical

### Foundation - Foundation

Name: Foundation
Abkuerzung: Foundation
Vollstaendige Bezeichnung: Foundation
Definition: Hoeschste Schutz- und Prinzipienschicht fuer Identitaet, Leitprinzipien, geschuetzte Regeln und grundlegende Entscheidungsgrenzen.
Zweck: Schuetzt den Kern der Architektur und begrenzt zulaessige Entscheidungen.
Architekturphase: Phase 1 - Architekturentwicklung; dauerhaft gueltig in Phase 2
Status: Canonical

Verantwortlichkeit:
- Foundation-Regeln schuetzen
- Identitaet und Leitprinzipien begrenzen
- Kompatibilitaet fuer Architekturentscheidungen pruefen

Verwandte Komponenten:
- Canonical Layer
- AGF
- CDG
- Governance
- Canonical Memory

### Canonical Layer - Canonical Layer

Name: Canonical Layer
Abkuerzung: Canonical Layer
Vollstaendige Bezeichnung: Canonical Layer
Definition: Systemweit verbindliche Struktur-, Vertrags-, Registry- und Policy-Schicht.
Zweck: Stellt stabile kanonische Ordnungs- und Vertragsgrundlagen bereit.
Architekturphase: Phase 1; Grundlage fuer Phase 2
Status: Canonical

Verantwortlichkeit:
- Projektstruktur definieren
- Architekturmodell und Manifeste fuehren
- API-/Daten-/Artefaktvertraege stabilisieren

Verwandte Komponenten:
- Foundation
- Operational Layer
- Learning Layer
- CAM
- Release Integrity

### Operational Layer - Operational Layer

Name: Operational Layer
Abkuerzung: Operational Layer
Vollstaendige Bezeichnung: Operational Layer
Definition: Austauschbare Implementierungsschicht unter stabilen kanonischen Vertraegen.
Zweck: Betreibt konkrete Agenten, Tools, GUI- und Connector-Funktionen.
Architekturphase: Phase 1 definiert; Phase 2 kontrolliert integriert
Status: Canonical

Verantwortlichkeit:
- Agenten, Tools, GUI und Connectoren betreiben
- Vertraege einhalten
- Runtime-Faehigkeiten bereitstellen

Verwandte Komponenten:
- Canonical Layer
- Orchestrator Core
- Runtime Schema
- Governance

### Learning Layer - Learning Layer

Name: Learning Layer
Abkuerzung: Learning Layer
Vollstaendige Bezeichnung: Learning Layer
Definition: Dynamische, provenienz- und auditpflichtige Wissens-, Chronik-, Lern- und Review-Bereiche.
Zweck: Fuehrt lern- und erfahrungsbezogene Informationen ohne automatische Kanon-Uebernahme.
Architekturphase: Phase 1 definiert; Phase 2 erweitert kontrolliert
Status: Canonical

Verantwortlichkeit:
- Lern- und Review-Daten fuehren
- Provenienz und Auditierbarkeit sichern
- Keine automatische Kanon-Uebernahme ohne Review

Verwandte Komponenten:
- Canonical Memory
- Learning / Reflection
- Governance
- Release Integrity

### AGF - Architecture Governance Framework 1.0

Name: Architecture Governance Framework
Abkuerzung: AGF
Vollstaendige Bezeichnung: Architecture Governance Framework 1.0
Definition: Governance-Richtlinie fuer Architekturentscheidungen unterhalb des CMIBF.
Zweck: Definiert Governance-Rollen, Aenderungsgrenzen und Architekturverbindlichkeit, ohne die Architekturverfassung des CMIBF zu ersetzen.
Architekturphase: Phase 1 Abschluss
Status: Canonical

Verantwortlichkeit:
- Architekturrollen definieren
- Aenderungsregeln festlegen
- Governance- und Release-Grenzen beschreiben

Verwandte Komponenten:
- CDG
- Foundation
- CAM
- Release Integrity

### CDG - Canonical Development Governance 1.0

Name: Canonical Development Governance
Abkuerzung: CDG
Vollstaendige Bezeichnung: Canonical Development Governance 1.0
Definition: Kanonisches Entwicklungsregelwerk fuer zukuenftige Codex-Auftraege.
Zweck: Macht Entwicklungsauftraege regelgebunden, nachvollziehbar und pruefbar.
Architekturphase: Phase 1 Abschluss / Phase 2 Vorbereitung
Status: Canonical

Verantwortlichkeit:
- Entwicklungsregeln klassifizieren
- Regel-IDs fuehren
- Fortschreibungsregeln definieren

Verwandte Komponenten:
- AGF
- CIPL
- Governance
- Release Integrity

### CAM - Canonical Artifact Manager

Name: Canonical Artifact Manager
Abkuerzung: CAM
Vollstaendige Bezeichnung: Canonical Artifact Manager
Definition: Kanonische Verwaltung von Artefakten, Speicherorten, Lifecycle und Konflikten.
Zweck: Ordnet Dokumente, Konfigurationen und Nachweise innerhalb der Projektstruktur.
Architekturphase: Phase 1
Status: Canonical, teilweise operationalisiert

Verantwortlichkeit:
- Artefakte klassifizieren
- Kanonischen Zweck und Speicherort pruefen
- Archivierungs- und Referenzpruefungen vorbereiten

Verwandte Komponenten:
- ALP
- CADP
- Release Integrity
- Canonical Layer

### CADP - Canonical Active Directory Policy 1.0

Name: Canonical Active Directory Policy
Abkuerzung: CADP
Vollstaendige Bezeichnung: Canonical Active Directory Policy 1.0
Definition: Policy fuer kanonisch reine aktive Projektordner.
Zweck: Verhindert historische Parallelstaende in aktiven Arbeitsordnern.
Architekturphase: Phase 1
Status: Canonical

Verantwortlichkeit:
- Aktive Ordner von historischen Parallelstaenden freihalten
- Archivpflicht fuer ersetzte Artefakte definieren
- Referenzpruefung nach Verschiebungen fordern

Verwandte Komponenten:
- CAM
- ALP
- CCP-Policy
- Release Integrity

### ALP - Artifact Lifecycle Policy 2.0

Name: Artifact Lifecycle Policy
Abkuerzung: ALP
Vollstaendige Bezeichnung: Artifact Lifecycle Policy 2.0
Definition: Verbindlicher Lebenszyklus fuer Projektartefakte.
Zweck: Regelt Erstellung, Ablage, Archivierung und Freigabe von Artefakten.
Architekturphase: Phase 1
Status: Canonical

Verantwortlichkeit:
- Artefaktklassen definieren
- Archivierung statt Loeschung festlegen
- Release- und Evidence-Regeln unterstuetzen

Verwandte Komponenten:
- CAM
- CADP
- Release Integrity
- Artifact Lifecycle Migration Plan

### CIPL - Canonical Intellectual Property Ledger 1.0

Name: Canonical Intellectual Property Ledger
Abkuerzung: CIPL
Vollstaendige Bezeichnung: Canonical Intellectual Property Ledger 1.0
Definition: Kanonisches Herkunfts- und Urheberregister fuer Architekturentscheidungen, Konzepte und Kernartefakte.
Zweck: Dokumentiert Herkunft, Schoepferbezug und IP-Grenzen zentraler Architekturartefakte.
Architekturphase: Phase 1 Abschluss
Status: Canonical

Verantwortlichkeit:
- Creator Identity referenzieren
- Herkunftsdaten vorbereiten
- Git- und Chronikreferenzen dokumentarisch ermoeglichen

Verwandte Komponenten:
- CDG
- CG
- Project Chronicle
- Governance

### CCP-Policy - Canonical Change Policy 1.0

Name: Canonical Change Policy
Abkuerzung: CCP-Policy
Vollstaendige Bezeichnung: Canonical Change Policy 1.0
Definition: Policy fuer kontrollierte kanonische Aenderungen.
Zweck: Sichert, dass Kanon-Aenderungen review-, dokumentations- und releasepflichtig bleiben.
Architekturphase: Phase 1
Status: Canonical

Verantwortlichkeit:
- Change Proposal verlangen
- Pre-Audit und Governance Review fordern
- Documentation Sync und Release Gate in Aenderungen einbinden

Verwandte Komponenten:
- CADP
- AGF
- CDG
- Release Integrity

### CCP-Cognitive / CCP-Cog - Canonical Cognitive Pipeline

Name: Canonical Cognitive Pipeline
Abkuerzung: CCP-Cognitive / CCP-Cog
Vollstaendige Bezeichnung: Canonical Cognitive Pipeline
Definition: Kuenftige kanonische Denk- und Verarbeitungsstruktur von K.
Zweck: Ordnet kognitive Verarbeitung von Wahrnehmung bis Lernen fuer Phase 2.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Canonical concept, implementation open

Verantwortlichkeit:
- Wahrnehmen, Verstehen, Denken, Planen, Handeln, Pruefen, Erinnern und Lernen einordnen
- CRE, Planner, Governance, Orchestrator, Review und Memory in einen kognitiven Ablauf integrieren
- Neue Faehigkeiten kognitiv einordnen

Verwandte Komponenten:
- CLU
- CRE
- Execution Planner
- Orchestrator Core
- Canonical Memory
- Learning / Reflection

### CLU - Canonical Language Understanding

Name: Canonical Language Understanding
Abkuerzung: CLU
Vollstaendige Bezeichnung: Canonical Language Understanding
Definition: Kanonische Sprachverstehensschicht fuer semantische und intentionale Einordnung.
Zweck: Bereitet natuerliche Sprache fuer kontrollierte Planung und Ausfuehrung auf.
Architekturphase: Phase 2
Status: Canonical concept, implementation open

Verantwortlichkeit:
- Intentionen und Bedeutungen erfassen
- Sprachverstehen in CCP-Cognitive einordnen
- Keine eigenstaendige Ausfuehrung ohne Governance ableiten

Verwandte Komponenten:
- CCP-Cognitive
- CRE
- Execution Planner
- Transformer-basierte Tokenisierung

### CRE - Capability Resolution Engine

Name: Capability Resolution Engine
Abkuerzung: CRE
Vollstaendige Bezeichnung: Capability Resolution Engine
Definition: Read-only Capability Resolution fuer Faehigkeitsfindung und Kandidatenauswahl.
Zweck: Findet passende Faehigkeiten, ohne selbst auszufuehren.
Architekturphase: Phase 2 vorbereitet / Runtime-Migration dokumentiert
Status: Canonical, implemented

Verantwortlichkeit:
- Capability Discovery
- Priorisierung
- Candidate Selection

Verwandte Komponenten:
- Execution Planner
- Governance
- CCP-Cognitive
- CLU

### Execution Planner - Execution Planner 1.0

Name: Execution Planner
Abkuerzung: Execution Planner
Vollstaendige Bezeichnung: Execution Planner 1.0
Definition: Planungsschicht fuer ausfuehrbare Schritte aus validierten Faehigkeiten.
Zweck: Erstellt kontrollierte Ausfuehrungsplaene unter bestehenden Architekturgrenzen.
Architekturphase: Phase 2 vorbereitet / Runtime-Migration dokumentiert
Status: Canonical, implemented

Verantwortlichkeit:
- Faehigkeitskandidaten in Schritte uebersetzen
- Planstatus vergeben
- Orchestrator-faehige Plaene bereitstellen

Verwandte Komponenten:
- CRE
- Orchestrator Core
- Runtime Schema
- CCP-Cognitive

### Orchestrator Core - Orchestrator Core 1.0

Name: Orchestrator Core
Abkuerzung: Orchestrator Core
Vollstaendige Bezeichnung: Orchestrator Core 1.0
Definition: Kontrollierte Ausfuehrungsschicht fuer validierte Plaene.
Zweck: Fuehrt nur gepruefte Plaene aus und plant nicht eigenstaendig.
Architekturphase: Phase 2 vorbereitet / Runtime-Migration dokumentiert
Status: Canonical, implemented behind feature flag

Verantwortlichkeit:
- Validierte Plaene ausfuehren
- Fallbacks einhalten
- Keine CRE- oder Planner-Rolle uebernehmen

Verwandte Komponenten:
- Execution Planner
- Runtime Schema
- Operational Layer
- Release Integrity

### Runtime Schema - Orchestrator Runtime Schema 34.1

Name: Runtime Schema
Abkuerzung: Runtime Schema
Vollstaendige Bezeichnung: Orchestrator Runtime Schema 34.1
Definition: Schema- und Vertragsgrundlage fuer Orchestrator-Laufzeitplaene.
Zweck: Definiert pruefbare Struktur fuer Plan- und Ausfuehrungsdaten.
Architekturphase: Phase 2 vorbereitet / Runtime-Migration dokumentiert
Status: Canonical, implemented

Verantwortlichkeit:
- Planstruktur festlegen
- Validierung ermoeglichen
- Orchestrator-Vertraege stabilisieren

Verwandte Komponenten:
- Execution Planner
- Orchestrator Core
- Operational Layer

### CMM - Canonical Memory

Name: Canonical Memory
Abkuerzung: CMM
Vollstaendige Bezeichnung: Canonical Memory
Definition: Kanonisch geschuetzter Erinnerungs- und Nachweisbereich.
Zweck: Bewahrt stabile, pruefbare Erinnerungs- und Kontinuitaetsinformationen.
Architekturphase: Phase 1 / Phase 2
Status: Canonical

Verantwortlichkeit:
- Memory-Regeln einhalten
- Nachvollziehbarkeit sichern
- Learning Layer begrenzen

Verwandte Komponenten:
- Foundation
- Learning Layer
- CCP-Cognitive
- Project Chronicle

### Governance - Canonical Governance

Name: Governance
Abkuerzung: Governance
Vollstaendige Bezeichnung: Canonical Governance
Definition: Gesamtheit der Regeln, Reviews, Gates und Verbindlichkeitsmechanismen.
Zweck: Haelt Architektur, Dokumentation und Entwicklung kontrolliert zusammen.
Architekturphase: Phase 1 Abschluss; Phase 2 dauerhaft
Status: Canonical

Verantwortlichkeit:
- Regelkonformitaet pruefen
- Aenderungs- und Release-Gates fuehren
- Inkonsistenzen dokumentieren

Verwandte Komponenten:
- AGF
- CDG
- CCP-Policy
- Release Integrity
- CKS

### Release Integrity - Release Integrity Framework

Name: Release Integrity
Abkuerzung: Release Integrity
Vollstaendige Bezeichnung: Release Integrity Framework
Definition: Releasebezogene Integritaets- und Evidenzpruefung.
Zweck: Sichert, dass Releases nur mit pruefbaren Nachweisen freigegeben werden.
Architekturphase: Phase 1 / Release 34.1
Status: Canonical, implemented

Verantwortlichkeit:
- Release-Gates pruefen
- Evidence dokumentieren
- Regressionen und Risiken sichtbar machen

Verwandte Komponenten:
- AGF
- CAM
- ALP
- Governance

### Transformer / Tokenisierung - Transformer-basierte Tokenisierung

Name: Transformer-basierte Tokenisierung
Abkuerzung: Transformer / Tokenisierung
Vollstaendige Bezeichnung: Transformer-basierte Tokenisierung
Definition: Konzeptioneller Mechanismus fuer kuenftige semantische Sprachvorverarbeitung.
Zweck: Ermoeglicht spaetere CLU- und CCP-Cognitive-Anbindung ohne aktuelle Implementierung.
Architekturphase: Phase 2 Konzept
Status: Canonical concept, implementation open

Verantwortlichkeit:
- Sprachsegmente strukturieren
- Semantische Vorverarbeitung konzeptionell einordnen
- Keine Runtime-Aenderung in CKS 1.0 ableiten

Verwandte Komponenten:
- CLU
- CCP-Cognitive
- Execution Planner

### CG - Canonical Glossary 1.0

Name: Canonical Glossary
Abkuerzung: CG
Vollstaendige Bezeichnung: Canonical Glossary 1.0
Definition: Kanonisches Architektur-Glossar fuer Begriffe und Abkuerzungen.
Zweck: Stellt einheitliche Sprache fuer Architekturwissen bereit.
Architekturphase: Phase 2 Vorbereitung
Status: Canonical

Verantwortlichkeit:
- Begriffe definieren
- Abkuerzungen disambiguieren
- verwandte Komponenten dokumentieren

Verwandte Komponenten:
- CKS
- CAMap
- CDI
- CHI
- CIPL

### CKS - Canonical Knowledge System 1.0

Name: Canonical Knowledge System
Abkuerzung: CKS
Vollstaendige Bezeichnung: Canonical Knowledge System 1.0
Definition: Knowledge Governance Layer fuer Wissen ueber die Architektur.
Zweck: Regelt Architekturwissen ueber Glossar, Architekturkarte, Entscheidungsindex und Historienindex.
Architekturphase: Phase 2 Vorbereitung
Status: Canonical

Verantwortlichkeit:
- Architekturwissen strukturieren
- Wissensartefakte verbinden
- Inkonsistenzen nur dokumentieren
- Knowledge Governance von Architektur- und Entwicklungsgovernance abgrenzen

Verwandte Komponenten:
- CG
- CAMap
- CDI
- CHI
- Governance
- AGF
- CDG
### CDF - Canonical Development Framework 1.0

Name: Canonical Development Framework
Abkuerzung: CDF
Vollstaendige Bezeichnung: Canonical Development Framework 1.0
Definition: Kanonischer Entwicklungsrahmen fuer die praktische Anwendung von Entwicklungs-, Architektur- und Wissensgovernance.
Zweck: Beschreibt, wie Entwicklungsarbeit in Orientierung, Konsistenzpruefung, Einordnung, Umsetzung und Abschlusspruefung ablaeuft.
Architekturphase: Phase 2 Vorbereitung
Status: Canonical

Verantwortlichkeit:
- CDG-Regeln in Arbeitsphasen uebersetzen
- Entwicklungsauftraege methodisch strukturieren
- Abschlusspruefungen und Wiedereinstiegspunkte absichern

Verwandte Komponenten:
- CDG
- AGF
- CKS
- Release Integrity
- CAM

### CRL - Canonical Reflective Layer 1.0

Name: Canonical Reflective Layer
Abkuerzung: CRL
Vollstaendige Bezeichnung: Canonical Reflective Layer 1.0
Definition: Dokumentarische Metaebene fuer evidenzgebundene Reflexion ueber die eigene Architektur- und Projektentwicklung von K.
Zweck: Ermoeglicht Selbstmodellierung, Entwicklungsanalyse, Architekturreflexion, Mustererkennung und Verbesserungsvorschlaege ausschliesslich anhand dokumentierter Fakten.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Canonical documentation and governance addition

Verantwortlichkeit:
- Entwicklung anhand dokumentierter Quellen beobachten
- Architekturhistorie und Entscheidungen vergleichen
- Muster und korrigierte Annahmen evidenzgebunden sichtbar machen
- Verbesserungsvorschlaege ohne Runtime-Wirkung formulieren
- Bewusstseins-, Erlebnis- und Freiwillensbehauptungen ausschliessen

Verwandte Komponenten:
- CCP-Cognitive
- CKS
- CG
- CAMap
- CDI
- CHI
- AGF
- CDG
- CDF
- CIPL
- Release Integrity
- Project Chronicle
- Roadmap

### MR - Meta-Reasoning 1.0

Name: Meta-Reasoning
Abkuerzung: MR
Vollstaendige Bezeichnung: Meta-Reasoning 1.0
Definition: Pruefende Reasoning-Review-Schicht fuer Schlussfolgerungen, Annahmen, Alternativen, Confidence und Governance-Konformitaet.
Zweck: Macht Denk- und Entscheidungswege nachvollziehbarer, ohne Bewusstsein, Selbstmodifikation oder Runtime-Automatik einzufuehren.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Concept reviewed, implementation later

Verantwortlichkeit:
- Schlussfolgerungen pruefen
- Annahmen sichtbar machen
- Confidence einschaetzen
- Alternativen und verworfene Pfade dokumentieren
- Governance-Bezug markieren
- Revisionsbedarf ausweisen

Verwandte Komponenten:
- Foundation
- Foundation Reasoning
- Query System
- CRE
- Execution Planner
- Orchestrator Core
- CDF
- CDG
- CAM
- ALP
- Release Integrity
- CRL
- CCP-Cognitive



### CEF - Canonical Enterprise Framework 1.0

Name: Canonical Enterprise Framework
Abkuerzung: CEF
Vollstaendige Bezeichnung: Canonical Enterprise Framework 1.0
Definition: Kanonischer Bezugsrahmen fuer den universellen Aufbau eines Unternehmens als System aus Menschen, Ressourcen, Wissen, Prozessen, Entscheidungen und Zielen.
Zweck: Definiert Unternehmensdimensionen, Beziehungen und Informationsfluesse, ohne ERP-, CRM-, BPM-, DMS-, Finanz- oder Buchhaltungsfunktionen zu implementieren.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Concept reviewed, implementation later

Verantwortlichkeit:
- Unternehmensdimensionen definieren
- Beziehungen und Informationsfluesse beschreiben
- CEF von ERP, CRM, BPM, DMS und BI abgrenzen
- spaetere Unternehmensanalyse, Beratung und Simulation vorbereiten
- Datenschutz-, Rollen- und Governance-Grenzen fuer spaetere Operationalisierung vormerken

Verwandte Komponenten:
- CMIBF
- CPVF
- CIF
- CCP-Cognitive
- CAICF
- CMLF
- Learning Layer
- CRE
- Execution Planner
- Orchestrator Core
- Canonical Memory
- CAM
- ALP
- CDF
- CDG
- Release Integrity

### CMLF - Canonical Media Learning Framework 1.0

Name: Canonical Media Learning Framework
Abkuerzung: CMLF
Vollstaendige Bezeichnung: Canonical Media Learning Framework 1.0
Definition: Kanonischer Medien- und Vermittlungsrahmen fuer Lernmedien, Darstellungsformen und Lernmethoden in Projekt Kontinuum.
Zweck: Definiert, welche Medienformen Wissen und Kompetenzen vermitteln koennen, wie Medien kombiniert werden duerfen und welche Kriterien spaetere adaptive Medienempfehlungen beachten muessen.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Concept reviewed, implementation later

Verantwortlichkeit:
- Medienbereiche definieren
- adaptive Medienauswahl vorbereiten
- CMLF von CAICF, CCP-Cognitive und CVF abgrenzen
- Ueberforderung durch Medienvielfalt vermeiden
- spaetere Tutor- und Education-Schnittstellen vorbereiten

Verwandte Komponenten:
- CPVF
- CIF
- CCP-Cognitive
- CAICF
- CVF
- Learning Agent
- CLG
- Canonical Memory
- Tutor / Education
- Governance
- Release Integrity

### CPVF - Canonical Project Vision Framework 1.0

Name: Canonical Project Vision Framework
Abkuerzung: CPVF
Vollstaendige Bezeichnung: Canonical Project Vision Framework 1.0
Definition: Kanonischer Vision-, Mission- und Orientierungsrahmen fuer den langfristigen Zweck von Projekt Kontinuum.
Zweck: Bestaetigt die Projektvision, grenzt sie von Foundation, Governance, CIF und dem fuer Computer Vision reservierten CVF ab und richtet kuenftige Entwicklung an Lernen, Verantwortung, Transparenz und nachhaltiger Architektur aus.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Concept reviewed, canonical naming confirmed, implementation later

Verantwortlichkeit:
- Projektvision definieren
- Mission und Leitprinzipien dokumentieren
- langfristige Orientierung bereitstellen
- CVF-Namenskollision vermeiden
- technische Operationalisierung fuer spaetere Freigabe vormerken

Verwandte Komponenten:
- CMIBF
- Canonical Glossary
- Foundation
- Governance
- CIF
- CCP-Cognitive
- CAICF
- CRL
- Meta-Reasoning

### CAICF - Canonical AI Competency Framework 1.0

Name: Canonical AI Competency Framework
Abkuerzung: CAICF
Vollstaendige Bezeichnung: Canonical AI Competency Framework 1.0
Definition: Kanonischer Kompetenzrahmen fuer den verantwortungsvollen, kritischen, kreativen und gestaltenden Umgang mit Kuenstlicher Intelligenz.
Zweck: Definiert Kompetenzbereiche und Bewertungsdimensionen fuer Lernpfade, Kompetenzentwicklung, adaptive Lernempfehlungen, Aufgabenplanung, Kompetenzbewertung sowie Tutor- und Education-Funktionen.
Architekturphase: Phase 2 - Controlled Integration, Operation & Cognitive Evolution
Status: Concept reviewed, implementation later

Verantwortlichkeit:
- Engage with AI definieren
- Create with AI definieren
- Manage AI definieren
- Design AI definieren
- Knowledge, Skills und Attitudes als Bewertungsdimensionen fuehren
- Kompetenzaufbau am individuellen Wissensstand ausrichten

Verwandte Komponenten:
- Canonical Learning Layer
- CCP-Cognitive
- CRE
- Execution Planner
- Orchestrator Core
- Learning Agent
- Canonical Memory
- Governance
- Foundation
- CRL
- Meta-Reasoning

### CLMSF - Canonical Licence Management System Framework

Name: Canonical Licence Management System Framework
Abkuerzung: CLMSF
Vollstaendige Bezeichnung: Canonical Licence Management System Framework 1.0
Definition: Kanonisches Architekturframework fuer zukuenftige Lizenzmechanismen in Projekt Kontinuum. CLMSF definiert Lizenzidentitaeten, Registry, Lifecycle, Validierungsmodell, Policies, Audit, Sicherheit, Compliance, Export und Erweiterungspunkte, ohne produktive Lizenzlogik zu implementieren.
Zweck: Schafft eine stabile Architekturgrundlage fuer spaetere Lizenzmanager, Lizenzvalidierungsdienste und Compliance-Prozesse, ohne CAF, CIPL, CAM oder Release Integrity zu ersetzen.
Architekturphase: Canonical Layer, Architektur- und Governance-Konzept vor Implementierung
Status: Canonical concept, Architekturfreigabe GO; Implementierung spaeter

Verantwortlichkeit:
- Lizenzarchitektur kanonisch definieren
- Lizenzidentitaet, licensed_subject, Lizenzprofile und Licence Assurance Level vorbereiten
- Lizenzierung strikt von Authentisierung, IP-Herkunft, Artefaktverwaltung und Runtime-Entscheidung trennen
- Erweiterungspunkte fuer spaetere Lizenzserver, Offline-Lizenzen, Unternehmens-, Forschungs- und Privatlizenzen beschreiben

Verwandte Komponenten:
- CMIBF
- CAF
- CIPL
- CAM
- CCP-Policy
- Release Integrity

### CODEAF - Canonical Code Agent Framework

Name: Canonical Code Agent Framework
Abkuerzung: CODEAF
Vollstaendige Bezeichnung: Canonical Code Agent Framework 1.0
Definition: Normative Agenten-Governance- und Kontrollschicht fuer Code-Agentenarbeit in Projekt Kontinuum. CODEAF definiert, wie Code-Agenten identifiziert, beauftragt, rollenbezogen begrenzt, capability- und permissionbezogen kontrolliert, risikoklassifiziert, auditiert und freigegeben werden.
Zweck: Verhindert, dass Code-Agenten allein aufgrund technischer Faehigkeiten handeln. CODEAF verbindet Auftrag, Agentenidentitaet, Rolle, Capability, Permission, Scope, Risiko, Gate, Audit und Freigabe, ohne selbst Agent, Registry, Planner, Orchestrator oder Runtime zu sein.
Architekturphase: Agent Governance / Architektur- und Governance-Konzept vor Implementierung
Status: Concept complete, Architecture Review completed with conditions; Implementierung spaeter nur nach ausdruecklicher Freigabe

Namensregel:
- `CODEAF` ist die kanonische Abkuerzung gemaess CMIBF-Framework-Registry `PK-FW-AGENT-005`.
- `CCAF` war ein Arbeitsname des Pruefauftrags und wird nicht als konkurrierende kanonische Benennung gefuehrt.

Verantwortlichkeit:
- kanonische Code-Agentenidentitaet definieren
- Canonical Agent Task definieren
- Rollen und Verantwortungsbereiche fuer Code-Agenten festlegen
- Capability und Permission trennen
- deny-by-default fuer nicht ausdruecklich erlaubte Aktionen festschreiben
- Read-only-, Write-, Execute- und Administrative-Grenzen definieren
- Risiko- und Vertrauensklassen definieren
- Freigabe-, Eskalations- und Kontroll-Gates definieren
- Delegation und Unteragenten begrenzen
- Laufzeitgrenzen und Abbruchbedingungen definieren
- Audit-, Provenienz- und Berichtspflichten definieren
- Konfliktregeln zwischen Beschreibung, Registry, Permission Profile und Runtime-Konfiguration festlegen

Abgrenzung:
- CODEAF ist keine Agent Registry; Agentenregistrierung bleibt Aufgabe von CAIM beziehungsweise der kanonischen Agent Registry.
- CODEAF ist keine Capability Resolution Engine; CRE loest Capabilities auf und priorisiert Kandidaten.
- CODEAF ist kein Execution Planner; der Planner erstellt validierte Plaene aus erlaubten Capability-Resolutionen.
- CODEAF ist kein Orchestrator; der Orchestrator fuehrt nur validierte Plaene innerhalb freigegebener Grenzen aus.
- CODEAF ist keine Runtime- oder Implementierungsfreigabe.

Verwandte Komponenten:
- CMIBF
- AFP
- CDF
- CDG
- CAWP
- AGF
- CAF
- CLMSF
- CAIM
- CRE
- Execution Planner
- Orchestrator Core
- CAM
- Release Integrity
- Audit und Provenienz

### Code-Agent

Name: Code-Agent
Abkuerzung: keine
Vollstaendige Bezeichnung: Code-Agent
Definition: Identifizierbare, regelgebundene Software- oder Modellinstanz, die innerhalb eines ausdruecklich freigegebenen Auftrags Quellcode, Konfigurationen, Tests, Dokumentation oder zugehoerige Entwicklungsartefakte analysiert, plant, erzeugt, veraendert, prueft oder verwaltet.
Zweck: Macht automatisierte Codearbeit identifizierbar, begrenzt, pruefbar und governancefaehig.
Architekturphase: Agent Governance, Analyse, Planung, Umsetzung, Review, Test, Dokumentation, Release
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CAIM
- CRE
- Execution Planner
- Orchestrator Core
- CAWP
- CDG

### Canonical Agent Task

Name: Canonical Agent Task
Abkuerzung: keine
Vollstaendige Bezeichnung: Canonical Agent Task
Definition: Kanonischer Auftrag fuer einen Code-Agenten mit Task-ID, Ziel, Begruendung, Auftraggeber, Rolle, Capabilities, Permission Profile, Scope, Risikoklasse, Vorpruefungen, Arbeitsablauf, Tests, Dokumentation, Audit, Abbruchbedingungen, Rueckfallpunkt, erwarteten Ergebnissen, Freigabeverfahren, Abschlussbericht und Status.
Zweck: Verhindert unklare, selbst erweiterte oder nicht nachvollziehbare Agentenarbeit.
Architekturphase: CODEAF-Auftragsmodell
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CDF
- CDG
- CAWP
- Execution Planner

### Agent Identity

Name: Agent Identity
Abkuerzung: keine
Vollstaendige Bezeichnung: Code Agent Identity
Definition: Dauerhafte, versionierbare und auditierbare Identitaet eines Code-Agenten mit eindeutiger Agenten-ID, Name, Version, Typ, Provider, Runtime, Vertrauensstufe, Status, Rollen, Capabilities, Permission Profile, Authentisierungsreferenz und Lizenzreferenz.
Zweck: Trennt identifizierbare Agenten von Anzeigenamen, Produkten oder temporaren Sessions.
Architekturphase: CODEAF Identity Gate
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CAF
- CLMSF
- CAIM

### Agent Run Identity

Name: Agent Run Identity
Abkuerzung: keine
Vollstaendige Bezeichnung: Code Agent Run Identity
Definition: Konkrete Lauf- oder Sitzungsidentitaet eines Agenten fuer einen bestimmten Auftrag, beispielsweise `agent_run_id`, `session_id`, `task_id` und `execution_id`.
Zweck: Verknuepft dauerhafte Agentenidentitaet, Auftrag, Ausfuehrung, Audit und Bericht.
Architekturphase: CODEAF Identity Gate, Audit und Provenienz
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CAF
- Orchestrator Core
- Audit

### Permission Profile

Name: Permission Profile
Abkuerzung: keine
Vollstaendige Bezeichnung: Code Agent Permission Profile
Definition: Auftragsspezifisches Berechtigungsprofil, das erlaubte und verbotene Aktionen, Pfade, Dateien, Dateitypen, Befehle, Tools, Datenbanken, Netzwerke, Git-Operationen, Laufzeiten und Aenderungsgroessen begrenzt.
Zweck: Trennt technische Faehigkeit von konkreter Erlaubnis und macht Scope-Grenzen maschinen- und menschenpruefbar.
Architekturphase: CODEAF Permission Gate
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CAF
- CDG
- CRE
- Execution Planner

### Capability-vs-Permission-Trennung

Name: Capability-vs-Permission-Trennung
Abkuerzung: keine
Vollstaendige Bezeichnung: Trennung von Capability und Permission
Definition: Architekturregel, nach der Capability nur beschreibt, was ein Agent technisch kann, waehrend Permission beschreibt, was er in einem konkreten Auftrag, Scope und Risikokontext tatsaechlich darf.
Zweck: Verhindert, dass registrierte technische Faehigkeiten automatisch als Ausfuehrungserlaubnis gelten.
Architekturphase: CODEAF Capability Gate und Permission Gate
Status: CODEAF-Regel

Verwandte Komponenten:
- CODEAF
- CRE
- CAIM
- CDG

### Deny-by-default

Name: Deny-by-default
Abkuerzung: keine
Vollstaendige Bezeichnung: Deny-by-default-Prinzip
Definition: Sicherheits- und Governance-Prinzip, nach dem alle nicht ausdruecklich erlaubten Aktionen, Pfade, Tools, Befehle, Datenbanken, Netzwerke, Git-Operationen, Delegationen und Runtime-Modi verboten sind.
Zweck: Erzwingt explizite Erlaubnis statt impliziter Ausfuehrbarkeit.
Architekturphase: CODEAF Permission Gate, Risk Gate, Execution Gate
Status: CODEAF-Regel

Verwandte Komponenten:
- CODEAF
- CDG
- CAWP
- AGF

### Controlled Write Mode

Name: Controlled Write Mode
Abkuerzung: keine
Vollstaendige Bezeichnung: Controlled Write Mode
Definition: CODEAF-Betriebsmodus fuer begrenzte, freigegebene Schreibaktionen innerhalb eines expliziten Scopes mit verpflichtender Diff-, Test-, Scope- und Abschlusspruefung.
Zweck: Erlaubt kontrollierte Implementierungsarbeit, ohne allgemeine Schreibrechte oder autonome Codearbeit zu aktivieren.
Architekturphase: CODEAF Operating Modes
Status: CODEAF-Begriff; Nutzung nur nach Implementierungsfreigabe

Verwandte Komponenten:
- CODEAF
- CDF
- CDG
- Execution Planner
- Orchestrator Core

### Administrative Boundary

Name: Administrative Boundary
Abkuerzung: keine
Vollstaendige Bezeichnung: Administrative Boundary
Definition: CODEAF-Grenze fuer administrative oder besonders riskante Aktionen wie Git-Schreiboperationen, Rechteaenderungen, Authentisierung, Lizenzierung, Datenbankmigration, Release-Vorbereitung, Architekturmodifikation und Migration.
Zweck: Trennt normale Analyse- oder Schreibarbeit von Aktionen mit erhoehtem Governance-, Sicherheits- oder Release-Risiko.
Architekturphase: CODEAF Permission Gate, Risk Gate, Approval Gate
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CAF
- CLMSF
- Release Integrity
- CDG

### Delegation / Unteragent

Name: Delegation / Unteragent
Abkuerzung: keine
Vollstaendige Bezeichnung: CODEAF Delegation / Sub-Agent
Definition: Auftraglich erlaubte Weitergabe eines begrenzten Teilauftrags an eine weitere Agenten- oder Laufidentitaet. Delegation darf Scope, Rolle, Capability, Permission oder Risiko nicht eigenmaechtig erweitern.
Zweck: Ermoeglicht spaetere kontrollierte Multi-Agent-Arbeit, ohne freie Agentensuche oder automatische Agentenketten zu erlauben.
Architekturphase: CODEAF Delegation Rules
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CAIM
- CRE
- Execution Planner
- Orchestrator Core

### CODEAF Risk Class

Name: CODEAF Risk Class
Abkuerzung: keine
Vollstaendige Bezeichnung: CODEAF Risk Class
Definition: Risikoklasse fuer Code-Agentenarbeit von CODEAF-R0 bis CODEAF-R5, die Umfang, Freigabebedarf, Testpflicht, Reviewpflicht, Security-Pruefung und Autonomiegrenzen bestimmt.
Zweck: Macht Code-Agentenarbeit risikobasiert steuerbar und verhindert Selbstfreigabe bei kritischen Aenderungen.
Architekturphase: CODEAF Risk Gate
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CDG
- CAWP
- Release Integrity

### CODEAF Gate

Name: CODEAF Gate
Abkuerzung: keine
Vollstaendige Bezeichnung: CODEAF Control Gate
Definition: Verbindlicher Kontrollpunkt innerhalb von CODEAF, beispielsweise Identity Gate, Task Gate, Role Gate, Capability Gate, Permission Gate, Risk Gate, Plan Gate, Execution Gate, Verification Gate und Final Approval Gate.
Zweck: Verhindert, dass Code-Agenten fehlende Identitaet, unklare Auftraege, fehlende Capabilities, fehlende Permissions, ungepruefte Risiken oder fehlende Freigaben umgehen.
Architekturphase: CODEAF Control Gates
Status: CODEAF-Begriff

Verwandte Komponenten:
- CODEAF
- CDF
- CDG
- CAWP
- Execution Planner
- Orchestrator Core
