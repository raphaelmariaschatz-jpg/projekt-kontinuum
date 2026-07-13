# Canonical Development Framework (CDF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: kanonischer Entwicklungsrahmen
Gueltig ab: 2026-07-09
Komponententyp: Dokumentation und Governance
Runtime-Wirkung: keine

## Zweck

Canonical Development Framework (CDF) 1.0 beschreibt, wie Projekt Kontinuum verantwortungsvoll weiterentwickelt wird. CDF dokumentiert nicht, was die Architektur ist, sondern wie Entwicklungsarbeit methodisch, pruefbar und abschliessbar ablaeuft.

CDF ist keine Runtime-Komponente. Es veraendert keine Foundation, keine Agenten, keine APIs, keine Datenbanken, keine Imports, keine Tests und keine Migrationen.

## Einordnung

Die kanonischen Governance-Ebenen bleiben getrennt:

- CMIBF ist die Architekturverfassung und einzige normative Architekturquelle.
- AFP regelt die verbindliche Reihenfolge von Architektur, Ableitung, Implementierung, Release, Betrieb und Evolution.
- CAWP regelt das verbindliche Arbeitsverhalten aller KI-Systeme unterhalb des AFP.
- AGF regelt Architektur-Governance unterhalb des CMIBF.
- CDG regelt Entwicklung.
- CKS regelt Architekturwissen.

CDF steht nicht anstelle von CDG. CDF ist der praktische Entwicklungsrahmen, der CDG-Regeln in Arbeitsphasen, Pruefungen, Rollen und Abschlussformen uebersetzt.

## Beziehung zu CDG

CDG ist die Entwicklungsverfassung mit verbindlichen Regeln und Regel-IDs.

CDF ist das Entwicklungsframework, das beschreibt:

- wann welche CDG-Regeln relevant werden;
- wie Auftraege vorbereitet, bearbeitet und abgeschlossen werden;
- welche Pruefungen vor, waehrend und nach Entwicklungsarbeit erfolgen;
- wie Dokumentation, Statusberichte und Wiedereinstiegspunkte entstehen.

CDG antwortet auf die Frage: Welche Regeln gelten?

CDF antwortet auf die Frage: Wie wird nach diesen Regeln gearbeitet?

## Regelbereiche

### A - Architekturregeln

Architekturregeln beschreiben, wie K aufgebaut ist und welche strukturellen Grenzen nicht verdeckt verschoben werden duerfen.

Beispiele:

- Architektur entsteht ausschliesslich im CMIBF.
- Implementierung darf erst nach CMIBF-Definition, Architekturpruefung, Freigabe und CAC-Verarbeitung erfolgen.
- Code besitzt keine normative Architekturautoritaet.
- Foundation-Kompatibilitaet bleibt oberste Grenze.
- Neue Architekturkomponenten muessen kanonisch eingeordnet werden.
- CRE, Execution Planner und Orchestrator Core behalten getrennte Rollen.
- CCP-Policy und CCP-Cognitive duerfen nicht vermischt werden.

Leitquellen:

- CMIBF 1.0
- Canonical Architecture First Principle
- CAWP 1.0
- AGF 1.0
- Canonical Architecture Model 34.1
- CG 1.0
- CAMap 1.0

### B - Governance-Regeln

Governance-Regeln beschreiben, wie Aenderungen kontrolliert, dokumentiert und freigegeben werden.

Beispiele:

- Change Proposal vor kanonischer Aenderung.
- Pre-Audit vor kontrolliertem Update.
- Release Integrity als Freigabeschwelle.
- Keine automatische Korrektur dokumentierter Inkonsistenzen ohne Auftrag.

Leitquellen:

- CDG 1.0
- AGF 1.0
- ALP 2.0
- CADP 1.0
- CCP-Policy
- Release Integrity

### C - Entwicklungsregeln

Entwicklungsregeln beschreiben, wie Codex und Raphael gemeinsam am Projekt arbeiten.

Beispiele:

- Kanonizitaet vor Geschwindigkeit.
- Konsistenz vor Funktionsumfang.
- Evolution statt Revolution.
- KI-Systeme arbeiten nach CAWP 1.0.
- Dokumentation ist Teil der Architektur.
- Keine parallelen Wahrheiten.
- Kein Stueckwerk ohne Wiedereinstieg.

Leitquellen:

- CAWP 1.0
- CDG 1.0
- Projektchronik
- Roadmap
- CKS 1.0
- Statusberichte

## CDF-Arbeitszyklus

### Phase 1 - Orientierung

Ziel: Auftrag, betroffene Schichten und erlaubte Aenderungsart klaeren.

Pflichtfragen:

