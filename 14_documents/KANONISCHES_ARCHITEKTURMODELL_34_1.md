# Kanonisches Architekturmodell 34.1

Kontinuum wird kanonisch aufgebaut, ohne alle Systembereiche gleich starr zu
behandeln. Die Verbindlichkeit richtet sich nach vier Ebenen.

## 1. Foundation Layer

Unveränderliche beziehungsweise nur durch geschützte Migration änderbare
Grundlagen:

- Schöpferwissen und Identity Core
- Foundation Rules und Leitprinzipien
- Foundation 2.2 mit FND-ID-048 als eigenständigem Improvement Principle
- Foundation-2.1-Kompatibilitätspfad für bestehende Importe
- Moral Core
- Foundation Memory

Änderungspolitik: `protected_migration_only`.

## 2. Canonical Layer

Systemweit verbindliche Strukturen:

- genau eine aktive Projektstruktur
- Datenbankschema und öffentliche Kern-APIs
- Agent- und Tool-Registries
- API Registry
- Startpunkte und Ordnerdefinitionen
- Release Integrity
- Canonical Architecture Manager
- Canonical Decision Engine 2.0 als Entscheidungsschicht fuer
  Projektartefakte
- Artefakt-Lifecycle-Policy und Migrationsarchiv
- Internet Knowledge Governance 1.0 als Policy fuer kontrollierte
  Internet-Quellen, Provenienz, Review und Kanon-Uebernahme
- Canonical Knowledge Decision Engine 1.0 als getrennte
  Wissensentscheidungsschicht ohne automatische Kanon-Uebernahme

Änderungspolitik: `release_controlled_migration`.

## 3. Operational Layer

Austauschbare Implementierungen unter stabilen Verträgen:

- Agenten
- Suchsysteme
- GUIs
- Modelle
- Tools und Connectoren
- `InternetLearningService` als deaktivierbarer Hintergrunddienst mit Queue,
  Review-Ablage, Provenienzdatensatz und Bandbreitenkontrolle
- `WebAgentService` als direkter URL-, HTML-Extraktions- und kontrollierter
  Crawl-Dienst mit Review-Uebergabe
- `FileAgentService` als read-only Datei-, Ordner- und Upload-Lernquelle mit
  Extraktion, Hashing und Review-Uebergabe
- `CanonicalKnowledgeDecisionEngine` als reine Bewertungs- und
  Review-Entscheidungsschicht fuer Wissensobjekte

Änderungspolitik: `replaceable_with_contract_checks`.

## 4. Learning Layer

Dynamische, provenance- und auditpflichtige Bereiche:

- Wissen und Forschung
- Chronik
- Lernprojekte
- Wissensgraph
- Internet-Learning-Queue unter `32_data/internet_learning_queue`
- Internet-Learning-Review unter `32_data/internet_learning_review`
- WebAgent-Quellennachweise unter `32_data/web_agent_sources`
- FileAgent-Quellennachweise unter `32_data/file_agent_sources`
- FileAgent-Review-Nachweise unter `32_data/file_agent_review`
- CKDE-Bewertungsbereiche `knowledge_evaluations`, `source_ratings`,
  `knowledge_conflicts` und `evaluation_history`

Änderungspolitik: `dynamic_with_provenance_and_audit`.

## Internet-Learning-Architektur

`InternetLearningService` ist ein kontrollierter Hintergrunddienst. Er liest die
Policy `24_config/internet_learning_policy_34_1.json`, ist kanonisch
standardmaessig aktiviert (`enabled=true`) und wird beim Systemstart automatisch
gestartet. Er arbeitet mit einem Daemon-Thread, kann ueber GUI oder
Konfiguration deaktiviert werden und legt Funde parallel in Queue und
Review-Verzeichnis ab.

Die Policy enthaelt IKG-erlaubte HTTPS-Seed-Quellen aus technischer
Dokumentation und staatlicher Dokumentation. Neue Funde bleiben
reviewpflichtig und werden nicht direkt in den kanonischen Wissensbestand
uebernommen.

