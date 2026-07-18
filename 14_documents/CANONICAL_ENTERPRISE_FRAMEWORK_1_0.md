# Canonical Enterprise Framework (CEF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Konzept geprueft, read-only Kernmodell aktiviert
Gueltig ab: 2026-07-16
Komponententyp: Enterprise and Operations Framework / kanonisches Unternehmensmodell
Runtime-Wirkung: read-only universelles Enterprise-Kernmodell

## 1. Zweck

Das Canonical Enterprise Framework (CEF) 1.0 definiert den kanonischen Bezugsrahmen fuer den Aufbau eines Unternehmens. Es beschreibt Unternehmen nicht als Sammlung einzelner Softwaremodule, sondern als dynamisches System aus Menschen, Ressourcen, Wissen, Prozessen, Entscheidungen und Zielen.

CEF ist kein ERP-System, kein CRM-System, kein BPM-System und kein DMS. Es beschreibt die universellen Funktionen, Strukturen, Beziehungen und Informationsfluesse eines Unternehmens unabhaengig von Branche, Groesse oder Rechtsform.

Grundsatz:

```text
Ein Unternehmen ist kein Softwarepaket.
Ein Unternehmen ist ein zusammenhaengendes System aus Funktionen, Beziehungen, Informationen, Entscheidungen und Wertschoepfung.
```

## 2. Bestandsanalyse

Projekt Kontinuum besitzt bereits mehrere Architekturbausteine, an die CEF anschliessen kann:

- CPVF definiert Vision, Mission und langfristige Orientierung von Projekt Kontinuum.
- CIF definiert intelligente Verarbeitung als kontrolliertes Verstehen, Begruenden, Handeln, Lernen und Reflektieren.
- CCP-Cognitive beschreibt den kanonischen Denk- und Verarbeitungsprozess.
- CAICF und CMLF beschreiben Kompetenzentwicklung und Medienvermittlung.
- CRE, Execution Planner und Orchestrator Core trennen Faehigkeitsauswahl, Planung und Ausfuehrung.
- Canonical Memory, Learning Agent und CLG regeln Wissen, Lernen, Review und Speicherung.
- CAM, ALP, CDF, CDG und Release Integrity sichern Artefakte, Entwicklung und Freigabe.
- Das CMIBF registriert CEF bereits als `PK-FW-ENT-001` im Bereich Enterprise and Operations.

CEF ergaenzt diese Architektur als fachliches Unternehmensmodell. Es erzeugt keine Unternehmenssoftware und keine Runtime-Funktion.

## 3. Architektur-Einordnung

Empfohlene Einordnung:

```text
Foundation Layer
        |
Governance Layer
        |
Canonical Architecture / CMIBF
        |
Canonical Enterprise Framework (CEF)
        |
Enterprise Analysis / Consulting / Simulation (spaeter)
        |
CRE / Execution Planner / Orchestrator Core (nur nach Freigabe)
        |
User / Organisation
```

CEF gehoert zur Enterprise-and-Operations-Domaene. Es beschreibt, welche Unternehmensdimensionen spaeter analysiert, modelliert, beraten oder simuliert werden koennen.

## 4. Kanonische Unternehmensdimensionen

### 4.1 Vision & Strategie

Definiert Mission, Ziele, Leitprinzipien, langfristige Planung und Unternehmensentwicklung.

### 4.2 Governance

Definiert Richtlinien, Verantwortlichkeiten, Compliance, Risikomanagement, Qualitaet und Entscheidungsstrukturen.

### 4.3 Organisation

Definiert Struktur, Rollen, Teams, Verantwortungsbereiche und Kommunikation.

### 4.4 Prozesse

Definiert Geschaeftsprozesse, Workflows, Standardprozesse, Optimierung und Automatisierung.

### 4.5 Ressourcen

Definiert Personal, Finanzen, Infrastruktur, IT, Maschinen, Material und Zeit als begrenzte Mittel.

### 4.6 Wissen

Definiert Dokumentation, Know-how, Lernen, Innovation, Wissensmanagement und Erfahrungen.

### 4.7 Kunden & Partner

Definiert Kunden, Lieferanten, Partner, Behoerden, Netzwerke und externe Kommunikation.

### 4.8 Produkte & Dienstleistungen

Definiert Ideen, Entwicklung, Produktion, Qualitaet, Bereitstellung und Lebenszyklus von Wertangeboten.

### 4.9 Steuerung & Kennzahlen

Definiert Ziele, KPIs, Monitoring, Audits, Bewertungen und Verbesserungen.

### 4.10 Nachhaltige Weiterentwicklung

Definiert Innovation, Reflexion, Lessons Learned, Anpassungen, Architekturentwicklung und Unternehmensentwicklung.

