# Architecture Governance Framework (AGF) 1.0

Status: kanonische Architektur-Richtlinie
Gueltig ab: 2026-07-05
Geltungsbereich: gesamte Architektur von Projekt Kontinuum

## 1. Zweck

Das Architecture Governance Framework 1.0, kurz AGF 1.0, ist die Architekturverfassung von Projekt Kontinuum. Es legt dauerhaft fest, wie sich die Architektur selbst weiterentwickeln darf.

AGF 1.0 definiert Regeln. Es fuehrt keine Runtime-Migration durch, verschiebt keine Dateien, loescht keine Dateien, benennt keine Dateien um und aendert keine Imports.

## 2. Unveraenderliche Architekturgrundsaetze

Die folgenden Grundsaetze gelten dauerhaft und duerfen nur durch geschuetzte Foundation-Migration erweitert werden:

1. Foundation besitzt hoechste Prioritaet.
2. Jede aktive Komponente besitzt genau einen kanonischen Zweck.
3. Jede aktive Komponente besitzt genau einen kanonischen Speicherort.
4. Jede Architekturentscheidung muss nachvollziehbar, ueberpruefbar und mit den bestehenden Foundation-Regeln vereinbar sein.
5. Architekturaenderungen erfolgen ausschliesslich kontrolliert.
6. Planung und Runtime bleiben strikt getrennt.
7. CAM verwaltet Artefakte, nicht fachliche Runtime-Entscheidungen.
8. Governance ueberwacht Regelkonformitaet.
9. Release Integrity prueft Freigabefaehigkeit.
10. Neue Komponenten duerfen nur eingefuehrt werden, wenn sie einen klar abgegrenzten Verantwortungsbereich besitzen, keine bestehende Verantwortung unnoetig duplizieren und sich nachvollziehbar in die kanonische Architektur einfuegen.

Diese Grundsaetze bilden die oberste Architekturordnung nach Foundation-Regeln und vor operativen Implementierungsentscheidungen.

## 3. Architekturrollen

### 3.1 Foundation

Aufgabe: Schuetzt unveraenderliche Grundsaetze, Identitaet, Leitprinzipien und geschuetzte Regeln.

Verantwortungsbereich:

- Foundation Rules;
- Identity Core;
- Moral Core;
- Foundation Memory;
- Foundation Decision;
- geschuetzte Architekturprinzipien.

Abhaengigkeiten:

- kanonische Memory- und Identity-Quellen;
- Governance- und Review-Nachweise.

Grenzen:

- Foundation fuehrt keine operativen Aufgaben aus;
- Foundation wird nicht fuer Komfortaenderungen angepasst;
- Erweiterungen benoetigen geschuetzte Migration und Benutzerfreigabe.

### 3.2 Canonical Layer

Aufgabe: Definiert verbindliche Systemstruktur, Vertrage, Registries, Architekturmodell und Freigaberegeln.

Verantwortungsbereich:

- kanonische Projektstruktur;
- Architekturmodell;
- Daten- und API-Vertraege;
- Policies wie CADP, CCP, ALP und AGF;
- Release-relevante Manifeste.

Abhaengigkeiten:

- Foundation;
- CAM;
- Release Integrity;
- Dokumentation.

Grenzen:

- ersetzt keine Runtime;
- darf operative Implementierung nur ueber stabile Vertrage steuern.

### 3.3 Canonical Artifact Manager (CAM)

Aufgabe: Verwaltet Projektartefakte, Klassifikation, Speicherorte, Lifecycle und Archivierungsentscheidungen.

Verantwortungsbereich:

- kanonischer Zweck und Speicherort;
- ALP-2.0-Klassen;
- Successor-/Retired-without-Successor-Linie;
- Archivierungs- und Referenzpruefung;
- Artefaktkonflikte.

Abhaengigkeiten:

- AGF;
- ALP;
- CADP;
- Release Integrity;
- Projektstruktur.

Grenzen:

- CAM entscheidet nicht ueber fachliche Agentenantworten;
- CAM verschiebt, loescht oder benennt nichts ohne Freigabe, wenn produktive oder unklare Artefakte betroffen sind.

### 3.4 Capability Resolution Engine (CRE)

Aufgabe: Loest Anforderungen in Faehigkeiten, Kandidaten und Governance-Kontext auf.

Verantwortungsbereich:

- Capability-Erkennung;
- Kandidatenpriorisierung;
- Governance-/Review-/CMM-Vorbereitung;
- read-only Empfehlung.

