# Artifact Lifecycle Migration Plan 1.0

Datum: 2026-07-05
Status: Planungsdokument, keine Bereinigung
Grundlage: Artifact Lifecycle Policy 2.0 (ALP 2.0), CADP 1.0, CCP 1.0, Architektur-Baseline vor Runtime-Migration 34.1

## 1. Zweck und Sicherheitsgrenzen

Dieser Plan wendet ALP 2.0 erstmals auf den aktuellen Projektbestand von Projekt Kontinuum an. Ziel ist eine nachvollziehbare Migrationsplanung, nicht die Ausfuehrung.

Verbindlich nicht ausgefuehrt:

- keine Dateien verschoben;
- keine Dateien geloescht;
- keine Dateien umbenannt;
- keine Imports geaendert;
- keine Runtime-Migration;
- keine Archivierung;
- kein Commit.

Zusaetzliche Sicherheitsanforderung:

Vor jeder spaeteren Archivierung muss fuer jedes Artefakt ein eindeutiger Nachfolger (`Successor`) oder ein begruendeter Endstatus (`Retired without Successor`) dokumentiert werden.

Regeln:

- Historical -> Successor vorhanden oder historischer Endzustand begruendet.
- Deprecated -> kein Nachfolger erforderlich, aber Endstatus und Begruendung erforderlich.
- Canonical -> eindeutige aktive Referenz und eindeutiger Speicherort erforderlich.
- Release Evidence -> Evidenzkette und Zweck muessen erhalten bleiben.
- Unklarer Sonderfall -> keine Archivierung ohne Benutzerentscheidung.

## 1.1 Migration-ID-Regel

Jede Datei oder zusammengefasste Dateigruppe mit Lifecycle-Konflikt erhaelt eine eindeutige Migration-ID im Format `MIG-0001`. Diese ID bleibt ueber Analyse, Freigabe, Archivierung, Referenzupdate, Tests und Abschlussbericht stabil. Eine Migration-ID darf nicht fuer andere Artefakte wiederverwendet werden.

Pflichtfelder je Migration-ID:

```text
Migration-ID:
Artefakt / Gruppe:
ALP-Klasse:
Successor / Retired without Successor:
Geplante Phase:
Aktion:
Risiko:
Referenzen:
Freigabestatus:
```
## 2. Vollstaendige Artefaktklassifikation nach ALP 2.0

### 2.1 Canonical

Aktuelle produktive oder architekturverbindliche Dateien.

| Artefaktgruppe | Beispiele | Begruendung | Successor / Endstatus |
|---|---|---|---|
| Core Runtime und Architektur | `01_system/kontinuum/core/capability_resolution_engine.py`, `execution_planner.py`, `orchestrator_core.py`, `application_services.py`, `system.py` | Aktuelle Architektur- und Runtime-Komponenten; produktiv initialisiert oder Migrationsanker | Canonical, aktive Referenz in System/Architektur |
| Canonical Manager | `canonical_architecture.py`, `canonical_database.py`, `canonical_api_registry.py`, `canonical_artifacts.py` | CAM-/Canonical-Layer-Bestandteil | Canonical, aktive Referenz |
| Aktuelle Architektur-Dokumentation | `14_documents/KANONISCHES_ARCHITEKTURMODELL_34_1.md`, `PROJEKTSTRUKTUR_34_1.md`, `ARTIFACT_LIFECYCLE_POLICY_2_0.md` | Aktuelle kanonische Architektur- und Projektregeln | Canonical, Nachfolger erst bei neuer Architekturversion |
| Aktuelle Release-/Runtime-Konfiguration | `24_config/canonical_architecture_34_1.json`, `release_integrity_34_1.json`, `execution_plan_schema_34_1.json`, `orchestrator_runtime_schema_34_1.json`, `capability_registry_34_1.json` | Durch Manifest/Tests/Runtime-Vertraege referenziert | Canonical oder Runtime Required; Nachfolger bei 34.2/35.0 |
| Stabile Starter | `16_installation/START_GUI.bat`, aktuelle `*_34_1.bat` | Aktuelle Einstiegspunkte laut Release Integrity | Canonical/Runtime Required; Successor waere versionloser Starter oder naechstes Release |
| Aktuelle Spezialberichte | `31_reports/ARCHITECTURE_BASELINE_PRE_RUNTIME_MIGRATION_34_1.md`, dieser Plan | Aktuelle Planungs- und Baseline-Evidence | Release Evidence, nicht produktive Runtime |

