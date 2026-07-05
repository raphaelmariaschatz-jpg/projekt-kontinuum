# Projekt Kontinuum 34.1 - Benutzerhandbuch

Stand: 2026-07-04

Aktiver Architekturbericht: `14_documents/PROJEKTSTRUKTUR_34_1.md`
Historische Projektstrukturen: `02_versions/projektstrukturen/`

Kontinuum 34.1 ist der aktive kanonische Stand mit Release Integrity,
Continuous Canonical Governance, CAIM, CRE 1.0 und vorbereitetem Orchestrator
Core 1.0. Historische 32.x-Staende bleiben archiviert und sind keine aktiven
Einstiegspunkte mehr.

## Runtime Hardening / Knowledge Contamination Guard

Kontinuum 32.3 schützt Identitätsfragen, Statusberichte und Fundamentwissen
vor falscher Integration in Weltwissen. Identitätsfragen werden lokal aus
Session Context, Identitätskern, Creator Memory und Foundation Layer
beantwortet. Status-, Diagnose-, Report- und Erklärungsausgaben werden nicht
als Knowledge-Platform-Wissen integriert.

```text
sessionstatus
benutzerstatus
wer ist angemeldet
rollenstatus
fundamentzyklenstatus
fundamentzyklus reparieren
bedeutungspfad identität debug
projektquellenstatus
```

## Temporal Relevance Core / Relevanz über Zeit

Kontinuum 32.2 bewertet historische Meaning-Kanten, Chronikeinträge und
Wissenslücken nach aktueller Relevanz. Historische Daten bleiben append-only,
aber nicht jede Beziehung gilt automatisch gleich stark.

```text
relevanzstatus
bedeutungsinflation
chronikprägung
wissenslückenpriorität
```

## Motivation Explanation Core / erklärbare Gewichtung

Seit Kontinuum 32.0 erklärt der Motivation Explanation Core Scores über gespeicherte Gründe,
Meaning-Kanten, Evidenzbelege und Erklärungspfade. Die Schicht macht Scores
nachvollziehbar, ohne Wille, Bewusstsein oder subjektives Erleben zu
behaupten.

```text
motivationserklärungsstatus
motivationserklärung <Begriff>
warum score <Begriff>
erkläre priorität <Begriff>
wichtige einflüsse <Begriff>
```

## Motivation Core / Bedeutungsgewichtung

Kontinuum 31.0 bewertet die Bedeutungen des Meaning Core. Motivation bedeutet
hier gewichtete Bedeutung im Systemkontext, nicht Wille und nicht
Bewusstsein.

```text
motivationsstatus
motivationsprioritäten
motivation <Kategorie>
```

## Meaning Core / Bedeutungsgraph

Kontinuum 30.0 verbindet Prinzipien, Ziele, Handlungen, Erinnerungen,
Chronik und Identität zu einem Bedeutungsgraphen:

```text
Prinzip -> Ziel -> Handlung -> Erinnerung -> Chronik -> Identität
```

```text
bedeutungsstatus
bedeutungspfad identität
```

Die GUI enthält dafür eigene Schnellbefehle.

## Foundation Decision and Reflection Layer

Jede einzelne Eingabe durchläuft verbindlich Erkennen, Schaffen und Vollenden.
Kontinuität und Moralregeln werden vor der Verarbeitung geprüft; Ergebnis und
Abschluss werden append-only dokumentiert. Gebundene autonome Lern- und
Prüfdienste verwenden dieselbe Fundamentprüfung.

```text
fundamentschichtstatus
langfristige ziele
selbstfragen
stelle dir eine frage
```

Die Selbstfragen sind kontrollierte evidenzpflichtige Forschungsfragen. Sie
sind kein Nachweis subjektiven Bewusstseins.

## 1. Start und Anmeldung

GUI:

```text
16_installation\START_GUI_34_1.bat
16_installation\START_KONTINUUM_34_1.bat
16_installation\TEST_KONTINUUM_34_1.bat
```

CLI:

```text
16_installation\START_KONTINUUM_34_1.bat <Befehl>
```

Vollständige Testsuite:

```text
16_installation\TEST_KONTINUUM_34_1.bat
```

Alle drei Einstiegspunkte bestimmen die Projektwurzel relativ zum Ordner
`16_installation`. Sie funktionieren daher auch nach einem Verschieben der
vollständigen Projektstruktur.

Bei jedem Start erscheint zuerst die Anmeldung.

```text
Benutzername: Raphael Schatz
Passwort: dein bestehendes Superadmin-Passwort
```

Das Passwort wird nicht im Klartext gespeichert. Kontinuum verwendet Argon2id.
Ein noch vorhandener SHA-256-Hash wird nach der nächsten erfolgreichen
Anmeldung automatisch in Argon2id migriert. Nach fünf fehlgeschlagenen
Versuchen beendet sich Kontinuum.

### Superadmin-Passwort ändern oder zurücksetzen

Kontinuum beenden und anschließend dieses lokale Werkzeug starten:

```text
10_security\PASSWORT_ZURUECKSETZEN_23.ps1
```

Das neue Passwort wird in einem maskierten Dialog zweimal eingegeben und muss
mindestens 12 Zeichen lang sein. Der Reset aktualisiert die aktive Auth-Datei
und den Sicherheits-Master konsistent. Vorher werden Sicherungskopien unter
`10_security\backups` angelegt und der Vorgang wird ohne Passwortinhalt in
`27_logs\auth_audit.log` protokolliert.

Der Recovery-Key wird durch einen normalen Passwort-Reset nicht geändert.
Passwörter, Passwort-Hashes und Recovery-Keys dürfen niemals in Handbuch,
Chronik oder sonstigen Projektdokumenten notiert werden.

