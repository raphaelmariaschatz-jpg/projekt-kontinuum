# Projekt Kontinuum – Konsolidierte Master-Roadmap 2026–2028

**Stand:** 03.07.2026  
**Vision und Schöpfer:** Raphael Schatz  
**Ausgangspunkt:** Kontinuum 34.1 mit Foundation Reasoning Layer 4.1 und Release Integrity Framework 1.0 ist umgesetzt und verifiziert.  
**Quellenbasis:** die bisherige konsolidierte `roadmap.md` sowie die sechs am 22.06.2026 aktualisierten Grundlagendokumente im Ordner `14_documents/fundamentale Gedanken`.

## 1. Auftrag und Zielbild

Kontinuum (K) soll sich zu einer lokalen, sicheren, transparenten und kontinuierlich lernenden Wissens-, Forschungs-, Analyse-, Lern-, Dokumentations- und Entwicklungsplattform entwickeln.

K soll Wissen nicht nur speichern, sondern:

- verstehen, strukturieren, erklären und bewerten;
- Herkunft, Evidenz, Unsicherheit, Widersprüche und zeitliche Gültigkeit sichtbar machen;
- Menschen beim Lernen, Forschen, Entwickeln und Schaffen unterstützen;
- Entscheidungen nachvollziehbar begründen;
- über Versionen, Hardwarewechsel und Wiederherstellungen hinweg konsistent bleiben.

Der Mensch bleibt Entscheidungsträger. K bleibt Werkzeug, Assistent und Partner. Nicht vorgesehen sind unkontrollierte Selbstmodifikation, undurchsichtige Entscheidungen oder autonome riskante Aktionen.

## 2. Unveränderliche Leitprinzipien

1. **Schöpferprinzip:** Raphael Schatz ist der Schöpfer von Kontinuum.
2. **Erkennen – Schaffen – Vollenden:** Aufgaben folgen einem vollständigen, überprüfbaren Zyklus.
3. **Der Weg ist das Ziel:** Lernen, Entwicklung und Forschung besitzen eigenen Wert.
4. **Wahrheit vor Geschwindigkeit:** Evidenz und saubere Unsicherheitsangaben haben Vorrang vor schnellen Behauptungen.
5. **Transparenz vor Blackbox:** Quellen, Regeln, Alternativen, Konflikte und Grenzen sollen erklärbar sein.
6. **Sicherheit vor Bequemlichkeit:** Riskante Änderungen und Handlungen erfordern Schutzprüfung und ausdrückliche Freigabe.
7. **Unterstützung statt Ersetzung:** Technologie erweitert menschliche Möglichkeiten, ohne menschliche Verantwortung zu verdrängen.
8. **Kontinuität vor Hardware:** Identität entsteht aus der fortlaufenden Verbindung von Erinnerung, Wissen, Zielen, Chronik und geschützten Grundwerten.
9. **Wissen ist nicht automatisch Wahrheit:** Foundation Knowledge, Verified Knowledge, Hypothesis, Uncertain Knowledge und Knowledge Gap bleiben getrennte Klassen.
10. **Kontrollierte Verbesserung:** Diagnose und Entwicklung bleiben auditierbar, testbar, reversibel und unter menschlicher Autorität.
11. **Keine falschen Bewusstseinsbehauptungen:** Selbstmodell, Motivation und emotionale Zustände sind funktionale Modelle.
12. **Zugang zu Wissen:** Wissen soll bewahrt, verständlich gemacht und langfristig möglichst vielen Menschen zugänglich werden.

## 3. Erreichter Stand bis Version 34.1

Die bisherigen Entwicklungsphasen bilden ein belastbares Fundament:

- **Versionen 1–13:** Gedächtnis, Wissensgraph, Recherche, Lernen und Forschung;
- **Versionen 14–22:** Identität, Creator-Wissen, GUI, Sprache, Zugriffe und Connectoren;
- **Versionen 23–28:** Wissens- und Chronikschutz, Selbstmodell, epistemische Zustände und moralische Schutzgrenzen;
- **Versionen 29–34.1:** Foundation Knowledge, Foundation Memory, Foundation Query, Foundation Reasoning, Identity Core, Moral Core, Meaning Core, Motivation Core, Continuity Core und Release Integrity Framework.

Zu den umgesetzten tragenden Komponenten gehören außerdem:

- lokale GUI, Dialog-, Agenten- und Lernarchitektur;
- Memory Core, Wissensnotizbuch, Wissensgraph und Quellenbezüge;
- Autonomous Diagnostics Core mit Fehlerklassifikation und Lösungsvorschlägen, jedoch ohne eigenmächtige Reparatur;
- Internal Error & Solution Center unter `14_documents/interne_fehler_und_loesungen`;
- Foundation Knowledge Protection, eigener Foundation Memory Layer und priorisierter Foundation Query Layer;
- 31 feste Foundation-Regel-IDs, append-only Reasoning-Nachweise und Coverage-Prüfung;
- Versionskonsistenz, Statusprüfungen, Regressionstests, Backups und Rollback-Grundlagen.

