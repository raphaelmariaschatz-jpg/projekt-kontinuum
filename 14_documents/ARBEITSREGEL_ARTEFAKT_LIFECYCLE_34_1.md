# Arbeitsregel: Artefakt-Lifecycle 34.1

## Vor endgültiger Freigabe behalten

- temporäre Testprojekte und Testfixtures
- CAM-Testmanifest-Dateien
- generierte Prüfberichte
- Release-Integrity-Reports
- Verifikationslogs
- Migrationsprotokolle und Migrationsberichte
- Architekturberichte und Audit-Logs

## Freigabeschwelle

Eine Archivierung erfolgt erst, wenn alle Bedingungen erfüllt sind:

1. alle Tests sind grün;
2. die Statusprüfung ist grün;
3. das Release-Gate ist grün;
4. die Dokumentation ist aktualisiert;
5. Codex hat die Freigabe bestätigt.

## Nach der Freigabe

Wichtige Artefakte werden nicht gelöscht, sondern nach
`02_versions/migration_artifacts/<migration>` oder ergänzend nach
`09_backups/migration_reports/` archiviert.

Löschen ist nur nach ausdrücklicher manueller Prüfung zulässig.

## Sofort bereinigbare Artefakte

- `__pycache__`
- `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
- `.pyc` und `.pyo`
- temporäre Build- und Entpackverzeichnisse
- generierte Laufzeit-Caches

Vor jeder rekursiven Bereinigung muss geprüft werden, dass der aufgelöste
Zielpfad innerhalb der vorgesehenen Projekt- oder Arbeitswurzel liegt.

## Niemals automatisch löschen

- Migrations- und Release-Berichte
- Architektur- und Verifikationsberichte
- Migrationsprotokolle
- Audit-Logs

Diese Unterlagen erklären später nachvollziehbar, warum eine Struktur geändert
wurde und auf welcher Evidenz die Freigabe beruhte.

## Dauerhafte Archivstruktur und Lifecycle-Regel

Ab sofort besitzt jeder aktive Hauptordner einen Unterordner `archive`.
Historische Dateien verbleiben nicht dauerhaft im aktiven Bereich, sondern
werden nach Sicherheitsprüfung in den jeweiligen Archivbereich verschoben.
Sinnvolle Unterordner sind je nach Kontext `releases`, `legacy`, `reports`,
`migrations`, `backups`, `tests` und `tmp`.

Im aktiven Bereich dürfen ausschließlich produktive oder kanonische Dateien
liegen: aktuelle Quelltexte, aktuelle Dokumentation, aktuelle Konfigurationen,
aktuelle Releases, aktive Tests, aktive Skripte und aktuelle Manifeste.

Vor jeder Archivierung prüft Codex verbindlich:

1. ob die Datei aktuell verwendet wird;
2. ob sie kanonisch ist;
3. ob Abhängigkeiten bestehen;
4. ob Referenzen angepasst werden müssen;
5. ob die Archivierung gefahrlos möglich ist.

Nach jeder Archivierung prüft Codex automatisch Dokumentationen, Manifeste,
Registry-Dateien, Konfigurationen, Startskripte, Tests, Build-Prozesse und
Release-Dateien. Betroffene Pfade werden aktualisiert; ungültige Referenzen
dürfen nicht zurückbleiben.

Dateien werden grundsätzlich nicht gelöscht. Historische Dateien werden
archiviert. Eine Löschung erfolgt nur auf ausdrückliche Anweisung von Raphael.

Nach jedem zukünftigen Release prüft Codex, ob neue Altversionen entstanden
sind, ob Archivierungen erforderlich sind, ob die Archive vollständig sind, ob
alle Referenzen stimmen und ob die Projektstruktur weiterhin kanonisch ist.
Diese Prüfung ist Bestandteil jedes zukünftigen Release-Prozesses.

Diese Regel gilt für alle zukünftigen Module, Foundation-Komponenten,
CAM-Module, Dokumentationen, Releases, Migrationen und Erweiterungen. Neue
Komponenten müssen die Archivstruktur automatisch einhalten.

## Canonical Active Directory Policy (CADP) 1.0

Ab sofort gilt fuer das gesamte Projekt Kontinuum: In allen aktiven
Projektordnern duerfen ausschliesslich die aktuell kanonischen Dateien liegen.
Historische Versionen, ersetzte Dokumente, fruehere Releases, veraltete
Konfigurationsdateien und nicht mehr kanonische Artefakte duerfen sich nicht
dauerhaft in aktiven Projektordnern befinden.

Die aktive Projektstruktur repraesentiert jederzeit ausschliesslich den
aktuellen kanonischen Projektzustand. Die vollstaendige Entwicklungshistorie
bleibt erhalten, befindet sich jedoch ausschliesslich innerhalb der
vorgesehenen `archive`-Strukturen.

Sobald eine Datei durch eine neue kanonische Version ersetzt wird, ist
verpflichtend auszufuehren:

1. Die bisherige Version wird in den passenden Unterordner `archive` des
   jeweiligen Projektbereichs verschoben.
2. Existiert noch kein geeigneter Archivordner, wird er nach der bestehenden
   Projektstruktur angelegt.
3. Die Archivstruktur erhaelt Versionshistorie und Nachvollziehbarkeit,
   beispielsweise nach Version, Release oder Datum.
4. Die neue kanonische Datei verbleibt als einzige aktive Datei im produktiven
   Bereich.

Nach jeder Verschiebung muessen saemtliche Verweise auf die verschobene Datei
automatisch geprueft und bei Bedarf angepasst werden. Dazu gehoeren
insbesondere:

- Dokumentationen
- kanonische Manifeste
- CAM-Registrierungen
- Architekturmodelle
- Handbuecher
- Projektchronik
- Release-Dateien
- Konfigurationsdateien
- `required_paths`
- Registry-Eintraege
- Skripte
- interne Referenzen

Nach Abschluss der Migration duerfen keine ungueltigen Pfade oder Verweise auf
veraltete Speicherorte bestehen.

Nach jeder Archivierung ist automatisch ein Konsistenz-Audit durchzufuehren.
Mindestens zu pruefen sind:

1. keine veralteten Dateien mehr im aktiven Bereich;
2. alle Referenzen gueltig;
3. keine doppelten aktiven Versionen;
4. keine verwaisten Pfade;
5. keine Inkonsistenzen zwischen Manifesten und Dateisystem.

CADP 1.0 ist dauerhaft Bestandteil der Entwicklungs- und Governance-Regeln von
Projekt Kontinuum und bei jeder zukuenftigen Aenderung automatisch anzuwenden.


## Canonical Change Policy (CCP) 1.0

CCP 1.0 regelt den Lebenszyklus kanonischer Aenderungen. Keine kanonische
Datei darf dauerhaft direkt und unkontrolliert veraendert werden. Jede
kanonische Aenderung benoetigt erkennbare Aenderungsabsicht, Begruendung,
Audit-Kontext und Governance-Konformitaet.

Verbindlicher Ablauf:

```text
Change Proposal
  -> Pre-Audit
  -> Governance Review
  -> Controlled Canonical Update
  -> CADP Archive / Path Sync
  -> Documentation Sync
  -> Release Integrity Gate
  -> Canonical Acceptance
