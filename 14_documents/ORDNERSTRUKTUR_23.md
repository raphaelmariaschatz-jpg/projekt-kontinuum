# Projekt Kontinuum 34.1 - Kanonische Ordnerstruktur

Stand: 2026-06-24

Diese Übersicht beschreibt die aktive Projektwurzel. Rekursive Dateidumps,
Sicherungsinhalte, Laufzeit-Caches und generierte Daten sind keine
Strukturdefinition.

Aktiver Projektstatus: `14_documents\projektstatus\PROJEKTSTATUS_AKTUELL_34_1.md`
Aktiver Architekturbericht: `14_documents\PROJEKTSTRUKTUR_34_1.md`
Historische Projektstrukturen: `02_versions\projektstrukturen\`

```text
C:\Projekt Kontinuum
|-- 01_system                 aktiver Python-Laufzeitkern
|-- 02_versions               historische Vollversionsstände und Projektstrukturen
|-- 03_memory                 feste Memory- und Kernpolicies
|-- 04_knowledge              lokaler Wissensbestand
|-- 05_connectors             Connector-Definitionen
|-- 06_learning               Lernprinzipien und Lernfortschritt
|-- 07_models                 lokale Modellablagen
|-- 08_workspace_index        Workspace-Indizes
|-- 09_backups                funktionale Entwicklungssicherungen
|-- 10_security               Sicherheitskonfiguration und Auth-Sicherungen
|-- 11_gui                    aktive Desktop-GUI
|-- 12_agents                 ergänzende Agentendaten
|-- 13_tools                  eingebettete Werkzeuge und isolierte Arbeitsbereiche
|-- 14_documents              Handbuch und technische Dokumentation
|-- 15_exports                erzeugte Exporte
|-- 16_installation           GUI-, CLI- und Test-Einstiegspunkte
|-- 17_tests                  aktive Testskripte
|-- 18_autonomous_learning    reservierter autonomer Lernbereich
|-- 19_university_sources     Universitäts-Fundstellen
|-- 20_library_sources        Bibliotheks-Fundstellen
|-- 21_internet_sources       Internet-Fundstellen
|-- 22_project_chronicle      Chronik, Pläne und Sitzungseinstiege
|-- 23_recovery               Wiederherstellungsbereich
|-- 24_config                 aktive Laufzeitkonfiguration
|-- 25_voice                  reservierte Sprachfunktionen
|-- 26_research               Forschungsarbeitsbereich
|-- 27_logs                   Laufzeit- und Auditprotokolle
|-- 30_import                 kontrollierter Importbereich
|-- 31_reports                Berichte
|-- 32_data                   aktive Datenbank und generierte Laufzeitdaten
|-- README.md                 erster Projektüberblick
`-- Ordnerstruktur.txt        kompakter Verweis auf diese Struktur
```

## Aktive Unterstruktur

```text
01_system\kontinuum
|-- agents                    aktive Agentenimplementierungen
|-- core                      Auth, System, Dialog, Memory-Core und Lernen
`-- tools                     aktive Werkzeugintegrationen

01_system\kontinuum\core\memory_core.py
`-- prüfbares Langzeitgedächtnis mit sechs Schichten und Memory-Prüfer

01_system\kontinuum\core\meaning_core.py
`-- Bedeutungsgraph: Prinzip, Ziel, Handlung, Erinnerung, Chronik, Identität

01_system\kontinuum\core\motivation_core.py
`-- Bedeutungsgewichtung: zentrale Beziehungen, Ziele, Erinnerungen, Wissenslücken, Selbstfragen

01_system\kontinuum\core\motivation_explanation.py
`-- erklärbare Score-Herkunft über Meaning-Kanten, Evidenz und Pfade

01_system\kontinuum\core\temporal_relevance.py
`-- Relevanz über Zeit: Kantenstatus, Chronikprägung, Wissenslückenpriorität

01_system\kontinuum\tools\search_engine_tools.py
`-- Suchanbieter-Router: lokal, Notebook, Universität, arXiv, Semantic Scholar, Brave, DuckDuckGo

01_system\kontinuum\agents\memory_agent.py
`-- Befehlsoberfläche für Speichern, Abrufen, Aktualisieren und Vergessen

01_system\kontinuum\agents\notebook_agent.py
01_system\kontinuum\tools\notebook_tools.py
`-- Wissensnotizbuch für Dokumente, Webseiten, Fragen und Quellenzitate

01_system\kontinuum\agents\research_agent.py
01_system\kontinuum\tools\search_engine_tools.py
`-- asynchrone Webrecherche, Zeitbudgets, Teilantwort und Anbieter-Fallback

01_system\kontinuum\core\auth.py
`-- lokale erneute Superadmin-Passwortprüfung für Kostenfreigaben