Abhaengigkeiten:

- CAIM;
- Request Router;
- Governance;
- Capability Registry.

Grenzen:

- CRE fuehrt keine Agenten aus;
- CRE veraendert keine Artefakte;
- CRE ersetzt den Orchestrator nicht.

### 3.5 Execution Planner

Aufgabe: Erstellt pruefbare Ausfuehrungsplaene aus Capability-Resolutionen.

Verantwortungsbereich:

- Planstatus;
- Plan-Schritte;
- Abhaengigkeiten;
- Governance-Kontext;
- Runtime-Vorbereitung.

Abhaengigkeiten:

- CRE;
- Execution-Plan-Schema;
- Governance-Regeln;
- Agenten-/Capability-Information.

Grenzen:

- Planner fuehrt nicht aus;
- Planner entscheidet nicht ueber Archivierung;
- Planner ersetzt keine Runtime-Pruefung.

### 3.6 Orchestrator Core

Aufgabe: Fuehrt freigegebene Plaene regelgebunden aus, sobald die Runtime-Migration freigegeben ist.

Verantwortungsbereich:

- Ausfuehrung geplanter Schritte;
- Agentenauswahl gemaess Plan;
- Fallback-Regeln;
- Runtime-Status;
- Ergebnisstruktur.

Abhaengigkeiten:

- Execution Planner;
- Agenten;
- Governance;
- Runtime-Schema;
- Review.

Grenzen:

- Orchestrator Core erzeugt keine Capabilities;
- Orchestrator Core plant nicht selbst;
- Orchestrator Core darf nicht ohne Feature-Flag oder Freigabe den produktiven Direktpfad ersetzen.

### 3.7 Governance

Aufgabe: Ueberwacht Regelkonformitaet und eskaliert Konflikte.

Verantwortungsbereich:

- Policy-Konformitaet;
- Architekturpruefung;
- Drift-Erkennung;
- Freigabeanforderungen;
- Konfliktbewertung.

Abhaengigkeiten:

- Foundation;
- AGF;
- CAM;
- Release Integrity;
- Review.

Grenzen:

- Governance ersetzt keine Benutzerentscheidung bei kritischen Aenderungen;
- Governance darf keine nicht gepruefte Runtime-Aenderung erzwingen.

### 3.8 Review

Aufgabe: Bewertet Ergebnisse, Wissensuebernahmen, Artefaktentscheidungen und kritische Aenderungen vor Kanonisierung.

Verantwortungsbereich:

- Qualitaetspruefung;
- menschliche oder regelbasierte Freigabe;
- Evidenzbewertung;
- Konfliktklaerung.

Abhaengigkeiten:

- Governance;
- CAM;
- CKDE/CMM;
- Release Evidence.

Grenzen:

- Review ist kein Ersatz fuer Tests;
- Review darf keine Foundation-Regeln umgehen.

### 3.9 Canonical Memory

Aufgabe: Speichert kanonisch freigegebene Identitaets-, Wissens-, Entscheidungs- und Verlaufskontexte.

Verantwortungsbereich:

- kanonische Speicherung;
- Provenienz;
- Review-Uebernahme;
- Gedachtnis- und Identitaetskonsistenz.

Abhaengigkeiten:

- Foundation;
- Review;
- Governance;
- Knowledge-/Memory-Manager.

Grenzen:

- Canonical Memory uebernimmt nichts ungeprueft;
- Runtime-Zwischenergebnisse sind nicht automatisch kanonisch.

## 4. Regeln fuer Architekturaenderungen

### 4.1 Neue Komponente

Eine neue Komponente darf entstehen, wenn alle Bedingungen erfuellt sind:

- klar abgegrenzter Verantwortungsbereich;
- keine unnoetige Duplikation bestehender Verantwortung;
- definierte Abhaengigkeiten und Grenzen;
- dokumentierter Platz in Foundation, Canonical, Operational oder Learning Layer;
- Tests oder nachvollziehbare Verifikationsstrategie;
- CAM-Klassifikation und Speicherort;
- Release-Integrity-Auswirkung bekannt.

Zwingend erforderlich:

- Architekturpruefung;
- CAM-Pruefung;
- Governance-Bewertung;
- Release-Integrity-Pruefung bei Release- oder Runtime-Wirkung;
- Benutzerfreigabe bei Foundation-, Runtime-, Daten- oder Strukturwirkung.

### 4.2 Bestehende Komponente ersetzen

