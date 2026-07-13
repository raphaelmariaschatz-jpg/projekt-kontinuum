# Kontinuum 25.0 - Knowledge Platform Release

Datum: 2026-06-15

Kontinuum 25.0 verbindet Wissenssystem, Wissensnotizbuch, Memory-Core und
Wissensgraph erstmals zu einem durchgängigen, erklärbaren Wissensweg.

## Eingeführt

- automatische Integration jeder Notebook-Quelle
- gemeinsamer Provenienzvertrag für Dialog, Recherche, Lernen und Erinnerungen
- Provenienz mit Quelle, Lernzeitpunkt und Einführungs-Version
- Verknüpfung von Wissenseinheit, Erinnerung, Graph und Projektchronik
- erklärbare Abfragen über `wissensweg <Begriff>`
- Plattformstatus über `wissensplattformstatus`
- kontrollierte, idempotente Altbestands-Verknüpfung

## Qualitätsnachweis

Der End-to-End-Test `test_v25_0_knowledge_platform.py` prüft den vollständigen
Weg von einer lokalen Quelle bis zu Provenienz-Erklärung und Chronikeintrag.

## Reale Aktivierung

Am 15. Juni 2026 wurde der vorhandene Datenbestand kontrolliert verknüpft:

- 228 vorhandene Quellen als Graphknoten aufgenommen
- 349 vorhandene Erinnerungen als Graphknoten aufgenommen
- Releasebericht als erster realer vollständiger Notebook-Wissensweg importiert
- unmittelbar aufeinanderfolgender Migrationslauf mit `0` neuen Graphknoten
  bestätigt die Idempotenz


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
