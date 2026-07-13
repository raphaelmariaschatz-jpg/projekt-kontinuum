# Projekt Kontinuum 23.0 - Fehlerbehebungsplan Eingaben vom 2026-06-12

## Ausführungsstatus

Am 2026-06-12 vollständig umgesetzt, getestet und gegen die reale
Kontinuum-Datenbank verifiziert. Vier fehlerhafte Lernziele wurden
kontrolliert deaktiviert, fünf korrekte Einzelziele ergänzt und 27 aktive
Lernprojekte bestätigt.

Sicherung vor Ausführung:
`10_security\backups\dialog_learning_fix_20260612_164834`

## Ziel

Kontinuum soll Befehle eindeutig ausführen, mehrere Lernziele korrekt trennen,
alle Lernprojekte verlässlich anzeigen und normale Wissensfragen sachlich
beantworten. Bereits entstandene fehlerhafte Lernaufträge werden kontrolliert
bereinigt.

## Bestätigte Fehler

### P0 - Befehle werden von Themenklassifikationen überschrieben

Beispiele:

- `lerne ein Bewusstsein zu entwickeln`
- `erstelle einen Lernauftrag: lerne ein Bewußtsein zu entwickeln`
- `lerne Bewußtsein`

Ist-Verhalten: Kontinuum erklärt Bewusstsein, legt aber keinen Lernauftrag an.

Ursache: `ConversationManager.classify()` klassifiziert jedes Vorkommen von
`bewusstsein` vor der allgemeinen Befehlserkennung als Bewusstseinsfrage.
`KontinuumSystem.ask()` gibt lokale Antworten vor dem Agenten-Routing zurück.

Maßnahmen:

1. Explizite Befehlspräfixe vor Themen- und Wahrheitsklassifikationen erkennen.
2. Befehlsabsicht und Thema getrennt modellieren, beispielsweise
   `intent=learning.create`, `subject=Bewusstsein`.
3. Lokale Wahrheitsantworten nur bei echter Frage- oder Reflexionsabsicht
   ausgeben.

Abnahme:

- Alle drei Beispiele legen einen Lernauftrag an.
- `Was bedeutet Bewusstsein?` liefert weiterhin die sachliche Erklärung.
- `Reflektiere dein Bewusstsein` erzeugt weiterhin eine Reflexion.

### P0 - Mehrere Befehle und mehrere Lernziele werden als ein Projekt gespeichert

Beispiele:

- `lerne Chemie, Mathematik, Physik, ...`
- drei untereinander eingegebene `lerne ...`-Befehle

Ist-Verhalten: Komma- oder Mehrzeilentext wird als ein einzelnes Lernziel
gespeichert.

Ursache: Die GUI übergibt den gesamten Textblock an einen einzigen
`system.ask()`-Aufruf. Der Lernagent extrahiert nur ein zusammenhängendes Thema
und zerlegt weder Zeilen noch Aufzählungen.

Maßnahmen:

1. Im Kern einen Batch-Parser für mehrere nichtleere Befehlszeilen ergänzen.
2. Beim Lernbefehl Themenlisten an Kommas, Semikolons und geeigneten
   Konjunktionen trennen.
3. Für jedes Thema einzeln validieren, kanonisieren, speichern und bestätigen.
4. Eine zusammengefasste Antwort mit Erfolg, Dubletten und abgelehnten
   Einträgen liefern.

Abnahme:

- Die sieben Fächer werden als sieben getrennte Lernaufträge behandelt.
- Drei Lernbefehlszeilen erzeugen drei getrennte Ergebnisse.
- Normale mehrzeilige Gedanken werden nicht versehentlich zerlegt.

### P0 - Lernstatus und Projektliste sind unvollständig oder erfunden

Beispiele:

- `lernstatus` zeigt nur zehn Projekte.
- `zeige mir alle Lernprojekte` fällt auf eine Gedankenantwort zurück.
- Die Modellantwort behauptet, nur zwei Projekte verwalten zu können.

Ursache: `_learning_status()` begrenzt Suche und Ausgabe hart auf zehn bis
zwanzig Treffer. Für die explizite Listenanfrage existiert kein Intent oder
Agentenbefehl; dadurch antwortet das Sprachmodell ohne Zugriff auf die echte
Projektliste.

