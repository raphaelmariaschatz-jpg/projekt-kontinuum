# Projektstruktur 34.1 – Release Integrity Framework

Stand: 2026-07-03

Kontinuum 34.1 übernimmt Foundation Reasoning 4.1 unverändert aus der Vorversion
und ergänzt ein technisch erzwungenes Release Integrity Framework 1.0 sowie den
Canonical Architecture Manager 1.0.

## Kanonische Dokumentationsstruktur

- `14_documents/PROJEKTSTRUKTUR_34_1.md` ist die einzige aktive und kanonische
  Projektstruktur.
- `02_versions/projektstrukturen/` enthält die historischen
  `PROJEKTSTRUKTUR_*`-Stände ab 24.3.
- `14_documents/KANONISCHES_ARCHITEKTURMODELL_34_1.md` definiert Foundation,
  Canonical, Operational und Learning Layer.
- Mehrere aktive Projektstrukturdateien blockieren Release Integrity.

## Kanonische GUI-Struktur

- `11_gui/desktop_gui.py`: einziger kanonischer produktiver GUI-Einstieg
- `11_gui/desktop_gui_34_1.py`: aktuelle versionsgebundene Implementierung
- `11_gui/gui_manifest.json`: kanonisches aktives GUI-Manifest
- `11_gui/README_GUI.md`: Betriebs- und Archivregel
- `11_gui/archive/<version>/`: historische ausführbare GUIs und Manifeste
- `16_installation/START_GUI.bat`: kanonischer GUI-Starter

Historische versionierte Starter sind ausschließlich Kompatibilitätsweiterleitungen
auf `START_GUI.bat`; sie starten keine archivierte GUI.

## Dauerhafte Archivstruktur

Jeder aktive Hauptordner besitzt einen kanonischen Unterordner `archive`.
Der aktive Bereich bleibt produktiven oder kanonischen Dateien vorbehalten.
Historische Releases, ersetzte Dokumente, Vorgängerversionen, abgeschlossene
Migrationen, veraltete Reports, historische Statusdateien, nicht mehr aktive
Tests und Legacy-Artefakte werden nach Sicherheitsprüfung in das jeweilige
`archive` verschoben.

Archivierung löst immer eine Referenzprüfung aus: Dokumentationen, Manifeste,
Registries, Konfigurationen, Startskripte, Tests, Build-Prozesse und
Release-Dateien müssen danach gültige Pfade enthalten. Löschungen erfolgen nur
auf ausdrückliche Anweisung von Raphael.

## Release-Gates

Eine Freigabe wird nur erteilt, wenn alle verbindlichen Gates erfolgreich sind:

1. signierte SHA-256-Baseline aller aktiven Runtime-, Test- und Release-Dateien;
2. signierter Audit-Snapshot mit Pflichtpfaden und SQLite-Integritätsprüfung;
3. erzeugtes und vollständig hashverifiziertes Release-Backup;
4. Rollback-Probe durch Wiederherstellung in ein temporäres Verzeichnis;
5. Altversionssuche über aktive Pfade mit expliziter historischer Allowlist;
6. vollständige aktive Testsuite mit festem Zeitlimit pro Test;
7. Versions-, Manifest-, Datei- und Einstiegspfadkonsistenz;
8. vorhandene Releasechronik und kanonische Wiedereinstiegspunkte.
9. vollständige Foundation-Core-Pflichtprüfung einschließlich FND-ID-048 und
   FND-ID-049 / CADP 1.0 und FND-ID-050 / CCP 1.0;
10. Foundation 2.2 als aktives Kernmodul mit schmalem
    Foundation-2.1-Kompatibilitätspfad;
11. CAM-1.1-Prüfung der Artifact Lifecycle Policy, Archivpfade,
    Freigabebedingungen und signierten Nachweise.
12. CAM-Pruefung von CADP 1.0: aktive Projektordner enthalten nur kanonische
    Dateien; historische Artefakte liegen in `archive`; Referenzen, doppelte
    aktive Versionen, verwaiste Pfade und Manifest-/Dateisystem-Konsistenz
    werden geprueft.
12. CAM-1.2-Prüfung des kanonischen SQLite-Vertrags einschließlich Tabellen,
    Spalten, Indizes, Trigger, FTS und Datendomänen.
10. CAM-Prüfung von Projektstruktur, Archiv, APIs, Startpunkten, Ordnern,
    Registries, Datenbankschema und den vier Architekturebenen.
11. kanonischer Root-Startpfad `START_KONTINUUM.bat` vorhanden und auf
    `PYTHONPATH=C:\Projekt Kontinuum\01_system` sowie `python -m kontinuum`
    festgelegt; `main.py` und `python -m 01_system.kontinuum` bleiben veraltet.

Nur wenn alle Gates `true` sind, enthält der signierte Bericht:

