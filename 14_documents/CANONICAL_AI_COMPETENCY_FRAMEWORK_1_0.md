# Canonical AI Competency Framework (CAICF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Konzept geprueft, kontrollierte Read-only-Aktivierung vorhanden
Gueltig ab: 2026-07-15
Komponententyp: Canonical Learning Layer / Kompetenzrahmen
Runtime-Wirkung: Read-only-Kompetenzkatalog und explizite Lernfokus-Planung

## 1. Zweck

Das Canonical AI Competency Framework (CAICF) 1.0 definiert den kanonischen Kompetenzrahmen, mit dem Projekt Kontinuum Menschen schrittweise zu einem kompetenten, verantwortungsvollen und kreativen Umgang mit Kuenstlicher Intelligenz befaehigen kann.

CAICF ist kein isoliertes Modul und keine Runtime-Komponente. Es ist ein uebergeordnetes Architekturprinzip fuer Lernpfade, Kompetenzentwicklung, adaptive Lernempfehlungen, Aufgabenplanung, Kompetenzbewertung sowie Tutor- und Education-Funktionen.

Grundsatz:

```text
CCP = K denkt kanonisch.
CAICF = K lehrt KI-Kompetenz kanonisch.
```

## 2. Bestandsanalyse

Projekt Kontinuum besitzt bereits kontrollierte Lern- und Review-Strukturen:

- Learning Agent 1.2 arbeitet read-only und erzeugt ausschliesslich pending Proposals.
- Continuous Learning Governance 1.1 fuehrt Proposal-Lifecycle, Queue, History, Audit und Compliance-Pruefung.
- Learning Layer und Review-Bereiche sind provenienz- und auditpflichtig.
- Canonical Memory uebernimmt Wissen erst nach Review und Freigabe.
- CRE, Execution Planner und Orchestrator Core sind als getrennte Faehigkeits-, Planungs- und Ausfuehrungsschichten vorbereitet.
- CRL und Meta-Reasoning sind als Reflexions- und Pruefkonzepte dokumentiert.

CAICF ergaenzt diese Lage, indem es nicht Lerninhalte speichert oder bewertet, sondern den kanonischen Kompetenzrahmen fuer KI-Kompetenz definiert.

## 3. Architektur-Einordnung

CAICF gehoert zum Canonical Learning Layer. Es definiert, welche Kompetenzen aufgebaut werden sollen. Die bestehenden Kernkomponenten entscheiden spaeter, wie der Kompetenzaufbau kontrolliert geplant, ausgefuehrt, geprueft und dokumentiert wird.

Zielbild:

```text
Foundation Layer
-> Governance Layer
-> Canonical Layer
-> Capability Resolution Engine (CRE)
-> Execution Planner
-> Orchestrator Core
-> Canonical Learning Layer
-> Canonical AI Competency Framework (CAICF)
-> Adaptive Tutor
-> User
```

CAICF ersetzt weder Learning Agent, Governance, CRE, Planner, Orchestrator noch Canonical Memory.

## 4. Beziehung zur Canonical Cognitive Pipeline

Die spaetere Canonical Cognitive Pipeline (CCP) beschreibt den kanonischen Verarbeitungsablauf von K bei Nutzereingaben.

CAICF beschreibt nicht diesen Ablauf, sondern die zu foerdernden KI-Kompetenzen des Nutzers.

Beziehung:

```text
CAICF definiert, welche KI-Kompetenzen beim Nutzer aufgebaut werden sollen.
CCP definiert, wie K Eingaben verarbeitet, um diese Kompetenzentwicklung sinnvoll zu unterstuetzen.
```

Damit liegt CAICF innerhalb des Learning Layer, waehrend CCP oberhalb oder quer zu User Input, Foundation, Governance, CRE, Planner, Orchestrator, Learning Layer, CAICF, Memory und Reflexion liegt.

## 5. Kanonische Kompetenzbereiche

### 5.1 Engage with AI

KI erkennen, verstehen und kritisch hinterfragen.

Ziele:

- KI im Alltag erkennen
- KI-Ergebnisse kritisch bewerten
- Quellen einschaetzen
- Halluzinationen erkennen
- Chancen und Risiken verstehen
- gesundes Vertrauen in KI entwickeln

### 5.2 Create with AI

KI kreativ und verantwortungsvoll einsetzen.

Ziele:

- Texte entwickeln
- Bilder erzeugen
- Programme erstellen
- Ideen und Loesungen gemeinsam mit KI entwickeln
- KI als kreatives Werkzeug sinnvoll nutzen

### 5.3 Manage AI

KI verantwortungsvoll steuern.

Ziele:

- entscheiden, wann KI sinnvoll eingesetzt wird
- Ergebnisse validieren
- Datenschutz und Informationssicherheit beruecksichtigen
- ethische Fragestellungen verstehen
- Verantwortung fuer den KI-Einsatz uebernehmen

### 5.4 Design AI

KI-Systeme verstehen und weiterentwickeln.

Ziele:

- Grundprinzipien moderner KI-Systeme verstehen
- Agenten entwickeln
- Workflows entwerfen
- Architekturen erweitern
- eigene KI-Systeme planen und verbessern

## 6. Kompetenzdimensionen

Alle Kompetenzbereiche werden ueber drei Dimensionen bewertet:

```text
Knowledge  = Wissen
Skills     = Faehigkeiten
Attitudes  = Haltungen und Verantwortungsbewusstsein
```

Diese Dimensionen bilden den kanonischen Bewertungsrahmen spaeterer Lernaktivitaeten. Der Kompetenzaufbau orientiert sich am individuellen Wissensstand des Nutzers, nicht an Alter, Klassenstufe oder formalen Bildungsabschluessen.