## 5. Beziehungen und Informationsfluesse

CEF betrachtet Unternehmen als Funktionsnetz:

```text
Funktionen
-> Beziehungen
-> Informationsfluesse
-> Entscheidungen
-> Wertschoepfung
-> Steuerung
-> Weiterentwicklung
```

| Von | Nach | Informationsfluss |
| --- | --- | --- |
| Vision & Strategie | Governance | Ziele und Leitprinzipien begruenden Richtlinien, Verantwortung und Entscheidungsgrenzen |
| Governance | Organisation | Governance definiert Rollen, Verantwortlichkeiten und Kommunikationsgrenzen |
| Organisation | Prozesse | Organisation traegt und betreibt Prozesse; Prozesse machen Verantwortung ausfuehrbar |
| Prozesse | Ressourcen | Prozesse verbrauchen, planen und optimieren Ressourcen |
| Wissen | Prozesse | Wissen verbessert Prozesse; Prozesse erzeugen neue Erfahrungen |
| Kunden & Partner | Produkte & Dienstleistungen | Bedarfe, Feedback und Beziehungen beeinflussen Wertangebote |
| Produkte & Dienstleistungen | Steuerung & Kennzahlen | Leistung, Qualitaet und Lebenszyklus erzeugen Mess- und Steuerungsdaten |
| Steuerung & Kennzahlen | Nachhaltige Weiterentwicklung | Messungen und Audits fuehren zu Verbesserungen, Innovation und Anpassung |
| Nachhaltige Weiterentwicklung | Vision & Strategie | Lessons Learned und Entwicklungserkenntnisse aktualisieren Strategiefragen kontrolliert |

## 6. Abgrenzung zu Unternehmenssoftware

| Systemtyp | Zweck | Grenze zu CEF |
| --- | --- | --- |
| ERP | operative Ressourcen- und Geschaeftsprozessverwaltung | CEF beschreibt Unternehmensdimensionen, implementiert keine Transaktionen |
| CRM | Kundenbeziehungsmanagement | CEF beschreibt Kunden & Partner als Dimension, fuehrt keine Kundendatenbank |
| BPM | Prozessmodellierung und Workflowausfuehrung | CEF beschreibt Prozesse als Unternehmensfunktion, fuehrt keine Workflows aus |
| DMS | Dokumentenmanagement | CEF beschreibt Wissen und Dokumentation, speichert keine Dokumente |
| BI / KPI-System | Kennzahlenanalyse | CEF beschreibt Steuerung & Kennzahlen, berechnet keine produktiven KPIs |

CEF kann spaeter als Ordnungsrahmen fuer solche Systeme dienen, ersetzt sie aber nicht.

## 7. Schnittstellenuebersicht

| Schnittstelle | Zweck | Grenze |
| --- | --- | --- |
| Foundation Layer | Verantwortung, Identitaet und Schutzgrenzen | CEF darf Foundation nicht veraendern |
| Governance Layer | Freigabe, Compliance, Risiko und Review | CEF entscheidet nicht autonom |
| Canonical Architecture / CMIBF | normative Einordnung und Framework-Registry | CMIBF bleibt Single Source of Truth |
| CPVF | Vision und Orientierung | CEF leitet Unternehmensmodelle nicht direkt aus Projektvision ab |
| CVF | Computer Vision / visuelle Wahrnehmung | nur spaeter relevant fuer visuelle Unternehmensartefakte |
| CIF | intelligente Analyse- und Bewertungsdimensionen | CEF definiert Unternehmen, nicht Intelligenz |
| CCP-Cognitive | Verarbeitung von Unternehmensfragen | CEF ersetzt die Pipeline nicht |
| CAICF | Kompetenzentwicklung | CEF kann Schulungs- und Organisationskompetenzen strukturieren, definiert CAICF nicht neu |
| CMLF | Medienvermittlung | CMLF kann CEF-Inhalte vermitteln, CEF waehlt keine Medien |
| Learning Layer | Lernen aus Organisationswissen | keine automatische Wissensuebernahme |
| CRE | spaetere Faehigkeitsauswahl | CEF loest keine Capabilities auf |
| Execution Planner | spaetere Planung von Analyse- oder Beratungsablaeufen | CEF erstellt keine Runtime-Plaene |
| Orchestrator Core | Ausfuehrung freigegebener Plaene | CEF fuehrt nichts aus |
| Canonical Memory | Speicherung validierter Organisationsmodelle | kein direkter Memory Write |
| CAM / ALP | Artefakt- und Lifecycle-Governance | CEF klassifiziert keine Projektartefakte automatisch |
| CDF / CDG | Entwicklungs- und Governance-Regeln | Implementierung bleibt freigabepflichtig |
| Release Integrity | spaetere Freigabepruefung | keine Release-Aenderung in CEF 1.0 |
| Canonical Glossary | Begriffskanon | CEF-Begriffe muessen eindeutig bleiben |
| Projektchronik | Entwicklungshistorie | Fortschreibung nur dokumentarisch |