```text
Status: VERIFIZIERT
Freigabe: JA
```

## Komponenten

- `core/release_integrity.py`: Nachweis-, Backup-, Restore- und Gate-Logik
- `core/canonical_architecture.py`: read-only Canonical Architecture Manager
- `24_config/canonical_architecture_34_1.json`: kanonisches Architekturmanifest
- `01_system/kontinuum/core/foundation_2_2.py`: aktives Foundation-Kernmodul
- `01_system/kontinuum/core/foundation_2_1.py`: Kompatibilitäts-Re-Export
- `FND-ID-049`: CADP 1.0 als Foundation-Regel fuer kanonisch reine aktive
  Projektordner
- `01_system/kontinuum/core/canonical_database.py`: read-only Canonical
  Database Manager 1.2
- `24_config/canonical_decision_engine_2_0.json`: CDE-2.0-Policy fuer
  Projektartefaktentscheidungen
- `01_system/kontinuum/core/canonical_knowledge_decision.py`: CKDE-1.0-
  Bewertungs- und Entscheidungsschicht fuer Wissensobjekte
- `24_config/canonical_knowledge_decision_engine_1_0.json`: CKDE-1.0-Policy
  ohne automatische kanonische Wissensuebernahme
- `24_config/canonical_database_34_1.json`: kanonischer Datenbankvertrag
- `24_config/release_integrity_34_1.json`: verbindliche Gate-Konfiguration
- `13_tools/release_integrity_34_1.py`: ausführbarer Gate-Runner
- `13_tools/status_check_34_1.py`: konsumiert und validiert den Gate-Nachweis
- `16_installation/RELEASE_GATE_34_1.bat`: kanonischer Release-Einstieg
- `16_installation/TEST_KONTINUUM_34_1.bat`: vollständige Verifikation
- `START_KONTINUUM.bat`: kanonischer CLI-Start im Projektstamm
- `24_config/internet_learning_policy_34_1.json`: Internet-Learning-Policy
- `24_config/internet_knowledge_governance_1_0.json`: IKG-1.0-Policy ohne
  automatische Wissensuebernahme
- `01_system/kontinuum/core/web_agent.py`: WebAgent 1.0 fuer direkte URL-
  Abrufe, HTML-Extraktion, Linkerkennung und kontrolliertes Crawling
- `24_config/web_agent_1_0.json`: WebAgent-Policy mit diagnostischem
  Review-Modus, Crawl-Limits und Providerliste
- `01_system/kontinuum/core/file_agent.py`: FileAgent 1.0 fuer read-only
  Datei-, Ordner- und Upload-Lernquellen
- `24_config/file_agent_1_0.json`: FileAgent-Policy mit erlaubten Wurzeln,
  Dateitypen, Groessenlimit und Review-Modus
- `01_system/kontinuum/core/capability_resolution_engine.py`: Capability
  Resolution Engine 1.0 als read-only Empfehlungs- und Priorisierungsschicht
  zwischen Request Router, CAIM, Governance, Agenten, Review und CMM
- `14_documents/CAPABILITY_RESOLUTION_ENGINE_1_0.md`: technische
  CRE-Architekturdokumentation
- `01_system/kontinuum/core/application_services.py`: heutiger
  PromptOrchestrator und Migrationsanker fuer Orchestrator Core 1.0
- `32_data/internet_learning_queue/`: Queue fuer neue Internet-Learning-Funde
- `32_data/internet_learning_review/`: Review-Ablage fuer pending Funde
- `32_data/web_agent_sources/`: gespeicherte WebAgent-Quellennachweise mit URL,
  Titel, Thema, Hash, Zeitstempel, Kurzinhalt und Lernzusammenfassung
- `32_data/file_agent_sources/`: gespeicherte FileAgent-Quellennachweise mit
  Dateiname, Pfad, Typ, Thema, Hash, Importdatum und Auszug
- `32_data/file_agent_review/`: Review-Nachweise fuer gelesene Dateien
- `knowledge_evaluations`, `source_ratings`, `knowledge_conflicts`,
  `evaluation_history`: append-only CKDE-Bewertungsbereiche in der
  kanonischen SQLite-Datenbank
- `17_tests/test_internet_learning_34_1.py`: Internet-Learning-, Queue-,
  Review- und Provenienztests
- `17_tests/test_canonical_decision_architecture_34_1.py`: CDE-/CKDE-
  Architektur-, Scope-, Entscheidungs- und Append-only-Tests
- `17_tests/test_web_agent_1_0.py`: WebAgent-URL-, Crawl-, Status-,
  Speicher- und Mathe-Regressionsabnahme
- `17_tests/test_file_agent_1_0.py`: FileAgent-Datei-, Ordner-, PDF-,
  Duplikat-, Pfadschutz- und Statusabnahme