- Ist der Auftrag Runtime, Dokumentation, Governance oder Architektur?
- Liegt fuer die beabsichtigte Aenderung eine freigegebene CMIBF-Grundlage vor?
- Muss vor Umsetzung zunaechst eine CMIBF-Definition oder CMIBF-Erweiterung erfolgen?
- Welche kanonischen Begriffe sind betroffen?
- Gibt es bestehende aktive Artefakte fuer denselben Zweck?
- Muss CDG, AGF oder CKS angewendet werden?

AFP-Gate: Ohne eindeutige CMIBF-Abdeckung darf keine Implementierung, kein Test, keine Konfiguration, keine Registry, kein Build und keine abgeleitete Dokumentation entstehen.

### Phase 2 - Konsistenzpruefung

Ziel: bestehende Quellen, Begriffe und Statuslage pruefen, bevor Aenderungen entstehen.

Pflichtpruefungen:

- relevante Dokumente lesen;
- CMIBF-Abdeckung, Freigabestatus und betroffene Architekturregeln pruefen;
- bestehende Begriffe im CG pruefen;
- Architekturbeziehungen in CAMap beachten;
- Entscheidungen im CDI nicht neu erfinden;
- Historie im CHI nur aus vorhandener Dokumentation ableiten.

### Phase 3 - Kanonische Einordnung

Ziel: Aenderung oder neues Artefakt einer Schicht und einem Zweck zuordnen.

Einordnung:

- Architekturwirkung: AGF/CAMap/CDI beachten.
- Entwicklungswirkung: CDG/CDF beachten.
- Wissenswirkung: CKS/CG/CHI beachten.
- Artefaktwirkung: CAM/ALP/CADP beachten.
- Releasewirkung: Release Integrity beachten.

### Phase 4 - Umsetzung

Ziel: nur die erlaubte Aenderung ausfuehren, nachdem CMIBF-Abdeckung, Architekturpruefung, Freigabe und bei Architekturartefakten CAC-Verarbeitung geklaert sind.

Regeln:

- keine verdeckten Nebenwirkungen;
- keine unangeforderten Runtime-Aenderungen;
- keine Dateiverschiebungen ohne ausdruecklichen Auftrag;
- keine neuen APIs, Imports, Tests oder Migrationen bei reinen Dokumentationsauftraegen;
- keine Implementierung ohne freigegebene CMIBF-Grundlage;
- keine Architektur aus bestehendem Code ableiten und ungeprueft kanonisieren;
- keine direkte Bearbeitung abgeleiteter kanonischer Artefakte ohne Rueckfuehrung in das CMIBF;
- bestehende Nutzer- oder Fremdaenderungen nicht zuruecksetzen.

### Phase 5 - Abschlusspruefung

Ziel: Ergebnis pruefbar abschliessen.

Pruefungen je nach Auftrag:

- JSON validieren;
- Markdown stichprobenartig pruefen;
- git diff --check;
- betroffene Dateien nennen;
- Grenzen und nicht ausgefuehrte Aenderungen dokumentieren;
- Statusbericht oder Wiedereinstiegspunkt erstellen, wenn der Auftrag dies verlangt.

## Codex-Arbeitsregeln

CDF 1.0 bindet dauerhafte Codex-Arbeitsregeln fuer Projekt Kontinuum:

- AFP anwenden: Architektur zuerst, Implementierung erst nach CMIBF-Freigabe;
- CMIBF als einzige normative Architekturquelle behandeln;
- CAC als Compiler und Pruefgate behandeln, nicht als freien Generator oder Architekten;
- bestehende kanonische Quellen zuerst lesen;
- keine historischen Dateien ungefragt veraendern;
- CAM, ALP und CADP bei Artefaktfragen beachten;
- AGF bei Architekturwirkung beachten;
- CDG bei Entwicklungswirkung beachten;
- CKS bei Wissenswirkung beachten;
- Release Integrity bei Freigabe- oder Releasewirkung beachten;
- Roadmap und Projektchronik als aktuelle Orientierung verwenden;
- grosse Auftraege phasenweise abschliessen;
- keine halbfertigen Zustaende ohne dokumentierten Wiedereinstiegspunkt hinterlassen.

## Abgrenzung

CDF 1.0 fuehrt keine neue Runtime ein. Es definiert keine neuen Agenten, APIs, Datenbanken, Imports, Tests oder Migrationen. Es ist ein Governance- und Dokumentationsbaustein fuer die Entwicklungsweise von Projekt Kontinuum.

## Status

CDF 1.0 ist kanonisch als Development Framework dokumentiert. CDG 1.0 bleibt das verbindliche Entwicklungsregelwerk.
