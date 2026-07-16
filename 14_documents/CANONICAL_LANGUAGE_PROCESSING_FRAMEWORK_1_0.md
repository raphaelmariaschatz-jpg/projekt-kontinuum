# Canonical Language Processing Framework (CLPF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Konzept geprueft, Architekturbaustein empfohlen  
Gueltig ab: 2026-07-16  
Komponententyp: Canonical Language Architecture / Sprachverarbeitungsrahmen  
Runtime-Wirkung: keine

## 1. Zweck

Das Canonical Language Processing Framework (CLPF) 1.0 definiert den
kanonischen Rahmen fuer Sprachverarbeitung in Projekt Kontinuum. Es beschreibt
den Weg von Text-, Sprach-, Datei- oder strukturierten Eingaben bis zu einer
modellunabhaengigen semantischen Repraesentation, die anschliessend durch
CCP-Cognitive, CLU, CRE, Learning, Memory und Meta-Reasoning genutzt werden
kann.

Grundsatz:

```text
CLPF verarbeitet Sprache.
CCP verarbeitet Bedeutung im kognitiven Ablauf.
```

CLPF bindet Projekt Kontinuum nicht an ein bestimmtes Sprachmodell. Transformer
sind in Version 1.0 die wichtigste konzeptionelle Referenzarchitektur, aber
nicht die Definition des Frameworks.

## 2. Bestandsanalyse

Projekt Kontinuum besitzt bereits mehrere Anschlussstellen:

- CCP-Cognitive beschreibt die kognitive Verarbeitung von Bedeutung, Ziel,
  Kontext, Risiko, Planung, Antwort, Review, Lernen und Memory-Handoff.
- Der Architekturabschlussbericht 34.1 ordnet Transformer-basierte
  Tokenisierung und semantische Repraesentation bereits als Phase-2-Zielbild
  ein.
- CLU ist als vorgelagerte Sprach- und Bedeutungsverarbeitung dokumentiert,
  aber noch nicht als eigenes technisches Modul implementiert.
- CRE loest Capabilities read-only auf und darf keine Rohsprache interpretieren
  muessen.
- Execution Planner und Orchestrator Core setzen strukturierte, bereits
  verstandene Eingaben voraus.
- CHIF beschreibt, wie Ergebnisse an Menschen vermittelt werden; CLPF
  beschreibt dagegen die technische Sprachvorbereitung vor der kognitiven
  Verarbeitung.
- CMLF beschreibt Medien fuer Lernvermittlung; CLPF ist keine Medienauswahl.
- CVF bleibt fuer Computer Vision reserviert; CLPF ist Sprachverarbeitung.

Ergebnis: CLPF ist als eigenstaendiger kanonischer Rahmen sinnvoll, weil es die
sprachliche Vorverarbeitung stabil von CCP, CLU, CRE und Runtime-Ausfuehrung
trennt.

## 3. Architektur-Einordnung

Empfohlene Einordnung:

```text
User Input / Text / Voice / Files / Structured Data
        |
Canonical Language Processing Framework (CLPF)
        |
Canonical Semantic Representation
        |
Canonical Language Understanding (CLU)
        |
Canonical Cognitive Pipeline (CCP-Cognitive)
        |
Capability Resolution Engine (CRE)
        |
Execution Planner
        |
Orchestrator Core
```

CLPF liegt vor CLU und CCP-Cognitive. CLPF erzeugt eine stabile sprachliche und
semantische Repraesentation. CLU kann diese Repraesentation fuer Intent-,
Kontext- und Bedeutungsaufgaben nutzen. CCP-Cognitive ordnet diese Bedeutung in
den kontrollierten kognitiven Gesamtprozess ein.

## 4. Beziehung zu bestehenden Frameworks

