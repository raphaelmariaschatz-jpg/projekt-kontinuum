# Artifact Lifecycle Policy 2.0

Status: kanonische Architektur-Richtlinie
Gueltig ab: 2026-07-05
Geltungsbereich: gesamtes Projekt Kontinuum

## 1. Zweck

Artifact Lifecycle Policy 2.0, kurz ALP 2.0, definiert die verbindlichen Lebenszyklusregeln fuer Projektartefakte. Sie ist Grundlage fuer Canonical Artifact Manager, Release Integrity, kuenftige Releases, automatische Archivierung, Runtime-Migration, Projektstruktur und Git-Historie.

ALP 2.0 fuehrt den folgenden Foundation-Grundsatz ein:

> Jede aktive Datei besitzt genau einen kanonischen Zweck und genau einen kanonischen Speicherort.

Daraus folgen drei verbindliche Regeln:

1. Eine aktive Datei darf nicht zugleich produktive Komponente, historische Evidenz und Ersatzkopie sein.
2. Eine aktive Datei darf nicht dauerhaft in mehreren Versionen neben sich selbst existieren.
3. Der kanonische Speicherort einer aktiven Datei muss aus Projektstruktur, CAM und Release Integrity eindeutig ableitbar sein.

Diese Policy beschreibt Regeln. Sie verschiebt, loescht oder benennt keine Dateien um.

## 2. Artefaktklassen

### 2.1 Canonical

Canonical bezeichnet die aktuell gueltige produktive Datei einer Komponente oder Regel.

Eigenschaften:

- wird aktiv verwendet;
- ist in CAM, Projektstruktur, Manifesten oder Dokumentation als aktuelle Quelle nachvollziehbar;
- besitzt genau einen kanonischen Zweck;
- besitzt genau einen kanonischen Speicherort;
- darf im aktiven Projektbereich liegen.

Beispiele:

- aktuelle Core-Module;
- aktuelle Agenten;
- aktuelle Startskripte;
- aktuelle Architektur- und Projektstruktur-Dokumentation;
- aktuelle Konfigurationen und Schemata.

### 2.2 Runtime Required

Runtime Required bezeichnet Artefakte, die fuer den produktiven Betrieb zwingend erforderlich sind.

Eigenschaften:

- werden durch Startskripte, Imports, Konfiguration, Registry, GUI, Tests oder Runtime geladen;
- duerfen nicht automatisch verschoben werden;
- muessen vor jeder Archivierung explizit gegen produktive Abhaengigkeiten geprueft werden;
- koennen zugleich Canonical sein.

Beispiele:

- produktiv importierte Python-Module;
- Runtime-Schemata;
- aktive Config-Dateien;
- aktuelle Starter;
- Agent- und Tool-Registries.

### 2.3 Release Evidence

Release Evidence bezeichnet Artefakte, die dem Nachweis eines Release-, Audit-, Migrations- oder Compliance-Zustands dienen.

Eigenschaften:

- duerfen versionierte Dateinamen besitzen;
- duerfen mehrere historische Staende abbilden;
- muessen unverfaelscht nachvollziehbar bleiben;
- duerfen nicht automatisch geloescht werden;
- duerfen nur verschoben werden, wenn Referenzen und Evidenzkette erhalten bleiben.

Beispiele:

- Release-Integrity-Dateien;
- Audit Reports;
- Baselines;
- Compliance Reports;
- Test Reports;
- Migrationsberichte;
- signierte Evidence-Snapshots.

### 2.4 Historical

Historical bezeichnet fruehere Versionen produktiver Komponenten, die nicht mehr produktiv verwendet werden.

Eigenschaften:

- nicht mehr Runtime Required;
- nicht mehr aktuelle kanonische Datei;
- kann weiterhin fuer Nachvollziehbarkeit wertvoll sein;
- ist nach vollstaendiger Pruefung archivierungsfaehig;
- gehoert nicht dauerhaft in aktive Hauptordner.

Beispiele:

- fruehere Agentenversionen;
- alte Start- und Testskripte;
- ersetzte Projektstatusdateien;
- fruehere Projektstruktur- oder Release-Dokumente.

