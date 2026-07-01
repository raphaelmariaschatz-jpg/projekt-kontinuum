# Phase 3 – Continuous Canonical Governance 34.1

Phase 3 ueberfuehrt Projekt Kontinuum von der abgeschlossenen Archivmigration
in dauerhaften stabilen Systembetrieb. Der Schwerpunkt liegt nicht auf weiterer
Bereinigung, sondern auf kontinuierlicher Kanonizitaetspruefung und Drift-
Vermeidung.

## Kernschichten

1. Canonical Stability Layer prueft Strukturkonsistenz, Archiv-/Aktiv-Trennung
   und Pflichtwurzeln.
2. Continuous Lifecycle Governance klassifiziert neue oder geaenderte Artefakte
   als `active`, `archive_candidate`, `review` oder `consolidate_suggest`.
3. Drift Detection erkennt Strukturabweichungen, Redundanz und unklare
   Top-Level-Eintraege in ueberwachten Bereichen.
4. Canonical Enforcement stellt sicher, dass keine automatische Loeschung,
   keine automatische Migration und keine unverifizierte Strukturveraenderung
   erfolgt.
5. Continuous Verification Loop bindet Canonical Architecture Manager,
   Canonical Artifact Manager und Release Integrity Status ein.

## Logging

Jede Governance-Entscheidung wird in
`31_reports/governance/phase3_continuous_governance_log.jsonl` protokolliert.
Ein Eintrag enthaelt Datei/Artefakt, Klassifikation, Begruendung,
Systemkontext, Zeitstempel und Verifikationsstatus.

## Sicherheitsgrenze

Phase 3 loescht keine Dateien, fuehrt keine Grossmigration durch und verschiebt
keine Artefakte automatisch. Strukturveraenderungen bleiben kontrollierte,
verifizierte Aenderungen.
## Governance Baseline 34.1

Die verifizierte Phase-3-Baseline liegt unter
`24_config/canonical_governance_baseline_34_1.json`. Sie referenziert den finalen
Release-Gate-Bericht, das Governance-Log, die zentrale Governance-Konfiguration
und die Hashes der wichtigsten Phase-3-Artefakte.

## Phase-3-Stabilisierungsschicht

Die Baseline 34.1 ist eine unveraenderliche Read-only-Referenz. Phase 3 nutzt
sie als Vergleichspunkt fuer alle laufenden Governance-Pruefungen.

Aktive Komponenten:

1. Canonical Governance Monitor (CGM): orchestriert Baseline-Vergleich,
   Driftanalyse, Integrity-Pruefung und Reportexport.
2. Drift Detection Engine (DDE): klassifiziert Abweichungen als LOW, MEDIUM
   oder HIGH.
3. Canonical Integrity Checker (CIC): validiert neue oder geaenderte Artefakte
   gegen Baseline, Registry- und Naming-Regeln im Read-only-Flagging-Modus.
4. Governance Event Logger (GEL): schreibt Governance-Ereignisse append-only in
   die auditierbare JSONL-Chronik.

Regelmaessig erzeugte Reports:

- `31_reports/governance/phase3/governance_status_report.json`
- `31_reports/governance/phase3/drift_report.json`
- `31_reports/governance/phase3/integrity_report.json`
- `31_reports/governance/phase3/baseline_compliance_score.json`

Leitprinzip: Das System darf wachsen, aber nicht vom Referenzzustand abweichen,
ohne es sichtbar zu machen.

## Integration Internet-Learning / IKG 1.0

Phase 3 fuehrt Internet-Learning als beobachteten Learning-Layer-Bereich. Die
Policy `24_config/internet_knowledge_governance_1_0.json`, die technische
Policy `24_config/internet_learning_policy_34_1.json`, Queue, Review und
Provenienzfelder sind governancepflichtig.

Der kanonische Standardzustand ist `enabled=true`: Internet-Learning startet
beim Systemstart automatisch, bleibt aber strikt auf Queue, Review,
Provenienzpflicht und IKG-1.0-Bewertung begrenzt.

Continuous Canonical Governance bewertet Abweichungen an diesen Artefakten als
Drift- oder Review-Ereignis. Automatische Wissensuebernahme, automatische
Archivierung und automatische Loeschung bleiben ausgeschlossen.

## Integration WebAgent 1.0

WebAgent 1.0 ist die direkte URL-, Extraktions- und Crawl-Schicht. Die Policy
`24_config/web_agent_1_0.json`, der Core `01_system/kontinuum/core/web_agent.py`,
die Webquellennachweise unter `32_data/web_agent_sources`, Queue, Review und
das Log `27_logs/web_agent_1_0.jsonl` sind governancepflichtig.

URL-haltige Befehle haben Vorrang vor lokaler Suche und vor externen
Suchprovidern. Brave-, Semantic-Scholar-, arXiv- oder DuckDuckGo-Fehler duerfen
den direkten URL-Abruf nicht blockieren.

Der Standardmodus ist `diagnostic_review_only`: Inhalte werden abgerufen,
extrahiert, gehasht, mit Zeitstempel und Quelle gespeichert und in Review
uebergeben. Direkte Memory-Schreibungen, automatische kanonische
Wissensuebernahme, Massen-Crawls und grosse Downloads ohne Freigabe bleiben
ausgeschlossen. Crawl-Auftraege sind auf `max_pages=20`, `max_depth=2`, gleiche
Domain und robots.txt-Respekt soweit moeglich begrenzt.