### 2.2 Runtime Required

Produktiv benoetigte Dateien oder Kontrakte.

| Artefaktgruppe | Beispiele | Begruendung | Successor / Endstatus |
|---|---|---|---|
| Produktiv importierte Core-Module | `application_services.py`, `system.py`, `request_router.py`, neue CRE/Planner/Orchestrator-Komponenten | Imports und Systeminitialisierung vorhanden | Aktiver Runtime-Vertrag |
| Runtime-Schemata | `execution_plan_schema_34_1.json`, `orchestrator_runtime_schema_34_1.json` | Planner und Orchestrator nutzen Schema-Vertraege | Successor nur bei Schema-Migration |
| Aktive Agent-/Tool-Registries | `agent_registry.py`, `tool_registry.py`, `canonical_agents.json` | Routing, CAIM und Tooling | Aktiver Vertrag |
| Aktuelle Start- und Testskripte | `START_GUI_34_1.bat`, `START_KONTINUUM_34_1.bat`, `TEST_KONTINUUM_34_1.bat`, `RELEASE_GATE_34_1.bat` | Release Integrity Required Paths | Successor: versionloser stabiler Starter oder naechste Release-Version |
| Aktive Datenbereiche | `32_data/internet_learning_queue`, `internet_learning_review`, `web_agent_sources`, `file_agent_sources`, `file_agent_review` | Learning-/Review-Runtime | Kein Archiv ohne Datenprovenienzpruefung |

### 2.3 Release Evidence

Versionierte Nachweise, Baselines, Audit- und Release-Dokumente.

| Artefaktgruppe | Beispiele | Begruendung | Successor / Endstatus |
|---|---|---|---|
| Release Integrity Evidence | `31_reports/release_integrity/34.1/baseline.json`, `audit_snapshot.json`, `release_gate.json` | Release-Nachweis | Retain as Release Evidence |
| Release-Chronik | `22_project_chronicle/RELEASE_34_1_*`, `RELEASE_34_0_*`, aeltere `RELEASE_*` | Historische Release-Nachweise | Retain as Release Evidence; ggf. in Chronik-Archiv strukturieren |
| Baselines und Audits | `ARCHITECTURE_BASELINE_PRE_RUNTIME_MIGRATION_34_1.md`, `CANONICAL_DOCUMENTATION_AUDIT_2026_07_04.md` | Vorher-/Nachher- und Audit-Nachweis | Retain as Release Evidence |
| Archive-Lifecycle-Reports | `31_reports/archive_lifecycle/phase*_report.md/json`, `archive_moves.jsonl` | Nachweis frueherer Lifecycle-Audits | Retain; niemals automatisch loeschen |
| Statusberichte versionierter Komponenten | `learning_agent_1_2_status_report.md`, `clg_1_1_status_report.md`, `cmm_1_0_status_report.md` | Komponentenstatus und Entwicklungslinie | Release Evidence; ggf. Report-Archiv |

### 2.4 Historical

Nicht mehr produktive oder fruehere Versionen, archivierungsfaehig nach Pruefung.

