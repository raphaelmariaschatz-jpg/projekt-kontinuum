# Canonical Knowledge System (CKS) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: kanonischer Knowledge Governance Layer
Gueltig ab: 2026-07-09
Komponententyp: Knowledge Governance Layer

## Zweck

Canonical Knowledge System (CKS) 1.0 ist der Knowledge Governance Layer von Projekt Kontinuum. Es verwaltet Wissen ueber die Architektur, indem es Begriffe, Komponentenbeziehungen, bereits getroffene Entscheidungen und die dokumentierte Entstehungsgeschichte zentraler Architekturbausteine ordnet. CKS implementiert keine Runtime und fuehrt keine Architekturentscheidung neu ein.

## Governance-Ebenen

- 'AGF' regelt Architektur.
- 'CDG' regelt Entwicklung.
- 'CKS' regelt Architekturwissen.

Diese drei Ebenen sind getrennt: AGF beschreibt Architekturverbindlichkeit, CDG beschreibt Entwicklungsverbindlichkeit, CKS beschreibt Wissensverbindlichkeit.

## Knowledge Governance Layer

~~~text
Knowledge Governance
|
+-- CG
|   Begriffe
|
+-- CAMap
|   Beziehungen
|
+-- CDI
|   Entscheidungen
|
+-- CHI
|   Historie
|
+-- CKS
    Gesamtsystem
~~~

## Struktur

- 'CG 1.0' definiert die kanonische Sprache.
- 'CAMap 1.0' dokumentiert Architekturbeziehungen.
- 'CDI 1.0' dokumentiert bereits getroffene Entscheidungen.
- 'CHI 1.0' dokumentiert die vorhandene Entstehungsgeschichte.

## Zusammenspiel

CG liefert die Begriffe, die CAMap fuer Beziehungen verwendet. CDI verweist auf dieselben Begriffe, um Entscheidungen eindeutig einzuordnen. CHI verbindet diese Begriffe mit ihrer dokumentierten Entstehung. CKS fasst diese vier Sichten zu einer Governance-Struktur fuer Architekturwissen zusammen.

## Rolle innerhalb der kanonischen Architektur

CKS gehoert zur Knowledge-Governance-Schicht. Es unterstuetzt Foundation, AGF, CDG, Release Integrity und Phase 2 durch einheitlich auffindbares Architekturwissen. Es veraendert keine Runtime, keine Agenten, keine APIs, keine Datenbanken, keine Imports und keine Tests.

## Governance-Regeln

- CKS dokumentiert Architekturwissen, aber erzwingt keine Runtime-Regeln.
- Inkonsistenzen werden im Statusreport dokumentiert und nicht automatisch korrigiert.
- Neue Architekturentscheidungen duerfen nicht im CDI erfunden werden.
- Historische Aussagen duerfen nur aus vorhandener Dokumentation abgeleitet werden.
- CKS-Artefakte duerfen spaeter nur kontrolliert nach AGF/CDG fortgeschrieben werden.

## Referenzartefakte

- '14_documents/CANONICAL_GLOSSARY_1_0.md'
- '14_documents/CANONICAL_ARCHITECTURE_MAP_1_0.md'
- '14_documents/CANONICAL_DECISION_INDEX_1_0.md'
- '14_documents/CANONICAL_HISTORY_INDEX_1_0.md'
- '24_config/canonical_knowledge_system_1_0.json'
- '31_reports/cks_1_0_status_report.md'
