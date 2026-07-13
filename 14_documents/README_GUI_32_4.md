# Projekt Kontinuum 32.4 - GUI

## Enthalten

```text
11_gui\desktop_gui_32_4.py
16_installation\START_GUI_32_4.bat
```

## Funktionen

- großes mehrzeiliges Eingabefeld
- Antwortfenster
- Such-/Aktivitätsfenster
- Agenten-/Modulübersicht
- Schnellbefehle
- Fallback-Betrieb, falls das Kontinuum-Backend noch nicht geladen ist

## Installation

Dateien nach `C:\Projekt Kontinuum` kopieren.

Danach starten:

```text
16_installation\START_GUI_32_4.bat
```

oder direkt:

```text
python 11_gui\desktop_gui_32_4.py
```

## Wichtig

Die GUI ist für Version 32.4 verifiziert und verwendet die zentrale
`APP_VERSION`. 32.4 ergänzt keine neue GUI-Funktion.
Sie versucht automatisch, `kontinuum.core.system.KontinuumSystem` zu laden.  
Falls das Backend noch fehlt, läuft sie im Fallback-Modus.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
