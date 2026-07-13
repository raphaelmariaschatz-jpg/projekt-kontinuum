# Chemistry Agent 1.0 - Referenzintegration

## 1. Zweck

Chemistry Agent 1.0 ist der erste Spezialagent im Canonical Agent Ecosystem.
Er dient nicht als maximaler Chemie-Funktionsumfang, sondern als
Referenzimplementierung fuer den vollstaendigen Integrationsweg:

CAIM registriert Agent -> Router erkennt Capability -> Agent wird ausgewaehlt
-> Agent liefert Ergebnis -> CMM speichert neue Erkenntnisse -> Governance
protokolliert -> CAM verwaltet erzeugte Artefakte.

Wenn dieser Ablauf stabil funktioniert, koennen spaetere Spezialagenten nach
dem gleichen Muster integriert werden.

## 2. Leitprinzip

Chemistry Agent 1.0 bleibt bewusst klein, read-only und governancefaehig.

Er soll:

- Stoffnamen erkennen
- Summenformeln erklaeren
- CAS-Nummern strukturiert verwalten
- einfache Stoffeigenschaften aus vertrauenswuerdigen Quellen abbilden
- Sicherheitsdaten strukturiert zurueckgeben
- Ergebnisse mit Provenienz fuer CMM vorbereiten

Er soll nicht:

- externe Chemie-Datenbanken automatisch abfragen
- RDKit, OPSIN, DeepChem oder PubChem sofort anbinden
- Gefahrstoffbewertungen ohne Quellen- und Review-Kontext kanonisieren
- Tools unkontrolliert nutzen
- bestehende Research-, Web- oder Memory-Agenten ersetzen

## 3. CAIM-Registrierung

Der Chemistry Agent wird in CAIM als Spezialagent registriert.

Vorgeschlagener CAIM-Eintrag:

```json
{
  "id": "agent_chemistry",
  "name": "chemistry_agent",
  "type": "internal",
  "status": "active",
  "version": "1.0",
  "description": "Read-only Spezialagent fuer Stoffnamen, Summenformeln, CAS-Nummern, einfache Stoffeigenschaften und Sicherheitsfelder.",
  "capabilities": [
    "chemistry.lookup",
    "chemistry.formula",
    "chemistry.cas",
    "chemistry.properties",
    "chemistry.safety"
  ],
  "allowed_tools": [],
  "governance_required": true,
  "read_only": true,
  "entrypoint": "kontinuum.agents.chemistry_agent.ChemistryAgent"
}
```

In Version 1.0 bleiben `allowed_tools` leer. Externe Datenquellen oder lokale
Chemie-Toolkits werden erst in spaeteren Versionen nach Governance-Freigabe
angebunden.

## 4. Capability-Modell

Chemistry Agent 1.0 definiert folgende Kernfaehigkeiten:

- `chemistry.lookup`: erkennt einen Stoffnamen und liefert eine strukturierte
  Stoffkarte.
- `chemistry.formula`: erklaert oder normalisiert eine Summenformel.
- `chemistry.cas`: erkennt, speichert und validiert CAS-Nummern strukturell.
- `chemistry.properties`: liefert einfache Eigenschaften wie Aggregatzustand,
  molare Masse, Stoffklasse oder bekannte Synonyme, sofern vorhanden.
- `chemistry.safety`: liefert Sicherheitsfelder wie Gefahrenhinweise,
  Signalwort, Schutzmassnahmen und Review-Status.

Capabilities werden in CAIM gepflegt. Der Router soll ab Phase 5.1 nicht nur
nach Agentennamen, sondern primaer nach benoetigter Capability fragen.

## 5. Router- und PromptOrchestrator-Ablauf

Der geplante Ablauf fuer eine Anfrage lautet:

1. Nutzer fragt nach einem Stoff, einer CAS-Nummer oder einer Summenformel.
2. Request Router klassifiziert die Anfrage als Chemie-Anfrage.
3. Router fragt CAIM nach passenden Capabilities.
4. CAIM liefert aktive Kandidaten fuer `chemistry.lookup`,
   `chemistry.formula`, `chemistry.cas`, `chemistry.properties` oder
   `chemistry.safety`.
5. PromptOrchestrator waehlt den Chemistry Agent aus.
6. Chemistry Agent liefert ein read-only Ergebnis.
7. PromptOrchestrator uebergibt Ergebnis, Provenienz und Capability-Kontext an
   Governance und optional CMM.
8. CMM speichert nur freigegebene oder reviewpflichtig markierte Erkenntnisse.

## 6. Ergebnisformat

Chemistry Agent 1.0 soll ein strukturiertes Ergebnis liefern:

```json
{
  "agent": "chemistry_agent",
  "version": "1.0",
  "capability": "chemistry.lookup",
  "query": "Ethanol",
  "result": {
    "name": "Ethanol",
    "formula": "C2H6O",
    "cas": "64-17-5",
    "synonyms": ["Ethyl alcohol", "Alcohol"],
    "properties": {
      "substance_class": "alcohol",
      "molar_mass": "46.07 g/mol",
      "state": "liquid"
    },
    "safety": {
      "signal_word": "Danger",
      "hazards": ["flammable liquid"],
      "review_required": true
    }
  },
  "provenance": {
    "source_type": "local_reference_or_review",
    "source": "",
    "confidence": "review_required",
    "timestamp": ""
  },
  "read_only": true,
  "cmm_candidate": true
}
```

Die konkrete Ausgabe darf menschenlesbar formatiert werden, muss aber intern
eine strukturierte Form behalten.

## 7. CMM-Uebergabe

Chemistry Agent 1.0 schreibt nicht ungeprueft in den kanonischen Memory-Bestand.

Zulaessiger Ablauf:

- Agent erzeugt ein Ergebnis mit `cmm_candidate = true`.
- Ergebnis enthaelt Capability, Query, strukturierte Felder und Provenienz.
- CMM speichert nur, wenn die Governance-Regel dies erlaubt.
- Reviewpflichtige Erkenntnisse werden als reviewpflichtig markiert.
- Sicherheitsdaten werden nie ohne Review als endgueltige Wahrheit kanonisiert.

Moegliche CMM-Klassen:

- `knowledge`
- `agent_state`
- `governance`

## 8. Governance-Protokollierung

Jede Chemistry-Agent-Ausfuehrung muss mindestens protokollieren:

- Zeitstempel
- Agent-ID
- Capability
- Anfrage
- Ergebnisstatus
- read-only-Status
- CMM-Uebergabe ja/nein
- Review erforderlich ja/nein
- verwendete Quelle oder Quellenklasse
- Fehler oder Sicherheitsblockade

Governance-Pflicht ist fuer Chemistry Agent 1.0 aktiv, weil Chemie- und
Sicherheitsinformationen fachlich sensibel sind.

## 9. CAM-Artefakte

CAM verwaltet erzeugte oder relevante Artefakte fuer den Chemistry Agent.

Moegliche Artefakte:

- Agentendefinition
- Capability-Mapping
- Sicherheitsfeldschema
- Testfaelle
- Beispielausgaben
- Review-Nachweise

Artefakte werden nicht automatisch kanonisiert. Sie muessen versioniert,
nachvollziehbar und pruefbar bleiben.

## 10. Sicherheitsregeln

Chemistry Agent 1.0 folgt diesen Regeln:

- read-only by default
- keine automatische externe API-Nutzung
- keine automatische RDKit-, OPSIN-, DeepChem- oder PubChem-Ausfuehrung
- keine Gefahrstoffempfehlung ohne Review-Hinweis
- keine medizinische, toxikologische oder rechtliche Beratung
- keine Syntheseanleitungen fuer gefaehrliche Stoffe
- keine Umgehung von CAIM, CMM, CIM, CAM oder Foundation Governance
- keine Tool-Ausfuehrung ohne explizite spaetere Freigabe

## 11. Minimaler Funktionsumfang fuer Version 1.0

Version 1.0 gilt als erfolgreich, wenn der Agent:

- einfache Stoffnamen erkennt
- einfache Summenformeln erkennt oder erklaert
- CAS-Nummern strukturell erkennt
- eine Stoffkarte im definierten Ergebnisformat erzeugt
- Sicherheitsfelder strukturiert ausgibt
- CAIM-registriert ist
- ueber Capabilities auffindbar ist
- read-only bleibt
- Governance-Eintraege erzeugt
- CMM-Kandidaten erzeugt, ohne ungepruefte Kanonisierung
- Regressionstests fuer Routing, Ergebnisformat und Sicherheitsgrenzen besitzt

## 12. Nicht-Ziele fuer Version 1.0

Nicht Teil von Chemistry Agent 1.0:

- automatische PubChem-Abfrage
- RDKit-Strukturberechnung
- OPSIN-Namensauflösung
- DeepChem-Modelle
- automatische Gefahrstoffklassifikation ohne Quelle
- Syntheseplanung
- Laboranweisungen
- externe Agentenausfuehrung

Diese Funktionen koennen spaeter als Version 1.1 oder hoeher geplant werden,
wenn CAIM Capability Routing, Governance und Tool-Freigaben stabil sind.

## 13. Abschlusskriterien

Die Referenzintegration gilt als definiert, wenn:

- CAIM-Eintrag beschrieben ist
- Capabilities beschrieben sind
- Router- und PromptOrchestrator-Ablauf beschrieben ist
- Ergebnisformat beschrieben ist
- CMM-Uebergabe beschrieben ist
- Governance-Protokollierung beschrieben ist
- CAM-Artefakte beschrieben sind
- Sicherheitsregeln und Nicht-Ziele dokumentiert sind

Die technische Implementierung beginnt erst nach dieser Definition und soll
zuerst den Integrationsweg pruefen, nicht den Chemie-Funktionsumfang maximieren.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
