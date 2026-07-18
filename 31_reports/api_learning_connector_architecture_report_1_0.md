# API Learning Connector 1.0 - Langfristiger Architekturbericht

Stand: 2026-07-15
Status: Architekturbericht; Phase-2-Analyseprototyp kontrolliert aktiviert
Auftrag: 04 - Langfristiger Umsetzungsplan eines API Learning Connectors

## 1. Zweck

Dieser Bericht beschreibt eine langfristige Architekturvariante fuer einen API
Learning Connector in Projekt Kontinuum. Der Connector soll oeffentliche
API-Quellen strukturiert analysieren koennen, ohne ungepruefte Inhalte direkt
in die Wissensbasis, die Capability Registry, Runtime-Komponenten oder
ausfuehrbare Agentenpfade zu uebernehmen.

Der Bericht ist ein Konzept- und Planungsergebnis. Er erzeugt keine neue
Runtime, keine Agenten, keine APIs, keine Datenbankmigration, keine Registry-
Aenderung, keine Tests und keine produktive Wissensuebernahme.

## 2. Architekturposition

Der API Learning Connector passt nicht als direkter Runtime-Executor in die
Architektur, sondern als kontrollierter Lern- und Analysezulieferer innerhalb
des Learning Layer und an der Grenze zum Operational Layer.

Empfohlene Zielposition:

```text
Oeffentliche API-Quelle
        |
        v
API Learning Connector
        |
        v
Quarantaene / Rohdatennachweis
        |
        v
Strukturierte API-Analyse
        |
        v
Governance Validator / CKDE / CLG
        |
        v
Review Queue
        |
        v
Governance Review
        |
        v
Canonical Knowledge / optionale spaetere Capability-Kandidaten
```

Damit folgt der Connector der bestehenden Linie von Internet Learning,
Learning Agent und CLG: externe Quellen duerfen Evidence, Proposals und
Review-Material erzeugen, aber keine automatische kanonische Wissensuebernahme
und keine automatische Ausfuehrbarkeit.

## 3. Einordnung in bestehende Komponenten

### 3.1 CRE

Die Capability Resolution Engine bleibt eine read-only Empfehlungsschicht. Der
API Learning Connector darf CRE nicht mit Rohdaten oder ungeprueften API-
Operationen befuellen. Erst nach Governance-Freigabe duerfen aus analysierten
API-Strukturen optionale Capability-Kandidaten entstehen.

CRE wuerde spaeter nur freigegebene, kanonisch registrierte oder eindeutig als
Kandidat markierte Capability-Beschreibungen sehen:

- Capability-Zweck,
- erlaubte Operationen,
- Governance-Level,
- benoetigte Freigaben,
- erlaubte Agenten oder Tools,
- Ausfuehrungsgrenzen,
- Provenienzreferenz.

### 3.2 Execution Planner

Der Execution Planner darf keine Plaene aus ungeprueften API-Spezifikationen
erzeugen. Spaeter duerfte er nur freigegebene Capability-Vertraege in
validierte Ausfuehrungsplaene ueberfuehren. Ein analysierter OpenAPI-Endpunkt
ist daher kein Ausfuehrungsplan.

### 3.3 Orchestrator Core

Der Orchestrator Core fuehrt ausschliesslich freigegebene und validierte
Plaene aus. Er darf keine selbststaendige Architektur-, Capability- oder
Planungsentscheidung aus einem API-Dokument ableiten. Der API Learning
Connector darf den Orchestrator deshalb nicht direkt triggern.

### 3.4 Governance, Audit und CLG

Governance entscheidet ueber:

- Zulassung der Quelle,
- Einstufung der Quelle,
- Speicherung von Metadaten,
- Annahme, Ablehnung oder Konfliktmarkierung,
- spaetere Uebergabe an Knowledge Agent, Memory Agent oder Capability-Pfad.

Audit muss jeden Schritt nachvollziehbar machen:

- Quelle,
- Abrufzeitpunkt,
- Hash,
- Format,
- Parser-Ergebnis,
- Redaktionen,
- Validator-Entscheidung,
- Review-Status,
- Handoff-Ziel.

CLG bleibt der kontrollierte Lernpfad. Der Connector erzeugt nur Proposals
oder Evidence und nimmt keine produktive Uebernahme vor.

### 3.5 CAM

CAM klassifiziert und prueft spaeter die zugehoerigen Artefakte, Speicherorte,
Policies und Handoff-Grenzen. Der API Learning Connector darf CAM nicht als
Schreibpfad fuer generierte Architektur- oder Registry-Artefakte verwenden.