| Artefaktgruppe | Beispiele | Begruendung | Successor / Endstatus |
|---|---|---|---|
| Alte Lernagenten | `12_agents/learning_agent_1_0.py`, `learning_agent_1_1.py` | Aktueller dokumentierter Stand ist `learning_agent_1_2.py`; aeltere Tests existieren noch | Successor: `learning_agent_1_2.py`, spaeter `learning_agent.py` |
| Alter Learning-Governance-Stand | `12_agents/continuous_learning_governance_1_0.py` | Aktueller Stand ist `continuous_learning_governance_1_1.py` | Successor: `continuous_learning_governance_1_1.py`, spaeter versionlos |
| Alte Starter/Testskripte | `16_installation/*_23.bat`, `*_32_3.bat`, `*_32_4.bat`, `*_33_0.bat`, `*_34_0.bat` | Historische Release-Staende neben 34.1 | Successor: jeweilige `*_34_1.bat` oder versionloser Starter |
| Alte Statuschecks | `13_tools/status_check_32_3.py`, `status_check_32_4.py`, `status_check_33_0.py`, `status_check_34_0.py` | Aktueller Stand `status_check_34_1.py` | Successor: `status_check_34_1.py`, spaeter `status_check.py` |
| Alte Projektstatus-/README-Dateien | `PROJEKTSTATUS_AKTUELL_34_0.md`, `README_GUI_32_4.md`, `README_AGENTS_TOOLS_23.md`, `ORDNERSTRUKTUR_23.md`, `HANDBUCH_23.md` | Historische oder ersetzte Dokumentation | Successor: aktuelle 34.1-Dokumentation oder historischer Endstatus |
| Alte Einstiegspunkte | `EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_32_4.md`, `_33_0.md`, `_34_0.md` | Historische Sitzungsuebergaenge | Successor: `_34_1.md` bzw. versionlos aktuelle Datei |
| Flache historische Datenkopien | `32_data/_version_*`, `_02_versions_*`, `_legacy_versions_*` | Historische Spiegeldateien direkt im aktiven Datenordner | Successor/Endstatus je Datenfamilie zu klaeren; nicht pauschal verschieben |

### 2.5 Deprecated

Derzeit keine Datei sicher als Deprecated freigegeben.

Begruendung: Ohne vollstaendige Referenz-, Provenienz- und Evidence-Pruefung darf keine Datei als entfernbar markiert werden. Reproduzierbare Caches waeren Deprecated-Kandidaten, wurden hier aber nicht als Projektartefakt-Migrationsziel behandelt.

### 2.6 Unklare Sonderfaelle

| Artefaktgruppe | Beispiele | Grund fuer Unklarheit | Naechste Pruefung |
|---|---|---|---|
| Versionierte aktive Tests | `test_v34_0_version_consistency.py`, `test_learning_agent_1_0.py`, `test_learning_agent_1_1.py`, viele `test_*_23.py` | Teils Regression/Kompatibilitaet, teils historische Testreste | Teststrategie pro Datei: aktive Regression oder Historical |
| `24_config/*_1_0.json` und `*_34_1.json` | `file_agent_1_0.json`, `web_agent_1_0.json`, `canonical_knowledge_decision_engine_1_0.json` | Version kann Teil des aktiven Konfigurationsvertrags sein | CAM/Release Integrity als Canonical oder Runtime Required markieren |
| `22_project_chronicle` aeltere Release-Dateien | `RELEASE_25_0_*` bis `RELEASE_34_0_*` | Chronik darf historisch sein, aber aktiver Ordner enthaelt viele Versionen | Chronik-Sonderregel anwenden, ggf. strukturierte `archive/releases` |
| `31_reports` alte Statusreports | `clg_1_0_status_report.md`, `learning_agent_1_0_status_report.md` | Evidence oder historischer Report? | Als Release Evidence behalten oder in Report-Archiv verschieben |
| `32_data/master/version_1_bis_29*` | `version_1_bis_29.json`, `.zip`, cleaning report | Datenhistorie/Provenienz wahrscheinlich relevant | Datenlineage pruefen, nicht automatisch archivieren |

## 3. Migrationsmatrix fuer Lifecycle-Konflikte