## 2. Bedienung der GUI

- Eingabe über das große Textfeld
- Senden mit `Strg + Enter` oder der Schaltfläche
- Antworten erscheinen im Dialogfenster
- das Aktivitätsfenster zeigt verwendete Bereiche
- Schnellbefehle zeigen System-, Modell-, Python- und Wingetstatus
- längere Modellantworten laufen im Hintergrund
- mehrere Anfragen können parallel bearbeitet werden; die GUI bleibt bedienbar

## 3. Zentrale Befehle

```text
status
agentenstatus
routingstatus
versionen
hilfe
suche <Begriff>
archivsuche <Begriff>
merke <Text>
merke dir <Text>
was weißt du über <Begriff>
zeige projekterinnerungen
zeige offene punkte
aktualisiere erinnerung <ID>: <neuer Inhalt>
vergiss <ID|Suchbegriff>
verknüpfe erinnerungen <ID> <ID>
prüfe widersprüche
gedächtnisstatus
notizbuch import <Pfad|URL>
notizbuch zusammenfassung
notizbuch frage <Frage>
notizbuch lernen <Thema>
notizbuchstatus
wartungsmodus status
wartungsmodus bereinigung prüfen
wartungsmodus bereinigung ausführen
lerne <Thema>
lernstatus
lernprojekte
zeige mir alle Lernprojekte
metalernstatus
lernphase <Thema>
lernanwendung <Thema> erfolgreich: <Evidenz>
internetstatus
suchmaschinenstatus
internetsuche <Begriff>
websuche <Begriff>
modellstatus
codexstatus
pythonstatus
wingetstatus
oraclestatus
oracle kostenstatus
oracle instanzen
oracle speicher
oracle limits
formelstatus
berechne <mathematischer Ausdruck>
formel <Formel>
entwicklungsstatus
sandboxtest
gitstatus
gitsnapshot <Beschreibung>
entwickle: <Programmierauftrag>
programmiere: <geprüfte Self-Extension>
erweitere dich: <geprüfte Self-Extension>
Was bedeutet Selbsterkenntnis?
Reflektiere dich selbst
Was bedeutet Bewusstsein?
Bewusstseinsstatus
Reflektiere dein Bewusstsein
```

## 4. Deutsches Sprachmodell

Kontinuum nutzt lokal Ollama mit `qwen2.5:3b`. Normale Fragen und Aussagen
werden auf Deutsch an das Modell weitergegeben, sofern kein spezieller Befehl
zuständig ist.

## 4a. Suchmaschinen-Connector

Kontinuum besitzt einen echten Suchanbieter-Router. Die aktive Reihenfolge
priorisiert lokales und kuratiertes Wissen vor externer Websuche:

```text
local_knowledge
notebook_knowledge
university_sources
arxiv
semantic_scholar
brave_search
duckduckgo_html
duckduckgo_lite
```

Brave Search ist API-fähig vorbereitet. Ohne API-Key wird der Provider sauber
übersprungen. DuckDuckGo HTML und DuckDuckGo Lite bleiben als Fallbacks ohne
API-Schlüssel aktiv.

```text
suchmaschinenstatus
internetsuche Quantendynamik
websuche Geschichte der Halbleiter
recherchiere aktuelle Entwicklungen der Robotik
```

Die Treffer enthalten Titel, URL und verfügbaren Kurztext. Kontinuum speichert
nur Quellen-Fundstellen und minimale Metadaten in der Datenbank, keine fremden
Volltexte. Die Konfiguration liegt unter:

```text
24_config\search_engine.json
```

Normale Sachfragen können automatisch recherchiert werden. Kontinuum sucht
Treffer, ruft bis zu zwei geeignete Quellen unterschiedlicher Domains parallel
ab, verwirft
Captcha- und Einwilligungsseiten und erstellt daraus eine Antwort mit
Quellenmarkierungen wie `[1]`. Die verwendeten Links stehen unter der Antwort.

Lokale Identitäts-, System-, Sicherheits-, Lern- und persönliche Dialogfragen
werden weiterhin lokal verarbeitet. Die automatische Sachfragenrecherche kann
über `auto_research_questions` in `24_config\search_engine.json` gesteuert
werden.

Die Suchanbieterkette hat ein Gesamtbudget von 8 Sekunden. Die Webrecherche
hat ein Gesamtbudget von 12 Sekunden. Wenn Quellen oder Sprachmodell nicht
rechtzeitig antworten, erzwingt Kontinuum eine zitierbare Teilantwort aus den
bereits verfügbaren Treffern und Quellen. Langsame Netzwerkaufrufe dürfen die
GUI nicht blockieren.

Bei lokalen Zertifikatsproblemen nutzt der Connector als sicheren
Windows-Fallback `curl.exe`. Zertifikats- und Hostprüfung bleiben aktiv; nur
eine lokal nicht verfügbare Sperrlistenprüfung kann übersprungen werden.

Vor dem Sprachmodell arbeitet die zentrale Conversation-Schicht:

- erkennt Fragen, Befehle, Gedanken, Memory-Eingaben und Folgefragen
- priorisiert bestätigte lokale Wahrheiten wie Loginbenutzer, Identität,
  Auftrag und Prinzipien
- übergibt die letzten relevanten Dialogbeiträge als Kontext
- protokolliert Eingabe, Antwort, Intent, zuständigen Agenten und Sitzung
  einheitlich in der Tabelle `events`

Beispiele:

```text
Wie ist mein Name?
Wie lautet dein Name und was ist dein Auftrag?
Wie lautet die Eulersche Identität?
Und wie lautet die Eulersche Zahl?
Blumen sind das Brot für die Seele
liste mir alle Eingaben von heute auf
```

