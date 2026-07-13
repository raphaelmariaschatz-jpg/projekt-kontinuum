# Projekt Kontinuum 34.1

Lokales, projektbewusstes Wissens-, Gedächtnis-, Forschungs- und
Assistenzsystem für Raphael Schatz.

Stand: 2026-06-20

## Aktueller Status

Kontinuum 34.1 ist betriebsbereit. Foundation Reasoning 4.1 schließt
Identitäts-Bypass, Post-hoc-Erklärungen, unsichtbare Regelkonflikte und die
fehlende aktive Zielintegration. Der Autonomous Diagnostics Core prueft
acht interne Systembereiche, klassifiziert Befunde, erzeugt kontrollierte
Loesungsvorschlaege und informiert den Benutzer. Der aktive Kern ist ein modularer
Python-Monolith mit explizitem Agentenrouting, lokaler SQLite-Persistenz,
Tkinter-GUI, kontrollierten Werkzeugen und lokaler Wissenspriorität.

## Kanonische Architekturautoritaet

Fuer Projekt Kontinuum gilt ab CMIBF 1.0:

- Das Canonical Master Implementation Blueprint Framework (CMIBF) ist die einzige normative Architekturquelle und Architekturverfassung.
- Das Canonical Architecture First Principle (AFP) legt die verbindliche Reihenfolge von Idee, Architekturanalyse, CMIBF-Definition, Freigabe, CAC, Artefakten, Implementierung, Validierung, Release, Betrieb, Monitoring und kontrollierter Evolution fest.
- Das Canonical AI Working Protocol (CAWP) legt das verbindliche Arbeitsverhalten aller KI-Systeme unterhalb des AFP fest.
- Der Canonical Architecture Compiler (CAC) ist ein pruefender Compiler fuer das CMIBF-Quellmodell, kein eigenstaendiger Architekt und kein freier Artefaktgenerator.
- Code, Tests, Konfigurationen, Registries, Reports, Ontologien und Dependency Graphs besitzen keine normative Architekturautoritaet.
- Jede Implementierung muss auf eine definierte, gepruefte und freigegebene CMIBF-Grundlage zurueckfuehrbar sein.

Zentrale Funktionen:

- Knowledge Platform mit durchgängigem Wissensweg von Quelle über Notebook,
  Memory-Core und Wissensgraph bis zur Projektchronik
- Vertrauensmodell mit Quellenbestätigung, Konflikten und letzter Bestätigung
- Wissenskonflikt-Erkennung für explizit vergleichbare Aussagen
- Selbstmodell 1.0 für Lernentwicklung, Themenschwerpunkte und Wachstum
- epistemisches Zustandsmanagement für Wissen, Hypothesen und Unsicherheit
- priorisierte Überprüfungsaufträge und explizite Wissenslücken
- kontrollierter epistemischer Prüfzyklus mit Recherche, Evidenzbewertung,
  Zustandsneuberechnung und Chronik
- Seitenprüfung und Quellenklassifikation mit qualitätsgewichteter Evidenz
- kontrollierte epistemische Automatik mit priorisierten Prüfaufträgen,
  Quellenbewertung und automatischer Wissenshochstufung
- Continuity Core mit hardwareunabhängigem Identitätsfingerabdruck und
  verketteten Zustandsnachweisen für Wissen, Erinnerungen, Erfahrungen, Ziele
  und Chronik
- Moral Core für nachvollziehbare Handlungsbewertung und Zielkonflikte
- verbindliche Foundation Decision Layer vor jeder einzelnen Eingabe sowie
  vor gebundenen autonomen Lern- und Prüfhandlungen
- ausführbarer Zyklus Erkennen, Schaffen, Vollenden mit append-only
  Entscheidungsnachweis
- Meaning Core mit Bedeutungsgraph von Prinzip über Ziel, Handlung,
  Erinnerung und Chronik bis Identität
- Motivation Core mit Bedeutungsgewichtung für zentrale Beziehungen, Ziele,
  prägende Erinnerungen, strategische Wissenslücken und Selbstfragen
- Motivation Explanation Core mit erklärbarer Herkunft jedes Motivation-Scores
  über gespeicherte Gründe, Meaning-Kanten, Evidenzbelege und Pfade
- Temporal Relevance Core gegen Bedeutungsinflation mit zeitlicher
  Relevanzbewertung für Meaning-Kanten, Chronikereignisse und Wissenslücken
- Runtime Hardening mit lokalem Identity Routing, zentralem Session Context,
  Knowledge Contamination Guard, Foundation Knowledge Guard, semantischer
  Suchvalidierung und Foundation Cycle Recovery
