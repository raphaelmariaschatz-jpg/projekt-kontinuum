# WebAgent 1.0 Umsetzung 2026-06-30

## Ziel

WebAgent 1.0 ergaenzt Kontinuum 34.1 um echte direkte URL-, HTML-Extraktions-
und kontrollierte Crawl-Faehigkeit. URL-haltige Nutzereingaben werden vor
lokaler Suche und vor externen Suchprovidern verarbeitet.

## Implementierte Komponenten

- `01_system/kontinuum/core/web_agent.py`: WebAgentService mit URL-Erkennung,
  HTTP-GET, HTML-/Text-Extraktion, Linkerkennung, Crawl-Modus, Speicherung,
  Statusausgabe und Fehlerlogging.
- `24_config/web_agent_1_0.json`: aktivierbare WebAgent-Policy im Modus
  `diagnostic_review_only`.
- `32_data/web_agent_sources/`: gespeicherte Webquellennachweise.
- `17_tests/test_web_agent_1_0.py`: deterministische Abnahmetests fuer die
  geforderten Beispielbefehle.

## Routing

Die Intent-Erkennung behandelt Eingaben mit `http`- oder `https`-URL als
Command. Der Prompt-Orchestrator uebergibt solche Eingaben direkt an den
WebAgent. Damit blockieren fehlende Brave-Keys, Semantic-Scholar-429-Fehler,
arXiv- oder DuckDuckGo-Probleme keine direkte URL-Verarbeitung.

Unterstuetzte Befehlsformen:

- `lerne auch hier: <URL>`
- `lies diese Webseite: <URL>`
- `nutze zum Lernen auch <URL>`
- `oeffne nacheinander alle Links auf folgender Webseite und lerne den Inhalt <URL>`
- `webagentstatus`

## Datenhaltung und Governance

Jeder Abruf speichert:

- URL
- HTTP-Status
- Titel
- Haupttext-Auszug
- erkannte Links
- Abrufzeitpunkt
- SHA-256-Content-Hash
- Kurz-Zusammenfassung
- Lernzusammenfassung
- Review-Pflicht

Die Uebergabe erfolgt in `32_data/internet_learning_queue`,
`32_data/internet_learning_review`, `32_data/web_agent_sources` und als
Quellenreferenz in der Tabelle `sources`. Direkte Memory-Schreibungen und
automatische kanonische Wissensuebernahme sind im Standardmodus gesperrt.

## Crawl-Grenzen

Der Crawl-Modus ist kontrolliert:

- `max_pages`: 20
- `max_depth`: 2
- gleiche Domain bevorzugt
- robots.txt wird soweit moeglich respektiert
- grosse/binaere Downloads sind ohne Freigabe blockiert
- keine Massenaufnahme

## Verifikation

Ergaenzte Tests pruefen:

- `lerne auch hier: https://www.python.org/`
- `nutze zum Lernen auch https://www.jetbrains.com/help/pycharm/getting-started.html`
- `oeffne nacheinander alle Links auf folgender Webseite und lerne den Inhalt https://docs.python.org/3/library/index.html`
- `webagentstatus`
- binomische Formeln nach vorherigem Mathematik-Lernstatus

Der Test nutzt kontrollierte HTML-Fixtures statt Live-Netzwerkzugriff, damit
Release-Tests reproduzierbar bleiben.