01_system\kontinuum\__main__.py
`-- CLI-Einstieg mit maskierter Oracle-Kostenbestätigung

16_installation
|-- START_GUI.bat             kanonischer GUI-Einstieg
|-- START_KONTINUUM_34_1.bat  CLI-Einstieg
|-- TEST_KONTINUUM_34_1.bat   vollständiger Test-Einstieg
`-- RELEASE_GATE_34_1.bat     kanonischer Release-Integrity-Einstieg

13_tools\development_sandbox
|-- .git                      eigene lokale Git-Historie
|-- README.md                 Regeln der isolierten Entwicklungsumgebung
|-- self_extension_candidate  temporäre Kandidatenkopie einer Self-Extension
`-- weitere Dateien           ausschließlich Sandbox-Programme und -Tests

13_tools\git_hooks_disabled   leerer Hook-Pfad für automatische Git-Snapshots

13_tools\oracle_cloud_workspace
`-- Arbeitsbereich für kontrollierte OCI-CLI-Aufrufe; keine Zugangsdaten

27_logs
|-- auth_audit.log            Login-, Auth- und Kostenfreigabe-Ergebnisse
|-- self_extension_audit.log  Self-Extension-Ergebnisse ohne Passwortinhalte
`-- oracle_cloud_audit.log    OCI-Aktionen ohne Schlüssel oder Geheimnisse

11_gui\desktop_gui.py
`-- einziger kanonischer produktiver GUI-Einstieg

14_documents\projektstatus
`-- gebündelte aktuelle Projektstatus-Dateien und Verknüpfungen zu Wiedereinstiegspunkten

09_backups
`-- self_extension_*          datierte Rollback-Sicherungen vor Promotion
```

## Strukturregeln

- Aktiver Code liegt ausschließlich unter `01_system\kontinuum`.
- Aktive Laufzeitdaten liegen unter `32_data`; Daten nicht in Unterordnern
  namens `32_data` oder `29_memory` verschachteln.
- Die veralteten Wurzelordner `28_documents` und `29_memory` sind verboten.
- Sicherungen gehören nach `09_backups` oder bei Sicherheitsänderungen nach
  `10_security\backups`.
- Normale `entwickle:`-Aufträge bleiben ausschließlich in
  `13_tools\development_sandbox`.
- Superadmin-gesteuerte Self-Extensions entstehen zuerst in der temporären
  Kandidatenkopie `13_tools\development_sandbox\self_extension_candidate`.
- Automatische Promotion ist ausschließlich in diese freigegebenen Bereiche
  möglich: `01_system\kontinuum`, `11_gui`, `14_documents`, `17_tests` und
  `22_project_chronicle`.
- Automatisch promotierbar sind nur `.py`, `.md` und `.txt`; mindestens eine
  neue Testdatei ist Pflicht und vorhandene Tests dürfen nicht verändert
  werden.
- `01_system\kontinuum\core\auth.py`,
  `01_system\kontinuum\tools\development_tools.py`,
  `01_system\kontinuum\agents\development_agent.py` und
  `24_config\development_sandbox.json` sind für Self-Extension geschützt.
- Vor jeder Promotion entsteht eine datierte Sicherung unter `09_backups`;
  fehlgeschlagene aktive Abschlusstests lösen automatisches Rollback aus.
- Oracle-Zugangsdaten und private Schlüssel liegen ausschließlich außerhalb
  der Projektwurzel; `24_config\oracle_cloud.json` enthält nur ungefährliche
  Laufzeitparameter und OCIDs.
- Potenziell kostenverursachende Oracle-Aktionen werden von der
  Oracle-Werkzeugintegration direkt vor dem OCI-Aufruf angehalten, bis eine
  einmalige ausdrückliche Bestätigung und erneute lokale Passwortprüfung
  erfolgreich sind.
- Passwörter erscheinen weder in `auth_audit.log` noch in
  `oracle_cloud_audit.log`.
- Dokumentation verweist auf aktive Pfade, nicht auf Sicherungskopien.
- Die aktuelle fachliche Modulübersicht liegt ausschließlich in
  `14_documents\PROJEKTSTRUKTUR_34_1.md`.
- Historische `PROJEKTSTRUKTUR_*`-Berichte ab 24.3 liegen ausschließlich unter
  `02_versions\projektstrukturen\`.
- Der Canonical Architecture Manager blockiert Releases bei mehreren aktiven
  Projektstrukturen oder fehlenden historischen Archivständen.
- `__pycache__`, Datenbankinhalte und Sicherungsbäume gehören nicht in eine
  kanonische Strukturübersicht.