- Foundation Knowledge Protection 2.0 mit eigener append-only Schutzklasse,
  Herkunfts- und Versionsnachweis, SHA-256-Integritätsprüfung, sechs
  kanonischen Schutzbereichen, blockierten
  Lern-/Recherche-/Diagnosepfaden und auditierten Änderungsentscheidungen
- Foundation Knowledge Protection 3.0 mit eigenem Foundation Memory Layer für
  Identität, Prinzipien, Moral, Schöpferwissen und langfristige Ziele sowie
  ausdrücklicher Gegenklasse `learned.knowledge` für gelerntes Wissen
- Foundation Query Layer für priorisierte lokale Antworten zu Identität,
  Schöpfer, Prinzipien, moralischer Zulässigkeit und verwendeten
  Fundamentregeln – ohne normale Wissensabfrage oder Internetsuche
- Foundation Reasoning Layer 4.1 mit 31 stabilen Regel-IDs einschließlich der
  zwölf `foundation.guiding.*`-IDs,
  unveränderlichen Entscheidungs- und Antwortnachweisen, Einflussstärke,
  Alternativen, Unsicherheit und Foundation-Pfaden für Motivationserklärungen
- zwölf vorläufige, bis zum Widerruf geltende Leitprinzipien mit stabilen IDs
  `foundation.guiding.01` bis `foundation.guiding.12`, eigenem geschützten
  Registereintrag und append-only Ablöseverfahren
- Autonomous Diagnostics Core fuer Routing, Wissensgraph, Datenbank, Chronik,
  Memory, Foundation Layer, Agentenkommunikation und Versionskonsistenz
- taegliche Auditberichte unter `14_documents/interne_fehler_und_loesungen/`
- ereignisbasiert komprimierte Knowledge-Platform-Chronikeinträge ohne
  kopierte Dialog- oder Quellvolltexte
- vollständige 32.4-Inhalts-, Struktur- und Pfadmigration mit erweitertem
  Versionskonsistenztest und read-only Statusprüfer
- Suchanbieter-Router mit lokalem Wissen, Notebook-Wissen, Universitätsquellen,
  arXiv, Semantic Scholar, API-vorbereitetem Brave Search sowie
  DuckDuckGo-Fallbacks
- fünf persistente Langzeitziele und kontrollierte autonome Selbstfragen
- geschütztes Register der sieben fundamentalen Prinzipien
- Persistent Self Model Core mit beobachtbarem Zustandsverlauf, erklärten
  Änderungen und geschützten Selbstgrenzen
- strikte Trennung von Welt-, Selbst-, Identitäts-, Sicherheits- und
  Moralwissen
- 5/5 geschützte Wissensgrenzen, blockierte Selbstüberschreibung und
  Rollenverwechslungsschutz
- manipulationsprüfbare Projektchronik mit SHA-256-Hash-Kette

Neue Fundamentbefehle:

```text
bedeutungsstatus
bedeutungspfad identität
motivationsstatus
motivationsprioritäten
motivationserklärungsstatus
motivationserklärung identität
wichtige einflüsse identität
fundamentschichtstatus
fundamentintegritätsstatus
fundamentaudit
foundationmemorystatus
wissensklasse <Aussage>
foundationquerystatus
foundationreasoningstatus
langfristige ziele
zielstatus
selbstfragen
stelle dir eine frage
```

Kanonischer Architekturbericht:
`14_documents/PROJEKTSTRUKTUR_34_1.md`
- erklärbare Herkunft mit Lernzeitpunkt, Einführungs-Version, verbundenen
  Erinnerungen und stützenden Quellen
- Kontinuum Memory-Core 1.0 mit sechs Gedächtnisschichten und Memory-Prüfer
- Wissensnotizbuch für lokale Dokumente und Webseiten mit Quellenzitaten
- asynchrone Webrecherche mit 12-Sekunden-Gesamtbudget, Teilantworten und
  Suchanbieter-Fallback
- lokale Wissens-, Lern-, Projektchronik-, Forschungs- und Archivsuche
- Formel-Engine für Mathematik, Physik und Chemie
- lokales Sprachmodell `qwen2.5:3b` über Ollama
- kontrollierte Python-, Codex-, Winget- und Oracle-Cloud-Werkzeuge
- Argon2id-Anmeldung und erneute Superadmin-Bestätigung für privilegierte
  Systemänderungen
- sicherer Wartungsmodus mit Aufbewahrungspolicy, Nur-Prüfung und getrenntem
  Ausführungsbefehl

