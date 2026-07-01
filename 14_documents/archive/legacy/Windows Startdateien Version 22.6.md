# Windows-Startdateien – Projekt Kontinuum 22.6

Diese Vollversion enthält nun die passenden `.bat`-Dateien.

## Dateien

### START\_KONTINUUM\_22\_6.bat

Startet die GUI von Projekt Kontinuum 22.6.

### INSTALL\_REQUIREMENTS\_22\_6.bat

Installiert optionale Python-Abhängigkeiten aus `requirements.txt`.

### RESET\_LOGIN\_22\_6.bat

Setzt die lokale Login-Datei `data/users.json` zurück.
Danach gelten wieder:

* Benutzername: Raphael
* Passwort: kontinuum

### TEST\_KONTINUUM\_22\_6.bat

Startet die Basistests im Ordner `tests`.

Hinweis: Für die Tests muss `pytest` installiert sein.
Falls nicht vorhanden:

```bash
python -m pip install pytest
```

