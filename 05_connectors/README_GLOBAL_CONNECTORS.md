# Globale öffentliche Connectoren

Diese Connectoren erschließen öffentliche Metadaten dynamisch über globale
Verzeichnisse und APIs. Kein Anbieter enthält nachweislich alle Universitäten,
Wissenschaftler, Publikationen, Vorträge oder öffentlichen Bibliotheken weltweit.

## Enthaltene Quellen

- ROR: Universitäten und Forschungsorganisationen
- OpenAlex: Wissenschaftler, Publikationen und Institutionen
- Crossref und DataCite: Publikationen, DOI-Metadaten und Forschungsoutputs
- Zenodo und Internet Archive: öffentliche Präsentationen, Vorträge und Medien
- Open Library und Library of Congress: Bücher und Bibliotheksbestände
- Wikidata: ergänzende verknüpfte offene Daten

## Verwendung

Python 3.10 oder neuer:

```powershell
$env:KONTINUUM_USER_AGENT='ProjektKontinuum/23.0 (kontakt@example.org)'
$env:OPENALEX_API_KEY='dein-kostenloser-openalex-schluessel'
$env:CROSSREF_MAILTO='kontakt@example.org'

python global_connectors.py universities "University of Heidelberg"
python global_connectors.py scientists "Albert Einstein"
python global_connectors.py publications "quantum gravity"
python global_connectors.py lectures "quantum physics lecture"
python global_connectors.py books "general relativity"
python global_connectors.py library-catalog "general relativity"
```

## Betriebsregeln

- Nur öffentliche Metadaten abfragen.
- API-Schlüssel ausschließlich als Umgebungsvariablen speichern.
- Ergebnisse zwischenspeichern und Anbieterlimits respektieren.
- Keine Massenabfragen über Such-APIs durchführen; dafür offizielle Daten-Dumps
  der Anbieter verwenden.
- Treffer vor wissenschaftlicher Nutzung anhand der Originalquelle prüfen.