CAM-relevante Fragen waeren spaeter:

- Wo liegen Rohdatenquarantaene, Analyseergebnisse und Review-Nachweise?
- Welche Artefakte sind aktiv, welche nur Evidence?
- Welche Dateien duerfen nie in aktive Projektbereiche gelangen?
- Welche Handoffs sind release- oder governancepflichtig?

## 4. Kernaufgaben des API Learning Connectors

Der Connector soll langfristig folgende Aufgaben uebernehmen:

1. Oeffentliche und erlaubte API-Quellen kontrolliert aufnehmen.
2. Format und Quellentyp erkennen.
3. API-Schemata, Endpunkte, Operationen, Parameter, Antwortmodelle und
   Authentifizierungsanforderungen strukturiert extrahieren.
4. Tokens, Cookies, Zugangsdaten und private Daten erkennen und entfernen.
5. API-Strukturen als nicht-ausfuehrbare Analyseobjekte dokumentieren.
6. Potenzielle Wissensobjekte und Capability-Kandidaten markieren.
7. Governance-, Sicherheits-, Quellen- und Lizenzregeln anwenden.
8. Review- und Audit-Nachweise erzeugen.
9. Nach menschlicher Freigabe Handoffs an Knowledge-, Memory- oder Capability-
   Governance vorbereiten.

Nicht-Aufgaben:

- keine Ausfuehrung fremder Requests,
- kein Import fremder Tokens,
- kein automatisches Schreiben in Memory,
- kein automatisches Schreiben in Capability Registry,
- kein automatisches Erzeugen von Tools oder Agenten,
- keine Umgehung von CRE, Execution Planner, Orchestrator Core oder Governance.

## 5. Unterstuetzte Quellenarten

Langfristig geeignete Quellenarten:

- Postman Collections,
- Swagger / OpenAPI,
- WSDL / SOAP,
- GitHub-Beispiele,
- Herstellerdokumentationen,
- RFCs,
- technische Lernquellen wie MDN, IBM Developer oder Microsoft Learn.

Zulaessig sind nur oeffentliche, rechtlich erlaubte und governance-konforme
Quellen. Loginpflichtige, private, vertrauliche, unsichere oder lizenzrechtlich
unklare Quellen werden blockiert oder nur als manuelle Prueffrage erfasst.

## 6. Datenfluss

### 6.1 Zielablauf

```text
Source Admission
  -> Source Fetcher
  -> Raw Source Quarantine
  -> Format Detector
  -> Schema Parser
  -> API Structure Model
  -> Capability Extractor
  -> Governance Validator
  -> Review Queue
  -> Governance Review
  -> Canonical Knowledge Writer
  -> optional spaeter: Capability Governance
```

### 6.2 Handoff-Regeln

Der Datenfluss muss an jeder Grenze typisiert bleiben:

| Stufe | Inhalt | Status | Darf ausfuehren? | Darf kanonisch schreiben? |
| --- | --- | --- | --- | --- |
| Rohdaten | Originalquelle, Metadaten, Hash | Quarantaene | Nein | Nein |
| Analysierte API-Struktur | Endpunkte, Schemas, Parameter, Auth-Hinweise | Analyse | Nein | Nein |
| Validiertes Wissen | Gepruefte API-Beschreibung mit Provenienz | Review/Approved | Nein | Nur nach Governance |
| Ausfuehrbare Capability | Freigegebener Capability-Vertrag | Canonical/Runtime | Nur ueber EP/OC | Nur nach separater Freigabe |

Diese Trennung ist verbindlich. Kein Analyseergebnis darf durch blosses
Vorhandensein zu einer Capability werden.

## 7. Modulkonzept

### 7.1 Source Fetcher

Aufgabe:

- ruft erlaubte oeffentliche Quellen kontrolliert ab,
- erzwingt HTTPS und erlaubte Quellklassen,
- respektiert Rate Limits, robots.txt soweit anwendbar und Policy-Grenzen,
- speichert nur quarantainisierte Rohdaten oder minimale Metadaten nach Policy.

Grenzen:

- keine Authentifizierung mit fremden Tokens,
- keine Session-Uebernahme,
- keine Formularausfuehrung,
- keine mutierenden HTTP-Methoden.

### 7.2 Format Detector

Aufgabe:

- erkennt OpenAPI, Swagger, Postman Collection, WSDL, SOAP, Markdown, HTML,
  RFC-Text oder Codebeispiel,
- erstellt ein Format-Signal fuer den Parser,
- markiert unsichere oder unbekannte Formate fuer manuelle Pruefung.