### 2.5 Deprecated

Deprecated bezeichnet Artefakte, die nach Pruefung nicht mehr benoetigt werden.

Eigenschaften:

- nicht Runtime Required;
- nicht Release Evidence;
- nicht fuer historische Rekonstruktion erforderlich;
- darf nicht automatisch geloescht werden;
- Entfernung ist nur nach ausdruecklicher manueller Freigabe erlaubt.

Beispiele:

- veraltete generierte Zwischenartefakte;
- doppelte Kopien ohne Evidenzwert;
- reproduzierbare Caches nach Sicherheitspruefung.

## 3. Kanonische Dateinamensregeln

Aktive produktive Komponenten besitzen grundsaetzlich stabile Dateinamen ohne technische Versionsnummer.

Beispiele fuer kuenftige kanonische Namen:

- `learning_agent.py` statt `learning_agent_1_2.py`;
- `continuous_learning_governance.py` statt `continuous_learning_governance_1_1.py`;
- `status_check.py` statt `status_check_34_1.py`, sofern der Statuscheck nicht selbst Release Evidence ist;
- `START_KONTINUUM.bat` und `TEST_KONTINUUM.bat` als stabile produktive Einstiegspunkte.

Versionen gehoeren ausschliesslich in:

- Archivbereiche;
- Releasebereiche;
- Git-Historie;
- CAM-/Release-Evidence;
- explizit historische Dokumentation.

Zulaessige Ausnahmen:

1. Release Evidence darf Versionsnummern im Dateinamen behalten.
2. Schemata und Konfigurationen duerfen Versionsnummern behalten, wenn die Version Bestandteil eines aktiven Vertrags ist.
3. Tests duerfen Versionsnummern behalten, wenn sie eine konkrete historische Regression, ein Release Gate oder eine Kompatibilitaet pruefen.
4. Chronik- und Release-Dokumente duerfen Versionsnummern behalten, wenn sie bewusst historische Ereignisse dokumentieren.
5. Migrationen und Baselines duerfen Versionsnummern behalten, wenn sie einen Vorher-/Nachher-Zustand beweisen.
6. Kompatibilitaetspfade duerfen Versionsnummern behalten, solange CAM sie als Runtime Required oder Compatibility Required fuehrt.

Jede Ausnahme muss einer Artefaktklasse zugeordnet sein. Eine Versionsnummer allein begruendet keine Ausnahme.

## 4. Lebenszyklus einer Komponente

Der verbindliche Lebenszyklus lautet:

```text
Development
  -> Verification
  -> Canonical
  -> Runtime
  -> Release
  -> Historical
  -> Deprecated
  -> Archive
```

### 4.1 Development

Verantwortlichkeit: Entwickler, Codex, Raphael.

CAM-Verhalten:

- erkennt neue Artefakte als Kandidaten;
- markiert sie nicht automatisch als Canonical;
- verlangt Zweck, Zielort und erwartete Artefaktklasse.

Release Integrity:

- prueft noch nicht als produktive Pflichtdatei;
- kann Entwicklungsartefakte als Vorbereitungsnachweis erfassen.

Git:

- Aenderungen sollen nachvollziehbar bleiben;
- grosse Schritte sollen getrennt abgeschlossen werden.

Dokumentation und Tests:

- geplante Funktion, Risiken und erwartete Tests muessen erkennbar sein.

### 4.2 Verification

Verantwortlichkeit: Codex und Release-/Architekturpruefung.

CAM-Verhalten:

- prueft Imports, Referenzen, Zielordner, Namensregel und Konflikte;
- klassifiziert das Artefakt vorlaeufig.

Release Integrity:

- fuehrt erforderliche Tests, Statuschecks und Release Gates aus oder dokumentiert begruendete Ausnahmen.

Git:

- prueft Arbeitsbaum und uncommitted Aenderungen;
- verhindert Vermischung unabhaengiger Release-Schritte, soweit praktikabel.

Dokumentation und Tests:

- Tests muessen die neue Komponente oder Aenderung abdecken;
- kanonische Dokumentation muss bei Architekturwirkung aktualisiert sein.

