# Release 34.1 – Release Integrity Framework

Stand: 2026-06-21

Version 34.1 führt die bisher prozessualen Freigaberegeln als ausführbare,
fehlerschließende Gate-Kette ein.

## Neu

- signierte Quellbaseline und Audit-Snapshot
- SQLite-konsistentes Release-Backup mit SHA-256-Manifest
- Restore- und Rollback-Probe außerhalb der Produktivwurzel
- vollständige Altversionssuche über aktive Pfade
- vollständiger Testlauf mit Einzeltest-Zeitlimit und Hängererkennung
- gemeinsame Versions-, Pfad-, Chronik- und Wiedereinstiegsprüfung
- manipulationsgeschützter Gate-Bericht
- Freigabe ausschließlich bei acht vollständig grünen Gates
- kanonischer Root-Starter `START_KONTINUUM.bat` mit automatischem
  `PYTHONPATH=C:\Projekt Kontinuum\01_system` und Paketstart
  `python -m kontinuum`
- IKG 1.0 als Policy fuer erlaubte Internetquellen, Review, Provenienz,
  Bandbreitenkontrolle und Ausschluss automatischer Wissensuebernahme
- Internet-Learning standardmaessig aktiviert: automatischer Start beim
  Systemstart, aber ausschliesslich Queue-/Review-Uebergabe und keine direkte
  kanonische Wissensuebernahme

Foundation Reasoning 4.1, die 31 stabilen Regeln und die zwölf vorläufigen
Leitprinzipien bleiben unverändert aktiv. `legacy_kontinuum_23.py` bleibt als
historischer Nachweis isoliert und ist kein aktiver Release-Test.

## Erweiterung 30.06.2026

Phase 3 wurde um die Continuous Canonical Engine 1.0 erweitert. Neu sind ein
lokaler append-only Event Bus, CDE-2.0-Entscheidungsklassen, Drift Layer,
Governance Hooks und ein Release-Integrity-Gate fuer HIGH_DRIFT und
BLOCKING_DRIFT.

Die Engine bleibt diagnostisch/read-only: keine automatische Loeschung, keine
automatische Archivierung und keine automatische Wissensuebernahme.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