Das Queue-System speichert pro Fund URL, Quellenklasse, Titel, Abrufzeit,
SHA-256, Kurzfassung, Bytezahl, Review-Pflicht, Status und Policy-Referenz. Das
Review-System erzeugt dazu einen `pending`-Nachweis. Direkte Memory-Schreibungen
sind deaktiviert (`write_to_memory_directly = false`).

Die Provenienzpflicht wird durch IKG 1.0 ergaenzt:
`24_config/internet_knowledge_governance_1_0.json` definiert erlaubte Quellen,
Vertrauensklassen, automatische Verwerfung, Konfliktregeln, Review-Pflicht,
kanonische Uebernahmeregeln, Sicherheitsregeln und Governance-Regeln. Es gibt
keine automatische Wissensuebernahme aus dem Internet.

Die Bandbreitenkontrolle ist verbindlich: 10 Prozent Policy-Limit, maximal zwei
Requests pro Minute, mindestens zehn Sekunden Abstand, maximal fuenf MB pro
Stunde und maximal 500000 Antwortbytes. Der Status wird in GUI und Systemstatus
als `Internet-Lernen: Aktiv` mit Zustand, Modus, letzter Quelle, Lernzeit, neuen
Funden und aktivem Bandbreitenlimit angezeigt.

## WebAgent 1.0

WebAgent 1.0 ist die direkte URL-Schicht vor Suchmaschinen-Providern. Sobald
eine Nutzereingabe eine `http`- oder `https`-URL enthaelt, wird sie als
WebAgent-Auftrag behandelt und nicht zuerst als lokale Suche, arXiv-,
Semantic-Scholar-, Brave- oder DuckDuckGo-Anfrage interpretiert.

Der WebAgent fuehrt kontrollierte HTTP-GET-Abrufe mit Timeout, User-Agent,
Fehlerbehandlung, Statuscode, Titel, Haupttext, Linkliste, Zeitstempel und
Content-Hash aus. HTML-Seiten werden um Navigation, Footer, Scripts, Styles und
Forms bereinigt; Titel, Ueberschriften, Absaetze, Listen und Codebloecke werden
extrahiert. Jede Quelle wird unter `32_data/web_agent_sources` dokumentiert und
parallel in Queue/Review abgelegt.

Der Crawl-Modus verarbeitet interne Links derselben Domain bevorzugt und ist
durch `max_pages=20`, `max_depth=2`, robots.txt-Pruefung soweit moeglich und
Download-Blockaden fuer grosse binaere Dateitypen begrenzt. Direkte
Memory-Schreibungen und automatische kanonische Wissensuebernahme bleiben
gesperrt. Providerfehler externer Suchdienste blockieren den direkten URL-Abruf
nicht.

## FileAgent 1.0

FileAgent 1.0 ist die kontrollierte Datei- und Ordner-Lernschicht. Befehle wie
`lies Datei`, `lerne aus Datei`, `analysiere Datei`, `importiere PDF als
Lernquelle` und `lerne aus Ordner` werden vor normaler Suche erkannt und als
FileAgent-Auftrag verarbeitet.

Der FileAgent arbeitet read-only, startet keine ausfuehrbaren Dateien und
beschraenkt sich auf freigegebene Projekt- und Importbereiche. Unterstuetzt
werden Text-, Markdown-, JSON-, CSV-, HTML-, PDF-, DOCX-, XLSX-, Code-, Log-,
EPUB- und begrenzt E-Book-Formate wie AZW/AZW3/KFX. Jeder Import speichert
Dateiname, Pfad, Typ, Thema, Kurzinhalt, Volltext-Auszug, SHA-256-Hash,
Dateigroesse, Importzeitpunkt und Lernstatus.

Ordnerimporte sind standardmaessig nicht rekursiv und auf `max_files=50` sowie
`max_file_size=400 MB` begrenzt. Direkte Memory-Schreibungen, Datei-
Veraenderungen, Loeschungen und automatische kanonische Wissensuebernahme sind
ausgeschlossen. Die GUI erlaubt Datei-/Ordnerauswahl ueber Buttons und, wenn
TkDND verfuegbar ist, Drag-and-Drop von Dateien ins Eingabefeld.

