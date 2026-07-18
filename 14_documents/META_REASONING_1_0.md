# Meta-Reasoning 1.0 - Konzeptpruefung fuer Projekt Kontinuum

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Konzept geprueft, kontrollierte technische Aktivierung vorhanden
Gueltig ab: 2026-07-15
Komponententyp: Reasoning Review und Governance-Konzept
Runtime-Wirkung: expliziter Review-Service, keine automatische Live-Pruefung

## 1. Zweck

Meta-Reasoning 1.0 beschreibt einen schlanken kanonischen Architekturbaustein, mit dem K kuenftig nicht nur Antworten, Entscheidungen oder Schlussfolgerungen erzeugt, sondern auch die eigene Denk- und Entscheidungslogik pruefbar einordnet.

Meta-Reasoning bedeutet:

```text
K prueft nicht nur eine Aufgabe,
sondern auch den Weg zur eigenen Einschaetzung.
```

Ziel ist nicht Bewusstsein. Ziel ist bessere Selbstpruefung, Fehlererkennung, Begruendbarkeit, Unsicherheitsklarheit und Governance-Konformitaet.

## 2. Bestandsanalyse

Projekt Kontinuum besitzt bereits mehrere Strukturen, an die Meta-Reasoning anschliessen kann:

- Foundation Layer: schuetzt Identitaet, Leitprinzipien, moralische Grenzen und geschuetzte Entscheidungsregeln.
- Foundation Reasoning und Foundation Decision: bestehende Entscheidungs- und Begruendungsschichten im Foundation-Kontext.
- Query System: bereitet Wissens- und Antwortkontexte vor.
- Capability Resolution Engine (CRE): loest Anforderungen read-only in Faehigkeiten, Kandidaten, Governance-Hinweise, Review-Pflicht und CMM-Relevanz auf.
- Execution Planner: erstellt pruefbare Ausfuehrungsplaene, fuehrt aber nicht aus.
- Orchestrator Core: fuehrt ausschliesslich validierte Plaene aus und implementiert keine Review-Logik.
- CDF und CDG: beschreiben Entwicklungsphasen, Regeln, Abschlusspruefung und Governance-Grenzen.
- CAM, ALP und Release Integrity: pruefen Artefaktstatus, Lifecycle und Freigabefaehigkeit.
- Projektchronik, Statusreports und Review-Artefakte: liefern Nachweise fuer spaetere Pruefung und Rueckverfolgung.
- CRL 1.0: reflektiert langfristige dokumentierte Architektur- und Projektentwicklung, nicht einzelne Schlussfolgerungen im Moment ihrer Entstehung.

Ergebnis der Bestandsanalyse: Meta-Reasoning kann bestehende Strukturen ergaenzen, ohne CRE, Planner, Orchestrator, CRL oder Governance zu ersetzen.

## 3. Sinnhaftigkeitsbewertung

Meta-Reasoning 1.0 ist sinnvoll, wenn es als schlanke pruefende Schicht definiert wird.

Nutzen:

- Entscheidungen werden nachvollziehbarer.
- Unsichere Annahmen werden frueher sichtbar.
- Alternativen und verworfene Pfade koennen dokumentiert werden.
- Governance- und Foundation-Bezug wird expliziter.
- Revisionsbedarf kann vor Lernen, Memory oder Freigabe markiert werden.

Risiko bei falscher Einordnung:

- Meta-Reasoning koennte als Bewusstseins- oder Autonomiemodul missverstanden werden.
- Es koennte bestehende Review- oder Governance-Komponenten duplizieren.
- Es koennte unkontrollierte Komplexitaet erzeugen, wenn es zu frueh implementiert wird.

Bewertung: GO fuer kanonische Konzept- und Dokumentationsvorbereitung; SPAETER fuer technische Implementierung.

## 4. Minimale Aufgaben

Meta-Reasoning 1.0 sollte minimal folgende Aufgaben beschreiben:

### 4.1 Reasoning Review

- Bewertung der eigenen Schlussfolgerung.
- Erkennung schwacher, unvollstaendiger oder widerspruechlicher Begruendungen.
- Trennung von Ergebnis, Begruendung und offener Unsicherheit.

### 4.2 Assumption Tracking

- Sichtbarmachung getroffener Annahmen.
- Kennzeichnung unsicherer oder nicht belegter Annahmen.
- Verweis auf notwendige Nachpruefung.

### 4.3 Confidence Assessment

- Einstufung als `high`, `medium` oder `low`.
- Begruendung der Confidence-Einstufung.
- Kennzeichnung von Faktoren, die Confidence senken.

### 4.4 Alternative Path Review

- Pruefung, ob andere Loesungswege existieren.
- Dokumentation, warum ein Weg bevorzugt wurde.
- Kennzeichnung verworfener Alternativen mit kurzer Begruendung.

### 4.5 Governance Alignment

- Pruefung gegen Foundation, CDF, CDG, CAM, ALP und Release Integrity.
- Markierung von Governance-Blockern.
- Keine Entscheidung ausserhalb kanonischer Regeln.

### 4.6 Revision Trigger

- Erkennen, ob eine Antwort, Entscheidung oder Architekturannahme spaeter erneut geprueft werden sollte.
- Einstufung des Revisionsgrundes: Unsicherheit, fehlende Quelle, Regelkonflikt, offener Test, spaetere Architekturentscheidung.

## 5. Grenzen

Meta-Reasoning 1.0 ist kein autonomes Bewusstseinsmodul.

