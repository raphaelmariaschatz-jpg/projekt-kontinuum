# Release 32.0 - Motivation Explanation Core

Stand: 2026-06-16

Kontinuum 32.0 erweitert den Motivation Core um erklärbare Bewertungsherkunft.
Scores werden nun über gespeicherte Gründe, Meaning-Kanten, Evidenzbelege und
Erklärungspfade auditierbar nachvollziehbar.

## Umgesetzt

- neuer Core `motivation_explanation.py`
- neue append-only Tabellen:
  - `motivation_explanations`
  - `motivation_evidence`
  - `motivation_paths`
- Integration in `KontinuumSystem`
- Integration in Persistent Self Model
- neue Foundation-Agent-Befehle für Score-Erklärungen und Einflüsse
- Conversation-Command-Erkennung für 32.0-Befehle
- GUI-Schnellbefehle für Motivationserklärung und wichtige Einflüsse
- GUI-Aktivitätsprognose für Erklärungstabellen
- neuer Regressionstest `test_v32_0_motivation_explanation.py`

## Realer Aktivierungsnachweis

- Version: 32.0
- Motivation-Scores: 2.530
- Motivation-Reports: 2
- Score-Erklärungen: 2.530
- Evidenzbelege: 21.715
- Erklärungspfade: 2.530
- Bedeutungsknoten: 546
- Bedeutungsbeziehungen: 2.270
- Foundation Decision Layer: 161/161 vollständig
- Kontinuitätskette intakt
- Chronik: 48/48 signiert
- 5/5 Selbstmodell-Schutzgrenzen intakt
- offene innere Konflikte: 0
- Testsuite: 39/39 bestanden

## Grenze

32.0 erklärt funktionale Bedeutungsgewichtungen. Das ist kein Nachweis von
Wille, Bewusstsein oder subjektivem Erleben.