| Migration-ID | Datei / Gruppe | Klasse | Ziel | Aktion | Risiko | Begruendung |
|---|---|---|---|---|---|---|
| MIG-0001 | `12_agents/learning_agent_1_0.py` | Historical | `12_agents/archive/legacy/learning_agent/` | archivieren nach Testentscheidung | MEDIUM | Successor `learning_agent_1_2.py`; Tests referenzieren Datei direkt |
| MIG-0002 | `12_agents/learning_agent_1_1.py` | Historical | `12_agents/archive/legacy/learning_agent/` | archivieren nach Testentscheidung | MEDIUM | Successor `learning_agent_1_2.py`; Tests referenzieren Datei direkt |
| MIG-0003 | `12_agents/learning_agent_1_2.py` | Canonical, perspektivisch umzubenennen | `12_agents/learning_agent.py` nach spaeterer Freigabe | bleibt produktiv, spaeter Rename-Plan | HIGH | Aktuell dokumentiert; Umbenennung betrifft Tests/Doku/Reports |
| MIG-0004 | `12_agents/continuous_learning_governance_1_0.py` | Historical | `12_agents/archive/legacy/continuous_learning_governance/` | archivieren nach Testentscheidung | MEDIUM | Successor `continuous_learning_governance_1_1.py`; Testreferenz vorhanden |
| MIG-0005 | `12_agents/continuous_learning_governance_1_1.py` | Canonical, perspektivisch umzubenennen | `12_agents/continuous_learning_governance.py` nach spaeterer Freigabe | bleibt produktiv, spaeter Rename-Plan | HIGH | Aktuell dokumentiert; Umbenennung hat Doku/Test-Auswirkungen |
| MIG-0006 | `13_tools/status_check_32_3.py`, `_32_4.py`, `_33_0.py`, `_34_0.py` | Historical | `13_tools/archive/reports/status_checks/` | archivieren nach Referenzupdate | MEDIUM | Successor `status_check_34_1.py`; historische Doku referenziert Altpfade |
| MIG-0007 | `13_tools/status_check_34_1.py` | Canonical/Runtime Required | perspektivisch `13_tools/status_check.py` | bleibt produktiv | MEDIUM | Aktuelles Release-Tool, in Release Integrity referenziert |
| MIG-0008 | `13_tools/release_integrity_34_1.py` | Runtime Required/Release Evidence | bleibt aktiv | Release Evidence | HIGH | Release-Gate-kritisch; nicht verschieben |
| MIG-0009 | `13_tools/archive_lifecycle_34_1.py`, `archive_phase2_runner_34_1.py` | Canonical oder Tool-Evidence | bleibt aktiv bis CAM-Entscheid | weitere Analyse | MEDIUM | Lifecycle-Tools, Version im Namen ggf. aktiver Vertragsstand |
| MIG-0010 | `14_documents/README_GUI_32_4.md` | Historical | `14_documents/archive/legacy/` | archivieren nach Referenzupdate | LOW-MEDIUM | Successor `README_GUI_34_1.md`; historische Referenzen vorhanden |
| MIG-0011 | `14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_34_0.md` und aelter | Historical/Release Evidence | `14_documents/archive/reports/projektstatus/` | Benutzerentscheidung | MEDIUM | Statushistorie kann Evidence sein; aktueller Successor 34.1 |
| MIG-0012 | `14_documents/HANDBUCH_23.md`, `ORDNERSTRUKTUR_23.md`, `README_AGENTS_TOOLS_23.md` | Historical | `14_documents/archive/legacy/` | Benutzerentscheidung | MEDIUM | Historische Dokumente; moegliche Referenzen im Bestand |
| MIG-0013 | `14_documents/*_1_0_*` Umsetzungsdokus | Release Evidence | bleibt oder Report-Archiv | Release Evidence | LOW | Implementierungsnachweise duerfen versioniert bleiben |
| MIG-0014 | `14_documents/KANONISCHES_ARCHITEKTURMODELL_34_1.md`, `PROJEKTSTRUKTUR_34_1.md`, `ARTIFACT_LIFECYCLE_POLICY_2_0.md` | Canonical | bleibt aktiv | bleibt produktiv | LOW | Aktuelle Architekturgrundlage |
| MIG-0015 | `16_installation/*_23.bat`, `*_32_3.bat`, `*_32_4.bat`, `*_33_0.bat`, `*_34_0.bat` | Historical | `16_installation/archive/legacy/` | archivieren nach Referenzupdate | HIGH | Starter koennen versehentlich genutzt werden; historische Statusdateien referenzieren sie |
| MIG-0016 | `16_installation/*_34_1.bat`, `RELEASE_GATE_34_1.bat` | Runtime Required | bleibt aktiv | bleibt produktiv | HIGH | Aktuelle Start-/Test-/Release-Gate-Pfade |
| MIG-0017 | `17_tests/test_learning_agent_1_0.py`, `_1_1.py` | Historical Test oder Regression | `17_tests/archive/legacy/learning_agent/` falls nicht aktiv | weitere Analyse | MEDIUM | Referenziert historische Agenten direkt |
| MIG-0018 | `17_tests/test_learning_agent_1_2.py` | Active Regression | bleibt aktiv | bleibt produktiv | MEDIUM | Testet aktuellen Agentenstand, spaeter auf versionlosen Namen umstellen |
| MIG-0019 | `17_tests/test_continuous_learning_governance_1_0.py` | Historical Test oder Regression | `17_tests/archive/legacy/continuous_learning_governance/` falls nicht aktiv | weitere Analyse | MEDIUM | Referenziert historischen Governance-Stand |
| MIG-0020 | `17_tests/test_continuous_learning_governance_1_1.py` | Active Regression | bleibt aktiv | bleibt produktiv | MEDIUM | Testet aktuellen Governance-Stand |
| MIG-0021 | `17_tests/test_v34_0_version_consistency.py` | Historical/Release Evidence | ggf. `17_tests/archive/legacy/` | Benutzerentscheidung | MEDIUM | Release-Integrity erlaubt einzelne Legacy-Pfade; kann bewusst Regression sein |
| MIG-0022 | `17_tests/test_v34_1_version_consistency.py`, `test_release_integrity_framework_34_1.py` | Runtime Required/Release Evidence | bleibt aktiv | bleibt produktiv | HIGH | Aktuelles Release Gate |
| MIG-0023 | `17_tests/test_*_23.py`, `legacy_*_23.py` | Historical Test | `17_tests/archive/legacy/23/` | weitere Analyse | MEDIUM | Altversionen; moegliche Regressionen klaeren |
| MIG-0024 | `22_project_chronicle/RELEASE_25_0_*` bis `RELEASE_34_0_*` | Release Evidence/Historical | `22_project_chronicle/archive/releases/` oder aktiv als Chronik | Benutzerentscheidung | MEDIUM | Chronik-Sonderregel erlaubt Historie; Strukturfrage offen |
| MIG-0025 | `22_project_chronicle/RELEASE_34_1_*`, `EINSTIEGSPUNKTE_NAECHSTE_SITZUNG_34_1.md` | Release Evidence/Canonical Chronicle | bleibt aktiv | Release Evidence | LOW | Aktueller Release-/Sitzungsnachweis |
| MIG-0026 | `24_config/*_34_1.json`, relevante `*_1_0.json`, `*_2_0.json` | Canonical/Runtime Required | bleibt aktiv | bleibt produktiv | HIGH | Viele Versionen sind aktive Vertrage; nicht pauschal archivieren |
| MIG-0027 | `24_config/canonical_governance_baseline_34_1_ACCEPTED.json` | Release Evidence/Canonical Accepted | bleibt aktiv oder Evidence-Archiv | Benutzerentscheidung | MEDIUM | Accepted-Snapshot hat Evidenzwert |
| MIG-0028 | `31_reports/*_1_0_status_report.md`, `learning_agent/*_status_report.md` | Release Evidence/Historical Report | `31_reports/archive/reports/` oder Fachunterordner | Release Evidence | LOW-MEDIUM | Nicht produktiv, aber Nachweiswert |
| MIG-0029 | `31_reports/archive_lifecycle/*` | Release Evidence | bleibt/strukturiert archivieren | Release Evidence | LOW | Audit- und Migrationsnachweis; niemals loeschen |
| MIG-0030 | `32_data/_version_*` | Historical Data | `32_data/archive/data_mirrors/` oder `02_versions` | weitere Analyse | KRITISCH | 3.969 flache Spiegel; Datenverlust-/Provenienzrisiko |
| `32_data/_02_versions_*` | Historical Data/Release Evidence | `32_data/archive/data_mirrors/` oder `02_versions` | weitere Analyse | KRITISCH | 82 flache Spiegel mit Versionsherkunft |
| `32_data/_legacy_versions_*` | Historical Data | `32_data/archive/data_mirrors/` | weitere Analyse | KRITISCH | Legacy-Daten; Provenienz ungeklaert |
| `32_data/master/version_1_bis_29*` | Historical Data/Release Evidence | bleibt bis Datenlineage geklaert | Benutzerentscheidung | HIGH | Master-/Cleaning-Artefakte koennen kanonische Datenhistorie darstellen |