### 7.3 Schema Parser

Aufgabe:

- extrahiert nicht-ausfuehrbare Strukturinformationen,
- normalisiert Operationen, Pfade, Parameter, Request/Response-Modelle,
  Statuscodes, Fehlerfaelle und Authentifizierungsmodelle,
- erzeugt ein API Structure Model.

Grenzen:

- keine Requests gegen Ziel-APIs,
- kein Ausfuehren von Beispielcode,
- keine Interpretation von Credentials als nutzbare Geheimnisse.

### 7.4 Capability Extractor

Aufgabe:

- identifiziert moegliche technische Faehigkeiten,
- unterscheidet Lese-, Schreib-, Mutations-, Admin- und Risikooperationen,
- erzeugt nur Capability-Kandidaten.

Grenzen:

- keine Registry-Aenderung,
- keine Tool-Erzeugung,
- keine automatische CRE-Anbindung.

### 7.5 Governance Validator

Aufgabe:

- prueft Quelle, Lizenz, Provenienz, Sicherheitsgrenzen, Sensibilitaet,
  Konflikte, Confidence und Review-Pflicht,
- klassifiziert Ergebnisse als `REJECT`, `REVIEW`, `CONFLICT` oder
  `APPROVAL_CANDIDATE`.

Wichtig: Auch ein positiver Validator-Befund bedeutet noch keine kanonische
Uebernahme.

### 7.6 Canonical Knowledge Writer

Aufgabe:

- schreibt erst nach Freigabe strukturierte Knowledge-Handoffs,
- referenziert Quelle, Analyse, Review und Governance-Entscheid,
- trennt Wissensuebernahme von Capability-Uebernahme.

Grenzen:

- kein Direktzugriff auf Memory,
- kein Schreiben in Capability Registry,
- kein Schreiben in Runtime-Konfiguration.

### 7.7 Audit Reporter

Aufgabe:

- erzeugt append-only Audit-Nachweise,
- dokumentiert Source-ID, Parser-ID, Policy-Version, Redaktionen,
  Entscheidungen, Reviewer und Handoffs,
- unterstuetzt spaetere Release- und Governance-Pruefungen.

## 8. Moegliche Datenmodelle

Die folgenden Modelle sind konzeptionell und nicht implementiert.

### 8.1 Source Record

| Feld | Bedeutung |
| --- | --- |
| `source_id` | stabile Quellen-ID |
| `source_url` | oeffentliche Fundstelle |
| `source_type` | OpenAPI, Postman, WSDL, RFC, Doku, Beispiel |
| `retrieved_at` | Abrufzeitpunkt |
| `content_hash` | Hash des quarantainisierten Inhalts |
| `license_signal` | erkannte Lizenz- oder Nutzungsinformation |
| `public_access` | oeffentlich / unklar / blockiert |
| `quarantine_status` | quarantined, rejected, expired |

### 8.2 API Structure Record

| Feld | Bedeutung |
| --- | --- |
| `api_structure_id` | Analyse-ID |
| `source_id` | Referenz auf Source Record |
| `format` | erkannter Spezifikationstyp |
| `service_name` | API- oder Produktname |
| `operations` | nicht-ausfuehrbare Operationsliste |
| `schemas` | Datenmodelle und Typen |
| `auth_schemes` | erkannte Authentifizierungsarten, redacted |
| `risk_flags` | Mutation, Admin, personenbezogene Daten, Payment, etc. |

### 8.3 Knowledge Proposal

| Feld | Bedeutung |
| --- | --- |
| `proposal_id` | CLG-kompatible Proposal-ID |
| `api_structure_id` | Analysebezug |
| `knowledge_claims` | vorgeschlagene Wissensaussagen |
| `confidence` | vorlaeufige Vertrauensbewertung |
| `provenance` | Quelle, Hash, Zeit, Parser, Reviewer |
| `decision_state` | pending, under_review, approved, rejected, conflict |

### 8.4 Capability Candidate

| Feld | Bedeutung |
| --- | --- |
| `candidate_id` | Kandidaten-ID |
| `proposal_id` | Wissens- oder Analysebezug |
| `capability_name` | vorgeschlagene Faehigkeit |
| `allowed_methods` | erlaubte Methoden nach Governance, nicht aus Quelle allein |
| `blocked_methods` | riskante oder verbotene Methoden |
| `governance_level` | required, human_approval, blocked |
| `execution_policy` | spaeterer Vertrag fuer EP/OC, falls freigegeben |

