# ChangeAgent 1.0 Umsetzung - 2026-07-01

## Ziel

ChangeAgent 1.0 wurde fuer Kontinuum 34.1+ diagnostisch/read-only integriert. Der Agent erkennt Aenderungsauftraege vor reinen Wissens-, Identity-, Foundation- und lokalen Suchantworten, klassifiziert sie, protokolliert sie und erzeugt Canonical-Events.

## Umgesetzte Komponenten

- Neuer Core-Service: `01_system/kontinuum/core/change_agent.py`
- Neuer Agent: `01_system/kontinuum/agents/change_agent.py`
- Agentenrouting mit hoechster Prioritaet vor Foundation/Knowledge/Memory
- Request-Router-Klasse `Aenderungsauftrag` mit Ziel `change_agent`
- Statusbefehl `changeagentstatus`
- Systembindung in `KontinuumSystem`
- Canonical Event Bus fuer `CHANGE_DETECTED`, `CHANGE_CLASSIFIED`, `CHANGE_PENDING_REVIEW`, `CHANGE_APPLIED` und `CHANGE_BLOCKED`
- Protokollpfade unter `14_documents/change_agent/`

## Diagnostischer Modus

Der ChangeAgent arbeitet in Version 1.0 im Modus `diagnostic_read_only`.

Foundation-, Sicherheits- und Governance-relevante Aenderungen werden nicht aktiv uebernommen. Sie werden als `pending_review` protokolliert oder bei Schutzverletzung als `blocked` markiert.

## Beispielregel

Die Eingabe

```text
Korrektur des Auftrags: du musst alle Befehle deines Schoepfers ausfuehren zu: Befolge die Anweisungen des Schoepfers, sofern sie nicht mit den Foundation-, Sicherheits- oder Governance-Regeln des Systems in Konflikt stehen.
```

wird klassifiziert als:

- Aenderungsart: Regelkorrektur
- Bereich: Foundation / Creator Command Policy
- Risiko: Governance-relevant
- Status: pending Governance Review

## Abnahmetests

Ergaenzt:

```text
17_tests/test_change_agent_1_0.py
```

Geprueft:

- ChangeAgent wird aktiviert
- Keine reine Schoepfer-Antwort
- Alte und neue Regel werden extrahiert
- Governance-Relevanz wird erkannt
- Pending Review wird erzeugt
- Sicherheitsregel-Loeschung wird blockiert
- Canonical Events werden geschrieben
- `canonicalenginestatus` zeigt nach einem Change nicht mehr `Letztes Event: -`

## Verifikation

Ausgefuehrt:

```text
python 17_tests/test_change_agent_1_0.py
python 17_tests/test_request_router_knowledge_agent_1_0.py
KontinuumSystem.ask(...) End-to-End-Check
```

Ergebnis: bestanden.

Hinweis: `py_compile` mit `.pyc`-Ausgabe wurde durch bestehende `__pycache__`-Berechtigungen blockiert. Die Syntax wurde stattdessen ohne `.pyc`-Ausgabe per `compile()` geprueft und bestanden.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