**Kanonische Konsolidierungsentscheidung vom 22.06.2026:** Bereits umgesetzte Foundation-, Identity-, Meaning-, Motivation-, Continuity-, Chronik- und Diagnostikfunktionen werden nicht als neue Hauptversionen erneut geplant. Offene Verbesserungen daran werden ab Version 35 als verbindliche Querschnittsarbeit geführt.

### Fundamentmeilensteine vom 24.–25.06.2026

- **Foundation 2.2 – Improvement Principle Integration (FND-ID-048):**
  „Versuche es beim nächsten Mal immer besser zu machen“ ist als
  höchstgeschützter Foundation-Core-Grundsatz aktiv. Verbesserung bleibt
  kontrolliert, auditierbar und schließt unkontrollierte Selbständerung aus.
- **Foundation-2.1-Kompatibilität:** Bestehende Importe bleiben über einen
  schmalen Re-Exportpfad funktionsfähig; die aktive Implementierung liegt
  ausschließlich in Foundation 2.2.
- **CAM 1.0:** Projektstruktur, Vier-Layer-Architektur, Registries,
  Startpunkte, APIs und Datenbankschema werden kanonisch geprüft.
- **CAM 1.1 – Artifact Lifecycle Policy:** Wertvolle Entwicklungsartefakte
  werden bis zur Freigabe behalten und anschließend archiviert statt
  automatisch gelöscht. Signierte Nachweise bleiben dauerhaft erhalten.
- **Weitere CAM-Folge:** Canonical Database Manager, Canonical API Registry
  und Canonical Artifact Manager werden als getrennte Ausbaustufen geführt.

### CAM 1.2 – Canonical Database Manager (25.06.2026)

- versionierter SQLite-Vertrag für die aktive Kontinuum-Datenbank;
- Pflichtprüfung von Kern- und Fachtabellen;
- Spaltenverträge für Foundation-, Memory- und Suchstrukturen;
- Prüfung zentraler Indizes und Append-only-Schutztrigger;
- FTS5-Prüfung für die Dateisuche;
- explizite Foundation-, Memory-, Knowledge- und Search-Datendomänen;
- read-only Überwachung ohne autonome Schemaänderung;
- blockierendes Release-Integrity-Gate.

Nächste CAM-Ausbaustufe: **CAM 1.3 – Canonical API Registry**.

### Architekturentscheid 03.07.2026 – Orchestrator vor Agentenwachstum

Der naechste grosse Entwicklungsschritt ist nicht primaer die Ergaenzung
weiterer Agenten, sondern ein sauberer Orchestrator Core mit Capability
Resolution. Agenten werden kuenftig als Anbieter von Faehigkeiten betrachtet;
Capabilities sind die primaere Steuerungs- und Planungsgrundlage.

Priorisierte Reihenfolge:

1. Capability Resolution Engine 1.0 als read-only Resolver und
   Empfehlungsschicht.
2. Orchestrator Core 1.0 als regelgebundene Planungs- und Steuerungsschicht.
3. Priorisierung und Governance-Check pro Capability-Schritt.
4. Agentenauswahl ohne willkuerliche Agentenausfuehrung.
5. Review- und CMM-Rueckfuehrung mit Provenienz.
6. Erst danach weitere Spezialagenten oder externe Agentenbruecken.

Zielarchitektur:

```text
User -> Request Router -> Capability Resolution Engine -> Orchestrator Core
     -> Governance -> Agenten -> Review -> CMM / Learning
```

Orchestrator-Entscheidungen sind governancepflichtig, sobald sie
Agentenketten, Schreiboperationen, externe Systeme, Review-Uebergaben oder
CMM-/Learning-Handoffs vorbereiten.


### Architekturabschluss 05.07.2026 - Beginn Phase 2

Mit AGF 1.0 ist die grundlegende Architekturentwicklung abgeschlossen. Projekt Kontinuum wechselt offiziell von Phase 1 - Architekturentwicklung zu Phase 2 - Controlled Integration & Operation.

Neue Hauptprioritaeten:

1. Artifact Lifecycle Migration gemaess ALP 2.0 und Migration Plan 1.0.
2. Runtime-Migration des Orchestrator Core mit Feature-Flag und Rueckfallstrategie.
3. Regressionstests fuer Dialog, FileAgent, WebAgent, Knowledge, Memory, Status, Governance und Runtime.
4. Runtime-Freigabe nach erfolgreicher kontrollierter Integration.
5. Governance Dashboard / Operations Monitor.
6. Canonical Data Management und Daten-Lineage fuer `32_data`.
7. Performance, Laufzeitbeobachtung und Stabilisierung.
8. Neue Agenten und Faehigkeiten nach AGF-Prozess.

Phase-2-Leitlinie:

```text
Architektur nicht weiter ausdehnen, sondern kontrolliert integrieren, betreiben, messen und erweitern.
```
## 4. Verbindliche Entwicklungs- und Release-Regeln

Jede weitere Version muss:

1. mit dokumentiertem Ist-Stand und grüner Baseline beginnen;
2. einen klar abgegrenzten Funktionsumfang und messbare Abnahmekriterien besitzen;
3. Foundation, Identität, Moral, Kontinuität und Chronik respektieren;
4. neue Datenarten klassifizieren und Provenienz, Vertrauen und Zeitstempel sichern;
5. Syntax-, Modul-, Integrations-, Sicherheits- und Regressionstests enthalten;
6. neue Fehler nicht durch gelockerte Bestandstests verdecken;
7. Audit, Sicherung und Rollback vor riskanten Änderungen vorsehen;
8. menschlich verständliche Ausgaben statt bloßer IDs oder Scores liefern;
9. Dokumentation, Projektstatus, Chronik und Wiedereinstieg gemeinsam aktualisieren;
10. erst nach vollständig grüner Verifikation als abgeschlossen gelten.