## 9. Sicherheitsregeln

Verbindliche Sicherheitsregeln fuer jede spaetere Umsetzung:

- keine ungepruefte Ausfuehrung fremder Requests,
- keine automatische Speicherung sensibler Daten,
- keine Uebernahme von Tokens, Cookies, API Keys, OAuth-Daten oder
  Zugangsdaten,
- nur oeffentliche, erlaubte Quellen,
- Rohdaten bleiben in Quarantaene,
- keine mutierenden HTTP-Methoden aus Lernquellen,
- keine automatische Tool- oder Agentenerzeugung,
- keine direkte Memory- oder Registry-Schreibung,
- keine Verarbeitung loginpflichtiger oder privater Quellen ohne separate
  Governance-Entscheidung,
- Redaction vor jeder Review- oder Knowledge-Uebergabe,
- Auditpflicht fuer Fetch, Parse, Redaction, Validation und Handoff.

## 10. Risiken

Wesentliche Risiken:

- API-Spezifikationen koennen veraltet, falsch oder unvollstaendig sein.
- GitHub-Beispiele koennen unsichere Patterns, Testtokens oder veraltete
  Endpunkte enthalten.
- Herstellerdokumentationen koennen kommerzielle, lizenzrechtliche oder
  versionsspezifische Grenzen haben.
- Authentifizierungsbeispiele koennen versehentlich echte Secrets enthalten.
- Eine zu fruehe Capability-Ableitung koennte fremde API-Handlungen als
  scheinbar interne Faehigkeit erscheinen lassen.
- Parserfehler koennen riskante Operationen falsch klassifizieren.
- SOAP/WSDL und OpenAPI unterscheiden sich stark in Semantik und
  Sicherheitsmodell.
- Automatische Request-Tests wuerden eine klare Grenze zwischen Lernen und
  Ausfuehrung verletzen.

## 11. Offene Fragen

Vor jeder Implementierung muessen mindestens diese Fragen entschieden werden:

1. Welche Quellenklassen sind fuer API Learning exakt erlaubt?
2. Wie lange duerfen Rohdaten in Quarantaene liegen?
3. Welche Speicherorte gelten fuer Rohdaten, Analyse, Review und Audit?
4. Welche Lizenz- und Nutzungsinformationen muessen maschinenlesbar erfasst
   werden?
5. Wann darf aus einem API Structure Record ein Knowledge Proposal werden?
6. Wann darf aus einem Knowledge Proposal ein Capability Candidate werden?
7. Welche Governance-Stufe ist fuer mutierende API-Operationen erforderlich?
8. Welche Rolle hat eine spaetere Canonical API Registry gegenueber externen
   API-Spezifikationen?
9. Wie werden API-Versionen, Deprecations und Breaking Changes verwaltet?
10. Wie wird verhindert, dass Beispielcode oder Postman-Skripte ausgefuehrt
    werden?

## 12. Notwendige Vorbedingungen

Eine technische Umsetzung sollte erst beginnen, wenn folgende Vorbedingungen
erfuellt sind:

- CMIBF-Abdeckung fuer API Learning Connector oder ein abgeleitetes Framework,
- klare Policy fuer API-Quellen, Quarantaene, Redaction und Handoff,
- definierte Speicherorte und CAM-Klassifikation,
- CLG-kompatibles Proposal-Modell,
- CKDE- oder Governance-Validator fuer API-Wissen,
- Audit-Schema fuer Fetch, Parse, Validation und Review,
- definierte Grenze zur Canonical API Registry,
- definierte Grenze zu CRE, Execution Planner und Orchestrator Core,
- Sicherheitsmodell fuer Secrets, Cookies, Tokens und mutierende Operationen,
- Tests erst nach freigegebener Architekturdefinition.

## 13. Langfristiger Umsetzungsplan

### Phase 0 - Architekturfreigabe

Ergebnis:

- Entscheidung, ob API Learning Connector als eigener Baustein oder als Teil
  eines groesseren Learning-/Integration-Frameworks gefuehrt wird.
- CMIBF-Referenz oder CMIBF-Erweiterung.
- Keine Implementierung.

### Phase 1 - Policy und Datenmodell

Ergebnis:

- API Learning Policy,
- Quarantaene- und Redaction-Regeln,
- Source Record, API Structure Record, Knowledge Proposal und Capability
  Candidate als Konzept oder Schema,
- CAM-Klassifikation.

### Phase 2 - Read-only Analyse-Prototyp

Ergebnis:

- Parser nur fuer lokale, bereitgestellte Testdateien,
- keine Netzabrufe,
- keine Request-Ausfuehrung,
- keine Registry-Schreibung,
- Audit-only.

### Phase 3 - Kontrollierter Source Fetcher

Ergebnis:

- erlaubte oeffentliche Quellen,
- harte Bandbreiten- und Quellgrenzen,
- Quarantaene,
- Redaction,
- Review-Handoff.

### Phase 4 - Governance Validator und CLG-Handoff

Ergebnis:

- Knowledge Proposals,
- Review Queue,
- CKDE-/CLG-Kompatibilitaet,
- Audit Reporter.

### Phase 5 - Optionaler Capability Candidate Path

Ergebnis:

- Capability-Kandidaten ohne Ausfuehrbarkeit,
- menschliche Freigabe,
- separate Registry- und CRE-Governance,
- keine automatische Runtime-Aktivierung.

### Phase 6 - Runtime-Anbindung nur nach separater Freigabe

Ergebnis:

- CRE sieht nur freigegebene Capability-Vertraege,
- Execution Planner plant nur validierte Schritte,
- Orchestrator Core fuehrt nur freigegebene Plaene aus,
- Release Integrity und Governance Gates pruefen den gesamten Pfad.

## 14. Empfehlung

Empfehlung: `GO` fuer Architekturvorbereitung, `NO-GO` fuer sofortige
Implementierung.

Der API Learning Connector ist architektonisch sinnvoll, weil er die bestehende
Learning- und Governance-Linie auf API-Wissen erweitert. Er darf aber erst
technisch umgesetzt werden, wenn die CMIBF-Abdeckung, Policy, Datenmodelle,
Quarantaene, Redaction, Governance-Handoffs und Grenzen zu CRE, Execution
Planner, Orchestrator Core, CAM, CLG und CKDE eindeutig definiert sind.

Empfohlener Zeitpunkt:

- nach Stabilisierung der Canonical Cognitive / Learning Architecture,
- nach verbindlicher Definition der API-Learning-Policy,
- nach Festlegung einer Canonical API Registry-Grenze,
- vor produktiver externer API-Automation,
- aber nach erfolgreicher Governance-Freigabe der reinen Analyse- und
  Quarantaenearchitektur.

## 15. Abschlussbewertung

| Bereich | Bewertung |
| --- | --- |
| Architekturpassung | sehr hoch |
| Governance-Kompatibilitaet | hoch, wenn Review-Pflicht erhalten bleibt |
| Sicherheitsbedarf | sehr hoch |
| Umsetzungsreife | noch nicht gegeben |
| Langfristiger Nutzen | hoch |
| Sofortige Implementierung | nicht empfohlen |

Der API Learning Connector sollte als langfristiger, streng governance-
gebundener Lern- und Analysebaustein vorgemerkt werden. Er ist kein Executor,
kein automatischer API-Client und kein direkter Capability-Schreiber. Seine
Staerke liegt in kontrollierter Strukturgewinnung, Provenienz, Review und
spaeterer kanonischer Wissensvorbereitung.

## 16. Kontrollierte Phase-2-Aktivierung vom 2026-07-18

Die serielle Implementierungsfreigabe aktiviert ausschliesslich den in Phase 2
vorgesehenen read-only Analyseprototyp.

Aktiviert sind:

- Analyse lokal bereitgestellter Inhalte im Arbeitsspeicher;
- explizite Public-Source-Zulassung;
- Groessenlimit und Sperre fuer Credential-tragende Quellenreferenzen;
- Formatdetektion fuer OpenAPI/Swagger JSON, Postman JSON, WSDL/XML, RFC,
  Markdown und generische Dokumente;
- Sperre fuer DTD- und Entity-Deklarationen;
- Redaction von Secret-aehnlichen JSON-Feldern;
- nicht ausfuehrbare Source-, Structure- und Capability-Candidate-Vertraege;
- Risikoerkennung fuer mutierende Operationen;
- Registrierung und Statusausgabe in `KontinuumSystem`.

Nicht aktiviert sind:

- kein Source Fetcher und kein Netzwerkzugriff;
- keine Ausfuehrung von Requests oder Beispielcode;
- keine Rohdatenpersistenz;
- kein Knowledge-, Memory- oder Registry-Write;
- kein Handoff an CRE, Planner oder Orchestrator;
- keine automatische kanonische Uebernahme.

Damit ist Phase 2 technisch aktiv. Phasen 3 bis 6 bleiben gesperrt und
benoetigen weiterhin eigene Policies, Governance-Freigaben und Tests.