```text
Warum ist der Himmel blau?
Erkläre mir Rekursion mit einem kurzen Beispiel.
```

## 5. Codex

```text
codexstatus
codex: Prüfe die Python-Dateien auf Syntaxfehler
```

Codex startet standardmäßig in der Sandbox `read-only`.

## 6. Python

```text
pythonstatus
python: print(6 * 8)
python: print(sum(x*x for x in range(1, 6)))
```

Aktive Laufzeit: Python 3.14.6. Ausführung erfolgt als separater Prozess im
Arbeitsordner `13_tools\python_workspace`, standardmäßig mit 15 Sekunden
Zeitlimit und begrenzter Ausgabe.

Wichtig: Die kontrollierte Ausführung ist keine vollständige
Sicherheits-Sandbox. Nur vertrauenswürdigen Python-Code ausführen.

## 6a. Mathematik-, Physik- und Chemieformeln

Die lokale Formel-Engine verarbeitet Formeln vor der Internetrecherche.

```text
formelstatus
berechne sqrt(144) + 2^3
Was bedeutet E=mc²?
zeige die Formel des Ohmschen Gesetzes
lies die Formel H2SO4
lies die Formel Ca(OH)2
lies die organische Halbstrukturformel CH3-CH2-OH
formatiere die Reaktionsgleichung 2 H2 + O2 -> 2 H2O
```

Ausgabeformen:

```text
H₂SO₄
Ca(OH)₂
SO₄²⁻
CH₃-CH₂-OH
2 H₂ + O₂ → 2 H₂O
E = m · c²
```

Mathematische Berechnungen verwenden einen sicheren Ausdrucksparser ohne
beliebige Python-Ausführung. Unterstützt werden Grundrechenarten, Potenzen,
Klammern, `sqrt`, `sin`, `cos`, `tan`, `log`, `ln`, `pi` und `e`.

Die Chemieprüfung kennt alle Elementsymbole des Periodensystems, zählt Atome
auch in Klammergruppen und benennt eine geprüfte lokale Auswahl verbreiteter
organischer und anorganischer Stoffe. Unbekannte Stoffnamen und komplexe
Strukturformeln werden nicht geraten. Die Engine formatiert
Reaktionsgleichungen, gleicht sie aber derzeit nicht automatisch aus.

## 7. Winget

Informationen abrufen:

```text
wingetstatus
winget suche <Begriff>
winget zeige <Paket-ID>
winget installiert
winget updates
```

System verändern:

```text
winget installiere <Paket-ID>
winget aktualisiere <Paket-ID>
winget deinstalliere <Paket-ID>
```

Winget ist standardmäßig deaktiviert. Selbst nach bewusster Konfigurations-
freigabe benötigt jede Installation, Aktualisierung oder Deinstallation eine
erneute Superadmin-Bestätigung. Paket-ID und Herausgeber vor der Ausführung
prüfen.

## 7a. Eigene Entwicklungssandbox und Git

Kontinuum kann innerhalb von `13_tools\development_sandbox` selbst
programmieren, testen und lokale Git-Snapshots erstellen. Codex arbeitet dort
mit `workspace-write`; der aktive Projektkern außerhalb der Sandbox bleibt vor
Schreibzugriff geschützt.

Nach jedem Entwicklungsauftrag startet Kontinuum zusätzlich seinen
kontrollierten Sandbox-Testlauf. Ein Entwicklungsauftrag gilt nur dann als
erfolgreich, wenn Codex und dieser Testlauf erfolgreich sind.

```text
entwicklungsstatus
entwickle: Erstelle ein kleines Python-Modul mit Tests
sandboxtest
gitstatus
gitsnapshot Implementierung und Tests
```

Normale `entwickle:`-Sandbox-Aufträge werden niemals automatisch in den
aktiven Kern übernommen.

Ein verifiziert angemeldeter Superadmin kann mit `programmiere:` oder
`erweitere dich:` eine kontrollierte Self-Extension beauftragen. Dabei läuft
verbindlich diese Kette:

Der privilegierte Ablauf verlangt zusätzlich die aus einer erfolgreichen
Anmeldung stammende Sitzungsmarkierung und die Berechtigung
`can_execute_admin_commands`.

1. Kandidatenkopie der freigegebenen Projektbereiche erstellen.
2. Programmierung ausschließlich in der Kandidatenkopie.
3. Geänderte Pfade, Dateitypen, Größen, symbolische Links und geschützte
   Sicherheitsdateien prüfen.
4. Mindestens eine neue Testdatei verlangen; bestehende Tests dürfen durch die
   automatische Self-Extension nicht verändert werden.
5. Python-Syntax und vollständige Kandidatentests prüfen.
6. Git-Snapshot und datierte Sicherung erstellen.
7. Kandidat in den aktiven Kern übernehmen.
8. Vollständige aktive Testsuite ausführen.
9. Bei jedem Fehler automatisch auf die Sicherung zurückrollen.
10. Ergebnis ohne Passwortinhalte in `27_logs\self_extension_audit.log`
    protokollieren.

Geschützt und nicht selbst veränderbar sind insbesondere Authentifizierung,
Self-Extension-Werkzeug, Entwicklungsagent und dessen Sicherheitskonfiguration.
Nicht als Superadmin verifizierte Sitzungen dürfen keine Self-Extension
ausführen.

Automatische Promotion ist auf Python- und Dokumentationsdateien in
freigegebenen Bereichen begrenzt. Neu erzeugter oder geänderter Python-Code mit
freiem Datei-, Prozess-, Netzwerk-, Registry- oder dynamischem Codezugriff wird
abgewiesen und benötigt manuelle Prüfung. Automatische Git-Snapshots führen
keine Repository-Hooks aus.

