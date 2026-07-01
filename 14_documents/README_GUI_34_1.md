# Projekt Kontinuum 34.1 – GUI

Aktiver GUI-Einstieg:

```text
11_gui\desktop_gui.py
11_gui\desktop_gui_34_1.py
11_gui\gui_manifest.json
11_gui\README_GUI.md
16_installation\START_GUI.bat
16_installation\START_GUI_34_1.bat
```

Die GUI verwendet weiterhin `APP_VERSION` als zentrale Versionsquelle. Die
Release-Freigabe wird bewusst außerhalb des GUI-Prozesses durch
`RELEASE_GATE_34_1.bat` erzeugt und kryptografisch nachgewiesen.

Historische ausführbare GUIs und ihre Manifeste liegen ausschließlich unter
`11_gui\archive\<version>`. Alte versionierte GUI-Starter sind reine
Kompatibilitätsweiterleitungen auf `START_GUI.bat`.

## Aktuelle GUI-Funktionen

- Kopieren-Button: kopiert die aktuelle Antwort aus dem Antwortfenster in die
  Zwischenablage und meldet leere Ausgaben im Footer.
- Suchmodus-Dropdown: `Automatisch`, `Lokal`, `Internet` und `Hybrid` steuern
  das Routing der Antwortpipeline.
- Quellen-/Routinganzeige: Antworten enthalten einen `Quellen:`-Block mit
  lokaler Datenbank, Memory, Internet, Internetergebnissen und aktivem
  Suchmodus.
- Anzeige lokaler Suche: Hybrid- und lokale Antworten zeigen den Abschnitt
  `Lokale Suche:` mit Treffern aus dem lokalen Suchrouter.
- Anzeige Internet-Recherche: Internet- und Hybridmodus zeigen
  `Internet-Recherche` beziehungsweise eine klare Nichtverfügbarkeitsmeldung.
- Internet-Lernen-Status: die Seitenleiste zeigt Status, Modus, letzte Quelle,
  letzte Lernzeit, neue Funde und aktives 10-Prozent-Bandbreitenlimit.
- Anzeige Internet-Lernen: Queue-/Review-Funde werden nur als Status sichtbar;
  keine automatische Übernahme in Memory oder kanonisches Wissen.
- Standardanzeige beim Start: `Internet-Lernen: Aktiv`, sofern die Policy
  `enabled=true` ist.
- Der GUI-Schalter aktiviert oder deaktiviert Internet-Learning ueber die
  Policy; Queue, Review, Provenienzpflicht und Bandbreitenlimit bleiben
  unveraendert verbindlich.
- CCE Status: der Schnellbefehl `canonicalenginestatus` zeigt Event-Bus,
  letzte Events, Drift-Status, offene Governance-Hooks, blockierende Findings
  und die letzte Gate-Entscheidung. Die Anzeige ist diagnostisch und fuehrt
  keine automatische Kanonisierung aus.