## 4. Abhaengigkeitsanalyse

### 4.1 Referenzpruefung: gruppierte Ergebnisse

| Gruppe | Referenzen vorhanden? | Verwendende Komponenten | Konsequenz |
|---|---|---|---|
| Alte Lernagenten 1.0/1.1 | Ja | `17_tests/test_learning_agent_1_0.py`, `test_learning_agent_1_1.py` | Tests zuerst klassifizieren; dann Archivierung moeglich |
| `learning_agent_1_2.py` | Ja | aktuelle Tests, Doku, Chronik, Reports | bleibt aktiv bis versionloser Nachfolger freigegeben ist |
| CLG 1.0/1.1 | Ja | jeweilige Tests, Statusreports, Doku | 1.1 bleibt aktiv; 1.0 erst nach Testentscheidung archivieren |
| 34.0 Starter/Status | Ja | historische Projektstatusdateien, Einstiegspunktdateien, alte Versionstests | Historische Doku-Referenzen kennzeichnen oder auf Archivpfade umstellen |
| 34.1 Starter/Status/Release Gate | Ja | Release Integrity, Dokumentation, aktive Tests | Runtime Required, keine Archivierung |
| Versionierte Configs | Ja/teilweise | CAM, Release Integrity, Services, Tests | Einzelfallpruefung; viele sind aktive Kontrakte |
| Versionierte Tests | Ja/indirekt | Release Gate und Testlaufmuster `17_tests/test_*.py` | Archivierung kann Testumfang veraendern; Strategie erforderlich |
| Chronik-Releases | Ja | Chronik, Statusberichte, Release Integrity teilweise | Als Release Evidence behandeln; Archiv nur strukturiert |
| 31_reports Evidence | Ja/teilweise | Manifeste, Audits, menschliche Nachvollziehbarkeit | Nicht loeschen; ggf. Report-Archiv |
| 32_data flache Spiegel | Unklar | moegliche Daten-/Wissenspfade, historische Rekonstruktion | Vor jeder Bewegung Datenlineage-Scan erforderlich |

