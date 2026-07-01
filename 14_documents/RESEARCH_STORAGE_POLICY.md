# Recherche-Speicherrichtlinie

Stand: 2026-06-10

Kontinuum darf Recherche-Inhalte während einer Anfrage vorübergehend verarbeiten,
aber nicht dauerhaft als Volltext speichern.

Dauerhaft gespeichert werden dürfen nur Fundstellen und minimale Metadaten:

- URL oder persistente Kennung wie DOI
- Titel
- Abrufstatus
- Zeitstempel
- Anbieter oder Quellentyp

Nicht dauerhaft gespeichert werden:

- Webseiten-Volltexte
- umfangreiche Textauszüge
- vollständige Publikationen oder Vorträge

Die aktive Laufzeit erzwingt diese Regel: `research.web`-Inhalte werden vom
Speicher abgelehnt; Recherche-Fundstellen werden in der Tabelle `sources`
gespeichert.
