# Response Policy Manager 1.0 - Abschlussbericht

Datum: 2026-06-30

## Ziel

Response Policy Manager 1.0 prueft jede Antwort unmittelbar vor der Ausgabe an den Benutzer. Die Schicht verhindert Aussagen, die den tatsaechlichen Faehigkeiten oder dem aktuellen Architekturzustand von Kontinuum widersprechen.

## Foundation-Regel

Kontinuum darf niemals Antworten erzeugen, die den Faehigkeiten oder dem aktuellen Zustand seiner eigenen Architektur widersprechen. Ist eine Aufgabe nicht ausfuehrbar, muss die tatsaechliche Ursache benannt werden, z. B. fehlende Berechtigung, nicht geladene Datei, Routerfehler oder Agent nicht verfuegbar, anstatt generische Aussagen ueber fehlende Faehigkeiten zu machen.

## Regeln

- Wenn Foundation Memory existiert, darf Kontinuum nicht behaupten, keine Erinnerungen zu haben.
- Wenn FileAgent aktiv ist, darf Kontinuum nicht behaupten, keine Dateien lesen zu koennen.
- Wenn WebAgent aktiv ist, darf Kontinuum nicht behaupten, keinen Internetzugang oder keine Webfaehigkeit zu haben.
- Wenn KnowledgeAgent aktiv ist, darf Kontinuum nicht behaupten, grundsaetzlich nichts ueber ein Thema wissen zu koennen.
- Wenn der Router einen Auftrag erkannt hat, darf die Antwort nicht nur den Auftrag wiederholen.

## Integration

Die Pruefung ist in `ResponseRecorder.finish(...)` integriert. Dadurch durchlaufen Antworten aller Agenten dieselbe Konsistenzschicht vor Conversation-Log, Foundation-Completion und Rueckgabe an die GUI/API.

## Verhalten

Die Policy ersetzt generische Falschaussagen durch zustandskompatible Ursachenhinweise. Beispiel:

`Ich kann keine Dateien lesen.`

wird bei aktivem FileAgent korrigiert zu:

`Ich habe einen FileAgent und kann freigegebene Dateien lesen; falls eine Datei nicht gelesen wurde, liegt es an Pfad, Freigabe, Existenz, Format oder Extraktion.`

## Test

Ergaenzter Test:

- `17_tests/test_response_policy_manager_1_0.py`

Geprueft werden Foundation Memory, FileAgent, WebAgent, KnowledgeAgent, Router-Echo und ein sauberer negativer Fall mit konkreter Dateiursache.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