Eine Komponente darf ersetzt werden, wenn ein eindeutiger Successor dokumentiert ist und die bestehende Komponente nicht ungeprueft aus der Runtime entfernt wird.

Pflichten:

- Successor-Linie;
- Abhaengigkeitsanalyse;
- Testabdeckung;
- Fallback- oder Rueckfallstrategie;
- CAM- und ALP-Klassifikation;
- Release-Integrity-Abgleich;
- Dokumentationsupdate.

### 4.3 Komponente archivieren

Eine Komponente darf archiviert werden, wenn ALP 2.0 erfuellt ist:

- Klasse Historical oder Deprecated bestaetigt;
- Successor oder Retired-without-Successor dokumentiert;
- Imports, Tests, Dokumentation, Registry, CAM, Release Integrity, Startskripte, Konfiguration und Feature Flags geprueft;
- Zielarchiv festgelegt;
- Benutzerfreigabe vorliegt, sofern produktive oder unklare Risiken bestehen.

### 4.4 Runtime aendern

Runtime darf nur kontrolliert geaendert werden.

Voraussetzungen:

- Architektur-Baseline;
- Feature-Flag oder Rueckfallpfad;
- Execution- und Runtime-Schema;
- Regressionstests;
- Governance-Freigabe;
- Release-Integrity-Pruefung;
- Benutzerfreigabe.

Planung, CRE und Execution Planner duerfen nicht stillschweigend Runtime ersetzen.

### 4.5 Foundation-Regel erweitern

Foundation-Regeln duerfen nur erweitert werden, wenn:

- die Erweiterung nicht im Widerspruch zu bestehenden Foundation-Regeln steht;
- die Regel dauerhaft und allgemein genug ist;
- Governance und Architekturmodell die Auswirkung pruefen;
- Benutzerfreigabe vorliegt;
- Migration und Rueckwirkung dokumentiert sind.

## 5. Governance-Eskalationsmodell

Architekturkonflikte folgen dieser Eskalationskette:

```text
Regelverstoss
  -> Governance
  -> CAM
  -> Release Integrity
  -> Review
  -> Benutzerentscheidung
```

### LOW

Bedeutung: Lokale Unklarheit ohne Runtime-, Daten-, Release- oder Foundation-Wirkung.

Reaktion:

- dokumentieren;
- CAM-Klassifikation pruefen;
- bei naechster Wartung bereinigen.

Eskalation: Governance-Bericht.

Freigabe: Codex/Governance ausreichend, sofern keine Datei bewegt wird.

### MEDIUM

Bedeutung: Mehrdeutige Artefakte, historische Referenzen, Dokumentationsdrift oder Testunklarheit.

Reaktion:

- CAM-Pruefung;
- Referenzanalyse;
- Migrations-ID und Successor/Endstatus dokumentieren.

Eskalation: Governance + CAM.

Freigabe: Benutzerfreigabe vor Archivierung oder Pfadaenderung.

### HIGH

Bedeutung: Runtime Required, Release Integrity, Tests, Startskripte, aktive Agenten oder Konfigurationsvertraege betroffen.

Reaktion:

- Architekturpruefung;
- CAM- und Release-Integrity-Pruefung;
- Regressionstestplan;
- Rueckfallstrategie.

Eskalation: Governance + CAM + Release Integrity + Review.

Freigabe: ausdrueckliche Benutzerfreigabe erforderlich.

### CRITICAL

Bedeutung: Foundation, Datenverlust, Historienverlust, Sicherheits-/Identitaetskontext, Canonical Memory oder produktive Runtime-Kette betroffen.

Reaktion:

- sofort stoppen;
- keine automatische Aenderung;
- vollstaendige Evidenz sichern;
- Architekturentscheidung vorbereiten;
- manuelle Freigabe einholen.

Eskalation: gesamte Kette bis Benutzerentscheidung.

Freigabe: ausschliesslich Raphael oder ausdruecklich definierte hoechste Governance-Freigabe.

## 6. Release Governance

Ein offizielles Architektur-Release darf nur erfolgen, wenn alle Pflichtbereiche konform sind:

- Foundation: keine Regelverletzung, geschuetzte Regeln konsistent.
- CAM: Artefakte klassifiziert, Speicherorte eindeutig, Lifecycle-Konflikte dokumentiert.
- ALP: Canonical, Runtime Required, Release Evidence, Historical und Deprecated getrennt.
- Architekturmodell: aktuelle Komponenten, Rollen und Pfade dokumentiert.
- Dokumentation: kanonische Dokumente synchronisiert.
- Release Integrity: Required Paths, Allowed Legacy Paths, Tests und Gates plausibel.
- Tests: relevante Regressionen gruend oder begruendet ausgenommen.
- Runtime: Startpfade, Feature Flags, Fallbacks und Runtime-Schemata geprueft.
- Governance: Eskalationen geschlossen oder als offene Risiken dokumentiert.
- Migrationen: Migrationsplan, Migration-IDs, Successor/Endstatus und Freigaben vorhanden.

Ein Release darf nicht erfolgen, wenn kritische Architekturkonflikte offen sind oder wenn Runtime, Foundation, Datenprovenienz oder Release Evidence ungeklaert sind.

## 7. Erweiterungsprozess

Zukuenftige Erweiterungen folgen verbindlich diesem Ablauf:

```text
Idee
  -> Architekturpruefung
  -> Governance-Bewertung
  -> Implementierungsauftrag
  -> Tests
  -> Release Integrity
  -> Freigabe
  -> Canonical
  -> Runtime
```

Regeln:

1. Neue Komponenten duerfen niemals direkt produktiv integriert werden.
2. Jede Erweiterung benoetigt Zweck, Grenzen, Abhaengigkeiten und erwartete Artefaktklasse.
3. Jede Erweiterung mit Runtime-Wirkung benoetigt Feature-Flag oder Fallback.
4. Jede Erweiterung mit Speicherortwirkung benoetigt CAM-Pruefung.
5. Jede Erweiterung mit Release-Wirkung benoetigt Release-Integrity-Pruefung.
6. Jede Erweiterung mit Foundation-Wirkung benoetigt geschuetzte Migration und Benutzerfreigabe.

## 8. Architekturverfassung

Projekt Kontinuum besitzt nicht nur eine Architektur, sondern eine verbindliche Architekturordnung.

### Leitprinzipien

- Foundation schuetzt Identitaet, Regeln und Grundsaetze.
- Canonical Layer definiert die stabilen Vertraege.
- Operational Layer darf austauschbar sein, solange Vertraege eingehalten werden.
- Learning Layer darf dynamisch sein, bleibt aber provenance- und auditpflichtig.
- Jede aktive Datei und Komponente hat einen eindeutigen Zweck und Speicherort.
- Jede Architekturentscheidung ist nachvollziehbar, pruefbar und foundation-kompatibel.

### Architekturphilosophie

Kontinuum waechst nicht durch unkontrollierte Erweiterung, sondern durch kontrollierte Kanonisierung. Neue Faehigkeiten entstehen zuerst als Idee und gepruefter Architekturentwurf, dann als Implementierung, danach als freigegebene kanonische Komponente und erst zuletzt als produktive Runtime.

### Verantwortlichkeiten

- Foundation setzt Grenzen.
- AGF definiert die Architekturordnung.
- CAM ordnet Artefakte.
- ALP regelt Lebenszyklen.
- CCP regelt kanonische Aenderungen.
- CADP schuetzt aktive Ordner.
- CRE loest Faehigkeiten auf.
- Execution Planner plant.
- Orchestrator Core fuehrt freigegebene Plaene aus.
- Governance ueberwacht.
- Release Integrity prueft Freigabe.
- Review bewertet.
- Canonical Memory bewahrt freigegebene Kontinuitaet.

### Schutzmechanismen

- keine Runtime-Aenderung ohne Freigabe;
- keine Archivierung ohne Successor oder Endstatus;
- keine neue Komponente ohne abgegrenzten Verantwortungsbereich;
- keine aktive Datei ohne eindeutigen Zweck und Speicherort;
- keine Release-Freigabe bei offenen kritischen Konflikten;
- keine Foundation-Erweiterung ohne geschuetzte Migration.

### Freigabeprozess

Architekturentscheidungen werden erst kanonisch, wenn sie dokumentiert, geprueft, klassifiziert, getestet oder begruendet ausgenommen, durch Release Integrity bewertet und bei Bedarf von Raphael freigegeben wurden.

## 9. Abschlussregel

AGF 1.0 ist ab seiner Aufnahme in die kanonische Architektur die uebergeordnete Governance-Richtlinie fuer die Weiterentwicklung von Projekt Kontinuum. Es soll die Architektur stabilisieren und den Schwerpunkt kuenftiger Arbeit auf kontrollierte Runtime-Integration, Governance-Operations und funktionalen Ausbau verlagern.