Nicht Ziel:

- keine Simulation von Bewusstsein
- keine emotionale Selbstdeutung
- keine Persoenlichkeitszuschreibung
- kein freies Denken
- keine unkontrollierte Selbstmodifikation
- keine Runtime-Migration
- keine Aenderung von Orchestrator-, Planner- oder CRE-Logik
- keine Aenderung aktiver Entscheidungswege
- keine automatische Selbstbewertung im Livebetrieb
- keine neue Agentenflut

Meta-Reasoning darf nur pruefen, markieren, begruenden und fuer Review vorbereiten.

## 6. Einordnung in eine spaetere CCP

Meta-Reasoning ist nicht identisch mit CRL.

- Meta-Reasoning prueft konkrete Schlussfolgerungen, Annahmen, Alternativen und Governance-Bezug im Moment einer Antwort, Entscheidung oder Planung.
- CRL prueft langfristige dokumentierte Entwicklungs- und Architekturmuster anhand Chronik, Roadmap, Reviews und Governance-Artefakten.

Vorgesehenes Zielbild fuer eine spaetere Canonical Cognitive Pipeline:

```text
Perception
-> Reasoning
-> Meta-Reasoning
-> Reflection (CRL)
-> Learning
-> Memory
```

Meta-Reasoning kann dabei als Pruefstufe zwischen Reasoning und Reflection dienen. Es erzeugt keinen eigenen Runtime-Pfad in Version 1.0.

## 7. Moegliche Artefakte

Empfohlene Artefakte:

```text
14_documents/META_REASONING_1_0.md
24_config/meta_reasoning_1_0.json
31_reports/meta_reasoning_1_0_status_report.md
```

Diese Artefakte bleiben Dokumentation und Konzeptmanifest. Sie sind keine Implementierung, kein Runtime-Schema und keine produktive Schnittstelle.

## 8. Schlankes JSON-Schema

Ein spaeteres Meta-Reasoning-Ergebnis koennte konzeptionell folgende Felder besitzen:

```json
{
  "review_id": "string",
  "target_type": "answer | decision | plan | architecture_assumption",
  "target_reference": "string",
  "reasoning_summary": "string",
  "assumptions": [],
  "uncertainties": [],
  "confidence": "high | medium | low",
  "alternatives_reviewed": [],
  "preferred_path_rationale": "string",
  "governance_alignment": {},
  "revision_trigger": {},
  "output_boundary": "review_only"
}
```

Dieses Schema ist nur ein Vorschlag. Es wird in Version 1.0 nicht als produktiver Runtime-Vertrag eingefuehrt.

## 9. Risiken und Schutzmassnahmen

| Risiko | Schutzmassnahme |
|---|---|
| Verwechslung mit Bewusstsein | Explizite Nicht-Ziele und Glossar-Abgrenzung |
| Duplikation von CRL | Meta-Reasoning fuer konkrete Schlussfolgerungen, CRL fuer langfristige Entwicklungsmuster |
| Duplikation von Governance | Meta-Reasoning markiert Governance-Bezug, entscheidet aber nicht selbst |
| Runtime-Komplexitaet | Version 1.0 bleibt Dokumentation und Konzeptmanifest |
| Scheinsicherheit durch Confidence | Confidence muss begruendet und mit Unsicherheiten verbunden werden |
| Selbstmodifikation | Ausdruecklich verboten ohne separaten Governance-Auftrag |

## 10. Empfehlung

Empfehlung: GO fuer Konzept und kanonische Vormerkung; SPAETER fuer Implementierung.

Begruendung:

- Meta-Reasoning macht K stabiler.
- Meta-Reasoning macht Entscheidungen nachvollziehbarer.
- Meta-Reasoning staerkt Governance und Review.
- Meta-Reasoning erkennt Fehler und Revisionsbedarf frueher.
- Meta-Reasoning ergaenzt bestehende Architektur ohne Runtime-Zwang.

## 11. Konkrete naechste Schritte

1. Meta-Reasoning 1.0 als kanonisches Konzeptdokument fuehren.
2. Glossar-Eintrag fuer `MR` / `Meta-Reasoning` aufnehmen.
3. In einer spaeteren CCP Meta-Reasoning als optionale Pruefstufe zwischen Reasoning und CRL vormerken.
4. Vor jeder Implementierung ein eigenes CMIBF-abgeleitetes Schnittstellen- und Validierungsmodell erstellen.
5. Keine Runtime-Integration ohne separate Freigabe, Tests, Review und Release Integrity.

## 12. Kontrollierte technische Aktivierung

Die serielle Implementierungsfreigabe vom 2026-07-18 aktiviert
Meta-Reasoning 1.0 als explizit aufrufbaren Review-Service.

Die Aktivierung umfasst:

- einen deterministischen Ergebnisvertrag fuer Antwort, Entscheidung, Plan und
  Architekturannahme;
- Reasoning Summary, Annahmen, Unsicherheiten, Confidence, Alternativen,
  Governance Alignment und Revision Trigger;
- einen reinen `assess`-Pfad ohne Persistenz;
- einen expliziten `review`-Pfad mit Audit-Ereignis;
- Registrierung und Statusausgabe in `KontinuumSystem`.

Die Aktivierung umfasst nicht:

- keine automatische Pruefung normaler Live-Antworten;
- keine Aenderung von CRE, Planner, Orchestrator oder Foundation;
- keine Entscheidungsautoritaet;
- keine direkte Memory-Schreibung;
- keine Selbstmodifikation.