### 4.2 Prueffelder vor jeder Archivierung

Fuer jede Archivierung muss eine Datei- oder Gruppenkarte gefuehrt werden:

```text
Artefakt:
ALP-Klasse:
Successor / Retired without Successor:
Imports geprueft: Ja/Nein
Startskripte geprueft: Ja/Nein
Runtime geprueft: Ja/Nein
Registry geprueft: Ja/Nein
CAM geprueft: Ja/Nein
Release Integrity geprueft: Ja/Nein
Tests geprueft: Ja/Nein
Dokumentation geprueft: Ja/Nein
Konfiguration geprueft: Ja/Nein
Feature Flags geprueft: Ja/Nein
Referenzen vorhanden: Ja/Nein
Referenzquellen:
Risiko:
Freigabe:
```

## 5. Optimale Reihenfolge der spaeteren Migration

### Migration-ID-Phasenanker

Die Migration-IDs sind den spaeteren Migrationsphasen wie folgt zugeordnet:

| Phase | Migration-IDs | Schwerpunkt |
|---|---|---|
| Phase 1 | MIG-0009 bis MIG-0014 | Dokumentation und Projektstatus |
| Phase 2 | MIG-0025 bis MIG-0027 | Reports und Release Evidence |
| Phase 3 | MIG-0015 bis MIG-0020 | historische und aktive Tests |
| Phase 4 | MIG-0006 bis MIG-0008 | Tools und Statuschecks |
| Phase 5 | MIG-0001 bis MIG-0005 | Agenten und Learning Governance |
| Phase 6 | MIG-0013 bis MIG-0014 | Start- und Installationsskripte |
| Phase 7 | MIG-0024 | Konfigurationen und Manifeste |
| Phase 8 | MIG-0028 bis MIG-0030 | Datenartefakte und Datenlineage |
| Phase 9 | MIG-0007, MIG-0021, MIG-0024 | Release Integrity und erlaubte Legacy-Pfade |
| Phase 10 | alle offenen MIG-IDs | CAM-Validierung und Freigabeentscheidung |
### Schritt 1: Dokumentation klassifizieren und historische Referenzen markieren