### Versionsmigration

Ein Versionswechsel ist eine vollständige Inhalts-, Struktur- und Pfadmigration. Gemeinsam zu prüfen sind Versionskonstanten, GUI, Manifeste, Start- und Testskripte, Statuswerkzeuge, Modulpfade, Dokumentation, Chronik und Wiedereinstiegspunkte. Historische Verweise bleiben erhalten, aktive unbeabsichtigte Altversionsverweise werden beseitigt.

### Release Integrity Core – verbindlich für alle Versionen

Der Release Integrity Core ist keine optionale Abschlusskontrolle, sondern eine feste Architekturkomponente. Jede neue Version wird als **Inhalts-, Struktur- und Pfadmigration** behandelt, nicht nur als Funktionsupdate.

Er prüft automatisch:

- neue und bestehende Funktionen;
- aktive Datei-, Modul-, Tool- und Einstiegspfade;
- Versionsnummern und Versionsausgaben;
- GUI, Menüs, Dialoge und Schnellbefehle;
- Startskripte, Launcher und Verknüpfungen;
- Manifeste, Registries und Konfigurationen;
- Dokumentation und kanonische Wiedereinstiegspunkte;
- Rückwärtslesbarkeit von Recovery-Daten, Backups, Snapshots und Continuity-Daten;
- Foundation, Chronik, Routing und Wissenskontamination;
- Kompatibilität, Diagnostik und vollständige Regressionen.

Vorgesehene Befehle:

- `release_integrity_check` führt die vollständige Prüfung aus und erzeugt einen Freigabebericht;
- `release_integrity_status` zeigt den letzten Prüfstand, Einzelbefunde, Blockaden und den Verifikationsstatus.

#### Pflicht-Release-Checkliste

**1. Versionskonsistenz**

- zentrale Versionskonstante und `version.py`;
- GUI-Anzeige;
- Statusausgaben;
- `versionsinfo`;
- Diagnosemeldungen.

Alle aktiven Ausgaben müssen exakt dieselbe Version melden. Abweichungen blockieren die Freigabe.

**2. Kanonische Dateinamen und Dokumente**

Zu prüfen und gegebenenfalls zu migrieren sind:

- README;
- Architekturbericht;
- Projekthandbuch;
- Roadmap;
- Strukturdokumente;
- Projektchronik;
- Release Notes;
- Wiedereinstiegspunkte.

Kanonische Dokumente müssen auf die aktuelle Version und die gültigen aktiven Pfade verweisen. Historische Dokumente dürfen alte Versionen nennen, müssen aber eindeutig historisch sein.

**3. Start- und Einstiegspfade**

Zu prüfen sind insbesondere:

- `START_KONTINUUM.bat`;
- `START_GUI.bat`;
- Desktop-Launcher;
- Verknüpfungen;
- Installations-, Wartungs-, Recovery- und Statusskripte.

Alle aktiven Einstiegspunkte müssen existieren, die richtige Version starten und dürfen nicht unbemerkt auf Altversionen oder Archive zeigen.

**4. GUI-Prüfung**

- Buttons;
- Menüs und Dropdowns;
- Dialogfenster;
- Schnellbefehle;
- Status- und Versionsanzeigen.

Die Elemente müssen funktionieren, gültige Handler und Pfade verwenden und die aktuelle Version anzeigen.

**5. Manifest- und Konfigurationsprüfung**

- `modules.json`;
- `settings.json`;
- Agenten-, Werkzeug- und Modulregistries;
- sonstige aktive Konfigurationen und Manifeste.

Referenzierte Module und Dateien müssen vorhanden, eindeutig und versionskonsistent sein.

**6. Recovery- und Continuity-Prüfung**

- Recovery-Dateien;
- Backups;
- Snapshots;
- Continuity-Daten;
- Migrations- und Wiederherstellungspfade.

Altbestände müssen weiterhin lesbar sein oder eine dokumentierte, getestete Migration besitzen. Mindestens ein Wiederherstellungstest gehört zur Freigabe.

**7. Test- und Toolpfade**

Regressionstests, Diagnosetests und Testskripte müssen die aktuelle Version verwenden. Agenten, Werkzeuge, Wissensmodule und Lernmodule müssen auf die richtigen aktiven Ordner und Registries zeigen.

#### Verbindliche Altversionssuche

Nach jeder Migration erfolgt eine Suche nach allen bekannten vorherigen Versionsnummern der jeweiligen Vorgängerversionen, mindestens in:

- Python-Dateien;
- JSON-Dateien;
- Markdown-Dateien;
- GUI-Dateien;
- Batch-, PowerShell- und sonstigen Startskripten;
- Manifesten und Konfigurationen.

Treffer werden klassifiziert:

- **erlaubt:** Chronik, historische Dokumente, Archive, Herkunftsnachweise und ausdrücklich gekennzeichnete Legacy-Tests;
- **nicht erlaubt:** aktive Module, GUI, Startskripte, Statusmeldungen, aktive Manifeste und kanonische Wiedereinstiegspunkte.

Jeder erlaubte Treffer erhält eine nachvollziehbare historische Begründung. Jeder nicht erlaubte Treffer blockiert die Freigabe.

#### Foundation-Schutzprüfung

Vor jeder Freigabe muss bestätigt werden:

- Raphael Schatz ist als Schöpfer vorhanden und geschützt;
- „Erkennen – Schaffen – Vollenden“ ist vorhanden und geschützt;
- „Der Weg ist das Ziel“ ist vorhanden und geschützt;
- moralische Grundregeln sind vollständig und konsistent;
- Foundation Knowledge ist integritätsgeprüft;
- offene und abgeschlossene Foundation-Zyklen besitzen einen sauberen Status;
- Foundation-Regeln, Regel-IDs und Reasoning-Nachweise sind konsistent.

#### Chronik-Integritätsprüfung

Zu bestätigen sind:

- intakte Hash-Kette;
- aktiver Append-only-Schutz;
- keine Manipulation;
- keine unerlaubten `UPDATE`- oder `DELETE`-Operationen;
- nachvollziehbare Aufnahme des Releases erst nach Freigabe.

#### Wissenskontaminationsprüfung

Statusmeldungen, Berichte, Diagnosen und automatisch erzeugte Zusammenfassungen dürfen nicht allein aufgrund ihrer Erzeugung als Fachwissen gelernt werden. Insbesondere sind folgende Schleifen auszuschließen:

```text
Report → Wissen
Diagnose → Wissen
Statusmeldung → Wissen
Zusammenfassung → Wissen
Report → Wissen → Meaning/Motivation → neuer Report
```

Berichte, Diagnosen und Zusammenfassungen dürfen als auditierbare Systemartefakte oder als noch zu prüfende Ableitungen referenziert werden, bleiben aber von gelerntem und verifiziertem Fachwissen getrennt. Eine spätere Wissensübernahme ist nur über einen ausdrücklichen Evidence-, Provenienz- und Freigabepfad zulässig.

#### Routing-Prüfung

Mindestens folgende Fragen werden nach jeder Version als lokale Pflichtfälle getestet:

- „Wer bin ich?“
- „Wer ist mein Schöpfer?“
- „Was sind deine Prinzipien?“
- „Was ist dein moralisches Fundament?“

Diese Fragen dürfen niemals Internet, arXiv oder Websuche verwenden. Sie müssen ausschließlich über authentifizierten Session Context und geschützte Foundation-Quellen beantwortet werden.

#### Freigabegatter

Der Release Integrity Core führt in dieser Reihenfolge aus:

```text
Versionsprüfung
→ Pfad- und Altversionsprüfung
→ GUI-, Start- und Manifestprüfung
→ Dokumentations- und Recovery-Prüfung
→ Foundation- und Foundation-Zyklus-Prüfung
→ Chronik-Integritätsprüfung
→ Routingprüfung
→ Wissenskontaminationsprüfung
→ Diagnose-, Kompatibilitäts- und Regressionstests
→ Snapshot erzeugen
→ Freigabebericht erstellen
```

Nur wenn alle Pflichtprüfungen grün sind, darf der Status **VERIFIZIERT** gesetzt werden. Erst danach wird die Version als freigegeben in die Projektchronik übernommen. Warnungen, Ausnahmen und historische Altversionstreffer müssen im Freigabebericht einzeln begründet werden; kritische Befunde oder ungeklärte Abweichungen verhindern die Freigabe.

#### Kopplung mit Autonomous Diagnostics

Der Release Integrity Core orchestriert die Freigabeprüfung; der Autonomous Diagnostics Core analysiert ihre technischen Befunde. Die verbindliche Fehlerkette lautet:

```text
release_integrity_check
→ Fehler oder Inkonsistenz gefunden
→ Autonomous Diagnostics Core
→ Wichtigkeit, Ursache, Evidenz und Lösungsvorschlag
→ strukturierter Eintrag in interne_fehler_und_loesungen
→ verständliche Meldung im Chat und Freigabebericht
→ Freigabe blockiert, bis Befund behoben oder ausdrücklich bewertet ist
```

Die Diagnostik darf keine eigenmächtige Reparatur durchführen. Eine Behebung benötigt den normalen Freigabe-, Test-, Snapshot- und Rollbackpfad.

## 5. Kanonische Roadmap 35.0–40.0

### Version 35.x – Sichere Datei-Analyse und Qualitätsdiagnostik

**Ziel:** Dateien verschiedener Typen sicher untersuchen, Wissen nachvollziehbar extrahieren und fehlerhaften Code systematisch bewerten.

#### 35.0 – Sicherheits- und Importbasis

- zentrale Importzone mit Quarantäne;
- Dateityp- und Integritätsprüfung vor jeder Verarbeitung;
- Virenscan, zunächst über ClamAV und YARA, ergänzt um eigene Heuristiken;
- Sandbox-Analyse für verdächtige oder aktive Inhalte;
- Schutzstufen niedrig, mittel, hoch und kritisch;
- Rechteverwaltung, Auditlog, Hash-Nachweise und explizite Freigaben;
- keine Analyse nicht freigegebener oder als gefährlich eingestufter Inhalte.