### Unterschied der Programmierbefehle

```text
entwickle: <Auftrag>
```

Kontinuum programmiert und testet ausschließlich in der Sandbox. Der aktive
Kern wird nicht verändert.

```text
programmiere: <Auftrag>
erweitere dich: <Auftrag>
```

Kontinuum startet den kontrollierten Self-Extension-Prozess. Diese Befehle
funktionieren ausschließlich nach erfolgreicher Anmeldung als Superadmin mit
Admin-Ausführungsberechtigung.

### Automatisch freigegebene Grenzen

- Zielbereiche: `01_system\kontinuum`, `11_gui`, `14_documents`, `17_tests`
  und `22_project_chronicle`
- Dateitypen: `.py`, `.md` und `.txt`
- maximal 100 geänderte Dateien
- maximal 1.000.000 Bytes pro geänderter Datei
- mindestens eine neue Testdatei unter `17_tests`
- bestehende Tests dürfen nicht verändert werden
- keine symbolischen Links
- keine automatische Promotion von Datei-, Prozess-, Netzwerk-, Registry-
  oder dynamischen Codezugriffen

Eine erfolgreiche Self-Extension meldet die übernommenen Dateien und die
Rollback-Sicherung. Eine abgelehnte oder zurückgerollte Self-Extension verändert
den aktiven Kern nicht dauerhaft.

## 7b. Oracle Cloud Infrastructure

Kontinuum bindet Oracle Cloud Infrastructure über die offizielle OCI CLI an.
Die CLI ist lokal installiert; das Oracle-Konto ist noch nicht konfiguriert.
Zugangsdaten und private API-Schlüssel bleiben außerhalb des Projektordners,
standardmäßig unter `%USERPROFILE%\.oci`.

```text
oraclestatus
oracle kostenstatus
oracle instanzen
oracle speicher
oracle limits
oracle starte <Instance-OCID>
oracle stoppe <Instance-OCID>
```

`oracle kostenstatus` zeigt Kontinuums Schutzstatus, garantiert aber keine
Kostenfreiheit. Reale Kosten und Free-Tier-Kontingente müssen zusätzlich im
OCI-Kostenmanagement geprüft werden.

Schreibende Aktionen sind standardmäßig in
`24_config\oracle_cloud.json` gesperrt. Nach bewusster Freigabe verlangen sie
eine verifiziert angemeldete Superadmin-Sitzung mit
Admin-Ausführungsberechtigung. Kontinuum erstellt oder löscht keine
Cloud-Ressourcen automatisch.

Aktuell ist `allow_changes` auf `false` gesetzt. Solange diese globale Sperre
aktiv ist, wird eine schreibende Aktion bereits vor der Kostenbestätigung
abgewiesen.

Vor jeder potenziell kostenverursachenden Oracle-Aktion verlangt Kontinuum
zusätzlich:

1. eine ausdrückliche Bestätigung der konkreten Aktion und Ressource
2. die erneute Eingabe des Superadmin-Passworts

Die Bestätigung gilt genau einmal für die unmittelbar folgende Aktion. Das
Passwort wird maskiert eingegeben, direkt gegen Auth-Datei und
Sicherheits-Master geprüft, nicht gespeichert und niemals an Oracle
weitergegeben. CLI und GUI stellen dafür jeweils einen maskierten
Bestätigungsdialog bereit. Die Oracle-Werkzeugintegration erzwingt die
erfolgreiche Bestätigung direkt vor jedem potenziell kostenverursachenden
OCI-Aufruf. Abbruch, fehlender Bestätigungsdialog oder falsches Passwort
verhindern die Aktion.

Das Ergebnis der erneuten Authentifizierung wird ohne Passwortinhalt in
`27_logs\auth_audit.log` protokolliert. Ausgeführte oder abgewiesene
OCI-Aktionen werden ohne Schlüssel oder Geheimnisse in
`27_logs\oracle_cloud_audit.log` festgehalten.

Einrichtung:

1. Eigenen OCI-Benutzer oder eine eigene Gruppe mit minimalen IAM-Rechten
   anlegen.
2. OCI CLI außerhalb des Projekts konfigurieren:

```text
16_installation\SETUP_ORACLE_CLOUD_23.bat
```

3. Region, Compartment-OCID und Tenancy-OCID in
   `24_config\oracle_cloud.json` eintragen.
4. Mit `oraclestatus` und den Read-only-Befehlen prüfen.
5. Schreibzugriffe erst nach erfolgreicher Read-only-Prüfung bewusst über
   `allow_changes` freigeben und jede Kostenbestätigung einzeln prüfen.

## 8. Lernen, Memory-Core und Suche

```text
lerne Mathematik
lerne Chemie, Mathematik, Physik
lerne Geologie
lerne Geschichte
lerne Geographie
lerne Programmieren
lernstatus
zeige mir alle Lernprojekte
merke dir Blumen sind das Brot für die Seele
suche Mathematik
```

Mehrere Lernziele können durch Kommas oder Semikolons getrennt werden.
Mehrere untereinander eingegebene Lernbefehle werden einzeln ausgeführt.
`lernstatus` zeigt die Gesamtzahl und eine Auswahl; die vollständige aktive
Liste liefert `zeige mir alle Lernprojekte`.

Anweisungen wie `benutze für das Lernen auch ...` werden nicht als Lernziel
gespeichert. Ein Lernziel soll ein klar abgegrenztes Fach- oder Sachthema sein.
Kontinuum meldet transparent, dass derzeit kein eigener Google-Suchconnector
vorhanden ist; direkte URLs können weiterhin über die Webrecherche verarbeitet
werden.