Begruendung: Dokumente enthalten viele Referenzen auf historische Starter, Statuschecks und Releases. Ohne Dokumentationsentscheidung entstehen scheinbare Abhaengigkeiten, die eigentlich nur historische Nachweise sind.

Risiko: LOW-MEDIUM.

### Schritt 2: Release Evidence und Reports strukturieren

Begruendung: `31_reports` und Release-Chronik muessen als Evidence erhalten bleiben, aber von produktiven Pflichten getrennt werden.

Risiko: LOW.

### Schritt 3: Teststrategie festlegen

Begruendung: Viele historische Dateien bleiben nur wegen Tests aktiv. Zuerst entscheiden, welche Tests aktive Regressionen sind und welche historische Tests ins Archiv gehoeren.

Risiko: HIGH.

### Schritt 4: Historische Tools planen

Begruendung: Alte `status_check_*` und Lifecycle-Tools beeinflussen Status- und Release-Wahrnehmung. Nach Teststrategie lassen sie sich geordnet archivieren oder als Evidence behalten.

Risiko: MEDIUM.

### Schritt 5: Historische Agenten planen

Begruendung: Agentenversionen sind echte aktive Parallelstaende. Erst nach Test- und Dokumentationsentscheidung koennen alte Versionen sicher archiviert und versionlose kanonische Namen vorbereitet werden.

Risiko: HIGH.

### Schritt 6: Historische Start- und Installationsskripte planen

Begruendung: Starter koennen direkt von Menschen oder Automationen genutzt werden. Archivierung erst nach Dokumentations- und Release-Integrity-Abgleich.

Risiko: HIGH.

### Schritt 7: Konfigurations- und Manifest-Ausnahmen festlegen

Begruendung: Versionierte Config-Dateien koennen aktive Vertrage sein. CAM und Release Integrity muessen klar ausweisen, welche Versionen produktiv sind.

Risiko: HIGH.

### Schritt 8: Historische Datenartefakte in `32_data` analysieren

Begruendung: Groesster Bestand und hoechstes Daten-/Provenienzrisiko. Erst nach stabiler Regel- und Toollage bearbeiten.

Risiko: KRITISCH.

### Schritt 9: Release Integrity aktualisieren

Begruendung: Nach Klassifikation muessen Required Paths, Allowed Legacy Paths und Evidence-Regeln ALP 2.0 widerspiegeln.

Risiko: HIGH.

### Schritt 10: CAM validieren

Begruendung: CAM muss die neue Klassifikation, Successor-Regel, Archivziele und Benutzerfreigaben abbilden.

Risiko: HIGH.

### Schritt 11: Regressionstests ausfuehren

Begruendung: Erst nach Plan- und Konfigurationsabgleich laesst sich pruefen, ob die aktive Struktur stabil bleibt.

Risiko: MEDIUM-HIGH.

### Schritt 12: Freigabe Runtime-Migration

Begruendung: Die Runtime-Migration sollte erst starten, wenn Canonical, Runtime Required, Release Evidence und Historical getrennt sind oder zumindest verbindlich dokumentiert wurden.

Risiko: abhaengig von offenen Punkten; derzeit HIGH.

## 6. Risikobewertung nach Migrationsgruppe

| Gruppe | Risiko | Begruendung |
|---|---|---|
| Architektur-Dokumentation 34.1/ALP 2.0 | LOW | Aktuelle kanonische Dokumente; keine Archivierung geplant |
| Historische Dokumentation | MEDIUM | Viele Referenzen; Verlust an Kontext moeglich, aber geringe Runtime-Gefahr |
| Reports und Release Evidence | LOW-MEDIUM | Nicht produktiv, aber hoher Nachweiswert; niemals loeschen |
| Historische Tests | MEDIUM-HIGH | Veraendern Testumfang und Release-Gate-Verhalten |
| Aktuelle Tests 34.1 | HIGH | Release-Gate-kritisch; nicht archivieren |
| Historische Tools/Statuschecks | MEDIUM | Koennen historische Doku und Statuswahrnehmung beeinflussen |
| Aktuelle Release-Tools | HIGH | Release Integrity und Gate kritisch |
| Historische Agenten | HIGH | Direkte Testreferenzen und potenzielle manuelle Nutzung |
| Aktuelle Agenten mit Versionsnamen | HIGH | Umbenennung betrifft Tests, Doku, Reports, Registry |
| Start-/Installationsskripte | HIGH | Menschliche und automatisierte Einstiegspunkte |
| Versionierte Configs | HIGH | Version oft aktiver Vertrag; pauschale Archivierung gefaehrlich |
| Chronik | MEDIUM | Historie ist fachlicher Inhalt; Strukturfrage statt Loeschfrage |
| `32_data` historische Spiegel | KRITISCH | Datenverlust, Provenienzverlust, unbekannte Runtime-/Wissensreferenzen |

