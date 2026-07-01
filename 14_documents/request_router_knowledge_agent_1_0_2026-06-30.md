# Request Router & KnowledgeAgent 1.0 - Abschlussbericht

Datum: 2026-06-30

## Ziel

Request Router 1.0 wurde als zentraler Einstiegspunkt der Anfragenverarbeitung diagnostisch integriert und aktiv in den Prompt-Orchestrator eingebunden. Jede Eingabe wird vor der Verarbeitung klassifiziert und einem Primaer-Agenten zugeordnet.

## Implementierte Klassen

- Wissensfrage -> KnowledgeAgent
- Lernauftrag -> LearningAgent
- Webauftrag -> WebAgent
- Dateioperation -> FileAgent
- Statusabfrage -> StatusAgent
- Governance -> CanonicalEngine
- Diagnose -> DiagnosticAgent
- Memory -> MemoryAgent
- Administration -> AdminAgent
- Programmierung/Rechenaufgabe -> MathAgent/ProgrammingAgent
- Sonstige -> DialogueAgent

## Routing-Prioritaeten

1. StatusAgent und CanonicalEngine fuer Status/Governance-Befehle
2. MathAgent fuer Rechenausdruecke
3. FileAgent fuer Datei- und Pfadangaben
4. WebAgent fuer URLs und Internetauftraege
5. LearningAgent fuer Lernbefehle
6. KnowledgeAgent fuer Wissensfragen

Der KnowledgeAgent prueft zuerst Kernwissen, lokale Lern- und Wissensquellen. Wenn lokal keine belastbare Antwort entsteht und der Suchconnector aktiv ist, nutzt er automatisch Internetrecherche; bei deaktiviertem Suchconnector faellt er auf das lokale Sprachmodell zurueck.

## Protokollierung

Jede Routerentscheidung wird in `27_logs/request_router_1_0.jsonl` protokolliert:

- Zeit
- erkannte Intention
- ausgewaehlter Agent
- alternative Agenten
- Fallback-Agenten
- Antwortdauer
- Ergebnis
- verwendete Quellen

Der Befehl `routingstatus` zeigt die letzte Entscheidung mit Begruendung, Quellen und Fallbacks.

## FileAgent-Nachbesserung

Der FileAgent erkennt nun Windows-Pfade und Dateiendungen auch ohne explizites Wort "Datei". Datei- und Pfadbefehle erhalten Vorrang vor Wissensantworten. Nicht vorhandene oder nicht freigegebene Pfade werden klar gemeldet und loesen keine Ersatzantwort aus altem Wissen aus.

Canonical-Events:

- FILE_READ_STARTED
- FILE_READ_COMPLETED
- FILE_LEARNED
- FILE_READ_FAILED

Ergebnisberichte enthalten Dateiname, Pfad, Hash, gelesene Seiten/Abschnitte und Lernstatus.

## MathAgent / Mathematikparser

Rechenausdruecke werden vor Suche, Memory und Internet erkannt. Unterstuetzt sind deutsche und internationale Dezimalzahlen, Grundrechenarten, Klammern, Potenzen, Wurzeln und Prozentnotation.

Beispiel:

`126 × 254,87 = 32 113,62`

## Abnahmetests

Ergaenzte Tests:

- `17_tests/test_request_router_knowledge_agent_1_0.py`
- `17_tests/test_file_agent_1_0.py`

Gepruefte Beispiele:

- `Was ist Quantendynamik?` -> KnowledgeAgent
- `Lerne Python.` -> LearningAgent
- `Öffne https://docs.python.org/3/` -> WebAgent
- `Lies Datei handbuch.pdf.` -> FileAgent
- `Lernstatus.` -> StatusAgent
- `CanonicalEngineStatus.` -> CanonicalEngine
- `126 × 254,87` -> MathAgent

## Status

Request Router 1.0 ist diagnostisch integriert und als zentraler Routing-Einstieg im Prompt-Orchestrator aktiv. Governance-, Foundation- und Canonical-Regeln bleiben unveraendert; der Router trifft nur Entscheidungen und schreibt sein Routing-Protokoll.
