# Canonical Media Learning Framework (CMLF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Konzept geprueft, situative Empfehlung kontrolliert aktiviert
Gueltig ab: 2026-07-16
Komponententyp: Canonical Learning Layer / Medien- und Vermittlungsrahmen
Runtime-Wirkung: read-only Medienkatalog und situative Empfehlung

## 1. Zweck

Das Canonical Media Learning Framework (CMLF) 1.0 definiert den kanonischen Rahmen, ueber welche Medien, Darstellungsformen und Lernmethoden Projekt Kontinuum Wissen und Kompetenzen vermitteln kann.

CMLF beschreibt nicht die Lerninhalte und bewertet keine Kompetenzen. Es beschreibt, welche Medienformen fuer Lernziele, Themen, Nutzerkontexte und kognitive Belastung geeignet sein koennen.

Grundsatz:

```text
CAICF definiert, welche Kompetenzen aufgebaut werden.
CMLF definiert, mit welchen Medien diese Kompetenzen vermittelt werden.
CCP-Cognitive definiert, wie K Eingaben verarbeitet und Antworten vorbereitet.
```

## 2. Bestandsanalyse

Projekt Kontinuum besitzt bereits mehrere Bausteine, die CMLF einordnen kann:

- CPVF definiert Vision, Mission und langfristige Orientierung.
- CIF definiert, was in Kontinuum als intelligente Verarbeitung gilt.
- CCP-Cognitive beschreibt den kanonischen Denk- und Verarbeitungsprozess.
- CAICF definiert den Kompetenzrahmen fuer verantwortungsvollen KI-Umgang.
- Learning Agent, CLG und Canonical Memory regeln kontrolliertes Lernen, Review und Speicherung.
- CRE, Execution Planner und Orchestrator Core sind als getrennte Faehigkeits-, Planungs- und Ausfuehrungsschichten vorbereitet.
- CVF ist im CMIBF fuer Computer Vision, visuelle Wahrnehmung, Interpretation und Bildverarbeitung reserviert.

CMLF ergaenzt diese Lage als Medien- und Vermittlungsrahmen. Es erzeugt keine Medien automatisch im Produktivbetrieb und fuehrt keine Runtime-Entscheidung aus.

## 3. Architektur-Einordnung

CMLF gehoert zum Canonical Learning Layer. Es beschreibt, wie Lerninhalte und Kompetenzziele mediengerecht vermittelt werden koennen.

Empfohlene Einordnung:

```text
Foundation Layer
        |
Governance Layer
        |
Canonical Layer
        |
Canonical Intelligence Framework (CIF)
        |
Canonical Cognitive Pipeline (CCP-Cognitive)
        |
Capability Resolution Engine (CRE)
        |
Execution Planner
        |
Orchestrator Core
        |
Canonical Learning Layer
        |
|-- CAICF
|-- CMLF
`-- Tutor / Education Components
        |
