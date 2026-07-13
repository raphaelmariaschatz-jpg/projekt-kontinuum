# Canonical Development Governance (CDG) 1.0

> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

Status: kanonisches Entwicklungsregelwerk
Gueltig ab: 2026-07-09
Version: 34.1
Geltungsbereich: alle zukuenftigen Codex-Auftraege fuer Projekt Kontinuum

## Zweck

Canonical Development Governance (CDG) 1.0 ist die Entwicklungsverfassung von Projekt Kontinuum. CDG beschreibt nicht, wie Kontinuum funktioniert, sondern nach welchen verbindlichen Regeln Kontinuum kuenftig weiterentwickelt wird.

CDG ist eine Governance-Ebene oberhalb der Implementierung. Es veraendert keine Runtime, keine Architektur, keine Datenbanken, keine APIs, keine Imports, keine Tests und keine Agenten.

## Beziehung zu AGF

Das Architecture Governance Framework (AGF) definiert die Regeln der Architektur. CDG definiert die Regeln ihrer Weiterentwicklung. Beide Systeme ergaenzen sich: AGF schuetzt Struktur und Rollen, CDG schuetzt die Arbeitsweise, nach der neue Aenderungen entstehen, geprueft, dokumentiert und abgeschlossen werden.

Seit der kanonischen Uebernahme des Canonical Master Implementation Blueprint Framework (CMIBF) 1.0 gilt ergaenzend: Das CMIBF ist die einzige normative Architekturquelle und Architekturverfassung von Projekt Kontinuum. AGF und CDG sind Governance- und Entwicklungsrahmen unterhalb des CMIBF. Sie duerfen keine Architektur definieren, ersetzen oder erweitern, die nicht im CMIBF definiert, geprueft und freigegeben wurde.

## Beziehung zu CAWP

Das Canonical AI Working Protocol (CAWP) 1.0 definiert das verbindliche Arbeitsverhalten aller KI-Systeme in Projekt Kontinuum. CAWP steht in der Governance-Hierarchie direkt unter dem AFP und vor der technischen Ableitung durch den CAC.

CDG regelt Entwicklungsgovernance. CAWP regelt, wie KI-Systeme diese Governance in Analyse, Kommunikation, Umsetzung, Review, Traceability, Fehlerkultur und Abschlussberichten befolgen. CAWP erzeugt keine eigene Architekturautoritaet und ersetzt keine CDG-Regeln.

## Architecture First Principle

Das Canonical Architecture First Principle (AFP) ist fuer alle Entwicklungsauftraege verbindlich:

```text
Idee
-> Architekturanalyse
-> CMIBF-Definition oder CMIBF-Erweiterung
-> Architekturpruefung
-> Freigabe
-> CAC
-> kanonische Artefakte
-> Implementierung
-> Validierung und Tests
-> Release
-> Betrieb
-> Monitoring
-> kontrollierte Evolution
```

Implementierung darf nicht beginnen, bevor eine gueltige und freigegebene CMIBF-Grundlage vorliegt. Code besitzt keine normative Architekturautoritaet. Erkenntnisse aus Implementierung, Betrieb oder Monitoring muessen als Architekturanalyse in den AFP-Zyklus zurueckgefuehrt werden und duerfen nicht direkt neue Architektur im Code erzeugen.

## Quellenkonsolidierung

CDG 1.0 fuehrt dauerhaft gueltige Entwicklungsregeln aus bestehenden kanonischen Quellen zusammen, insbesondere AGF 1.0, CAM, ALP 2.0, CADP 1.0, CCP 1.0, Release Integrity, Phase 3 Continuous Canonical Governance, Projektchronik, Handbuch, Architekturmodell, CIPL 1.0 und bisherigen Codex-Auftraegen.

Einmalige Arbeitsanweisungen, konkrete Tagesauftraege und erledigte Sonderfaelle werden nicht als CDG-Regeln uebernommen.

## Kategorien

- A: Grundprinzipien
- B: Entwicklungsregeln
- C: Governance-Regeln
- D: Dokumentationsregeln
- E: Qualitaetsregeln
- F: Grossauftraege

## Regeln

### CDG-001 - Kanonizitaet vor Geschwindigkeit

Kategorie: A - Grundprinzipien

Entwicklungsentscheidungen bevorzugen kanonische Klarheit, stabile Einordnung und nachvollziehbare Governance gegenueber schneller, aber mehrdeutiger Umsetzung.