- `17_tests/test_gui_internet_routing_34_1.py`: GUI-/Routingtests
- `31_reports/governance/phase3/`: Governance-, Drift-, Integrity- und
  Compliance-Reports
- `31_reports/release_integrity/34.1/`: signierte Baseline-, Audit- und Gate-Berichte
- `09_backups/release_integrity/`: verifizierte Release-Backups

## Internet-Learning und IKG 1.0

Internet-Learning ist als kontrollierte Learning-Layer-Erweiterung kanonisiert.
Der Dienst ist standardmaessig aktiviert, startet beim Systemstart automatisch,
arbeitet nur nach Policy, nutzt Queue und Review, erzeugt Provenienznachweise
und bleibt vom kanonischen Memory-Schreiben getrennt. IKG 1.0 klassifiziert
erlaubte Quellen, verwirft blockierte Quellen automatisch, fordert Review bei
widerspruechlichen Quellen und erlaubt kanonische Uebernahme nur nach
menschlicher Pruefung, vollstaendiger Provenienz und Governance-Nachweis. Eine
Deaktivierung ist jederzeit ueber GUI oder `24_config/internet_learning_policy_34_1.json`
moeglich.

Die technische Policy enthaelt IKG-erlaubte HTTPS-Seed-Quellen. Diese Quellen
duerfen nur in Queue und Review geschrieben werden; Memory- oder Kanon-
Uebernahme bleibt bis zur erfolgreichen Bewertung gesperrt.

## WebAgent 1.0

Der WebAgent ist die direkte URL-Faehigkeit von Kontinuum. Eingaben wie
`lerne auch hier: <URL>`, `lies diese Webseite: <URL>`, `nutze zum Lernen auch
<URL>` oder `oeffne nacheinander alle Links ... <URL>` werden vor lokaler Suche
und vor Suchmaschinen-Providern verarbeitet.

Der WebAgent ruft HTML- und Textseiten per HTTP-GET ab, extrahiert Titel,
Ueberschriften, Absaetze, Listen, Codebloecke und Links, erzeugt eine
Kurz-Zusammenfassung sowie eine Lernzusammenfassung und speichert
Quellennachweise mit URL, Titel, Thema, Hash und Zeitstempel. Inhalte werden in
Review/Queue uebergeben und als Quellen referenziert; direkte Memory- oder
kanonische Wissensuebernahme bleibt im Standardmodus blockiert.

Der Befehl `webagentstatus` zeigt Aktivstatus, letzten Abruf, letzte URL,
Fehler, gespeicherte Webquellen, Crawl-Limits und Provider. Crawl-Auftraege
sind durch `max_pages=20`, `max_depth=2`, gleiche Domain, robots.txt soweit
moeglich und Download-Blockaden begrenzt.

## FileAgent 1.0

Der FileAgent ist die direkte Datei- und Ordner-Lernfaehigkeit von Kontinuum.
Eingaben wie `lies Datei <Pfad>`, `lerne aus Datei <Pfad>`, `analysiere Datei
<Pfad>`, `importiere PDF als Lernquelle <Pfad>` und `lerne aus Ordner <Pfad>`
werden vor normaler Suche erkannt und read-only verarbeitet.

Unterstuetzte Dateitypen sind `.txt`, `.md`, `.json`, `.csv`, `.html`, `.pdf`,
`.docx`, `.xlsx`, `.py`, `.js`, `.css`, `.log`, `.epub`, `.azw`, `.azw3` und
`.kfx`. Code-Dateien werden zusaetzlich nach Sprache, Funktionen, Klassen und
Kommentaren analysiert. Tabellen liefern Spalten und Vorschauzeilen. DOCX,
PDF, XLSX und EPUB werden soweit technisch moeglich extrahiert.

Der Standardmodus ist diagnostisch/read-only: keine Datei wird veraendert,
geloescht oder ausgefuehrt. Jeder Import erzeugt Quelle, Hash, Zeitstempel,
Kurzinhalt, Auszug und Review-Nachweis. Ordnerimporte sind standardmaessig
nicht rekursiv und auf `max_files=50` sowie `max_file_size=400 MB` begrenzt.

Die GUI besitzt die Buttons `Datei öffnen`, `Datei lernen` und `Ordner lernen`.
Wenn TkDND verfuegbar ist, koennen Dateien oder Ordner auch per Drag-and-Drop
ins Eingabefeld uebernommen werden; andernfalls bleiben die Buttons als
Fallback aktiv.

## Capability Resolution Engine 1.0

Die Capability Resolution Engine 1.0 ist als read-only Empfehlungsschicht
kanonisch vorbereitet. Sie ersetzt weder Request Router noch PromptOrchestrator
und fuehrt keine Agenten eigenmaechtig aus. CRE 1.0 kann einzelne und mehrere
Intent-Segmente bewerten, daraus Capabilities ableiten, CAIM nach passenden
Agenten fragen, Kandidaten priorisieren und Hinweise fuer Governance, Review
und CMM erzeugen.

