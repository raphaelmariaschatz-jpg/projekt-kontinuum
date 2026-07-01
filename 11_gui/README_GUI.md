# Projekt Kontinuum – produktive GUI

Aktive Version: **34.1**

Kanonischer Einstieg:

```text
11_gui/desktop_gui.py
```

Aktuelle Implementierung:

```text
11_gui/desktop_gui_34_1.py
```

Das kanonische Manifest ist `11_gui/gui_manifest.json`. Historische, weiterhin
ausführbare GUI-Versionen und ihre damaligen Manifeste liegen ausschließlich
unter `11_gui/archive/<version>/`.

Versionierte Kompatibilitätsstarter starten keine historischen GUIs. Sie leiten
auf `16_installation/START_GUI.bat` und damit auf den aktuellen kanonischen
Einstieg weiter.

Aktuelle 34.1-Oberfläche:

- Kopieren-Button im Antwortbereich
- Suchmodus-Dropdown `Automatisch`, `Lokal`, `Internet`, `Hybrid`
- Quellen-/Routinganzeige im Antworttext
- sichtbare Abschnitte für lokale Suche und Internet-Recherche
- Internet-Lernen-Status `Internet-Lernen: Aktiv` mit Quelle, Lernzeit, Funden
  und Bandbreitenlimit
- GUI-Schalter zum Aktivieren oder Deaktivieren von Internet-Learning ueber die
  Policy