## 7. Offene Sonderfaelle

1. Versionierte Tests muessen in aktive Regression, historische Kompatibilitaet oder archivierungsfaehigen Altbestand getrennt werden.
2. Versionierte Config-Dateien brauchen CAM-Kennzeichnung: aktiver Vertrag, Release Evidence oder Historical.
3. `22_project_chronicle` braucht eine klare Unterstruktur fuer aktuelle Chronik vs. historische Release Evidence.
4. `31_reports` braucht eine Report-Archivregel, ohne Evidence-Ketten zu brechen.
5. `32_data` braucht einen separaten Daten-Lineage-Plan mit Hashing, Referenzscan und Provenienzbewertung.
6. Aktive Agenten mit Versionsnummern brauchen spaeter einen kontrollierten Rename-Plan mit Successor-Linie.
7. `orchestrator_runtime_enabled` ist als Feature-Flag noch nicht implementiert und bleibt Voraussetzung fuer kontrollierte Runtime-Migration.

## 8. Runtime-Freigabepruefung

| Kriterium | Status | Bewertung |
|---|---|---|
| Projektstruktur | Nicht bereit | Aktive Ordner enthalten historische Parallelstaende |
| ALP 2.0 | Bereit | Policy existiert und liefert Regelgrundlage |
| CAM | Teilweise bereit | Muss ALP-Klassen, Successor-Regel und Freigabestatus automatisierbar abbilden |
| Release Integrity | Teilweise bereit | Aktuelle 34.1-Gates existieren, aber Legacy-/Evidence-Regeln muessen ALP-konform geschaerft werden |
| Dokumentation | Teilweise bereit | Aktuelle Doku vorhanden; historische Referenzen noch nicht klassifiziert |
| Baseline | Bereit | Pre-Runtime-Migration-Baseline existiert |
| Architektur | Bereit mit Vorbehalt | CRE, Execution Planner und Orchestrator Core existieren; Feature-Flag fehlt |
| Risiken | Nicht bereit | `32_data`, Tests, Starter und versionierte Agenten bleiben hohe Risiken |

### Hindernisse vor Runtime-Migration

1. Keine eindeutige Trennung aller aktiven und historischen Artefakte.
2. Feature-Flag `orchestrator_runtime_enabled` fehlt.
3. Versionierte Agenten sind noch aktiv und nicht versionlos kanonisiert.
4. Historische Tests koennen Release-Gate-Verhalten beeinflussen.
5. Alte Starter und Statuschecks liegen weiter aktiv neben 34.1.
6. `32_data` enthaelt kritischen flachen historischen Datenbestand.
7. Release Integrity muss ALP-2.0-Klassen und Legacy-Ausnahmen expliziter abbilden.
8. CAM muss Successor/Retired-without-Successor dokumentieren koennen.

## 9. Empfehlung

Die eigentliche Archivierung sollte noch nicht gestartet werden. Empfohlen ist eine gestufte Freigabe:

1. Freigabe dieses Plans als Planungsgrundlage.
2. Separate Teststrategie fuer historische Tests.
3. Separate Daten-Lineage-Pruefung fuer `32_data`.
4. CAM-Erweiterung um ALP-Klasse, Successor und Endstatus.
5. Release-Integrity-Abgleich.
6. Erst danach erste kontrollierte Archivierungswelle mit Dokumentation/Reports, anschliessend Tools, Tests, Agenten und zuletzt Datenartefakte.

Runtime-Migration sollte noch nicht begonnen werden. Sie kann vorbereitet werden, sobald Projektstruktur, CAM, Release Integrity und Feature-Flag die ALP-2.0-Trennung aktiv absichern.


