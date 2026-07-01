# Kontinuum 27.0 - Epistemisches Zustandsmanagement

Datum: 2026-06-15

Kontinuum 27.0 führt Hypothesen, Unsicherheit, Wissenslücken und priorisierte
Überprüfungsaufträge als aktive Bestandteile der Knowledge Platform ein.

## Eingeführt

- Zustände `knowledge`, `hypothesis`, `uncertain` und `review_required`
- erklärbare Unsicherheitsgründe
- idempotente Prüfaufträge in der Lernauftragstabelle
- gemeinsame Sicht auf epistemische Prüfbedarfe und Meta-Lernlücken
- neue Abfragen für Vermutungen, Unsicherheit, Prüfbedarf und Wissenslücken

## Qualitätsnachweis

`test_v27_0_epistemic_state.py` bestätigt das vollständige epistemische
Zustandsmanagement end to end.

## Reale Aktivierung

Nach der Aktivierung auf dem bestehenden Wissensbestand:

- 29 integrierte Wissenseinheiten epistemisch bewertet
- 1 Wissenseinheit als ausreichend belegtes `knowledge` klassifiziert
- 28 Wissenseinheiten als `uncertain` klassifiziert
- keine ausdrücklich markierten Hypothesen im aktuellen Bestand
- keine aktuellen explizit vergleichbaren Wissenskonflikte
- 44 aktive epistemische Prüf- und Meta-Lernlücken sichtbar
- historische Versionsübergänge erfolgreich von aktuellen Konflikten getrennt
- Kontrolllauf bestätigte keine Selbstreintegration durch epistemische Abfragen