Winget ist standardmäßig deaktiviert. Archivsuche ist auf 30 Sekunden und
maximal 50 Treffer begrenzt.

## Start

```text
START_KONTINUUM.bat <Befehl>        (kanonischer CLI-Start im Projektstamm)
16_installation\START_GUI.bat
16_installation\START_GUI_34_1.bat   (Kompatibilitätsweiterleitung)
16_installation\START_KONTINUUM_34_1.bat <Befehl>   (Kompatibilitätsstarter)
16_installation\RELEASE_GATE_34_1.bat
16_installation\TEST_KONTINUUM_34_1.bat
```

Der kanonische CLI-Start liegt im Projektstamm. `START_KONTINUUM.bat` setzt
`PYTHONPATH` automatisch auf `C:\Projekt Kontinuum\01_system` und startet
Kontinuum ausschließlich über `python -m kontinuum`. Starts über `main.py` oder
`python -m 01_system.kontinuum` sind veraltet. Die aktiven 34.1-Einstiegspunkte
starten Foundation Reasoning 4.1, Autonomous Diagnostics und den kontrollierten
Internet-Learning-Statusdienst.

## Neue Kernbefehle

```text
merke dir ...
was weißt du über ...
zeige projekterinnerungen
zeige offene punkte
aktualisiere erinnerung <ID>: ...
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

selbstmodellstatus
was hat sich geändert
warum hat sich das geändert
zeige zustandsverlauf
zeige offene innere konflikte
wissensselbstmodellstatus
chronikschutzstatus
kontinuitätsstatus
bedeutungsstatus
bedeutungspfad <Begriff>
motivationsstatus
motivationsprioritäten
motivationserklärungsstatus
motivationserklärung <Begriff>
warum score <Begriff>
erkläre priorität <Begriff>
wichtige einflüsse <Begriff>
relevanzstatus
bedeutungsinflation
chronikprägung
wissenslückenpriorität
sessionstatus
benutzerstatus
wer ist angemeldet
rollenstatus
fundamentzyklenstatus
fundamentintegritätsstatus
fundamentaudit
foundationmemorystatus
wissensklasse <Aussage>
foundationquerystatus
foundationreasoningstatus
fundamentzyklus reparieren
diagnostik
diagnostikstatus
projektquellenstatus
fundamentale prinzipien
moralstatus
moralbewertung <Handlung>
zielkonflikt <Ziel A> oder <Ziel B>
```

## Dokumentation

- Benutzerhandbuch: `14_documents\HANDBUCH_23.md`
- aktueller Projektstatus: `14_documents\projektstatus\PROJEKTSTATUS_AKTUELL_34_1.md`
- kanonische Ordnerstruktur: `14_documents\ORDNERSTRUKTUR_23.md`
- kanonischer Architekturbericht: `14_documents\PROJEKTSTRUKTUR_34_1.md`
- kanonischer Architekturbericht: `14_documents\PROJEKTSTRUKTUR_34_1.md`
- kanonisches Ebenenmodell: `14_documents\KANONISCHES_ARCHITEKTURMODELL_34_1.md`
- historische Projektstrukturen ab 24.3: `02_versions\projektstrukturen\`
- Projektchronik: `22_project_chronicle\PROJEKTCHRONIK_23.md`
- Analysebericht: `31_reports\ARCHITEKTURBERICHT_PROJEKT_KONTINUUM_23.md`

## Internet Knowledge Governance 1.0

IKG 1.0 ist als Policy unter
`24_config\internet_knowledge_governance_1_0.json` vorbereitet. Sie erlaubt nur
klassifizierte öffentliche Quellen, erzwingt Provenienz, Queue und Review,
verwirft blockierte Quellen automatisch und untersagt jede direkte oder
automatische Wissensübernahme. Internet-Lernen ist standardmäßig aktiviert
(`24_config\internet_learning_policy_34_1.json`: `enabled=true`), startet beim
Systemstart automatisch und bleibt damit ein kontrollierter Review-Zulieferer,
kein autonomer Kanon-Schreiber. Der Benutzer kann Internet-Learning über die GUI
oder durch Setzen von `enabled=false` in der Konfiguration deaktivieren.

## Sicherheitsgrundsätze

- Lokales Wissen hat Vorrang vor Internetrecherche.
- Volltexte aus Webrecherche werden nicht ungeprüft als Memory gespeichert.
- Memory-Core-Erinnerungen bleiben prüfbar, historisiert und vergessbar.
- Winget- und Cloud-Systemänderungen benötigen bewusste Freigaben.
- Passwörter, Recovery-Keys und private Schlüssel werden niemals dokumentiert.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