Status: active; verpflichtend: true

### CDG-001A - Architecture First Principle

Kategorie: A - Grundprinzipien

Architektur muss vor Implementierung entstehen. Jede Entwicklung beginnt mit Architekturanalyse und CMIBF-Abdeckung; Implementierung, Tests, Release und Betrieb duerfen erst nach Architekturpruefung, Freigabe und CAC-Verarbeitung folgen.

Status: active; verpflichtend: true

### CDG-001B - CMIBF als Architekturautoritaet

Kategorie: A - Grundprinzipien

Das CMIBF ist die einzige normative Architekturquelle und Architekturverfassung. Dokumente, Code, Tests, Konfigurationen, Registries, Reports, Dependency Graphs und Ontologien sind ohne korrekte CMIBF-Ableitung nicht normativ.

Status: active; verpflichtend: true

### CDG-001C - CAC als Compiler

Kategorie: A - Grundprinzipien

Der Canonical Architecture Compiler ist ausschliesslich Compiler und Pruefinstanz. Er liest das CMIBF, prueft Syntax, Semantik, Regeln, Inkonsistenzen und AFP-Konformitaet und erzeugt nur deterministische Ableitungen. Er darf keine Architekturentscheidung erfinden.

Status: active; verpflichtend: true

### CDG-001D - CAWP als KI-Arbeitsprotokoll

Kategorie: A - Grundprinzipien

Alle KI-Systeme muessen bei Arbeiten an Projekt Kontinuum das Canonical AI Working Protocol anwenden. CAWP definiert Arbeitsverhalten, Kommunikationsregeln, Architekturdisziplin, Traceability, Qualitaets-Gates und Fehlerkultur der KI-Systeme, ohne eigene Architekturprinzipien zu erzeugen.

Status: active; verpflichtend: true

### CDG-002 - Konsistenz vor Funktionsumfang

Kategorie: A - Grundprinzipien

Neue Funktionen oder Erweiterungen duerfen nur wachsen, wenn bestehende Struktur, Dokumentation, Manifeste und Governance konsistent bleiben.

Status: active; verpflichtend: true

### CDG-003 - Evolution statt Revolution

Kategorie: A - Grundprinzipien

Projekt Kontinuum wird kontrolliert erweitert. Bestehende kanonische Schichten werden nicht durch verdeckte oder abrupte Umbrueche ersetzt.

Status: active; verpflichtend: true

### CDG-004 - Dokumentation ist Teil der Architektur

Kategorie: A - Grundprinzipien

Dokumentation, Manifeste, Chronik und Abschlussberichte sind nicht nachgeordnet, sondern Bestandteil der kanonischen Entwicklung.

Status: active; verpflichtend: true

### CDG-005 - Foundation-Kompatibilitaet bleibt oberste Grenze

Kategorie: A - Grundprinzipien

Jede dauerhafte Entwicklungsentscheidung muss mit Foundation-Regeln, Leitprinzipien und geschuetzten Identitaets-/Memory-Grenzen vereinbar sein.

Status: active; verpflichtend: true

### CDG-006 - Eine aktive Wahrheit pro Zweck

Kategorie: B - Entwicklungsregeln

Aktive Projektbereiche duerfen keine parallelen kanonischen Wahrheiten fuer denselben Zweck enthalten. Historie gehoert in definierte Archiv- oder Chronikbereiche.

Status: active; verpflichtend: true

### CDG-007 - Jede aktive Datei hat Zweck und Speicherort

Kategorie: B - Entwicklungsregeln

Aktive Dateien muessen einen eindeutigen kanonischen Zweck und einen eindeutigen kanonischen Speicherort besitzen.

Status: active; verpflichtend: true

### CDG-008 - Keine verdeckten Architekturaenderungen

Kategorie: B - Entwicklungsregeln

Architekturwirkung muss sichtbar dokumentiert, begruendet, auf das CMIBF zurueckgefuehrt und governance-konform eingeordnet werden. Verdeckte Architekturaenderungen sind unzulaessig. Refactorings mit Architekturwirkung benoetigen vorab eine CMIBF-Grundlage und Freigabe.

Status: active; verpflichtend: true

### CDG-009 - Planung und Runtime bleiben getrennt

Kategorie: B - Entwicklungsregeln

Planungs-, Resolver- und Governance-Schichten duerfen nicht heimlich Runtime-Verhalten ersetzen oder produktive Ausfuehrung starten.

