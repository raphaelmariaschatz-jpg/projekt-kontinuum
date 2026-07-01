# Projekt Kontinuum 34.1 – Versionsgebundener Wiedereinstieg

Stand: 2026-06-21

Aktiver Release ist 34.1 mit Release Integrity Framework 1.0.

```text
START_KONTINUUM.bat
16_installation\START_GUI_34_1.bat
16_installation\START_KONTINUUM_34_1.bat
16_installation\RELEASE_GATE_34_1.bat
16_installation\TEST_KONTINUUM_34_1.bat
13_tools\status_check_34_1.py
```

`START_KONTINUUM.bat` ist der kanonische CLI-Start im Projektstamm. Die Datei
setzt `PYTHONPATH` automatisch auf `C:\Projekt Kontinuum\01_system` und startet
Kontinuum ueber `python -m kontinuum`. Starts ueber `main.py` oder
`python -m 01_system.kontinuum` sind veraltet und nicht mehr kanonisch.

Kanonische Nachweise liegen unter `31_reports/release_integrity/34.1`; das
verifizierte Backup liegt unter `09_backups/release_integrity`. Ohne gültigen
Gate-Bericht ist die Freigabe technisch `NEIN`.
