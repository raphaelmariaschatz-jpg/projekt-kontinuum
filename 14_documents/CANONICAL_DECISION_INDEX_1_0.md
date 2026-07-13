# Canonical Decision Index (CDI) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: kanonischer Entscheidungsindex
Gueltig ab: 2026-07-09

## Zweck

CDI 1.0 dokumentiert bereits getroffene wesentliche Architekturentscheidungen. Es trifft keine neuen Entscheidungen und veraendert keine Architekturimplementierung.

## CDI-001 - Foundation is the highest protection layer

Decision-ID: CDI-001
Titel: Foundation is the highest protection layer
Hintergrund: Foundation-Regeln und Identitaetsgrenzen wurden als dauerhaft verbindlicher Kern etabliert.
Problemstellung: Ohne oberste Schutzschicht koennten Architekturentscheidungen Kernprinzipien verletzen.
Entscheidung: Foundation bleibt oberste Schutz- und Prinzipienschicht.
Begruendung: Alle weiteren Governance-Mechanismen benoetigen eine nicht beliebig verschiebbare Grenze.
Vorteile:
- Stabiler Identitaetskern
- Klare Kompatibilitaetspruefung
- Reduzierte Architekturdrift

Moegliche Nachteile:
- Hoehere Pruefpflicht bei Aenderungen

Betroffene Komponenten: Foundation, AGF, Governance, Canonical Memory
Status: Documented existing decision

## CDI-002 - Architecture knowledge is separated from runtime

Decision-ID: CDI-002
Titel: Architecture knowledge is separated from runtime
Hintergrund: CG und CKS wurden als Dokumentations- und Governance-Komponenten beauftragt.
Problemstellung: Wissensstrukturierung duerfte sonst versehentlich Runtime-Verhalten veraendern.
Entscheidung: CKS, CG, CAMap, CDI und CHI bleiben reine Dokumentation und Governance.
Begruendung: Architekturwissen soll stabilisieren, nicht unkontrolliert implementieren.
Vorteile:
- Keine Runtime-Risiken
- Klarer Audit-Pfad
- Saubere Phase-2-Vorbereitung

Moegliche Nachteile:
- Keine automatische Durchsetzung in Runtime

Betroffene Komponenten: CKS, CG, CAMap, CDI, CHI
Status: Documented existing decision

## CDI-003 - CCP is split into policy and cognitive meanings

Decision-ID: CDI-003
Titel: CCP is split into policy and cognitive meanings
Hintergrund: Aeltere Dokumente verwenden CCP unspezifisch; Phase 2 unterscheidet CCP-Policy und CCP-Cognitive.
Problemstellung: Eine gleiche Abkuerzung kann Policy- und Kognitionskonzepte vermischen.
Entscheidung: CG fuehrt CCP-Policy und CCP-Cognitive / CCP-Cog getrennt.
Begruendung: Disambiguierung verhindert falsche Governance- und Architekturreferenzen.
Vorteile:
- Eindeutige Sprache
- Bessere Phase-2-Konsistenz

Moegliche Nachteile:
- Aeltere Dokumente muessen spaeter redaktionell bereinigt werden

Betroffene Komponenten: CG, CCP-Policy, CCP-Cognitive, CKS
Status: Documented existing decision

## CDI-004 - CRE resolves capabilities read-only

Decision-ID: CDI-004
Titel: CRE resolves capabilities read-only
Hintergrund: CRE wurde als Capability Resolution Engine eingefuehrt.
Problemstellung: Capability-Auswahl und Ausfuehrung duerfen nicht vermischt werden.
Entscheidung: CRE findet und priorisiert Kandidaten, fuehrt aber nicht aus.
Begruendung: Trennung von Discovery, Planung und Ausfuehrung stabilisiert Governance.
Vorteile:
- Klare Rollen
- Geringeres Ausfuehrungsrisiko
- Bessere Testbarkeit

Moegliche Nachteile:
- Mehr Komponentenabstimmung noetig

Betroffene Komponenten: CRE, Execution Planner, Orchestrator Core, Governance
Status: Documented existing decision

## CDI-005 - Execution Planner plans, Orchestrator executes

Decision-ID: CDI-005
Titel: Execution Planner plans, Orchestrator executes
Hintergrund: Runtime-Migration dokumentiert Planner- und Orchestrator-Rollen.
Problemstellung: Unklare Zustandsverantwortung koennte zu Planungs- oder Ausfuehrungsdrift fuehren.
Entscheidung: Execution Planner erzeugt Plaene; Orchestrator Core fuehrt nur validierte Plaene aus.
Begruendung: Eine harte Rollentrennung verhindert selbsttaetige Orchestrator-Planung.
Vorteile:
- Kontrollierte Integration
- Einfachere Fallbacks
- Pruefbare Runtime-Vertraege

Moegliche Nachteile:
- Feature-Flag- und Schemaabhaengigkeit

Betroffene Komponenten: Execution Planner, Orchestrator Core, Runtime Schema, Release Integrity
Status: Documented existing decision

## CDI-006 - Active project folders must remain canonical

Decision-ID: CDI-006
Titel: Active project folders must remain canonical
Hintergrund: CADP und ALP regeln aktive Ordner, Archivierung und Referenzpruefung.
Problemstellung: Historische Parallelstaende in aktiven Ordnern erschweren Release- und Governance-Pruefung.
Entscheidung: Ersetzte oder historische Artefakte gehoeren in Archiv-/History-Bereiche, nicht in aktive Kanonordner.
Begruendung: Aktive Projektbereiche muessen eindeutige Gegenwartsreferenzen enthalten.
Vorteile:
- Saubere Projektstruktur
- Weniger Konflikte
- Bessere Release Integrity

Moegliche Nachteile:
- Redaktionelle Pflege bleibt notwendig

Betroffene Komponenten: CADP, ALP, CAM, Release Integrity
Status: Documented existing decision

## CDI-007 - Origin and copyright are governance knowledge

Decision-ID: CDI-007
Titel: Origin and copyright are governance knowledge
Hintergrund: CIPL wurde als Herkunfts- und Urheberregister angelegt.
Problemstellung: Architekturkonzepte brauchen nachvollziehbare Herkunft und Schoepferbezug.
Entscheidung: CIPL fuehrt IP- und Herkunftswissen als kanonische Governance-Information.
Begruendung: Langfristige Governance braucht Nachweise ueber Entstehung und Besitz.
Vorteile:
- Herkunftstransparenz
- IP-Schutz
- Bessere Chronikreferenzen

Moegliche Nachteile:
- Ledger muss redaktionell fortgeschrieben werden

Betroffene Komponenten: CIPL, CG, CKS, Governance
Status: Documented existing decision