## 7. Schnittstellenuebersicht

| Schnittstelle | Zweck | Grenze |
|---|---|---|
| Foundation Layer | Schutz von Identitaet, Leitprinzipien und moralischen Grenzen | CAICF darf Foundation nicht ueberschreiben |
| Governance Layer | Freigabe, Review, Risikobegrenzung und Compliance | CAICF entscheidet nicht selbst ueber Freigaben |
| Canonical Architecture | Einordnung in Learning Layer und CMIBF-Ableitung | CAICF besitzt keine eigenstaendige Architekturautoritaet |
| CCP | Verarbeitung von Eingaben zur Lernunterstuetzung | CAICF ersetzt CCP nicht |
| CRE | Faehigkeitsauswahl fuer Lernimpulse | CAICF fuehrt keine Capability-Auswahl aus |
| Execution Planner | Planung von Lernschritten | CAICF erstellt keine Runtime-Plaene |
| Orchestrator Core | Ausfuehrung validierter Plaene | CAICF fuehrt nichts aus |
| Learning Agent | spaetere Proposal- und Lernpfad-Erzeugung | keine automatische Wissensuebernahme |
| Canonical Memory | Speicherung validierter Kompetenz- und Lernnachweise | nur nach Review und Freigabe |
| Tutor / Education | adaptive Lernbegleitung | keine Implementierung in CAICF 1.0 |
| Audit / Review | Nachvollziehbarkeit und Qualitaetspruefung | CAICF liefert Bewertungsrahmen, nicht Review-Entscheidung |
| Release Integrity | Freigabepruefung spaeterer Implementierung | keine Release-Freigabe durch CAICF selbst |
| Canonical Glossary | Begriffskanon | CAICF-Begriffe muessen eindeutig bleiben |
| Projektchronik | Entwicklungshistorie | Fortschreibung nur dokumentarisch |

## 8. Notwendige Architekturkomponenten

Fuer eine spaetere Entwicklungsphase waeren mindestens erforderlich:

- CAICF-Kompetenzmodell
- Kompetenzmatrix
- Nutzer-Kompetenzprofil als separates, reviewpflichtiges Datenmodell
- Lernziel- und Lernpfadmodell
- Tutor-Policy fuer altersunabhaengige, wissensstandsbasierte Anpassung
- Bewertungs- und Evidence-Regeln
- Governance- und Datenschutzgrenzen
- Review- und Memory-Handoff fuer validierte Kompetenzentwicklung

Diese Komponenten werden in CAICF 1.0 nur vorbereitet, nicht implementiert.

## 9. Risiken und offene Fragen

| Risiko / Frage | Bewertung / Schutzmassnahme |
|---|---|
| Verwechslung mit Schulstufen | CAICF ist wissensstandsbasiert, nicht alters- oder schulformbasiert |
| Automatische Kompetenzbewertung im Livebetrieb | in CAICF 1.0 nicht erlaubt |
| Datenschutz bei Nutzerprofilen | spaeteres separates Datenschutz- und Speicherprofil erforderlich |
| Ueberkomplexe Lernarchitektur | stufenweise Implementierung und Governance-Gates |
| Vermischung mit CCP | CCP verarbeitet, CAICF definiert Kompetenzen |
| Ungepruefte Memory-Uebernahme | nur Review- und Governance-Handoff |

## 10. Empfehlung

Empfehlung: GO fuer kanonische Konzept- und Dokumentationsvorbereitung; SPAETER fuer technische Implementierung.

Begruendung:

- CAICF staerkt die Lernarchitektur.
- CAICF ergaenzt CCP, ersetzt sie aber nicht.
- CAICF unterstuetzt kompetenten KI-Umgang.
- CAICF bleibt alters- und schulformunabhaengig.
- CAICF ist mit Foundation und Governance vereinbar.
- CAICF erzeugt in Version 1.0 keine Runtime-Komplexitaet.

## 11. Freigegebene Artefakte fuer diese Phase

```text
14_documents/CANONICAL_AI_COMPETENCY_FRAMEWORK_1_0.md
24_config/canonical_ai_competency_framework_1_0.json
31_reports/caicf_1_0_status_report.md
14_documents/CAICF_IMPLEMENTATION_PLAN_1_0.md
24_config/caicf_competency_matrix_1_0.json
```

## 12. Nicht-Ziele von CAICF 1.0

- keine produktive Runtime-Integration
- keine Aenderung an CRE, Planner oder Orchestrator
- keine automatische Kompetenzbewertung im Livebetrieb
- keine neue Agentenimplementierung
- keine Datenbankmigration
- keine Datei-Loeschung oder Verschiebung
- keine Aenderung bestehender Lernlogik

## 13. Kontrollierte technische Aktivierung

Die serielle Implementierungsfreigabe vom 2026-07-18 aktiviert CAICF 1.0 in
einem reversiblen, read-only Minimalumfang.

Aktiviert sind:

- deklaratives Laden der kanonischen Kompetenzmatrix;
- Abfrage der vier Kompetenzbereiche;
- Abfrage der drei Dimensionen Knowledge, Skills und Attitudes;
- explizite Planung eines Lernfokus fuer einen Bereich und eine Dimension;
- stabile Fokus-IDs;
- Evidenz- und Review-Pflicht im Ergebnisvertrag;
- Systemregistrierung und Statusausgabe.

Nicht aktiviert sind:

- keine automatische Kompetenzbewertung;
- kein Nutzer-Kompetenzprofil;
- keine Alters-, Schulform- oder Abschlussklassifikation;
- keine Persistenz und keine Memory-Uebernahme;
- keine Aenderung an Learning Agent, CRE, Planner, Orchestrator oder CCP;
- kein Tutor-Automatismus.