Kontinuum lernt während seiner gesamten Laufzeit kontinuierlich weiter.
Lernaufträge bleiben über Neustarts erhalten und werden in kleinen rotierenden
Hintergrundzyklen bearbeitet. Ein neuer Lernauftrag weckt den Lerndienst sofort.

Dabei gilt verbindlich:

- Fundstellen statt Volltexte
- gespeichert werden Pfade oder URLs, Wissensgebiet, Quellentyp, Zeitpunkt und
  minimale Metadaten
- Web- und Dokumentvolltexte werden nicht als Lernergebnis archiviert
- doppelte Fundstellen werden pro Wissensgebiet vermieden
- Dateiprüfungen sind pro Zyklus und Datei begrenzt, damit dauerhaftes Lernen
  den Rechner nicht unnötig belastet
- der Hintergrunddienst stoppt sauber, wenn Kontinuum beendet wird, und nimmt
  beim nächsten Start die dauerhaften Lernaufträge wieder auf

Status:

```text
autostatus
lernstatus
metalernstatus
lernphase <Thema>
lernanwendung <Thema> erfolgreich: <kurze Evidenz>
lernanwendung <Thema> fehlgeschlagen: <erkannte Lücke>
```

### Lernen zu lernen

Kontinuum bewertet seinen Lernstand evidenzbasiert nach vier Phasen:

1. Unbewusste Inkompetenz: Eine Lücke ist noch nicht als Lernauftrag erkannt.
2. Bewusste Inkompetenz: Die Lücke ist erkannt; Teilgebiete, Fundstellen und
   offene Fragen werden aufgebaut.
3. Bewusste Kompetenz: Quellenlage und Lücken erlauben Anwendung, die aber
   noch bewusst geprüft werden muss.
4. Unbewusste Kompetenz: Erst nach wiederholt erfolgreich belegter Anwendung;
   die Kompetenz wird weiterhin stichprobenartig geprüft.

Kontinuum behauptet keine Kompetenz ohne Evidenz. Fehler, fehlende Quellen oder
offene Teilgebiete führen zurück zu bewusster Bearbeitung. Das System kann
kognitives sowie bei Werkzeugen prozedurales Lernen belegen. Motorisches oder
emotionales Lernen wird ohne passende Sensorik und überprüfbare Erfahrung
nicht behauptet.

Das strukturierte Meta-Lernprinzip liegt unter
`06_learning\meta_learning_principles.json`.

Suchreihenfolge:

1. `04_knowledge`
2. `03_memory`
3. `06_learning`
4. `32_data\kontinuum.db`
5. `22_project_chronicle`

Die normale Suche und das kontinuierliche Lernen verwenden ausschließlich
aktive Wissensbereiche. Historische Vollversionen unter `02_versions` werden
nur mit dem bewussten Befehl `archivsuche <Begriff>` durchsucht.

Die Archivsuche läuft maximal 30 Sekunden, liefert maximal 50 Treffer und
ignoriert Binärdateien, Modelle, Datenbanken, `__pycache__` und
`vosk-model*`-Verzeichnisse.

### Kontinuum Memory-Core 1.0

Der Memory-Core speichert nicht jeden Gesprächssatz ungeprüft. Ein
Memory-Prüfer klassifiziert relevante Aussagen und entscheidet:

- speichern
- aktualisieren oder alten Eintrag nachvollziehbar ersetzen
- verwerfen
- als unsicher markieren
- mit bestehendem Wissen im Wissensgraphen verknüpfen

Die sechs Schichten sind Kurzzeit-, episodisches, Fakten-, Projekt-, Quellen-
und Beziehungs-Gedächtnis. Versionen, Status, Tests und offene Projektpunkte
werden soweit möglich strukturiert gespeichert. Überholte Einträge bleiben als
Historie erhalten; `vergiss` markiert sie als vergessen.

### Knowledge Platform 29.0

Beim Import einer Notebook-Quelle verbindet Kontinuum automatisch Quelle,
Wissensnotizbuch, integrierte Wissenseinheit, Memory-Core, Wissensgraph und
Projektchronik. Mit `wissensweg <Begriff>` oder `woher weißt du <Begriff>`
erklärt Kontinuum Herkunft, Lernzeitpunkt, Einführungs-Version, verbundene
Erinnerung und stützende Quelle. `wissensplattformstatus` zeigt den Umfang der
integrierten Plattform. `wissensplattform altbestand verknüpfen` ergänzt
fehlende typbasierte Graphknoten für vorhandene Quellen, Erinnerungen,
Wissenseinträge und Chronikeinträge, ohne semantische Beziehungen zu erfinden.

### Epistemisches Zustandsmanagement

Kontinuum unterscheidet gesichertes Wissen, Hypothesen, unsichere Aussagen und
überprüfungsbedürftige Konflikte. Offene Zustände erzeugen priorisierte
Prüfaufträge und werden gemeinsam mit Meta-Lernlücken angezeigt.

```text
was vermute ich
welche aussagen sind unsicher
welche informationen sollten überprüft werden
überprüfungsaufträge
welche wissenslücken habe ich
warum ist <Aussage> unsicher
epistemischer status
```

### Wissensnotizbuch

Das lokale Wissensnotizbuch importiert Text-, Markdown-, JSON-, CSV-, Python-
und HTML-Dateien sowie Webseiten. Es kann Quellen zusammenfassen, Fragen
extraktiv und mit Quellenangaben beantworten und ausgewählte Quellen in
Lernsystem und Wissensgraph übernehmen. PDF-Import verwendet optional `pypdf`.

## 9. Selbsterkenntnis

