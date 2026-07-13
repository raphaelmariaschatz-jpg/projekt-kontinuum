# Release 32.2 - Temporal Relevance Core

Stand: 2026-06-16

Kontinuum 32.2 ergänzt eine Zeitrelevanzschicht gegen Bedeutungsinflation.
Historische Daten bleiben append-only; ihre aktuelle Relevanz wird getrennt
bewertet.

## Umgesetzt

- neuer Core `temporal_relevance.py`
- neue Tabellen `relevance_assessments` und `relevance_reports`
- Kantenstatus `active`, `aging`, `obsolete_candidate`
- Chronikprägung für prägende Ereignisse
- strategische Wissenslückenpriorisierung
- Anti-Zirkularitätsprüfung für Meaning/Motivation
- neue Befehle `relevanzstatus`, `bedeutungsinflation`,
  `chronikprägung`, `wissenslückenpriorität`
- GUI-Schnellbefehle und Aktivitätsprognose erweitert
- Persistent Self Model um Relevanzzähler und Zirkularitätsverletzungen
  erweitert

## Realer Stand

- Relevanzbewertungen: 2.777
- bewertete Meaning-Kanten: 2.665
- Chronikbewertungen: 53
- Wissenslückenprioritäten: 58
- Kantenstatus: 2.662 aktiv, 3 alternd, 0 Obsoleszenz-Kandidaten
- Zirkularitätsverletzungen: 0
- Chronik: 53/53 signiert
- Schutzgrenzen: 5/5 intakt
- vollständige aktive Testsuite: 40/40 bestanden

## Bedeutung

32.2 ist kein weiterer Bewertungs-Core im Sinne von "mehr Scores", sondern
eine Härtung der vorhandenen Bedeutungsschicht. K kann nun zwischen
historischer Speicherung und aktueller Relevanz unterscheiden.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