| Framework / Komponente | Beziehung zu CLPF |
| --- | --- |
| Foundation Layer | schuetzt Identitaet, Prinzipien und Grenzen der Sprachverarbeitung |
| Governance Layer | regelt Modellwahl, Datenschutz, Risiko, Review und Freigaben |
| Canonical Architecture | ordnet CLPF als kanonisches Sprachverarbeitungsframework ein |
| CVF | bleibt Computer Vision; CLPF ist kein Bildverstehen |
| CIF | definiert Intelligenzdimensionen, CLPF liefert sprachliche Repraesentationen |
| CCP-Cognitive | verarbeitet Bedeutung; CLPF liefert die sprachliche Grundlage |
| CHIF | gestaltet Mensch-KI-Interaktion; CLPF verarbeitet Eingaben vor dem Dialogoutput |
| CAICF | kann Lernziele nutzen, aber CLPF bewertet keine Kompetenzen |
| CMLF | waehlt Medienformen; CLPF ist keine Medienvermittlung |
| CLU | nutzt CLPF-Ergebnisse fuer Intent, Kontext und Bedeutungsverstehen |
| CRE | nutzt strukturierte Bedeutungs- und Capability-Hinweise, nicht Rohsprache |
| Execution Planner | setzt bereits geklaerte Ziele und Capabilities voraus |
| Orchestrator Core | fuehrt validierte Plaene aus, keine Sprachverarbeitung |
| Canonical Memory | speichert nur freigegebene, validierte Kontexte; keine Rohdatenuebernahme |
| Learning Agent | kann Erkenntnisse aus validierten Repraesentationen ableiten |
| Meta-Reasoning | prueft Annahmen und Schlussfolgerungen auf Basis expliziter Repraesentationen |
| Release Integrity | prueft spaetere Artefakte und Freigaben |
| Canonical Glossary | definiert Begriffe wie Token, Embedding, Semantic Representation |

## 5. Kanonische Verarbeitungsschritte

### 5.1 CLPF-01 Input Acquisition

Zweck:

- Texteingaben erfassen
- Spracheingaben nach vorgelagerter Transkription aufnehmen
- Dateiinhalte strukturiert uebernehmen
- strukturierte Daten als Sprache-/Kontexttraeger erkennen

Grenze: CLPF definiert keine Mikrofon-, Audio-, GUI-, OCR- oder Dateiparser-
Implementierung.

### 5.2 CLPF-02 Normalization

Zweck:

- Unicode und Zeichensaetze normalisieren
- Sprache und Locale markieren
- Format vereinheitlichen
- Steuerzeichen, Satzgrenzen und Dokumentgrenzen kontrolliert erfassen

Grenze: Normalisierung darf Bedeutung nicht ungeprueft veraendern.

### 5.3 CLPF-03 Tokenization

Zweck:

- Eingaben in kanonische Tokenobjekte ueberfuehren
- Token-ID, Position, Sprache, Satzgrenzen, Dokumentgrenzen und Metadaten
  fuehren
- Subword-, BPE-, SentencePiece- und WordPiece-Tokenizer modellunabhaengig
  abbilden

Grenze: CLPF schreibt keinen konkreten Tokenizer vor.

### 5.4 CLPF-04 Embedding Preparation

Zweck:

- Token Embeddings vorbereiten
- Positionsinformationen einordnen
- Segment-, Satz- und Dokumentkontext verfuegbar machen
- Modellinput fuer austauschbare Sprachmodelle vorbereiten

Grenze: CLPF verwaltet keine Modellgewichte und trainiert keine Embeddings.

### 5.5 CLPF-05 Transformer Processing

Zweck:

- Transformer als austauschbare Verarbeitungsschicht konzeptionell einordnen
- Self Attention, Multi Head Attention, Feed Forward Layer,
  Layer Normalization und Residual Connections als moegliche Bestandteile
  beschreiben
- kontextuelle Repraesentationen erzeugbar machen

Grenze: keine Implementierung, kein Training, kein Fine-Tuning, keine GPU-
Optimierung und keine Modellgewichtverwaltung.

### 5.6 CLPF-06 Semantic Representation

Zweck:

- modellunabhaengige semantische Repraesentation erzeugen
- Sprache, Tokens, Kontext, Satz-/Dokumentstruktur, erkannte Entitaeten,
  Unsicherheiten und Provenienz sichtbar halten
- Uebergabe an CLU, CCP-Cognitive, CRE, Learning, Memory und Meta-Reasoning
  vorbereiten

Grenze: CLPF erzeugt eine Repraesentation; es trifft keine Governance-,
Capability-, Planungs- oder Ausfuehrungsentscheidung.

## 6. Kanonisches Token-Schema

Ein kanonisches Tokenobjekt ist sinnvoll, weil unterschiedliche Tokenizer
verschiedene Segmentierungslogiken verwenden. CLPF braucht daher eine
abstrakte Tokenstruktur, die konkrete Modelltoken abbilden kann, ohne das
Framework an BPE, SentencePiece, WordPiece oder eine Modellfamilie zu binden.