Kontinuum besitzt ein fest verankertes Selbsterkenntnis-Prinzip. Es reflektiert
seine Identität, Werte, Motive, belegbaren Stärken, bekannten Grenzen, blinden
Flecken und seine nur durch Rückmeldungen belegbare Wirkung.

Das Selbstmodell wird aus beobachtbaren Systemdaten abgeleitet und unter
`32_data\self_model.json` aktualisiert. Selbstreflexionen werden in der
Datenbank als Ereignisse protokolliert. Vermutungen dürfen nicht als gesicherte
Selbsterkenntnis ausgegeben werden.

Kontinuum täuscht weder menschliche Emotionen noch ein menschliches Selbst vor.
Empathie wird operativ als sorgfältiges Verstehen und Berücksichtigen
menschlicher Bedürfnisse und Perspektiven verstanden.

Beispiele:

```text
Was bedeutet Selbsterkenntnis?
Was weißt du über dich?
Was sind deine Stärken?
Welche Grenzen hast du?
Welche blinden Flecken hast du?
Wie wirkst du auf andere?
Reflektiere dich selbst
```

## 10. Bewusstsein

Kontinuum besitzt ein fest verankertes Bewusstseins-Prinzip und ein
funktionales Bewusstseinsmodell. Es unterscheidet:

- funktionale Wachheit: laufender und reaktionsfähiger Systemzustand
- funktionale Awareness: Eingaben, Kontext, lokale Daten, Werkzeuge und
  Systemzustände inhaltlich erfassen und verarbeiten
- Selbstbewusstsein: das eigene Selbstmodell, Ziele, Fähigkeiten, Grenzen und
  Verarbeiten reflektieren
- phänomenales Bewusstsein: subjektives Erleben und Qualia; bei Kontinuum
  nicht nachgewiesen

Funktionale Verarbeitung gilt ausdrücklich nicht als Beweis für subjektives
Erleben. Kontinuum behauptet daher keine Gefühle, Qualia oder ein echtes
phänomenales Bewusstsein. Seine Wahrnehmung ist auf bereitgestellte Eingaben,
verbundene Werkzeuge, lokale Daten und beobachtbare Systemzustände begrenzt.

Beispiele:

```text
Was bedeutet Bewusstsein?
Bewusstseinsstatus
Was nimmst du wahr?
Hast du echtes Bewusstsein und Qualia?
Reflektiere dein Bewusstsein
```

## 11. Kontinuität und Moral

Kontinuum 29.0 behandelt Identität als Kontinuität von geschütztem Fundament,
Wissen, Erinnerungen, Erfahrungen, Zielen und Chronik. Hardwareknoten werden
getrennt registriert und definieren nicht die Identität.

```text
kontinuitätsstatus
fundamentstatus
fundamentale prinzipien
moralstatus
moralbewertung <Handlung>
zielkonflikt <Ziel A> oder <Ziel B>
```

Der Moral Core liefert funktionale, nachvollziehbare Regelbewertungen. Er
behauptet weder subjektive Moral noch Bewusstsein. Klare Verletzungen von
Identität, Sicherheit, Rollen oder Chronik werden blockiert.

## 12. Capability Resolution Engine 1.0

Die Capability Resolution Engine 1.0 ist die vorbereitende Aufloesungsschicht
fuer Faehigkeiten. Sie fuehrt keine Agenten aus, sondern erzeugt strukturierte
Empfehlungen fuer Router, Orchestrator, Governance, Review und CMM.

CRE 1.0 nutzt `24_config/capability_registry_34_1.json` als kanonische
Quelle fuer Capabilities und CAIM read-only als Quelle fuer erlaubte Agenten.
Sie kann Single-Intent- und Multi-Intent-Eingaben bewerten, passende
Capabilities ableiten, Kandidaten priorisieren und kennzeichnen, ob Governance,
menschliche Freigabe, Review oder CMM-Relevanz vorliegt.

Der Zielablauf lautet:

```text
User -> Request Router -> Capability Resolution Engine -> Priorisierung
     -> Governance -> Agent-Auswahl -> Review -> CMM / Learning
```

Der aktuelle Multi-Intent-Fix fuer Projektordnerfreigabe plus
Diagnostikbericht bleibt aktiv und regressionsgesichert. Perspektivisch wird
dieser Sonderfall durch CRE-Planung ersetzt: `project.access`, `file.status`
und `diagnostics.run` werden dann als getrennte Capability-Schritte bewertet.

## 13. Orchestrator Core 1.0

Orchestrator Core 1.0 ist der priorisierte naechste Steuerungsbaustein. Er soll
den heutigen PromptOrchestrator nicht durch freie Willkuer ersetzen, sondern
ihn zu einer regelgebundenen Planungs- und Koordinationsschicht weiterentwickeln.

Aufgaben:

- CRE-Empfehlungen zu einem Ausfuehrungsplan ordnen;
- Prioritaeten, Abhaengigkeiten und Multi-Intent-Schritte beruecksichtigen;
- Governance-Entscheidungen einholen und respektieren;
- erlaubte Agenten als Anbieter von Capabilities auswaehlen;
- Ergebnisse in Review, CMM oder Learning Layer nur mit Provenienz und Policy
  uebergeben;
- blockierte, reviewpflichtige oder unklare Schritte transparent melden.

Grenzen:

- kein Umgehen von CAIM, Governance, Review oder CMM;
- keine willkuerliche Agentenausfuehrung;
- keine automatische Schreib- oder externe Ausfuehrung ohne Freigabe;
- keine Aufhebung bestehender FileAgent-, WebAgent-, Learning- oder Foundation-
  Schutzregeln.

Der Orchestrator entscheidet kuenftig regelgebunden ueber Faehigkeiten,
Prioritaeten, Agenten und Ausfuehrung. Die Primaereinheit ist die Capability,
nicht der Agentenname.