Status: active; verpflichtend: true

### CDG-010 - Read-only bleibt read-only

Kategorie: B - Entwicklungsregeln

Diagnose-, Pruef-, Resolver-, Learning- und Governance-Komponenten mit read-only-Status duerfen keine produktiven Aenderungen ausloesen.

Status: active; verpflichtend: true

### CDG-011 - Historische Nachvollziehbarkeit erhalten

Kategorie: B - Entwicklungsregeln

Aenderungen muessen ueber Git, Chronik, Reports, Manifeste oder Governance-Nachweise spaeter nachvollziehbar bleiben.

Status: active; verpflichtend: true

### CDG-012 - Keine automatische Wissensuebernahme

Kategorie: B - Entwicklungsregeln

Externe Quellen, Lernfunde und Wissensobjekte werden nicht automatisch in kanonisches Wissen oder Memory uebernommen.

Status: active; verpflichtend: true

### CDG-013 - Change Proposal vor kanonischer Aenderung

Kategorie: C - Governance-Regeln

Kanonische Aenderungen benoetigen erkennbare Aenderungsabsicht, Begruendung, betroffene Komponente, erwartete Auswirkungen und Folgepruefungen.

Status: active; verpflichtend: true

### CDG-014 - Pre-Audit vor kontrolliertem Update

Kategorie: C - Governance-Regeln

Vor kontrollierten kanonischen Updates sind Pfade, Architekturbegriffe, aktive Duplikate, Legacy-Verweise, CADP-Verletzungen und Foundation-Konflikte zu pruefen.

Status: active; verpflichtend: true

### CDG-015 - Governance Review fuer kanonische Wirkung

Kategorie: C - Governance-Regeln

Aenderungen mit kanonischer oder architektureller Wirkung muessen Foundation-Kompatibilitaet, Architekturmodell, Policy-Konformitaet, Drift-Risiko und Dokumentationsfolgen pruefen.

Status: active; verpflichtend: true

### CDG-016 - Release Integrity als Freigabeschwelle

Kategorie: C - Governance-Regeln

Release-relevante Aenderungen muessen Tests, Status, Release Gate, Dokumentation, Pflichtdateien und erlaubte Legacy-Pfade pruefbar bestehen oder begruendet dokumentieren.

Status: active; verpflichtend: true

### CDG-017 - CAM prueft Artefakte, nicht Fachantworten

Kategorie: C - Governance-Regeln

CAM ist fuer Artefaktklassifikation, kanonischen Speicherort, Lifecycle, Referenzen und Archivierungsentscheidungen zustaendig, nicht fuer operative Fachantworten.

Status: active; verpflichtend: true

### CDG-018 - Archivierung statt Loeschung

Kategorie: C - Governance-Regeln

Historisch relevante Dateien, Reports, Logs und Nachweise werden archiviert. Loeschungen erfolgen nur nach ausdruecklicher manueller Freigabe.

Status: active; verpflichtend: true

### CDG-019 - Aktive Ordner bleiben kanonisch rein

Kategorie: C - Governance-Regeln

Aktive Hauptordner enthalten nur aktuelle produktive oder kanonische Artefakte; historische Versionen gehoeren in Archive oder ausgewiesene Chronikbereiche.

Status: active; verpflichtend: true

### CDG-020 - Dokumentationssync ist Pflicht

Kategorie: D - Dokumentationsregeln

Nach Aenderungen mit Architektur-, Pfad-, Manifest-, Start-, Test- oder Governance-Wirkung muessen betroffene Dokumente synchronisiert werden.

Status: active; verpflichtend: true

### CDG-021 - Projektchronik bleibt historische Spur

Kategorie: D - Dokumentationsregeln

Wesentliche Entwicklungsmeilensteine, Governance-Entscheidungen, Releases und offene Punkte muessen in Chronik- oder Release-Dokumenten nachvollziehbar bleiben.

Status: active; verpflichtend: true

### CDG-022 - Wiedereinstiegspunkt nach Phasenarbeit

Kategorie: D - Dokumentationsregeln

Nach groesseren Arbeitsphasen muss ein kanonischer Wiedereinstiegspunkt oder Abschlussbericht den aktuellen Stand, offene Punkte und naechste Schritte festhalten.

Status: active; verpflichtend: true

### CDG-023 - Abschlussberichte nennen geaenderte Artefakte

