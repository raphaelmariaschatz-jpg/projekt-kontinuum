# Kontinuum 27.2 - Seitenprüfung und Quellenqualität

Datum: 2026-06-15

Kontinuum 27.2 erweitert den epistemischen Prüfzyklus:

```text
Snippet -> Seiteninhalt -> Quellenklassifikation -> Evidenz
```

## Eingeführt

- Seitenabruf als Voraussetzung für neue Evidenz
- sieben nachvollziehbare Quellenklassen
- Qualitätsgewichte je Quellenklasse
- qualitätsgewichtete Vertrauensberechnung
- persistente Klassifikationsgründe und Seitenauszüge

## Qualitätsnachweis

`test_v27_2_source_quality.py` bestätigt alle Quellenklassen.
`test_v27_1_epistemic_actions.py` bestätigt den erweiterten geschlossenen
Prüfkreislauf mit Seitenprüfung.

## Reale Aktivierung

Ein kontrollierter Prüfzyklus auf dem vorhandenen Datenbestand akzeptierte
zwei erfolgreich abgerufene Seiten als Evidenz. Beide wurden konservativ als
`unknown` mit Gewicht `0.40` klassifiziert. Das resultierende
Quellenqualitätsgewicht von `0.80` führte gemeinsam mit den vorhandenen
Bestätigungen zu Vertrauen `0.58` (`mittel`) und zum Zustandswechsel
`uncertain -> knowledge`.

Damit wurde der vollständige 27.2-Pfad auch außerhalb der Regressionstests
erfolgreich aktiviert.