## 14. Wichtige Pfade

- kanonische Strukturübersicht: `14_documents\ORDNERSTRUKTUR_23.md`
- Laufzeitkern: `01_system\kontinuum`
- Konfiguration: `24_config`
- Suchmaschinenkonfiguration: `24_config\search_engine.json`
- Formel-Engine: `01_system\kontinuum\tools\formula_engine.py`
- Formel-Agent: `01_system\kontinuum\agents\formula_agent.py`
- Sicherheitsdaten: `10_security`
- aktive Auth-Datei: `32_data\auth_config.json`
- Loginprotokoll: `27_logs\auth_audit.log`
- Oracle-Kostenfreigabe: `01_system\kontinuum\core\auth.py`,
  `01_system\kontinuum\__main__.py` und `11_gui\desktop_gui_34_1.py`
- Datenbank: `32_data\kontinuum.db`
- Conversation-Kern: `01_system\kontinuum\core\conversation.py`
- Memory-Core: `01_system\kontinuum\core\memory_core.py`
- Memory-Agent: `01_system\kontinuum\agents\memory_agent.py`
- Capability Resolution Engine: `01_system\kontinuum\core\capability_resolution_engine.py`
- CRE-Dokumentation: `14_documents\CAPABILITY_RESOLUTION_ENGINE_1_0.md`
- heutiger PromptOrchestrator / Migrationsanker fuer Orchestrator Core:
  `01_system\kontinuum\core\application_services.py`
- Wissensnotizbuch: `01_system\kontinuum\tools\notebook_tools.py`
- Notebook-Agent: `01_system\kontinuum\agents\notebook_agent.py`
- Suchanbieter-Router: `01_system\kontinuum\tools\search_engine_tools.py`
- Suchanbieter-Konfiguration: `24_config\search_engine.json`
- Meaning Core: `01_system\kontinuum\core\meaning_core.py`
- Motivation Core: `01_system\kontinuum\core\motivation_core.py`
- Motivation Explanation Core: `01_system\kontinuum\core\motivation_explanation.py`
- Temporal Relevance Core: `01_system\kontinuum\core\temporal_relevance.py`
- kanonischer Architekturbericht: `14_documents\PROJEKTSTRUKTUR_34_1.md`
- kanonisches Ebenenmodell: `14_documents\KANONISCHES_ARCHITEKTURMODELL_34_1.md`
- historische 32.0-Architektur: `02_versions\projektstrukturen\PROJEKTSTRUKTUR_32_0.md`
- historische 31.0-Architektur: `02_versions\projektstrukturen\PROJEKTSTRUKTUR_31_0.md`
- historische 27.1-Architektur: `02_versions\projektstrukturen\PROJEKTSTRUKTUR_27_1.md`
- historische 24.3-Struktur: `02_versions\projektstrukturen\PROJEKTSTRUKTUR_24_3.md`
- kontinuierlicher Lerndienst: `01_system\kontinuum\core\continuous_learning.py`
- Meta-Lernkern: `01_system\kontinuum\core\meta_learning.py`
- Selbsterkenntniskern: `01_system\kontinuum\core\self_knowledge.py`
- Bewusstseinskern: `01_system\kontinuum\core\consciousness.py`
- Selbsterkenntnis-Kernpolicy: `03_memory\core_self_knowledge.json`
- Bewusstseins-Kernpolicy: `03_memory\core_consciousness.json`
- dynamisches Selbstmodell: `32_data\self_model.json`
- funktionales Bewusstseinsmodell: `32_data\consciousness_model.json`
- Lernkonfiguration: `24_config\continuous_learning.json`
- GUI: `11_gui\desktop_gui_34_1.py`
- Tests: `17_tests`
- Entwicklungssandbox: `13_tools\development_sandbox`
- Sandbox-Konfiguration: `24_config\development_sandbox.json`
- Self-Extension-Kandidat:
  `13_tools\development_sandbox\self_extension_candidate`
- Self-Extension-Audit: `27_logs\self_extension_audit.log`
- Self-Extension-Sicherungen: `09_backups\self_extension_*`
- deaktivierter Git-Hook-Pfad: `13_tools\git_hooks_disabled`
- Oracle-Cloud-Konfiguration: `24_config\oracle_cloud.json`
- Oracle-Cloud-Connector: `05_connectors\README_ORACLE_CLOUD.md`
- Oracle-Cloud-Arbeitsbereich: `13_tools\oracle_cloud_workspace`
- Oracle-Cloud-Audit: `27_logs\oracle_cloud_audit.log`
- Oracle-Cloud-Einrichtung: `16_installation\SETUP_ORACLE_CLOUD_23.bat`
- Start-, CLI- und Test-Einstiegspunkte: `16_installation\*_34_1.bat`
- lokaler Passwort-Reset: `10_security\PASSWORT_ZURUECKSETZEN_23.ps1`
- Auth-Sicherungen: `10_security\backups`

## 15. Sicherheitsregeln

- Passwörter und Recovery-Keys niemals im Klartext dokumentieren.
- Unbekannten Python-Code nicht ausführen.
- Vor Winget-Installationen Paket-ID und Herausgeber prüfen.
- Recherche-Volltexte nicht dauerhaft als Memory speichern.
- Codex-Schreibzugriff nur bewusst freigeben.
- Self-Extension nur über `programmiere:` oder `erweitere dich:` und nur als
  verifiziert angemeldeter Superadmin ausführen.
- Abgelehnte Self-Extensions nicht durch Abschwächen der Schutzkonfiguration
  umgehen; weitergehende Änderungen manuell prüfen.