Kategorie: D - Dokumentationsregeln

Abschlussberichte muessen neu angelegte und aktualisierte Dateien, Integrationswirkung, offene Punkte und bestaetigte Nicht-Aenderungen sichtbar ausweisen.

Status: active; verpflichtend: true

### CDG-024 - Kanonische Manifeste bleiben maschinenlesbar

Kategorie: D - Dokumentationsregeln

JSON-Manifeste muessen gueltig, strukturiert, spaeter automatisierbar auswertbar und mit menschenlesbarer Dokumentation konsistent sein.

Status: active; verpflichtend: true

### CDG-025 - Konsistenzpruefung vor Abschluss

Kategorie: E - Qualitaetsregeln

Vor Abschluss eines Auftrags sind betroffene Dokumente, Manifeste, Pfade, Referenzen und erklaerte Grenzen auf Konsistenz zu pruefen.

Status: active; verpflichtend: true

### CDG-026 - Regression darf nicht verdeckt entstehen

Kategorie: E - Qualitaetsregeln

Funktionale Aenderungen erfordern angemessene Verifikation. Dokumentationsauftraege muessen ausdruecklich bestaetigen, dass keine Runtime betroffen ist.

Status: active; verpflichtend: true

### CDG-027 - Drift sichtbar machen

Kategorie: E - Qualitaetsregeln

Abweichungen von Baseline, Struktur, Governance oder Dokumentationsstand werden nicht verdeckt, sondern als Drift, Review-Bedarf oder offene Arbeit dokumentiert.

Status: active; verpflichtend: true

### CDG-028 - Keine ungueltigen Referenzen zuruecklassen

Kategorie: E - Qualitaetsregeln

Nach Archivierung, Umbenennung, Kanonisierung oder Dokumentationssync duerfen aktive Dokumente, Manifeste, Skripte und Tests keine ungueltigen Pfade enthalten.

Status: active; verpflichtend: true

### CDG-029 - Grossauftraege phasenweise bearbeiten

Kategorie: F - Grossauftraege

Umfangreiche Codex-Auftraege werden in klaren Phasen bearbeitet. Jede Phase hat Ziel, Ergebnis, Pruefung und dokumentierten Abschluss.

Status: active; verpflichtend: true

### CDG-030 - Keine neue Phase bei offenem Abschluss

Kategorie: F - Grossauftraege

Eine neue Phase beginnt erst, wenn die aktuelle Phase vollstaendig abgeschlossen, geprueft oder als offen dokumentiert wurde.

Status: active; verpflichtend: true

### CDG-031 - Kein Stueckwerk ohne Wiedereinstieg

Kategorie: F - Grossauftraege

Wenn ein Grossauftrag nicht vollstaendig abgeschlossen werden kann, muessen offene Arbeiten, Risiken, naechste Schritte und ein kanonischer Wiedereinstiegspunkt dokumentiert werden.

Status: active; verpflichtend: true

### CDG-032 - Auftragsgrenzen respektieren

Kategorie: F - Grossauftraege

Codex-Auftraege duerfen nicht nebenbei Runtime, Architektur, Datenbanken, APIs, Imports, Tests, Agenten oder Migrationen veraendern, wenn der Auftrag dies ausschliesst.

Status: active; verpflichtend: true

## Fortschreibungsregeln

Neue dauerhafte Entwicklungsregeln duerfen nur durch definierte Governance-Prozesse ergaenzt oder geaendert werden. Jede neue Regel benoetigt eine neue Regel-ID, eine Begruendung, einen Projektchronik-Eintrag und eine Versionshistorie.

Bestehende CDG-Regeln duerfen niemals stillschweigend geaendert werden. Aenderungen muessen nachvollziehbar, versioniert und mit AGF, Foundation, CAM, ALP, CADP, CCP und Release Integrity vereinbar sein.

## Maschinenlesbare Grundlage

Die maschinenlesbare kanonische Grundlage liegt unter:

```text
24_config/canonical_development_governance_34_1.json
```

## Abschlusspruefung fuer CDG 1.0

- Es wurden ausschliesslich Dokumentations- und Governance-Artefakte erstellt.
- Keine Runtime-Dateien wurden fuer CDG 1.0 veraendert.
- Keine Datenbanken wurden geaendert.
- Keine Imports wurden geaendert.
- Keine Tests wurden geaendert.
- Keine Agenten wurden geaendert.
- Keine Commits wurden erstellt.