User
```

CMLF ersetzt keine dieser Komponenten. Es liefert Kriterien fuer spaetere, governancepflichtige Medienauswahl und Lernoutput-Gestaltung.

## 4. Beziehung zu CAICF und CCP

| Framework | Frage | Antwort |
| --- | --- | --- |
| CAICF | Welche Kompetenzen sollen Menschen entwickeln? | Kompetenzbereiche und Bewertungsdimensionen |
| CMLF | Welche Medien und Vermittlungsformen passen zu Lernziel, Thema und Nutzerkontext? | Medienbereiche, Kombinationsregeln und adaptive Auswahlkriterien |
| CCP-Cognitive | Wie verarbeitet K eine Eingabe? | Denk- und Prozessordnung bis zur Antwortvorbereitung |

Beziehung:

```text
CAICF -> Kompetenzziel
CCP-Cognitive -> Verarbeitung und Antwortplanung
CMLF -> mediengerechte Lernvermittlung
```

CMLF unterstuetzt die Ausgabephase der CCP, trifft aber keine freie Runtime-Entscheidung und erzeugt keine Medien ohne Freigabe.

## 5. Kanonische Medienbereiche

### 5.1 Text Learning

Text Learning nutzt erklaerende, strukturierende und verdichtende Sprache.

Beispiele:

- Erklaerungen
- Zusammenfassungen
- Schritt-fuer-Schritt-Anleitungen
- Fachtexte
- Dialoge
- Checklisten

Geeignet fuer:

- Begriffsverstaendnis
- Argumentation
- Nachschlagen
- genaue Anleitungen
- dokumentationspflichtige Lernpfade

Grenze: Text allein kann bei raeumlichen, prozessualen oder praktischen Themen unzureichend sein.

### 5.2 Visual Learning

Visual Learning nutzt sichtbare Strukturen, Beziehungen und Formen.

Beispiele:

- Diagramme
- Mindmaps
- Infografiken
- Tabellen
- Prozessgrafiken
- Architekturdiagramme
- Vergleichsmatrizen

Geeignet fuer:

- Beziehungen und Abhaengigkeiten
- Architektur- und Prozessverstaendnis
- Mustererkennung
- Uebersichten und mentale Modelle

Grenze: Visual Learning darf Erklaerung und Quellen nicht ersetzen. CVF kann spaeter fuer visuelle Wahrnehmung relevant sein, CMLF bleibt aber Vermittlungsrahmen.

### 5.3 Interactive Learning

Interactive Learning nutzt aktive Rueckfragen, Aufgaben und Experimente.

Beispiele:

- Fragen
- Quiz
- Aufgaben
- Simulationen
- Experimente
- Uebungen
- interaktive Schrittfolgen

Geeignet fuer:

- Verstaendnispruefung
- Wiederholung
- Transfer
- Problemlosen
- adaptive Lernpfade

Grenze: Interaktion darf nicht zu ungepruefter Bewertung oder automatischer Profilbildung fuehren.

### 5.4 Audio Learning

Audio Learning nutzt hoerbare Vermittlung und dialogische Wiederholung.

Beispiele:

- Sprachausgabe
- Hoerlektionen
- Dialogtraining
- Aussprache
- Zusammenfassungen zum Anhoeren

Geeignet fuer:

- Wiederholung unterwegs
- Sprach- und Aussprachetraining
- niedrigschwellige Erklaerung
- barrierearme Vermittlung

Grenze: Audio benoetigt oft begleitende Struktur, Quellen oder visuelle Orientierung.

### 5.5 Video Learning

Video Learning nutzt zeitbasierte visuelle und auditive Darstellung.

Beispiele:

- Lernvideos
- Demonstrationen
- Animationen
- Prozessdarstellungen
- Screencasts

Geeignet fuer:

- Ablaufe
- Bedienhandlungen
- Demonstrationen
- dynamische Prozesse
- komplexe Schrittfolgen

Grenze: Videoerzeugung im Produktivbetrieb ist in CMLF 1.0 nicht erlaubt.

### 5.6 Practical Learning

Practical Learning nutzt reale oder realitaetsnahe Anwendung.

Beispiele:

- Programmieraufgaben
- Laboruebungen
- Projekte
- Fallstudien
- Praxisaufgaben
- Diagnose- und Reparaturaufgaben

Geeignet fuer:

- Kompetenzaufbau durch Handeln
- Transfer in reale Situationen
- Fehlerlernen
- Projektarbeit

Grenze: Praktische Aufgaben benoetigen klare Sicherheits-, Datenschutz- und Governance-Grenzen.

### 5.7 Reflective Learning

Reflective Learning nutzt Rueckblick, Selbstpruefung und Transfer.

Beispiele:

- Selbstreflexion
- Lerntagebuch
- Wissenspruefung
- Transferaufgaben
- Feedback
- Fortschrittsrueckblick

Geeignet fuer:

- nachhaltiges Lernen
- Metakognition
- Fehlerverstaendnis
- Transfer in neue Kontexte
- Kompetenzbewusstsein

Grenze: Reflexion darf keine Bewusstseins- oder Persoenlichkeitsbehauptungen ueber K erzeugen und keine ungeprueften Nutzerprofile speichern.

## 6. Adaptive Medienauswahl

CMLF 1.0 definiert nur Kriterien fuer spaetere Medienempfehlungen, keine automatische Runtime-Auswahl.

Kriterien:

| Kriterium | Bedeutung | Beispiel |
| --- | --- | --- |
| Lernziel | Was soll erreicht werden? | Verstehen, Anwenden, Ueben, Reflektieren |
| Thema | Welche Struktur hat der Inhalt? | Begriff, Prozess, System, Handlung, Entscheidung |
| Kompetenzbereich | CAICF-Bezug | Engage, Create, Manage, Design AI |
| Komplexitaet | Kognitive Last | einfach, mittel, hoch |
| Nutzerpraeferenz | bekannte oder angefragte Darstellungsform | Text, Grafik, Quiz, Praxis |
| Evidenzbedarf | Nachvollziehbarkeit | Quellen, Schritte, Belege |
| Barrierefreiheit | Zugang und Nutzbarkeit | Audio, Textalternative, klare Struktur |
| Ueberforderung | Schutz vor zu vielen Medien | Reduktion, Schrittfolge, Pausen |

Adaptive Auswahlregeln:

1. Beginne mit dem einfachsten Medium, das das Lernziel sauber erfuellt.
2. Ergaenze ein zweites Medium nur, wenn es Verstaendnis, Transfer oder Sicherheit verbessert.
3. Nutze Visual Learning fuer Beziehungen, Strukturen und Prozesse.
4. Nutze Interactive Learning fuer Verstaendnispruefung und Uebung.
5. Nutze Practical Learning erst, wenn Voraussetzungen, Risiken und Ziel klar sind.
6. Nutze Reflective Learning nach komplexen oder fehleranfaelligen Lernschritten.
7. Reduziere Medienvielfalt bei erkennbarer Ueberforderung.
8. Bevorzuge nachvollziehbare Medien bei governance- oder sicherheitsrelevanten Themen.
9. Speicher keine dauerhaften Praeferenzen oder Lernprofile ohne separate Governance-Freigabe.

## 7. Schnittstellenuebersicht

| Schnittstelle | Zweck | Grenze |
| --- | --- | --- |
| Foundation Layer | Schutz von Identitaet, Leitprinzipien und Verantwortung | CMLF darf Foundation nicht ueberschreiben |
| Governance Layer | Freigabe, Review, Datenschutz und Risikobegrenzung | CMLF entscheidet nicht autonom |
| Canonical Architecture | CMIBF- und Framework-Registry-Einordnung | CMIBF bleibt normative Quelle |
| CPVF | langfristige Vision und Mission | CMLF operationalisiert CPVF nicht automatisch |
| CIF | Intelligenzdimensionen, insbesondere Perception und Learning | CMLF definiert Medien, nicht Intelligenz |
| CCP-Cognitive | Antwort- und Lernoutput-Vorbereitung | CMLF ersetzt die Pipeline nicht |
| CAICF | Kompetenzzielraum | CMLF vermittelt Kompetenzen, definiert sie aber nicht |
| CVF | visuelle Wahrnehmung und Bildverarbeitung | CVF analysiert visuelle Inhalte; CMLF waehlt Vermittlungsmedien |
| CRE | spaetere Faehigkeitsauswahl | CMLF fuehrt keine Capability-Aufloesung aus |
| Execution Planner | spaetere Planung von Lernschritten | CMLF erstellt keine Runtime-Plaene |
| Orchestrator Core | Ausfuehrung validierter Plaene | CMLF fuehrt nichts aus |
| Learning Agent | Proposal- und Lernpfad-Unterstuetzung | keine automatische Wissensuebernahme |
| Canonical Memory | Speicherung validierter Lernnachweise | kein direkter Memory Write |
| Tutor-Komponenten | adaptive Lernbegleitung | keine Tutor-Implementierung in CMLF 1.0 |
| Education Layer | didaktische Strukturierung | CMLF bleibt Medienrahmen |
| Meta-Reasoning | Pruefung von Annahmen und Alternativen | CMLF prueft nicht selbst |
| Reflection / CRL | Rueckblick und Entwicklungsreflexion | CMLF erzeugt keine Selbstzuschreibungen |
| Release Integrity | spaetere Freigabepruefung | keine Release-Aenderung durch CMLF 1.0 |
| Canonical Glossary | Begriffskanon | CMLF, CAICF, CCP und CVF muessen getrennt bleiben |
| Projektchronik | Entwicklungshistorie | Fortschreibung nur dokumentarisch |

## 8. Erweiterbarkeit

Spaetere Versionen koennen aufnehmen:

- Media Recommendation Policy
- Tutor Media Profile
- Accessibility Profile
- Cognitive Load Model
- Multimodal Learning Plans
- Evidence-aware Learning Outputs
- Media Effectiveness Review
- Nutzerpraeferenzmodell mit Datenschutz- und Review-Grenzen

Jede Erweiterung benoetigt eine eigene Governance-Freigabe.

## 9. Risiken und offene Fragen

| Risiko / Frage | Schutzmassnahme |
| --- | --- |
| Verwechslung mit CAICF | CAICF definiert Kompetenzen, CMLF Medien |
| Verwechslung mit CCP | CCP verarbeitet, CMLF strukturiert Lernoutput-Medien |
| Verwechslung mit CVF | CVF bleibt Computer Vision; CMLF ist Vermittlungsrahmen |
| Ueberkomplexe Medienauswahl | einfachstes geeignetes Medium zuerst |
| Medienueberladung | Ueberforderungsregel und stufenweiser Medienwechsel |
| Datenschutz bei Praeferenzen | keine dauerhafte Speicherung ohne separate Freigabe |
| Automatische Mediengenerierung | in CMLF 1.0 ausdruecklich nicht erlaubt |
| Barrierefreiheit | spaeteres Accessibility Profile erforderlich |
| Qualitaet von Medienempfehlungen | spaetere Wirksamkeitspruefung und Review |

Offene Fragen:

1. Welche Nutzerpraeferenzen duerfen spaeter gespeichert werden?
2. Welche Medienauswahl soll nur situativ und welche dauerhaft gelten?
3. Welche Accessibility-Regeln sollen verbindlich werden?
4. Wie wird Medienwirksamkeit gemessen, ohne Nutzer zu ueberwachen?
5. Welche Tutor-Komponenten benoetigen eigene Schnittstellenvertraege?

## 10. Empfehlung

Empfehlung: `GO` fuer kanonische Konzept- und Dokumentationsvorbereitung; `SPAETER` fuer technische Implementierung.

Begruendung:

- CMLF ergaenzt die Lernarchitektur sinnvoll.
- CMLF unterstuetzt CAICF, ohne es zu ersetzen.
- CMLF unterstuetzt die CCP-Ausgabephase, ohne Runtime-Entscheidungen zu treffen.
- CMLF beruecksichtigt unterschiedliche Lernstile und kognitive Belastung.
- CMLF bleibt langfristig erweiterbar.
- CMLF erzeugt in Version 1.0 keine Runtime-Komplexitaet.

## 11. Freigegebene Artefakte fuer diese Phase

```text
14_documents/CANONICAL_MEDIA_LEARNING_FRAMEWORK_1_0.md
14_documents/CMLF_IMPLEMENTATION_PLAN_1_0.md
24_config/canonical_media_learning_framework_1_0.json
24_config/cmlf_media_types_1_0.json
31_reports/cmlf_1_0_status_report.md
```

## 12. Nicht-Ziele von CMLF 1.0

- keine Runtime-Aenderungen
- keine Aenderungen an CRE, Execution Planner oder Orchestrator Core
- keine neue Agentenimplementierung
- keine Datenbankmigration
- keine automatische Mediengenerierung im Produktivbetrieb
- keine Refactorings bestehender Komponenten
- keine automatische Speicherung von Nutzerpraeferenzen
- keine Kompetenzdefinition ausserhalb CAICF

## 13. Kontrollierte technische Aktivierung

Die serielle Implementierungsfreigabe vom 2026-07-18 aktiviert die sicheren
Teile der Phasen 1 und 2.

Aktiviert sind:

- deklaratives Laden und Validieren der sieben Medienbereiche;
- read-only Medienkatalog;
- situative Empfehlung aus explizitem Lernziel, Themenstruktur, Komplexitaet,
  Accessibility, Ueberforderungsrisiko und Evidenzbedarf;
- hoechstens zwei empfohlene Medientypen;
- Reduktion auf ein Medium bei hoher Komplexitaet oder Ueberforderungsrisiko;
- stabile Empfehlungs-IDs;
- Registrierung und Statusausgabe in `KontinuumSystem`.

Nicht aktiviert sind Medienerzeugung, Nutzerprofil, dauerhafte Praeferenzen,
Kompetenzbewertung, Tutor-Automatik, Memory-Schreibung oder operative
Entscheidungsautoritaet.