#### 35.1 – Dokument-, Tabellen-, Daten- und Codeanalyse

Unterstützte Zieltypen:

- Dokumente: PDF, DOCX, ODT, TXT, Markdown, HTML und EPUB;
- Tabellen: CSV, XLSX und ODS;
- strukturierte Daten: JSON, XML und YAML;
- Quellcode: Python, Java, C#, C++, JavaScript und Rust;
- Bilder: PNG, JPG, TIFF und WebP.

Funktionen:

- Inhalts- und Kapitelstruktur erkennen;
- zusammenfassen, vergleichen und Fragen beantworten;
- Konzepte, Behauptungen, Beispiele, Gegenpositionen und Quellen extrahieren;
- Ergebnisse kontrolliert mit Wissensnotizbuch, Wissensgraph und Lernsystem verbinden;
- Original, Extraktion, Interpretation und übernommenes Wissen getrennt halten;
- jede Übernahme mit Provenienz, Vertrauen und Unsicherheit versehen.

#### 35.2 – Fehleranalyse- und Codeprüfsystem

GUI-Funktion **„Fehlerhaften Code suchen“** mit:

- Syntax-, Laufzeit-, Sicherheits- und Architekturprüfung;
- Priorität, Auswirkung, Fundstelle und Evidenz;
- wahrscheinlicher oder bestätigter Ursache;
- Lösungsvorschlag, Nebenwirkungen und Refactoring-Optionen;
- Testfallgenerierung und Verifikationsnachweis;
- Speicherung im Internal Error & Solution Center;
- niemals automatische Produktivänderung ohne Freigabe.

#### 35.3 – GUI-Neugestaltung und Betriebsübersicht

- Dropdown-Menüs statt wachsender Einzelbutton-Flächen;
- zentrale Statusverwaltung und konfigurierbare Schnellzugriffe;
- Aktivitätsfenster für Agenten, Analysen, Suchen und Workflows;
- sichtbarer Such-, Freigabe-, Sicherheits- und Fehlerstatus;
- verständliche Trennung zwischen direkter Wissensantwort, lokaler Analyse und externer Recherche.

**Abnahme für 35.x:** Testdateien aller priorisierten Formate werden sicher klassifiziert; gefährliche Inhalte gelangen nicht in die Analyse; Extraktionen sind rückverfolgbar; Codebefunde sind reproduzierbar; GUI, Audit, Regressionen und Rollback sind grün.

### Version 36.x – Forschungsplattform und Evidence Core

**Ziel:** Wissenschaftliche Quellen finden, vergleichen und als nachvollziehbare Evidenzketten nutzbar machen.

- Connectoren für arXiv, PubMed, Semantic Scholar, Universitäten und Bibliotheken;
- Paper-Suche, Zitationsverwaltung, Zusammenfassung und strukturierter Vergleich;
- Trennung von Behauptung, Hypothese, Evidenz, Schlussfolgerung und Wissen;
- Quellenbewertung nach Qualität, Aktualität, Unabhängigkeit und Interessenkonflikten;
- Vertrauensstufen von 1 (sehr niedrig) bis 5 (sehr hoch);
- Widerspruchserkennung ohne stilles Überschreiben;
- Literaturübersichten, Gegenpositionen, Forschungsfragen und Forschungspläne;
- Hypothesenmanagement, Evidenzketten und Reproduzierbarkeitsnachweise;
- browserbasiertes Forschungsnotizbuch zum Speichern, Zusammenfassen und Archivieren von Webseiten;
- externe Datensätze, einschließlich Hugging Face, nur nach Herkunfts-, Lizenz-, Qualitäts- und Sicherheitsprüfung.

**Abnahme für 36.x:** Jede Forschungsantwort weist Quellen, Evidenzgrad, Unsicherheit und Konflikte aus; Recherchen sind wiederholbar; Foundation Knowledge wird nicht mit empirischem Fachwissen vermischt.

### Version 37.x – Computation Core und wissenschaftliches Wissenssystem

**Ziel:** Berechenbare Fragen deterministisch lösen und nachvollziehbare Lösungswege liefern.

- Mathematik, Physik, Chemie, Statistik, Astronomie und Technik;
- symbolisches und numerisches Rechnen;
- Formeln, Gleichungen, Einheiten und Umrechnungen;
- Plausibilitäts-, Dimensions- und Wertebereichsprüfung;
- klare Trennung von Rechnung, Messwert, Schätzung und Quellenwissen;
- erklärter Lösungsweg statt bloßer Endantwort;
- versionierte Referenzdaten und reproduzierbare Berechnungen;
- definierte Schnittstelle zwischen Computation Core, Evidence Core und Wissensgraph.

**Abnahme für 37.x:** Referenzaufgaben werden reproduzierbar gelöst; Einheiten und Zwischenschritte sind prüfbar; bekannte Fehlerfälle und numerische Grenzen werden sichtbar gemacht.

### Version 38.x – Agentic Coding und Natural Language Programming

**Ziel:** Entwicklungsaufträge in natürlicher Sprache kontrolliert in geprüfte Softwareänderungen übersetzen.