Phase 3 Continuous Canonical Governance beobachtet diese Policy-, Queue-,
Review- und Provenienzartefakte als driftpflichtige Learning-/Governance-
Artefakte. Automatisches Loeschen, automatisches Verschieben und automatische
kanonische Wissensuebernahme bleiben ausgeschlossen.

## Kanonische Entscheidungsarchitektur CDE 2.0 / CKDE 1.0

Kontinuum 34.1 trennt zwei Entscheidungswege verbindlich:

```text
Internet
        ↓
Internet Learning
        ↓
IKG 1.0
        ↓
CKDE 1.0
        ↓
Review Queue
        ↓
Governance Review
        ↓
Canonical Knowledge
```

```text
Projektdateien
        ↓
CAM
        ↓
CDE 2.0
        ↓
Archiv / Aktiv / Review
```

CDE 2.0 bleibt ausschliesslich fuer Projektartefakte verantwortlich: Dateien,
Dokumente, Reports, Konfigurationen, Skripte, Manifeste, Projektstruktur,
Archivierung, Konsolidierungsvorschlaege und Review-Markierungen. Die CDE
loescht nicht automatisch, konsolidiert nicht automatisch, schreibt nur
nachvollziehbare Entscheidungen und folgt Canonical Governance.

CKDE 1.0 ist ausschliesslich fuer Wissensobjekte verantwortlich. Sie bewertet
Quellenqualitaet, Evidenz, Aktualitaet, Vollstaendigkeit, Provenienz,
Konsistenz, Governance-Konformitaet, Konflikte und Vertrauensniveau. Die
Entscheidungsklassen sind nur `ACCEPT`, `REVIEW`, `REJECT` und `CONFLICT`.
Auch `ACCEPT` bedeutet keine automatische Uebernahme in den kanonischen
Wissensbestand; die Review Queue und Governance Review bleiben Pflicht.

Die CKDE-Datenhaltung erfolgt append-only, versioniert, auditierbar und
reproduzierbar in `knowledge_evaluations`, `source_ratings`,
`knowledge_conflicts` und `evaluation_history`. Konflikte werden niemals
automatisch entschieden: beide Quellen und Provenienzen bleiben erhalten, der
Konflikt wird protokolliert und Governance Review wird erzeugt.

Das Vertrauensmodell ist erweiterbar und startet mit fuenf Klassen:

- Klasse A: Universitaeten, wissenschaftliche Publikationen, Behoerden,
  offizielle Dokumentationen.
- Klasse B: Fachbuecher, Fachorganisationen, technische Standards.
- Klasse C: etablierte Fachportale, Wikipedia, serioese Nachrichtenquellen.
- Klasse D: Foren, Communitys, Reddit.
- Klasse E: Social Media und unbekannte Quellen.

CAM und CDE bearbeiten den Artefaktpfad. Internet Learning, IKG und CKDE
bearbeiten den Wissenspfad. Continuous Canonical Governance beobachtet beide
Pfade als getrennte Governance-Domaenen. Das Release Integrity Framework
verifiziert die Pflichtartefakte, Policies, Datenbankvertraege und Tests,
entscheidet aber nicht fachlich ueber Wissen oder Artefaktlebenszyklen.

## Canonical Architecture Manager 1.1

CAM ist eine read-only prüfende Kernkomponente. Er:

- erkennt mehrere aktive Projektstrukturen;
- prüft das historische Projektstrukturarchiv;
- prüft kanonische Startpunkte, Ordner und Registries;
- prüft definierte API-Symbole;
- prüft das erforderliche Datenbankschema;
- bildet alle vier Architekturebenen mit eigener Änderungspolitik ab;
- überwacht die verbindliche Artifact Lifecycle Policy samt Archivpfaden,
  fünf Freigabebedingungen und dauerhaft aufbewahrten signierten Nachweisen;
- liefert eine blockierende Prüfung an Release Integrity.