## Integration FileAgent 1.0

FileAgent 1.0 ist die read-only Datei- und Ordner-Lernschicht. Die Policy
`24_config/file_agent_1_0.json`, der Core
`01_system/kontinuum/core/file_agent.py`, die Quellennachweise unter
`32_data/file_agent_sources`, die Review-Nachweise unter
`32_data/file_agent_review` und das Log `27_logs/file_agent_1_0.jsonl` sind
governancepflichtig.

Datei- und Ordnerbefehle werden vor normaler Suche verarbeitet. Der Agent liest
nur freigegebene Projekt- und Importbereiche, startet keine Dateien, loescht
nichts, veraendert nichts und schreibt keine Inhalte direkt in Memory oder den
kanonischen Wissensbestand. Jeder Import wird mit Dateipfad, Groesse,
Dateityp, Hash, Zeitstempel, Kurzinhalt und Review-Status protokolliert.

Ordnerimporte bleiben kontrolliert: standardmaessig nicht rekursiv,
`max_files=50`, `max_file_size=400 MB`, nur erlaubte Endungen. Drag-and-Drop in
der GUI erzeugt lediglich FileAgent-Befehle im Eingabefeld und umgeht keine
Pfad-, Format- oder Governance-Pruefung.

## Entscheidungsarchitektur CDE 2.0 / CKDE 1.0

Phase 3 fuehrt zwei strikt getrennte Entscheidungsdomaenen:

- CAM beobachtet und prueft Projektstruktur, Pfade, Registries,
  Datenbankvertrag und Artefakte read-only.
- CDE 2.0 nutzt diese Artefaktbeobachtungen fuer Entscheidungen ueber
  `active`, `archive_candidate`, `review` und `consolidate_suggest`.
- Internet Learning sammelt nur kontrollierte Quellenfunde und schreibt sie in
  Queue und Review.
- IKG 1.0 begrenzt erlaubte Quellen, Provenienzpflicht, Sicherheitsregeln und
  Review-Pflicht.
- CKDE 1.0 bewertet nur Wissensobjekte mit `ACCEPT`, `REVIEW`, `REJECT` oder
  `CONFLICT` und schreibt append-only Nachweise in `knowledge_evaluations`,
  `source_ratings`, `knowledge_conflicts` und `evaluation_history`.
- Continuous Canonical Governance beobachtet beide Pfade getrennt und
  protokolliert Drift, Review-Bedarf und Policy-Abweichungen.
- Das Release Integrity Framework prueft, ob die benoetigten Policies,
  Kernmodule, Datenbankvertraege, Dokumente und Tests vorhanden und konsistent
  sind.

Die CDE darf keine Wissensobjekte entscheiden. Die CKDE darf keine Dateien,
Dokumente oder Quellcode-Lebenszyklen entscheiden. Konflikte im Wissenspfad
werden niemals automatisch aufgeloest; beide Quellen und Provenienzen bleiben
erhalten und Governance Review wird erzeugt.

## Continuous Canonical Engine Blueprint 1.0

Phase 3 wird um eine Continuous Canonical Engine erweitert. Sie verbindet lokale
Systemereignisse, CDE 2.0, Drift Layer, Governance Hooks und Release-Gates in
einer auditierten Entscheidungskette:

```text
System Event -> Event Bus -> Canonical Decision Engine -> Drift Layer -> Governance Hooks -> Review/Gate/Release Decision
```

Der Event Bus ist lokal, append-only und ohne Netzwerk-Broker. Kanonische Events
verwenden die Felder `event_id`, `event_type`, `source_component`,
`affected_path`, `affected_object_id`, `timestamp`, `severity`, `payload`,
`provenance`, `governance_context` und `processing_state`.

CDE 2.0 klassifiziert Events als `ACTIVE`, `ARCHIVE_CANDIDATE`,
`REVIEW_REQUIRED`, `CONSOLIDATION_SUGGESTED` oder `BLOCKED`. Der Drift Layer
klassifiziert `EXPECTED_DRIFT`, `LOW_DRIFT`, `MEDIUM_DRIFT`, `HIGH_DRIFT` und
`BLOCKING_DRIFT`. Erwarteter Dokumentationsdrift wird nur dokumentiert,
LOW_DRIFT wird geloggt, MEDIUM_DRIFT erzeugt Review, HIGH_DRIFT blockiert
Release und BLOCKING_DRIFT stoppt das Gate.

Governance Hooks entstehen bei HIGH/BLOCKING Drift, fehlender Provenienz,
Policy-Verletzung, unregistrierten Artefakten, unklarer Kanonizitaet,
Code-/Dokumentationskonflikten, Internet-Lernen ohne Review und Release-Gates
mit offenen Review-Punkten. Keine Hook-Regel loescht, verschiebt, archiviert
oder uebernimmt Inhalte automatisch.

Aktive Nachweise:

- `24_config/continuous_canonical_engine_34_1.json`
- `01_system/kontinuum/core/continuous_canonical_engine.py`
- `31_reports/events/canonical_events.jsonl`
- `31_reports/events/event_processing_log.jsonl`
- `31_reports/drift/drift_events.jsonl`
- `31_reports/governance/governance_hooks.jsonl`