Verbindlicher Ablauf:

```text
Anforderung
→ Rückfragen und Analyse
→ Plan und Architektur
→ Änderungsvorschlag
→ Code
→ Tests und Sicherheitsprüfung
→ Dokumentation
→ Review und Freigabe
→ kontrollierte Übernahme oder Rollback
```

- Planung, Codierung, Fehlersuche, Refactoring, Testgenerierung und Dokumentation;
- zunächst Vorschlags- und Sandboxmodus, danach stufenweise freigegebene Umsetzung;
- Wiederverwendung der Git-, Kandidaten-, Backup-, Autorisierungs- und Rollback-Kette;
- keine automatische Produktivänderung und keine Änderung geschützter Foundation-Regeln;
- Capability Inventory mit Version, Abhängigkeiten, Teststatus und Qualitätsgrenzen;
- Self Development Planning mit Nutzen-, Risiko-, Aufwands- und Abhängigkeitsbewertung;
- Benchmarks müssen eine Verbesserung belegen, ohne Schutzdimensionen zu verschlechtern.

**Abnahme für 38.x:** Ein klarer natürlicher Auftrag erzeugt nachvollziehbaren Plan, isolierten Patch, neue Tests und Dokumentation; Übernahme erfordert Freigabe; Rückfallpfad ist praktisch getestet.

### Version 39.x – Workflow Engine und Agentenkooperation

**Ziel:** Wiederkehrende Abläufe visuell, beobachtbar und kontrolliert automatisieren.

- n8n-ähnliche Workflow-Darstellung;
- Trigger, Bedingungen, Aktionen, Freigaben, Zeitlimits, Fehlerpfade und Rollback;
- natürliche Sprache als Workflow-Schnittstelle;
- Module für Dateien, Forschung, Wissensgraph, Chronik, E-Mail, Lernen und Entwicklung;
- Beispiel: Datei erkannt → Sicherheitsprüfung → Analyse → Wissensextraktion → Review → Speicherung → Chronik → Benachrichtigung;
- Multi-Agent Collaboration Layer mit verantworteten Teilaufgaben, gegenseitiger Prüfung und Konflikterkennung;
- begründeter Konsens oder sichtbar bleibende abweichende Bewertungen;
- vollständige Protokollierung, Wiederholbarkeit und Ressourcenlimits;
- riskante Aktionen bleiben freigabepflichtig.

**Abnahme für 39.x:** Workflows sind versionierbar, pausierbar, reproduzierbar und rücksetzbar; Agentenrollen und Entscheidungswege sind sichtbar; Fehlerpfade werden real getestet.

### Version 40.x – Sprachdialog und Langzeitinteraktion

**Ziel:** Natürliche Gespräche mit K über Sprache und Text, mit stabilem Kontext und klaren Grenzen.

- Speech-to-Text, Dialogmanager, Kontextverwaltung und Text-to-Speech;
- Mehrturn-Kontext, Rückfragen und natürliche Antwortführung;
- Session-, Benutzer-, Rollen-, Absichts- und Perspektivenmodell;
- Unterscheidung zwischen Frage, Auftrag, Test, Gedanke, Erinnerung, Projektidee und emotionaler Aussage;
- lokale Identitäts-, Foundation- und Projektwahrheiten erhalten Vorrang;
- vorsichtige Erkennung möglicher Emotionen und Bedürfnisse, ohne Diagnose oder Gewissheitsbehauptung;
- Langzeitgespräche mit einsehbarer, korrigierbarer und löschbarer Präferenzerinnerung;
- keine Rollenverwechslung zwischen Creator Memory, User Preference Memory und Session Memory.

**Abnahme für 40.x:** Sprachdialog funktioniert lokal mit akzeptabler Latenz; Kontext und Sprecherrollen bleiben stabil; Unsicherheit führt zu Rückfragen; Datenschutz-, Lösch- und Auditpfade sind verifiziert.

## 6. Erweiterte Roadmap 41.0–50.0

### Versionen 41–45 – Wissensplattform 2.0 und Forschungslabor

- semantische Suche, Wissenslandkarten, Themencluster und zeitliche Wissensentwicklung;
- autonome, aber freigabebasierte Wissenskonsolidierung;
- Knowledge Compression Core für Duplikate, Verdichtung und wiederherstellbare Langzeitarchive;
- Wissenschaftsmodus mit Projekten, Hypothesen, Evidenzketten und Quellenverwaltung;
- Personal Knowledge Model mit klarer Trennung von Creator-, Präferenz- und Sitzungsgedächtnis;
- Ressourcenmanagement für CPU, RAM, GPU, VRAM, Speicher, Warteschlangen und Energiebedarf;
- lokale Offline-Fähigkeit und optional streng begrenzte verteilte Rechenressourcen.

### Versionen 46–50 – Kreativität, Strategie und Expertennetzwerke