CAM nimmt keine selbstständigen Architekturänderungen vor. Archivierungen und
sonstige Änderungen erfolgen ausschließlich über kontrollierte Migrationen.

## Artefakt-Lifecycle

Wertvolle Test-, Migrations-, Architektur-, Release-, Verifikations- und
Audit-Artefakte bleiben bis zur vollständigen Freigabe erhalten. Eine
Archivierung ist erst zulässig, wenn Tests, Statusprüfung und Release-Gate grün
sind, die Dokumentation aktualisiert wurde und Codex die Freigabe bestätigt
hat. Danach werden wichtige Artefakte unter
`02_versions/migration_artifacts/` oder `09_backups/migration_reports/`
archiviert. Automatisches Löschen bleibt ausgeschlossen.

Dieser Ausbau wird als `CAM 1.1 – Artifact Lifecycle Policy` geführt. Die
weiteren CAM-Ausbaustufen sind Canonical Database Manager, Canonical API
Registry und Canonical Artifact Manager.

## CAM 1.2 – Canonical Database Manager

Der Canonical Database Manager überwacht die aktive SQLite-Datenbank
read-only anhand eines versionierten Vertrags unter
`24_config/canonical_database_34_1.json`.

Er prüft:

- `PRAGMA integrity_check`;
- kanonische Kern- und Fachtabellen;
- Spaltenverträge zentraler Foundation-, Memory- und Suchtabellen;
- erforderliche Indizes;
- Append-only-Schutztrigger;
- die FTS5-Struktur der Dateisuche;
- Foundation-, Memory-, Knowledge- und Search-Datendomänen.

Zusätzliche legitime Tabellen bleiben zulässig und werden als nicht
kanonisch verwaltete Erweiterungen sichtbar ausgewiesen. CAM 1.2 verändert
keine Datenbankobjekte. Schemaänderungen erfolgen ausschließlich durch
kontrollierte, getestete und freigegebene Migrationen.

Reproduzierbare Cache- und Build-Artefakte wie `__pycache__`, `.pytest_cache`,
Python-Bytecode und temporäre Entpackverzeichnisse dürfen nach sicherer
Pfadprüfung entfernt werden.

## Phase 3 – Continuous Canonical Governance

Phase 3 etabliert ein dauerhaftes Canonical Governance System. Es klassifiziert
neue oder geaenderte Artefakte unmittelbar als `active`, `archive_candidate`,
`review` oder `consolidate_suggest`, protokolliert Entscheidungen unter
`31_reports/governance/phase3_continuous_governance_log.jsonl` und bindet
Canonical Architecture Manager, Canonical Artifact Manager und Release Integrity
Status in eine kontinuierliche Verifikationsschleife ein.

Diese Schicht ist read-only gegenueber der Projektstruktur: keine automatische
Loeschung, keine automatische Migration und keine unverifizierte Struktur-
veraenderung. Phase 2 bleibt abgeschlossen; Phase 3 verhindert Drift.

## Continuous Canonical Engine 1.0

Die Continuous Canonical Engine bildet die technische Phase-3-Schleife zwischen
Event Bus, CDE 2.0, Drift Layer, Governance Hooks und Release Integrity. Sie ist
lokal, append-only und diagnostisch aktiv.

Kanonischer Ablauf:

```text
System Event -> Event Bus -> Canonical Decision Engine -> Drift Layer -> Governance Hooks -> Review/Gate/Release Decision
```

Architekturschichten:

- Canonical: `24_config/continuous_canonical_engine_34_1.json`
- Operational: `01_system/kontinuum/core/continuous_canonical_engine.py`
- Learning/Audit: `31_reports/events/*.jsonl`,
  `31_reports/drift/drift_events.jsonl`,
  `31_reports/governance/governance_hooks.jsonl`

Das Release Integrity Framework nutzt
`continuous_canonical_engine_check()`. HIGH_DRIFT und BLOCKING_DRIFT blockieren
die Release-Freigabe; EXPECTED_DRIFT bleibt zulaessig, solange keine offenen
Hooks oder blockierenden Findings vorliegen.