```

Pflichtinhalte eines Change Proposal:

- betroffene Datei
- Grund der Aenderung
- Ziel der Aenderung
- betroffene Architekturkomponente
- erwartete Auswirkungen
- notwendige Folgepruefungen

Pre-Audit prueft mindestens ungueltige Pfade, widerspruechliche
Architekturbegriffe, doppelte aktive kanonische Dateien, offene Legacy-
Verweise, CADP-1.0-Verletzungen und Foundation-Regelverletzungen.

Governance Review prueft Foundation-Kompatibilitaet, Vereinbarkeit mit dem
kanonischen Architekturmodell, Policy-Konformitaet, Drift-Risiko sowie
Auswirkungen auf Dokumentation und Manifeste.

Eine Aenderung gilt erst als kanonisch akzeptiert, wenn Pre-Audit, Governance
Review, kontrolliertes Update, CADP-/Pfadsync, Dokumentationssync,
Release-Integrity-Gate und Canonical Acceptance abgeschlossen oder begruendet
dokumentiert sind.
## Orchestrator- und Capability-Governance

Orchestrator Core, Capability Resolution Engine und CAIM-relevante
Capability-Definitionen gelten als governancepflichtige Architekturartefakte.

Verbindlich:

1. Orchestrator-Entscheidungen fuer Agentenketten, Schreiboperationen,
   externe Systeme, Review-Uebergaben oder CMM-/Learning-Handoffs muessen
   protokolliert werden.
2. Blockierte Schritte duerfen nicht stillschweigend durch Fallback-Agenten
   ersetzt werden.
3. Freigegebene Schritte muessen Capability, Agentenkandidat, Governance-
   Ergebnis, Review-Status und Zielablage ausweisen.
4. Read-only-Diagnosen duerfen keine produktiven Aenderungen ausloesen.
5. Neue oder geaenderte Capabilities duerfen bestehende CAIM-Definitionen nicht
   ohne Backup, Test und Review ueberschreiben.
6. Agenten sind Anbieter von Faehigkeiten; Steuerungslogik gehoert in Router,
   CRE, Governance und Orchestrator, nicht in einzelne Spezialagenten.

## Abschlussbedingung fuer Architekturaufgaben

Eine Architekturaufgabe darf erst abgeschlossen werden, wenn Implementierung,
kanonische Dokumente, Architekturdiagramme, aktive Referenzen, Git-Tracking und
Canonical Documentation Audit zusammen konsistent sind.

Pflichtpruefung vor Abschlussbericht:

1. Implementierung erfolgreich verifiziert.
2. Alle kanonischen Dokumente synchronisiert.
3. Architekturdiagramme in aktiven Dokumenten identisch.
4. Keine Legacy-Referenzen in aktiven Dokumenten.
5. Neue kanonische Dateien in Git versioniert.
6. Canonical Documentation Audit ohne Restspannungen erfolgreich.

Erst danach wird der Abschlussbericht ausgegeben.