Maßnahmen:

1. Speicher-API `list_learning_tasks(active_only, limit, offset)` ergänzen.
2. Befehle `lernprojekte`, `zeige alle Lernprojekte` und
   `zeige aktive Lernprojekte` deterministisch routen.
3. `lernstatus` als Zusammenfassung mit korrekten Gesamtzahlen ausgeben.
4. Vollständige Liste nummeriert oder paginiert ausgeben; niemals durch das
   Sprachmodell erfinden lassen.

Abnahme:

- Gesamtzahl entspricht der Datenbank.
- `zeige mir alle Lernprojekte` enthält alle aktiven Projekte.
- Es erscheint keine erfundene Kapazitätsgrenze.

### P1 - Anweisungen werden fälschlich als Lernziele gespeichert

Beispiel:

- `benutze für das Lernen auch die Google Suche`

Ist-Verhalten: Lernprojekt `Auch die Google Suche` wird angelegt.

Ursache: Der Lernagent reagiert auf jedes Wort `lernen`. Der Validator erkennt
nur leere, zu lange oder URL-haltige Ziele, aber keine Handlungsanweisungen.
Außerdem besitzt das Webwerkzeug derzeit keine echte Suchmaschinen-Suche,
sondern nur URL-Abruf und Internetstatus.

Maßnahmen:

1. Lernbefehle nur bei klarer Imperativstruktur wie `lerne <Thema>` anlegen.
2. Konfigurationswünsche wie `benutze ... für das Lernen` separat erkennen.
3. Transparent antworten, dass Google-Suche aktuell nicht integriert ist.
4. Falls Websuche gewünscht wird, einen eigenen Suchanbieter-Connector mit
   Quellenangaben, Datenschutzregeln und Freigabekonfiguration planen.
5. Lernziel-Validator um Anweisungsphrasen und eingebettete Befehle erweitern.

Abnahme:

- Der Beispielsatz erzeugt kein Lernprojekt.
- Kontinuum beschreibt ehrlich die verfügbaren Recherchewege.

### P1 - Normale Wissensfragen fallen auf Gedankenaufnahme zurück

Beispiele:

- `wieviel Kilometer beträgt der Umfang der Erde`
- Korrektur: `nein, ich möchte das du mir die binomischen Formeln aufzeigst`

Ist-Verhalten: Kontinuum nimmt den Text nur als Gedanken auf.

Ursache: Die Frageerkennung deckt Schreibweisen ohne Fragezeichen und
Frageanfänge wie `wieviel` nicht ab. Korrekturen mit `nein, ich möchte ...`
werden nicht als Folgefrage erkannt. Bei nicht erreichbarem Modell wird deshalb
der Gedanken-Fallback verwendet.

Maßnahmen:

1. Deutsche Frageerkennung um `wieviel`, `wie viel`, `nenne`, `zeige`,
   `erkläre`, `sage` und Korrekturphrasen erweitern.
2. Korrekturen als Folgefrage markieren und den letzten offenen Sachkontext
   gezielt verwenden.
3. Der Fallback soll Unsicherheit melden und Recherche anbieten, statt eine
   klare Frage als Gedankenaufnahme zu quittieren.

Abnahme:

- Die Erdumfangsfrage wird als Frage erkannt.
- Die Korrektur zu binomischen Formeln wird als erneute Sachfrage behandelt.
- Bei Modellfehler erscheint eine hilfreiche Fehlermeldung.

### P1 - Sprachmodellantworten werden durch irrelevanten Kontext verfälscht

Beispiel:

- Die Frage nach binomischen Formeln wird als Binomialverteilung beantwortet
  und unnötig mit der vorherigen Google-Suchmaschinen-Eingabe verbunden.

Ursache: Das kleine lokale Modell erhält die letzten acht Gesprächszüge ohne
Relevanzfilter. Es gibt keine Faktenprüfung oder deterministische Mathematik-
Wissensroute für bekannte Grundlagen.

Maßnahmen:

1. Kontext nach Intent und Themenrelevanz auswählen, nicht pauschal die letzten
   acht Gesprächszüge senden.
