# CDM 1.0 Status Report

Erstellt: 2026-07-02T13:19:48

## Status

- CDM 1.0 ist read-only.
- Es wurde keine Migration durchgefuehrt.
- Es wurden keine Daten geloescht, verschoben oder veraendert.
- Bestehende Pfadzugriffe wurden nicht ersetzt.

## Zahlen

- Erkannte Datenobjekte: 17434
- Aktive/kanonische Daten: 46
- Historische Daten: 17311
- Laufzeitdaten: 18
- Unklare Daten: 36

## Kategorien

- canonical_master_data: 12
- exports: 35
- historical_version_data: 17311
- logs: 16
- runtime_data: 18
- temporary_data: 6
- unclear_review_required: 36

## Risiken

- `32_data` enthaelt weiterhin aktive Laufzeitdaten, Stammdaten, Logs, Exporte, Test-/Backup-Artefakte und historische Versionsdaten im selben Bereich.
- 152 Projektdateien referenzieren Datenpfade oder historische Praefixmuster; direkte Migration wuerde Release-Integritaet riskieren.
- `02_versions`, `17_tests`, `_version_*`, `_legacy_*` und `_02_versions_*` sind historisch gewachsen und duerfen erst nach Referenzanpassung bewegt werden.
- `internet_learning_queue` und `internet_learning_review` koennen Workflow-Status sein; vor Archivierung ist manuelle Pruefung erforderlich.
- Unklare Datenobjekte bleiben `manual_review_required` und werden nicht automatisch korrigiert.

## Empfohlene naechste Schritte

1. CDM 1.0 in Status-Checks nur lesend verwenden.
2. Fuer CDM 1.1 eine zentrale Pfadadapter-API fuer neue Komponenten definieren.
3. Referenzen aus `32_data_referenzen.json` priorisieren und manuell bewerten.
4. Erst nach Tests und Governance-Freigabe Archivziele fuer historische Daten aktivieren.
5. Loeschungen weiterhin ausschliessen; Duplikate nur als Archiv-/Review-Thema behandeln.

## Governance

- Keine automatische Migration.
- Keine stillen Aenderungen.
- Keine Loeschung.
- Vollstaendige Nachvollziehbarkeit ueber Registry und Statusreport.
- Release-Integrity bleibt unberuehrt.