## 8. Erweiterbarkeit

CEF 1.0 bleibt branchen-, groessen- und rechtsformunabhaengig. Spaetere Erweiterungen koennen aufnehmen:

- Enterprise Ontology
- Enterprise Capability Map
- Process Landscape Model
- Knowledge Map Model
- Decision Map Model
- KPI and Control Model
- Digital Enterprise Twin
- Consulting and Simulation Profiles
- Industry-specific Extensions
- Organisation Maturity Model

Jede Erweiterung benoetigt eine eigene Governance-Freigabe.

## 9. Risiken und offene Fragen

| Risiko / Frage | Schutzmassnahme |
| --- | --- |
| Verwechslung mit ERP/CRM/BPM/DMS | CEF bleibt konzeptionelles Unternehmensmodell |
| Ueberabstraktion | Dimensionen bleiben universell, aber konkret pruefbar |
| Branchenspezifische Sonderfaelle | spaetere Extensions, Kernmodell bleibt neutral |
| Datenschutz bei Unternehmensdaten | keine Datenverarbeitung in CEF 1.0 |
| Scheingenauigkeit bei Kennzahlen | keine produktive KPI-Berechnung in CEF 1.0 |
| Automatische Beratung ohne Kontext | spaetere Review- und Governance-Pflicht |
| Konflikt mit realer Organisationsverantwortung | Menschliche Entscheidung bleibt verantwortlich |
| Digitale Zwillinge | nur als spaeteres, freigabepflichtiges Modell |

Offene Fragen:

1. Welche Mindestdaten duerfen fuer spaetere Organisationsanalyse verwendet werden?
2. Welche Unternehmensdimensionen brauchen eigene Submodelle?
3. Wie werden Branchenprofile eingefuehrt, ohne das Kernmodell zu verzerren?
4. Wie wird Entscheidungsunterstuetzung von automatischer Entscheidung getrennt?
5. Welche Datenschutz- und Rollenmodelle sind fuer Enterprise-Analysen erforderlich?

## 10. Empfehlung

Empfehlung: `GO` fuer kanonische Konzept- und Dokumentationsvorbereitung; `SPAETER` fuer technische Implementierung.

Begruendung:

- CEF beschreibt Unternehmen als universelles System.
- CEF ist unabhaengig von Branche, Groesse und Rechtsform anwendbar.
- CEF ersetzt keine Unternehmenssoftware.
- CEF ist mit CMIBF, Foundation und Governance vereinbar.
- CEF bleibt langfristig erweiterbar.
- CEF kann spaeter Analyse-, Beratungs- und Simulationsfunktionen tragen.

## 11. Freigegebene Artefakte fuer diese Phase

```text
14_documents/CANONICAL_ENTERPRISE_FRAMEWORK_1_0.md
14_documents/CEF_IMPLEMENTATION_PLAN_1_0.md
24_config/canonical_enterprise_framework_1_0.json
24_config/cef_enterprise_model_1_0.json
31_reports/cef_1_0_status_report.md
```

## 12. Nicht-Ziele von CEF 1.0

- keine ERP-Implementierung
- keine CRM-Implementierung
- keine Finanz- oder Buchhaltungsfunktionen
- keine Runtime-Aenderungen
- keine Datenbankmigrationen
- keine Refactorings bestehender Komponenten
- keine produktive Unternehmensdatenverarbeitung
- keine automatische Unternehmensberatung

## 13. Kontrollierte technische Aktivierung

Die serielle Implementierungsfreigabe vom 2026-07-18 aktiviert Phase 1 als
read-only Enterprise-Kernmodell.

Aktiviert sind:

- deklaratives Laden und Validieren von zehn Unternehmensdimensionen;
- Validierung der Beziehungen und Informationsfluesse;
- read-only Katalogzugriff;
- explizite Scope-Ansicht ausgewaehlter Dimensionen;
- stabile Scope-IDs;
- ausschliesslich das generische, branchenneutrale Kernmodell;
- Registrierung und Statusausgabe in `KontinuumSystem`.

Nicht aktiviert sind Unternehmensdatenverarbeitung, Transaktionen,
KPI-Berechnung, ERP/CRM/BPM/DMS/BI-Funktionen, Beratung, Simulation,
Entscheidungsautoritaet oder Memory-Schreibung.
