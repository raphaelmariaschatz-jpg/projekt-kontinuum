# FileAgent 1.0 Umsetzung 2026-06-30

## Ziel

FileAgent 1.0 ergaenzt Kontinuum 34.1 um kontrolliertes Lesen, Analysieren und
Lernen aus lokalen oder bereitgestellten Dateien. Der Agent arbeitet
diagnostisch/read-only und veraendert keine Quelldateien.

## Implementierte Komponenten

- `01_system/kontinuum/core/file_agent.py`: FileAgentService mit
  Datei-/Ordnererkennung, Pfadschutz, Format-Extraktion, Hashing,
  Duplikaterkennung, Review-Speicherung und Statusausgabe.
- `24_config/file_agent_1_0.json`: aktivierbare FileAgent-Policy mit
  erlaubten Wurzeln, Dateitypen, Groessenlimit und Review-Modus.
- `32_data/file_agent_sources/`: gespeicherte Datei-Quellennachweise.
- `32_data/file_agent_review/`: Review-Nachweise gelesener Dateien.
- `17_tests/test_file_agent_1_0.py`: deterministische Abnahmetests.

## Unterstuetzte Befehle

- `lies Datei <Pfad>`
- `lerne aus Datei <Pfad>`
- `analysiere Datei <Pfad>`
- `importiere PDF als Lernquelle <Pfad>`
- `lerne aus Ordner <Pfad>`
- `fileagentstatus`

## Unterstuetzte Formate

Mindestens abgedeckt:

- Text: `.txt`, `.md`, `.log`
- Struktur: `.json`, `.csv`, `.html`
- Dokumente: `.pdf`, `.docx`, `.xlsx`
- Code: `.py`, `.js`, `.css`, `.html`
- E-Books: `.epub`, `.azw`, `.azw3`, `.kfx`

Code-Dateien werden auf Sprache, Funktionen, Klassen und Kommentare
analysiert. CSV/XLSX liefern Spalten und Vorschauzeilen. DOCX/PDF/EPUB werden
soweit technisch moeglich extrahiert; AZW/AZW3/KFX nutzen begrenzte
Textstring-Extraktion.

## Sicherheit und Governance

Der FileAgent:

- liest nur freigegebene Projekt- und Importbereiche;
- startet keine Dateien;
- loescht und veraendert keine Dateien;
- begrenzt Dateien standardmaessig auf 400 MB;
- begrenzt Ordnerimporte auf 50 Dateien;
- importiert Ordner standardmaessig nicht rekursiv;
- verhindert Doppelimporte per SHA-256-Dateihash;
- protokolliert jeden Import append-only;
- schreibt nicht direkt in Memory;
- nimmt keine automatische kanonische Wissensuebernahme vor.

## GUI-Integration

Die GUI wurde erweitert um:

- Button `Datei öffnen`
- Button `Datei lernen`
- Button `Ordner lernen`
- Aktivitaetsmeldungen im Such-/Aktivitaetsfenster
- Drag-and-Drop von Dateien oder Ordnern ins Eingabefeld, sofern TkDND
  verfuegbar ist
- stabiler Button-Fallback, wenn Drag-and-Drop auf dem System nicht verfuegbar
  ist

Drag-and-Drop erzeugt nur FileAgent-Befehle im Eingabefeld. Pfadschutz,
Dateityppruefung, Groessenlimit und Governance-Regeln bleiben unveraendert
wirksam.

## Verifikation

Ergaenzte Tests pruefen:

- `lies Datei test.txt`
- `lerne aus Datei beispiel.md`
- `analysiere Datei beispiel.py`
- `importiere PDF als Lernquelle`
- `lerne aus Ordner 14_documents`
- `fileagentstatus`
- Duplikatimport derselben Datei
- nicht erlaubter Pfad
- unbekannter Dateityp
- GUI-Buttons und Drag-and-Drop-Hook


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