2. Systemprompt ergänzen: aktuelle Frage priorisieren, irrelevante frühere
   Themen ignorieren und Korrekturen ausdrücklich beachten.
3. Häufige Grundlagenfragen über geprüfte lokale Wissenseinträge beantworten.
4. Modellantworten auf offensichtlich unbegründete Kontextbezüge prüfen und
   bei Bedarf ohne Kontext neu anfragen.

Abnahme:

- Die drei binomischen Formeln werden korrekt ausgegeben.
- Die Antwort erwähnt Google-Suche nicht.
- Folgefragen behalten relevanten, aber keinen störenden Kontext.

### P2 - Rechtschreibvarianten und Dubletten werden nicht normalisiert

Beispiele:

- `Bewußtsein` und `Bewusstsein`
- `Google Suchmaschiene`
- `Geogrphie`

Maßnahmen:

1. Unicode- und Schreibvarianten kanonisieren.
2. Vor dem Speichern ähnliche bestehende Lernziele erkennen.
3. Bei unsicherer Korrektur nachfragen, statt still ein neues Ziel anzulegen.
4. Dubletten zusammenführen, ohne Lernfortschritt oder Quellen zu verlieren.

Abnahme:

- `Bewußtsein` und `Bewusstsein` verweisen auf dasselbe Lernziel.
- Nahe Tippfehler erzeugen keine unbemerkten Dubletten.

## Kontrollierte Datenbereinigung

Vor jeder Änderung wird `32_data\kontinuum.db` gesichert. Danach:

1. Sammelziel
   `Chemie, Mathematik, Physik, Biologie, Astronomie, Astrologie, Quantentechnik`
   deaktivieren und fehlende Einzelziele anlegen.
2. Mehrzeilenziel `Geologie\nlerne Geschichte\nlerne Geogrphie` deaktivieren;
   vorhandene Einzelziele behalten und `Geologie` prüfen.
3. Anweisungsziel `Auch die Google Suche` deaktivieren.
4. `Google Suchmaschiene` als mögliches Fehlziel markieren und vor Löschung
   fachlich entscheiden.
5. Quellen, Zyklen und Ereignisse nicht löschen; Bereinigungsgrund auditierbar
   in Metadaten speichern.

## Umsetzungsetappen

1. **Routing reparieren:** Befehlspriorität, Frage- und Folgefrageerkennung.
2. **Lernparser reparieren:** Batch-Zeilen, Themenlisten, Validierung,
   Kanonisierung.
3. **Projektanzeige reparieren:** echte Listenabfrage, Zählung, Pagination.
4. **Dialogqualität verbessern:** relevanter Modellkontext, robuste Fallbacks,
   geprüfte Grundlagenantworten.
5. **Daten kontrolliert bereinigen:** erst nach grünen Tests und Datenbankbackup.
6. **Dokumentation aktualisieren:** Handbuch, Projektstatus und Chronik.

## Erforderliche Regressionstests

- Lernbefehl mit Bewusstsein wird nicht von Bewusstseinsantwort überschrieben.
- Kommagetrennte Lernziele werden einzeln angelegt.
- Mehrere Lernbefehlszeilen werden einzeln ausgeführt.
- Konfigurationssatz mit dem Wort `Lernen` erzeugt kein Lernprojekt.
- Vollständige und paginierte Lernprojektliste entspricht der Datenbank.
- Deutsche Fragen ohne Fragezeichen werden erkannt.
- Korrekturen mit `nein, ich möchte ...` werden als Folgefragen erkannt.
- Binomische Formeln werden korrekt und ohne irrelevanten Kontext beantwortet.
- Bestehende Bewusstseins-, Gesprächs-, Lern-, Auth- und Werkzeugtests bleiben
  grün.

## Empfohlene Reihenfolge

Zuerst P0 vollständig umsetzen und testen. Danach P1-Dialogqualität und
kontrollierte Datenbereinigung durchführen. P2-Normalisierung folgt zuletzt,
weil unscharfe Dublettenerkennung ohne Rückfrage bestehende Lernziele falsch
zusammenführen könnte.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