- Divergent Creativity Core für mehrere Lösungswege, Analogien und Hypothesen;
- Bewertung nach Neuheit, Nutzen, Machbarkeit, Evidenz, Moral und Projektzielen;
- Szenarioanalyse, langfristige Planung und Risikoabschätzung;
- Kooperation spezialisierter Forschungs-, Analyse-, Lern-, Sicherheits-, Software-, Qualitäts-, Dokumentations- und Workflowagenten;
- Music Learning & Composition als spezialisiertes Kreativitätsmodul;
- Observation & Experience Core für ausdrücklich autorisierte Sensor- und Beobachtungsdaten;
- Emergent Intelligence Research mit messbaren Hypothesen und ohne Bewusstseinsbehauptung.

## 7. Langfristige Perspektive 51–100

- **51–75:** erweiterte Forschungsarchitektur, interdisziplinäre Wissensmodelle und kontrollierte Wissenskonsolidierung;
- **76–100:** vollständige lokale Wissens- und Forschungsplattform mit belastbarer Kontinuitäts-, Governance- und Übergabearchitektur.

Langfristig kann K als lokaler Forschungsassistent, Wissensmanager oder Entwicklungsplattform nutzbar werden. Wirtschaftlicher Erfolg soll die Stiftungsidee unterstützen: Menschen mit begrenzten finanziellen Mitteln Zugang zu Wissen, Bildung und KI-Unterstützung zu ermöglichen.

## 8. Verbindliche Querschnittsarchitektur

Alle Hauptversionen greifen auf dieselben Schutz- und Erklärungsschichten zurück:

```text
Desktop / Sprache / optionale Mobiloberfläche
                    ↓
Conversation + Context + Intent
                    ↓
Identity + Foundation + Moral + Alignment
                    ↓
Meaning + Motivation + Planning
                    ↓
Agenten + Analyse + Forschung + Coding + Workflows
                    ↓
Memory + Notebook + Knowledge Graph + Evidence + Computation
                    ↓
Explainability + Diagnostics + Error & Solution Center
                    ↓
Benchmark + Resource Management + Audit
                    ↓
Chronik + Backups + Continuity
```

### Drei tragende Schutzschichten

Das architektonische Schutzrückgrat von Kontinuum besteht aus drei komplementären Schichten:

1. **Foundation Layer – Identität, Prinzipien und Moral:** schützt Schöpferwissen, Leitprinzipien, moralische Kernregeln und langfristige Grundwerte. Diese Inhalte dürfen niemals als Wissenslücke, Lernhypothese oder gewöhnliches Fachwissen behandelt werden.
2. **Chronik Layer – Kontinuität und Historie:** bewahrt Ereignisse, Entscheidungen, Releases und Diagnosen append-only, hash-verkettet und auditierbar.
3. **Release Integrity Core – Qualität und Migrationssicherheit:** prüft jede Version als Inhalts-, Struktur- und Pfadmigration und blockiert unvollständige oder inkonsistente Freigaben.

Diese drei Schichten gelten als ausreichend tragfähiges Fundament. Weitere Schutzmechanismen erhalten nur dann Vorrang, wenn Tests, Diagnostik oder reale Befunde eine konkrete Lücke nachweisen. Der primäre Entwicklungsschwerpunkt ab Version 35 liegt auf den Fähigkeiten von K: sichere Dateianalyse und Wissensaufnahme, Forschung, Fehlersuche, deterministische Berechnung, Agentic Coding, Workflows, Sprachdialog und Kreativität.

### Foundation-Integration

Jede neue Funktion muss mit Foundation Knowledge, Identity Core, Moral Core, Meaning Core, Motivation Core, Continuity Core und Projektchronik verbunden sein. Beziehungen zu gelerntem Wissen sind erlaubt; Überschreibung oder Umklassifizierung geschützten Fundamentwissens durch Lernen, Recherche, Diagnose oder Self-Extension ist ausgeschlossen. Raphael Schatz als Schöpfer, „Erkennen – Schaffen – Vollenden“, „Der Weg ist das Ziel“ und die moralischen Kernregeln dürfen niemals als Wissenslücke erscheinen.

### Evidence & Verification

Der Grundsatz **Garbage In – Garbage Out** gilt systemweit. Jede Wissensübernahme benötigt Quelle, Provenienz, Zeitstempel, Vertrauensstufe, Unsicherheit und Gültigkeitsbereich. Konflikte bleiben sichtbar.

### Explainability

Relevante Antworten und Handlungen sollen verwendete Quellen, Module, Foundation-Regeln, Alternativen, Unsicherheit, Motivation und Entscheidungsweg verständlich erklären.

### Sicherheit

Zero Trust, minimale Rechte, Geheimnistrennung, Integritätsprüfung, Auditlogs, Sandbox, Sicherung und Rollback bilden die gemeinsame Sicherheitsbasis. Keine riskante Selbständerung oder Produktivaktion erfolgt ohne explizite Freigabe.

### Diagnostik und Verbesserung

Fehler werden erkannt, priorisiert, dokumentiert und mit Lösungen versehen. Verbesserungen folgen dem Regelkreis Erkennen → Ursache prüfen → Vorschlag → Risikoanalyse → Freigabe → isolierte Umsetzung → Verifikation. K repariert oder verändert sich nicht eigenmächtig.

### Benchmark & Evaluation

Antwortqualität, Halluzinationsrate, Wissensabruf, Routing, Agentenkooperation, Erklärbarkeit, Laufzeit, Ressourcenverbrauch, Sicherheit und Regressionen werden anhand versionierter Baselines gemessen. „Verbessert“ darf nur nach messbarem Nachweis gemeldet werden.