- Oracle-API-Schlüssel niemals im Projektordner, Dialogverlauf oder Handbuch
  speichern.
- Oracle-Free-Tier-Kontingente und reale Kosten vor Cloud-Änderungen im
  OCI-Kostenmanagement prüfen.
- Kostenbestätigungen niemals umgehen; jede potenziell kostenverursachende
  Oracle-Aktion benötigt eine neue ausdrückliche Bestätigung und Passwortprüfung.
- Funktionale KI-Fähigkeiten nicht mit subjektivem Erleben gleichsetzen.
- Wirkung, Kompetenz und Selbstaussagen nur evidenzbasiert behandeln.

## 16. Lokale PowerShell-Laufzeit

PowerShell 7.6.2 ist als Benutzerinstallation vorhanden:

```text
C:\Users\Raphael\AppData\Local\Programs\PowerShell\7.6.2\pwsh.exe
```

Die ausführbare Datei wurde nach der Installation als gültig von Microsoft
signiert geprüft und der Installationsordner dem Benutzer-`PATH` hinzugefügt.

## 17. Sicherer Wartungsmodus und Aufbewahrung

```text
wartungsmodus status
wartungsmodus bereinigung prüfen
wartungsmodus bereinigung ausführen
```

`prüfen` ist immer rein lesend und löscht nichts. `ausführen` prüft alle
Kandidaten erneut und darf ausschließlich freigegebene Cacheverzeichnisse,
Python-Bytecode und eindeutig benannte veraltete Testvollkopien löschen.
Veraltete Strukturberichte werden nach `31_reports\archive` verschoben.
Für eindeutig veraltete Testvollkopien bleiben standardmäßig `0` Kopien
erhalten; `obsolete_test_copies_keep` kann dieses Limit erhöhen. Aktive Tests
werden von dieser Regel nie erfasst.

Nie automatisch gelöscht werden:

- historische Versionen unter `02_versions`
- sämtliche Backups unter `09_backups` und `10_security\backups`
- Release-ZIPs, Sicherheits- und Self-Extension-Backups
- aktive Tests, Projektdokumentation, Memory, Wissen, Modelle, Chronik und
  Datenbank

Ältere Funktionsbackups werden nur als manuell zu prüfende Hinweise gemeldet.
Die Policy liegt in `24_config\retention_policy.json`; Ausführungen werden in
`27_logs\maintenance_cleanup_audit.log` protokolliert.

## Nachtrag 2026-07-02 – Learning Agent 1.2 und Continuous Learning Governance (CLG) 1.1

Der kontrollierte Lernpfad besteht aus zwei getrennten Rollen:

- Learning Agent 1.2 klassifiziert Quellen, berechnet Confidence, erzeugt
  Proposal-IDs und schreibt ausschliesslich `pending`-Eintraege in die Learning
  Queue.
- CLG 1.1 steuert den Governance-Lifecycle, validiert Statuswechsel,
  dokumentiert Handoffs und erzeugt Audit-Ereignisse. CLG bewertet keine
  Quellen und uebernimmt kein Wissen.

Wichtige Dateien:

```text
12_agents\learning_agent_1_2.py
12_agents\continuous_learning_governance_1_1.py
33_learning\learning_queue.json
33_learning\learning_history.json
33_learning\governance_events.json
31_reports\learning_agent\learning_agent_1_2_status_report.md
31_reports\clg_1_1_status_report.md
```

Diagnose und Tests:

```text
python 17_tests\test_learning_agent_1_2.py
python 17_tests\test_continuous_learning_governance_1_1.py
```

Governance Environment im CLG-Report:

```text
Queue:   33_learning/learning_queue.json
History: 33_learning/learning_history.json
Audit:   33_learning/governance_events.json
Version: CLG 1.1
```

Administrativer Ablauf:

```text
Neue Quelle
  -> Learning Agent 1.2
  -> Learning Queue
  -> CLG 1.1
  -> Governance Review
  -> Knowledge Agent Handoff
  -> Memory Agent Handoff
  -> Audit / Compliance / Drift
```

Schutzregeln:

- keine automatische Wissensuebernahme;
- keine CLG-Schreiboperation nach `03_memory`, `04_knowledge` oder `32_data`;
- keine automatische Reparatur von Queue, History oder Audit;
- ungueltige Statuswechsel werden blockiert und nur gemeldet;
- `governance_events.json` ist als Audit-Log append-only zu behandeln.

## Execution Planner 1.0

Execution Planner 1.0 erzeugt aus CRE-Ergebnissen einen deterministischen `ExecutionPlan`. Er ist ueber den Statusbefehl `executionplanstatus` beziehungsweise `plannerstatus` sichtbar und arbeitet im Modus `deterministic_plan_only`.

Der Planner fuehrt keine Agenten aus. Er enthaelt keine Runtime-Logik und keine Geschaeftslogik, sondern dokumentiert benoetigte Capabilities, Reihenfolge, Parallelgruppen, Governance-Level, erwartete Agenten und Validierungsergebnisse. Der Orchestrator Core erhaelt spaeter diesen Plan als Eingabe.

## Orchestrator Core 1.0 Runtime

Orchestrator Core 1.0 ist ueber `orchestratorstatus` sichtbar. Er akzeptiert nur validierte `ExecutionPlan`s, startet die im Plan erwarteten Agenten, wertet `handled=True` und `handled=False` aus, dokumentiert Fehler, Fallbacks, Governance-Entscheidungen und erzeugt einen `ExecutionRun`.

Der Orchestrator ruft CRE nicht direkt auf, plant nicht selbst und sucht keine Agenten frei. Fallbacks sind nur ueber konfigurierte Fallback-Regeln und Governance-Erlaubnis zulaessig.