Mindestfelder:

- `token_id`: stabile ID innerhalb der Eingabe
- `surface`: sichtbare Tokenform oder normalisierte Form
- `tokenizer_type`: verwendete Tokenizer-Klasse
- `tokenizer_local_id`: modell- oder tokenizerinterne ID
- `position`: absolute und relative Position
- `language`: erkannte oder uebergebene Sprache
- `sentence_id`: Satzzuordnung
- `document_id`: Dokumentzuordnung
- `span`: Zeichenoffsets im Ursprung
- `metadata`: Quelle, Normalisierung, Unsicherheit und Provenienz

## 7. Rolle von Transformer-Modellen

Transformer sind in CLPF 1.0 eine austauschbare Referenzarchitektur fuer
kontextuelle Sprachrepraesentation. Sie duerfen nicht mit der gesamten
Kognition von K verwechselt werden.

Transformer leisten:

- Kontextbezug zwischen Tokens modellieren
- mehrdeutige Tokenbedeutungen kontextuell einordnen
- Repraesentationen fuer nachgelagerte semantische Verarbeitung erzeugen
- moderne Sprachmodellarchitekturen anschlussfaehig machen

Transformer leisten in CLPF 1.0 nicht:

- autonome Entscheidungen
- Governance
- Planung
- Orchestrierung
- Memory-Uebernahme
- Training oder Selbstoptimierung

## 8. Erweiterbarkeit

CLPF bleibt offen fuer:

- klassische regelbasierte Tokenisierung
- statistische NLP-Verfahren
- Transformer-Encoder
- Decoder-only-Modelle
- Encoder-Decoder-Modelle
- multimodale Sprach-Bild-Modelle, sofern CVF/CHIF-Grenzen beachtet werden
- zukuenftige Modellarchitekturen jenseits von Transformern

Erweiterungen muessen das kanonische Token- und Repraesentationsmodell
respektieren und duerfen Runtime-Integration nur nach separater
Governance-Freigabe einfuehren.

## 9. Risiken und offene Fragen

Risiken:

- Vermischung von CLPF mit CCP-Cognitive oder CLU.
- Transformer werden faelschlich als Denkarchitektur interpretiert.
- Tokenizer-spezifische Details sickern in kanonische Verträge ein.
- Rohdaten, Sprachdaten oder Dokumentinhalte werden ungeprueft gespeichert.
- Modellbias und Spracherkennungsfehler bleiben unsichtbar.
- Mehrsprachigkeit wird zu frueh technisch verengt.
- Datenschutz- und Governance-Pflichten werden bei Sprach-/Dateieingaben
  unterschaetzt.

Offene Fragen:

- Soll CLU spaeter als eigenes Framework oder als Nutzschicht ueber CLPF
  dokumentiert werden?
- Welche Felder der semantischen Repraesentation werden releasepflichtig?
- Wie werden Unsicherheit, Tokenizer-Version und Modellversion kanonisch
  dokumentiert?
- Welche Mindestanforderungen gelten fuer Mehrsprachigkeit?
- Wie wird Audio-Transkription zu CSIF abgegrenzt?
- Welche Datenschutzregeln gelten fuer Rohsprache und tokenisierte Inhalte?

## 10. Entscheidung

Empfehlung: `GO` fuer Konzept und kanonische Vorbereitung; `SPAETER` fuer
technische Implementierung.

Begruendung:

- CLPF trennt Sprachverarbeitung klar von kognitiver Verarbeitung.
- Transformer werden als austauschbare Implementierungsoption behandelt.
- Eine kanonische Tokenisierung ist definiert.
- Das Framework bleibt modellunabhaengig.
- CLPF ergaenzt CCP, CLU, CRE und CHIF ohne Vermischung.
- CLPF ist fuer zukuenftige Modellarchitekturen erweiterbar.

## 11. Kanonische Grenzen fuer Version 1.0

- kein Training eines Sprachmodells
- keine LLM-Integration
- keine Runtime-Migration
- keine GPU-Optimierung
- keine produktiven Komponenten
- keine Modellgewichte
- kein Fine-Tuning
- keine Aenderungen an CRE, Execution Planner oder Orchestrator Core
- keine automatische Memory-Schreibung