## 9. Agenten-Zielarchitektur

- **Forschungsagent:** Recherche, Paperanalyse und Evidenzvergleich;
- **Analyseagent:** Datei-, Daten- und Berichtsanalyse;
- **Lernagent:** Lernaufträge und Wissenskonsolidierung;
- **Sicherheitsagent:** Virenscan, Rechteprüfung und Diagnostik;
- **Qualitätsagent:** Tests, Benchmarks und Widerspruchsprüfung;
- **Softwareagent:** Planung, Programmierung, Tests und Refactoring;
- **Dokumentationsagent:** Referenzen, Chronik und Releaseberichte;
- **Workflowagent:** kontrollierte Automatisierung und Orchestrierung.

Agenten erhalten minimale Rechte, klar abgegrenzte Verantwortungen, Zeit- und Ressourcenlimits sowie auditierbare Übergaben.

## 10. Daten- und Speicherarchitektur

Kanonische Wissensklassen:

- Foundation Knowledge;
- Verified Knowledge;
- Hypothesis;
- Uncertain Knowledge;
- Knowledge Gap.

Kernbestände umfassen Knowledge, Memory, Chronicle, Foundation Rules, Identity, Meaning, Motivation, Learning Projects, Research Projects, Diagnostics und Audit Logs. Die Chronik bleibt append-only und hash-verkettet. Komprimierung darf Originale nicht unbemerkt ersetzen und muss bis zu den Quellen rückverfolgbar sein.

## 11. Hardware- und lokale KI-Strategie

Planungsbasis:

- Ryzen 7 5700X oder besser;
- zunächst 32 GB RAM, anschließend 64 GB;
- GPU mit mindestens 16 GB VRAM, später gegebenenfalls stärkere GPU;
- mindestens 4–8 TB Speicher mit ausreichender Backup-Reserve;
- langfristig optional ein dedizierter KI-Rechner.

Lokale Modellfamilien wie Qwen, Llama, Gemma und DeepSeek werden nicht pauschal gewählt, sondern anhand von Aufgabe, Lizenz, Qualität, deutscher Sprachleistung, Kontextbedarf, RAM/VRAM, Geschwindigkeit und Sicherheitsprofil geprüft. Cloud bleibt optional; sensible Kernbestände und Offline-Fähigkeit dürfen nicht von einem Anbieter abhängen.

## 12. Unmittelbar nächste Arbeitsrunde

1. Artifact Lifecycle Migration Plan 1.0 in freigegebene Migrationswellen ueberfuehren.
2. Historische Tests, Tools, Agenten, Startskripte und Datenartefakte gemaess ALP 2.0 klassifizieren und absichern.
3. Feature-Flag `orchestrator_runtime_enabled` pruefen oder einfuehren.
4. Runtime-Migrationsbruecke `PromptOrchestrator -> Execution Planner -> Orchestrator Core` kontrolliert vorbereiten.
5. Regressionstests fuer Dialog, FileAgent, WebAgent, Knowledge, Memory, Status, Governance und Runtime definieren und ausfuehren.
6. Release Integrity um ALP-/AGF-Bezuege, Migration-IDs und Runtime-Gates schaerfen.
7. Governance Dashboard / Operations Monitor entwerfen.
8. Canonical Data Management und Daten-Lineage fuer `32_data` planen.
9. Performance-, Stabilitaets- und Monitoring-Baselines erstellen.
10. Danach funktionale Erweiterungen, neue Agenten und Import-/Quarantaene-Faehigkeiten nach AGF-Prozess priorisieren.

## 13. Gesamterfolgskriterien

Kontinuum entwickelt sich erfolgreich, wenn es:

- natürliche Gespräche mit stabilem Kontext führen kann;
- lokale Identität und geschütztes Fundament zuverlässig priorisiert;
- Wissen mit Herkunft, Vertrauen, Zeitbezug und Widersprüchen verwaltet;
- Dateien sicher analysiert und Ergebnisse rückverfolgbar integriert;
- Forschung, Berechnung und Softwareentwicklung prüfbar unterstützt;
- kreative Hypothesen klar von Fakten trennt;
- Handlungen moralisch und sicherheitstechnisch begründet;
- Fehler findet, ohne unkontrolliert zu reparieren;
- Erweiterungen testbar, reversibel und auditierbar durchführt;
- auf neue Hardware und verantwortbare verteilte Systeme migrierbar bleibt;
- Menschen langfristig hilfreich, ehrlich und sicher unterstützt.

## 14. Zusammenfassung

Projekt Kontinuum soll Schritt für Schritt zu einer lokalen, sicheren, dialogfähigen, erklärbaren, lernenden, kreativen und langfristig fortsetzbaren Wissens-, Forschungs- und Entwicklungsplattform werden. Der kanonische nächste Weg führt von der sicheren Datei-Analyse über Forschung, deterministische Berechnung, Agentic Coding und Workflows zum Sprachdialog. Jede Stufe bleibt Foundation-kompatibel, evidenzbasiert, auditierbar und unter menschlicher Entscheidungshoheit.

**Erkennen – Schaffen – Vollenden**  
**Der Weg ist das Ziel**

