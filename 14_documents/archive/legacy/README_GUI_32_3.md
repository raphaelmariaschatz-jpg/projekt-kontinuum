# Projekt Kontinuum 32.3 - Neue GUI

## Enthalten

```text
11_gui\desktop_gui_32_3.py
16_installation\START_GUI_32_3.bat
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
16_installation\START_GUI_32_3.bat
```

oder direkt:

```text
python 11_gui\desktop_gui_32_3.py
```

## Wichtig

Die GUI ist für Version 32.3 vorbereitet.
Sie versucht automatisch, `kontinuum.core.system.KontinuumSystem` zu laden.  
Falls das Backend noch fehlt, läuft sie im Fallback-Modus.
