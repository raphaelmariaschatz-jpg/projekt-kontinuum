# HISTORISCH - Projektstatus Kontinuum 32.0

Dieser Stand ist nicht aktiv. Der kanonische Ist-Stand liegt in
`PROJEKTSTATUS_AKTUELL_32_4.md`.

Stand: 2026-06-16

## Aktiver Kern

Kontinuum 32.0 war der damalige aktive Stand. Die wichtigste Ergänzung war der
Suchanbieter-Router für robuste Recherche.

## Suchanbieter-Router

Aktive Provider-Reihenfolge:

```text
local_knowledge
notebook_knowledge
university_sources
arxiv
semantic_scholar
brave_search
duckduckgo_html
duckduckgo_lite
```

Eigenschaften:

- lokales Wissen und Notebook-Wissen werden vor Websuche berücksichtigt
- Universitätsquellen werden über eine eigene Suchstufe bevorzugt
- arXiv und Semantic Scholar sind als wissenschaftliche Spezialprovider
  eingebunden
- Brave Search ist API-fähig vorbereitet und wird ohne API-Key sauber
  übersprungen
- DuckDuckGo HTML und Lite bleiben als robuste Fallbacks aktiv
- alte Konfigurationen mit `provider` und `fallback_providers` bleiben
  kompatibel

## Direkte Befehle

```text
suchmaschinenstatus
recherchiere <Thema>
internetsuche <Begriff>
websuche <Begriff>
motivationserklärungsstatus
motivationserklärung identität
wichtige einflüsse identität
```


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
