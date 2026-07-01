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