Zielpfad:

```text
User -> Request Router -> Capability Resolution Engine -> Priorisierung
     -> Governance -> Agent-Auswahl -> Review -> CMM / Learning
```

Der aktuelle Multi-Intent-Fix fuer Projektordnerfreigabe plus Diagnostikbericht
bleibt als stabiler Uebergangspfad bestehen. Die naechste Ausbaustufe migriert
diese Sonderlogik auf CRE-Planung mit getrennten Capabilities wie
`project.access`, `file.status` und `diagnostics.run`.

## Orchestrator Core 1.0 – geplanter Steuerungsbaustein

Orchestrator Core 1.0 ist als naechster Architekturmeilenstein priorisiert. Er
soll den bestehenden PromptOrchestrator regelgebunden erweitern und aus
Router-, CRE- und Governance-Ergebnissen einen nachvollziehbaren
Ausfuehrungsplan erstellen.

Der Orchestrator Core:

- verarbeitet Single-Intent- und Multi-Intent-Plaene;
- nutzt Capabilities als primaere Planungseinheit;
- behandelt Agenten als Anbieter von Faehigkeiten;
- respektiert Governance-Entscheidungen fuer Blockieren, Freigeben,
  Human-Approval, Protokollierung und Review;
- uebergibt Ergebnisse nur policykonform an Review, CMM oder Learning Layer.

Orchestrator Core 1.0 ist kein Freibrief fuer automatische Agentenketten. Jede
schreibende, externe, governancepflichtige oder reviewpflichtige Ausfuehrung
bleibt an Freigabe, Audit und bestehende Schutzregeln gebunden.

## CDE 2.0 und CKDE 1.0

CDE 2.0 und CKDE 1.0 sind getrennte kanonische Entscheidungspfade.

Der Artefaktpfad bleibt:

```text
Projektdateien -> CAM -> CDE 2.0 -> Archiv / Aktiv / Review
```

CDE 2.0 entscheidet nur ueber Dateien, Dokumente, Reports, Konfigurationen,
Skripte, Manifeste, Projektstruktur, Archivierung, Konsolidierungsvorschlaege
und Review-Markierungen. Automatische Loeschung und automatische
Konsolidierung bleiben ausgeschlossen.

Der Wissenspfad lautet:

```text
Internet -> Internet Learning -> IKG 1.0 -> CKDE 1.0 -> Review Queue -> Governance Review -> Canonical Knowledge
```

CKDE 1.0 entscheidet nur ueber Wissensobjekte und nutzt die Klassen `ACCEPT`,
`REVIEW`, `REJECT` und `CONFLICT`. Die CKDE bewertet Quellenqualitaet, Evidenz,
Aktualitaet, Vollstaendigkeit, Provenienz, Konsistenz, Governance-Konformitaet,
Konflikte und Vertrauensniveau. Eine automatische Uebernahme in den
kanonischen Wissensbestand findet nicht statt.

Historische Versionen, Archive und Backups bleiben unverändert erhalten. Der
isolierte `legacy_kontinuum_23.py` gehört nicht zur aktiven Release-Suite.

## Continuous Canonical Engine 1.0

Neue aktive Phase-3-Komponenten:

- `01_system/kontinuum/core/continuous_canonical_engine.py`
- `24_config/continuous_canonical_engine_34_1.json`
- `17_tests/test_continuous_canonical_engine_34_1.py`
- `14_documents/continuous_canonical_engine_34_1_umsetzung_2026_06_30.md`

Neue Audit- und Drift-Ordner:

- `31_reports/events`
- `31_reports/drift`
- `31_reports/governance`

Die Dateien `canonical_events.jsonl`, `event_processing_log.jsonl`,
`drift_events.jsonl` und `governance_hooks.jsonl` sind append-only
Auditnachweise. Sie duerfen nicht automatisch bereinigt, verschoben oder
verdichtet werden.

## Execution Planner 1.0

Execution Planner 1.0 ist als kanonischer Core-Baustein registriert:

- `01_system/kontinuum/core/execution_planner.py`: deterministischer Planer fuer CRE-Resolutionen.
- `24_config/execution_plan_schema_34_1.json`: Strukturvertrag fuer `ExecutionPlan`.
- `17_tests/test_execution_planner_1_0.py`: Regressionstests fuer Planerzeugung, Reihenfolge, Parallelisierung, Governance-Blockierung, unbekannte Capabilities, fehlende Agenten, Zyklen, leere Plaene und fehlende Agentenausfuehrung.

Die Architekturfolge lautet:

```text
User -> Request Router -> Capability Resolution Engine -> Execution Planner
     -> Orchestrator Core -> Governance -> Agent -> Review
     -> Canonical Memory Manager
```