### 4.3 Canonical

Verantwortlichkeit: CAM, Architekturmodell, Raphael-Freigabe bei Strukturwirkung.

CAM-Verhalten:

- erklaert genau eine aktive Datei pro Zweck und Speicherort als kanonisch;
- markiert ersetzte aktive Dateien als Historical-Kandidaten;
- verhindert parallele aktive Versionen ohne Ausnahme.

Release Integrity:

- nimmt die Datei in Required Paths oder erlaubte Ausnahmen auf, sofern releasekritisch.

Git:

- kanonische Aenderungen sollen getrennt nachvollziehbar sein.

Dokumentation und Tests:

- Dokumentation nennt den kanonischen Pfad;
- Tests verwenden den kanonischen Pfad, ausser sie pruefen bewusst historische Kompatibilitaet.

### 4.4 Runtime

Verantwortlichkeit: Runtime, Orchestrator, Starter, Config, Registries.

CAM-Verhalten:

- markiert produktiv geladene Dateien als Runtime Required;
- blockiert automatische Verschiebung;
- fordert Sicherheitspruefung bei jeder Pfadaenderung.

Release Integrity:

- prueft Startskripte, Config, Imports, Schemata, Registries und produktive Tests.

Git:

- Runtime-relevante Aenderungen muessen rueckverfolgbar bleiben.

Dokumentation und Tests:

- Runtime-Pfade muessen dokumentiert und regressionsgetestet sein.

### 4.5 Release

Verantwortlichkeit: Release Integrity, CAM, Governance.

CAM-Verhalten:

- trennt Canonical, Runtime Required und Release Evidence;
- erzeugt oder prueft Evidence-Ablagen;
- markiert fruehere Versionen als Historical, sobald die neue Version freigegeben ist.

Release Integrity:

- prueft Tests, Status, Release Gate, Dokumentation, erforderliche Dateien und erlaubte Legacy-Pfade.

Git:

- Release-Zustand muss nachvollziehbar sein;
- Evidence darf nicht nachtraeglich stillschweigend umgedeutet werden.

Dokumentation und Tests:

- Release-Dokumente, Baselines und Testberichte werden als Release Evidence gefuehrt.

### 4.6 Historical

Verantwortlichkeit: CAM und Archivpruefung.

CAM-Verhalten:

- klassifiziert fruehere produktive Versionen als Historical;
- prueft, ob sie noch referenziert oder testrelevant sind;
- empfiehlt Archivierung, fuehrt sie aber nur nach Freigabe und vollstaendiger Pruefung aus.

Release Integrity:

- unterscheidet zwischen erlaubter historischer Evidenz und unzulaessiger aktiver Altversion.

Git:

- Git bleibt historische Quelle, ersetzt aber nicht zwingend Release Evidence oder Archivpflicht.

Dokumentation und Tests:

- historische Referenzen muessen als historisch gekennzeichnet sein;
- aktive Tests duerfen Historical nur laden, wenn sie Kompatibilitaet oder Regression pruefen.

### 4.7 Deprecated

Verantwortlichkeit: Raphael-Freigabe, CAM, Governance.

CAM-Verhalten:

- empfiehlt Entfernung nur, wenn kein produktiver, historischer oder evidenzbezogener Zweck bleibt;
- darf nicht automatisch loeschen.

Release Integrity:

- prueft, dass Entfernung keine Gates, Tests oder Evidence-Ketten bricht.

Git:

- Entfernung muss nachvollziehbar und begruendet sein.

Dokumentation und Tests:

- Verweise auf Deprecated-Artefakte muessen entfernt oder historisch erklaert sein.

### 4.8 Archive

Verantwortlichkeit: CAM und freigegebene Archivierungsroutine.

CAM-Verhalten:

- bestimmt Zielarchiv;
- prueft Pfadkonsistenz;
- protokolliert Quelle, Ziel, Grund, Pruefungen und Freigabe.

Release Integrity:

- prueft nach Archivierung, dass keine ungueltigen aktiven Referenzen bleiben.

Git:

- Archivierung muss als eigener, nachvollziehbarer Schritt erkennbar sein.

Dokumentation und Tests:

- notwendige Referenzen werden auf Archivpfade oder kanonische Nachfolger aktualisiert.

## 5. Ordnerregeln

### 5.1 Kanonisch reine Hauptordner

Die folgenden aktiven Hauptordner duerfen grundsaetzlich nur Canonical, Runtime Required oder ausdruecklich aktive Tests enthalten:

- `12_agents`
- `13_tools`
- `14_documents`
- `16_installation`
- `17_tests`
- `24_config`

In diesen Ordnern sind parallele historische Versionen derselben Komponente unzulaessig, sofern keine ausdrueckliche Ausnahme als Runtime Required, Release Evidence oder Compatibility Required dokumentiert ist.

### 5.2 Historische und versionsbezogene Bereiche

Historische Artefakte gehoeren in dafuer vorgesehene Bereiche:

- `archive`
- `02_versions`
- `history`
- `releases`
- `migration_artifacts`
- `09_backups/migration_reports`

Archivbereiche duerfen Versionsnummern, Releasebezeichnungen, alte Pfade und historische Paketstrukturen enthalten, solange Provenienz und Zielordnung nachvollziehbar bleiben.

### 5.3 Sonderregel `22_project_chronicle`

`22_project_chronicle` darf historische Informationen enthalten, weil Chronik und Release-Historie selbst fachlicher Inhalt sind.

Verbindlich:

- aktuelle Einstiegspunkte und aktuelle Chronikdateien muessen eindeutig erkennbar sein;
- historische Release-Dateien duerfen versioniert bleiben;
- produktive Start- oder Runtime-Pfade duerfen nicht allein aus historischen Chronikdateien abgeleitet werden;
- CAM muss zwischen Chronikinhalt und aktiver Projektsteuerung unterscheiden.

### 5.4 Sonderregel `31_reports`

`31_reports` darf Release Evidence, Audit Reports, Baselines, Compliance Reports und Statusberichte enthalten.

Verbindlich:

- Reports duerfen versioniert und datiert sein;
- Reports sind nicht automatisch produktive Komponenten;
- Reports duerfen nicht automatisch geloescht werden;
- alte Reports gehoeren bei wachsendem Bestand in strukturierte Report-Archive, sofern Referenzen erhalten bleiben.

### 5.5 Sonderregel `32_data`

`32_data` darf dynamische Daten, Wissensartefakte, Review-Ablagen, Queue-Daten und historische Datenprovenienz enthalten.

Verbindlich:

- produktive Datenbereiche muessen von historischen Datenkopien unterscheidbar sein;
- flach abgelegte historische Spiegeldateien sind als Historical- oder Release-Evidence-Kandidaten zu pruefen;
- automatische Verschiebung ist nur nach Datenprovenienz-, Referenz- und Runtime-Pruefung zulaessig;
- Wissens-, Review- und Queue-Daten duerfen nicht pauschal als bereinigbare Altdateien behandelt werden.

## 6. CAM-Regeln

Der Canonical Artifact Manager darf kuenftig folgende Entscheidungen vorbereiten oder treffen:

### 6.1 Automatisch zulaessige Klassifikation

CAM darf automatisch vorschlagen:

- Datei bleibt produktiv;
- Datei ist Canonical;
- Datei ist Runtime Required;
- Datei ist Release Evidence;
- Datei ist Historical;
- Datei ist Deprecated-Kandidat;
- Datei benoetigt Benutzerfreigabe.

### 6.2 Automatisch zulaessige Massnahmen

CAM darf ohne Benutzerfreigabe nur read-only Entscheidungen treffen:

- klassifizieren;
- berichten;
- Konflikte markieren;
- Referenzen scannen;
- Risiken bewerten;
- Archivierungsziel vorschlagen;
- Release-Integrity-Ausnahmen anzeigen.

### 6.3 Benutzerfreigabe erforderlich

Benutzerfreigabe ist erforderlich fuer:

- Verschieben produktiver oder historischer Dateien;
- Umbenennen aktiver Dateien;
- Aendern von Imports;
- Aendern von Startskripten;
- Aendern von Release-Integrity-Required-Paths;
- Archivieren von Runtime Required, Release Evidence oder unklaren Artefakten;
- Entfernen oder Loeschen von Dateien.

### 6.4 Niemals automatisch verschieben

CAM darf niemals automatisch verschieben:

- Runtime Required;
- Release Evidence ohne Evidenzkettenpruefung;
- aktive Konfigurationen;
- Startskripte;
- kanonische Architektur- und Foundation-Dateien;
- Daten mit ungeklaerter Provenienz;
- Dateien mit ungeklaerten Referenzen;
- Dateien, die in Tests, Imports oder Manifesten aktiv referenziert sind.

## 7. Archivierungsrichtlinien

Eine Archivierung ist nur zulaessig, wenn alle Voraussetzungen erfuellt sind.

Vorher zu pruefen:

1. Imports;
2. Tests;
3. Dokumentation;
4. Release Integrity;
5. CAM;
6. Startskripte;
7. Konfiguration;
8. Registries;
9. Manifeste;
10. interne und externe Referenzen;
11. Git-Status;
12. Zielarchiv;
13. Rueckfallstrategie.

Mindestbedingungen:

- Die Datei ist nicht mehr produktiv oder es existiert ein freigegebener kanonischer Nachfolger.
- Alle aktiven Referenzen sind bekannt.
- Tests und Release Gates sind gruen oder Abweichungen sind dokumentiert.
- Das Archivziel liegt in einem zugelassenen Archiv-, Versions- oder Releasebereich.
- Die Archivierung ist protokolliert.
- Raphael oder eine ausdruecklich festgelegte Governance-Regel hat die Archivierung freigegeben.

Ohne vollstaendige Pruefung erfolgt keine Archivierung.

## 8. Release-Integrity-Regeln

Release Integrity muss ALP 2.0 beruecksichtigen:

- Required Paths duerfen nur aktive Canonical- oder Runtime-Required-Dateien verlangen.
- Allowed Legacy Paths muessen begruendet und befristet oder als Release Evidence klassifiziert sein.
- Historische Release-Dateien duerfen nicht als produktive Pflichtdateien missverstanden werden.
- Versionierte Tests muessen entweder aktive Regressionen oder historische Kompatibilitaet pruefen.
- Release Evidence darf nicht durch automatische Bereinigung entfernt werden.

## 9. Git-Regeln

Git ist die technische Historie, ersetzt aber nicht die kanonische Projektordnung.

Verbindlich:

- Aktive Ordner repraesentieren den aktuellen kanonischen Zustand.
- Git bewahrt Aenderungshistorie, aber keine aktive Mehrdeutigkeit.
- Groessere Architekturphasen sollen getrennt abgeschlossen werden.
- Archivierung, Runtime-Migration und Release-Updates sollen nicht unnoetig in einem Commit vermischt werden.
- Keine Bereinigung erfolgt ohne vorherige Analyse und Freigabe.

## 10. Anwendung auf Runtime-Migration

Vor der Runtime-Migration muessen aktive Altversionen, historische Starter, versionierte Agenten und flache historische Datenartefakte mindestens klassifiziert sein.

Die Runtime-Migration darf nur beginnen, wenn:

- Runtime Required eindeutig bestimmt ist;
- Canonical-Dateien eindeutig sind;
- historische Parallelstaende kein produktives Routing mehr beeinflussen;
- Feature-Flags und Rueckfallpfade dokumentiert sind;
- Release Integrity die neue Runtime-Kette pruefen kann.

## 11. Abschlussregel

ALP 2.0 ist verbindlich fuer alle kuenftigen Komponenten, Agenten, Tools, Dokumente, Konfigurationen, Reports, Datenartefakte, Releases und Migrationen.

Keine aktive Datei darf dauerhaft mehrdeutig bleiben. Wenn eine Datei nicht eindeutig klassifiziert werden kann, wird sie nicht verschoben, sondern als `unklarer Sonderfall` an CAM, Release Integrity und Raphael-Freigabe uebergeben.
