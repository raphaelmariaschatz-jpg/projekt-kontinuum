# Phase 5 - Canonical Agent Ecosystem

## 1. Zielbild

Phase 5 baut das kanonische Agenten-Oekosystem von Projekt Kontinuum auf.
Die vorhandenen Foundation-Bausteine CAM, CIM, CMM und CAIM werden genutzt,
um spezialisierte Agenten systematisch, sicher und nachvollziehbar in
Kontinuum zu integrieren.

Das Ziel ist nicht, moeglichst viele Agenten parallel auszufuehren. Ziel ist
eine klare, governancefaehige Agenten- und Capability-Ordnung:

- Agenten sind kanonisch registriert.
- Faehigkeiten sind explizit beschrieben.
- Routingentscheidungen koennen ueber Capabilities begruendet werden.
- Tool-Nutzung bleibt kontrolliert.
- Ergebnisse werden mit Provenienz und Review-Pfad in CMM oder passenden
  Review-Speichern abgelegt.
- Externe Agenten werden in Phase 5.0 nicht automatisch ausgefuehrt.
- Agenten gelten als Anbieter von Capabilities, nicht als primaere
  Steuerungseinheit.
- Orchestrator Core 1.0 wird als naechster Steuerungsbaustein vorbereitet.

Phase 5 ist damit die Bruecke zwischen den Foundation-Schichten und den ersten
Spezialagenten.

## 2. Beteiligte Foundation-Bausteine

Phase 5 nutzt vier kanonische Kernbausteine:

- CAM: Canonical Architecture Manager als Architektur- und Strukturinstanz.
- CIM: Canonical Identity Manager als Identitaets-, Rollen- und
  Berechtigungsgrundlage.
- CMM: Canonical Memory Manager als kanonischer Speicher fuer gepruefte
  Erinnerungen, Ergebnisse und Agentenwissen.
- CAIM: Canonical Agent Integration Manager als zentrale Agentenregistrierung.

Ergaenzend bleiben Foundation Decision, Foundation Integrity, Request Router,
PromptOrchestrator, Capability Resolution Engine, FileAgent, WebAgent,
CodeAgent und Governance-Logs Teil der operativen Sicherheits- und
Nachvollziehbarkeitsschicht.

## 3. Rolle von CAIM

CAIM ist in Phase 5 die Single Source of Truth fuer Agentenregistrierung.

CAIM verwaltet:

- Agenten-ID und Agentenname
- Agententyp
- Status
- Version
- Beschreibung
- Capabilities
- erlaubte Tools
- Governance-Pflicht
- Read-only-Markierung
- EntryPoint
- Integritaetsstatus

CAIM fuehrt keine externen Agenten automatisch aus. Der Manager beantwortet
zunaechst read-only Fragen wie:

- Welcher Agent besitzt eine Capability?
- Ist der Agent aktiv?
- Ist Governance erforderlich?
- Darf der Agent prinzipiell ausgefuehrt werden?
- Welche Tools sind fuer diesen Agenten erlaubt?

Damit wird CAIM zur kanonischen Kontrollinstanz vor Agentenrouting,
Tool-Nutzung und Spezialagenten-Ausbau.

## 4. Rolle von Router, CRE und PromptOrchestrator

Der Request Router klassifiziert Nutzeranfragen und erkennt, ob eine Anfrage
eine Capability benoetigt. Die Capability Resolution Engine loest die
Capability read-only auf, fragt CAIM nach moeglichen Agenten, priorisiert
Kandidaten und markiert Governance-, Review- und CMM-Relevanz.

Der PromptOrchestrator bleibt die heutige Ausfuehrungs- und Antwortschicht,
die Routingentscheidungen mit Systemzustand, Foundation-Kontext und Governance
verbindet. Orchestrator Core 1.0 ist die geplante Weiterentwicklung dieser
Schicht: Er soll regelgebunden planen, nicht willkuerlich Agenten auswaehlen.

In Phase 5.0 bleibt das Routing konservativ:

- bestehende Agentenpfade werden nicht gebrochen
- neue Capability-Auskunft wird vorbereitet
- riskante automatische Agentenketten werden nicht aktiviert
- CAIM wird als Registry- und Auskunftsschicht genutzt

Ab Phase 5.1 soll der Router Capabilities wie `file.read`, `code.inspect`,
`memory.write`, `research.web` oder `chemistry.safety` explizit aufloesen
koennen, bevor ein Agent ausgewaehlt wird.

Ab Phase 5.2 soll Orchestrator Core 1.0 CRE-Empfehlungen, Prioritaeten,
Governance-Entscheidungen, Agentenkoordination, Review und CMM-Handoffs zu einem
nachvollziehbaren Ausfuehrungsplan verbinden.

## 5. Agent-Capability-Modell

Capabilities beschreiben konkrete Faehigkeiten. Sie sind nicht dauerhaft an
einen Agentennamen gebunden. Ein Agent bietet eine oder mehrere Capabilities
an; eine Capability kann mehrere Anbieter haben. Die Steuerung erfolgt
perspektivisch ueber Capability, Prioritaet und Governance, nicht ueber einen
hart codierten Agentennamen.

Beispiele:

- `chemistry.lookup`
- `chemistry.structure`
- `chemistry.safety`
- `research.web`
- `memory.write`
- `file.read`
- `code.inspect`

Capability-Regeln:

- Capabilities muessen eindeutig benannt sein.
- Capabilities werden in CAIM registriert.
- Ein Agent kann mehrere Capabilities besitzen.
- Eine Capability kann mehrere Kandidaten haben, aber nur aktive Agenten sind
  routingfaehig.
- Orchestrator und CRE duerfen Capabilities priorisieren, muessen aber
  CAIM-Status, Governance, Read-only-Markierung und Freigaben respektieren.
- Read-only-Capabilities duerfen keine Schreib- oder Tool-Seiteneffekte
  ausloesen.
- Schreibende Capabilities benoetigen klare Governance- und Provenienzregeln.

## 6. Sicherheitsregeln

Phase 5 folgt dem Grundsatz: Registrierung vor Ausfuehrung, Governance vor
Automatisierung.

Verbindliche Sicherheitsregeln:

- Keine automatische Ausfuehrung externer Agenten ohne ausdrueckliche Freigabe.
- Keine automatische Tool-Nutzung ausserhalb erlaubter Tools.
- Keine Umgehung von CAIM, CIM, CMM oder Foundation Governance.
- Keine Umgehung von CRE- und Orchestrator-Governance, sobald diese Schichten
  produktiv fuer Ausfuehrungsplanung verwendet werden.
- Keine unkontrollierte Schreiboperation in Memory, Dateien, Datenbank oder
  externe Systeme.
- Externe Agenten werden in Phase 5.0 nur als `experimental` oder `disabled`
  registriert.
- Spezialagenten starten read-only, bis ihr Sicherheitsprofil geprueft ist.
- Agenten duerfen nur auf freigegebene Pfade, Quellen und Tools zugreifen.
- Jede Erweiterung muss nachvollziehbar testbar sein.

## 7. Governance-Regeln

Jede relevante Agentenaenderung muss governancefaehig dokumentiert werden.

Governance umfasst:

- Registrierung neuer Agenten
- Aenderung von Status, Capabilities oder erlaubten Tools
- Aktivierung oder Deaktivierung eines Agenten
- Wechsel von read-only zu schreibend
- Anbindung externer APIs oder lokaler Modelle
- Uebergabe von Ergebnissen an CMM oder Review-Speicher
- Orchestrator-Entscheidungen fuer Agentenketten, Schreiboperationen,
  externe Systeme, Review-Uebergaben oder CMM-/Learning-Handoffs

Ein Governance-Eintrag muss mindestens enthalten:

- Zeitstempel
- Aktion
- Agent-ID
- alter Status
- neuer Status
- Actor
- Hash oder Integritaetsnachweis
- Ergebnis
- Backup- oder History-Pfad

Agentenergebnisse muessen Provenienz enthalten: Quelle, Agent, Capability,
Zeitpunkt, Eingabe, Ergebniszusammenfassung, Review-Status und Zielablage.
Orchestrator-Entscheidungen muessen zusaetzlich Plan-ID, beteiligte
Capabilities, priorisierte Kandidaten, Governance-Ergebnis, blockierte
Schritte und Handoff-Ziele protokollieren.

## 8. Kriterien fuer Spezialagenten

Ein Spezialagent darf in Phase 5 nur eingefuehrt werden, wenn folgende
Kriterien erfuellt sind:

- eindeutiger Zweck
- klarer Name und stabile Agenten-ID
- registrierte Capabilities
- definierter Status
- read-only-Startmodus
- erlaubte Tools explizit benannt
- keine versteckte externe Ausfuehrung
- Governance-Pflicht geprueft
- Fehler- und Statusausgabe vorhanden
- Regressionstest vorhanden
- Ergebnisablage oder Review-Pfad definiert

Spezialagenten duerfen bestehende Agenten nicht ersetzen, sondern muessen sich
in die vorhandene Agentenordnung einfuegen.

## 9. Erste Zielagenten

### Chemistry Agent

Der Chemistry Agent ist der erste fachliche Spezialagent fuer Stoffe,
chemische Strukturen, Sicherheitsfelder und spaetere externe
Chemie-Integrationen.

Phase-5.0-Rahmen:

- Stoffnamen erkennen
- strukturierte Stoffabfrage vorbereiten
- Sicherheits- und Gefahrstofffelder definieren
- Ergebnis read-only ausgeben
- keine automatische externe Suche ohne Freigabe
- RDKit, OPSIN oder PubChem-Anbindung erst spaeter

Moegliche Capabilities:

- `chemistry.lookup`
- `chemistry.structure`
- `chemistry.safety`

### Research Agent

Der Research Agent bleibt die kontrollierte Recherche- und Quellenebene. In
Phase 5 wird seine Rolle ueber Capabilities praezisiert.

Moegliche Capabilities:

- `research.web`
- `research.source_review`
- `research.summarize`

Der Research Agent darf Internetquellen nur im Rahmen der bestehenden
Governance-, Bandbreiten- und Review-Regeln nutzen.

### Tool Agent

Der Tool Agent ist keine allgemeine freie Werkzeugausfuehrung, sondern eine
spaetere kontrollierte Vermittlungsschicht fuer explizit erlaubte Tools.

Moegliche Capabilities:

- `tool.status`
- `tool.inspect`
- `tool.execute_approved`

In Phase 5.0 wird keine freie Tool-Ausfuehrung aktiviert.

## 10. Abgrenzung

Phase 5.0 umfasst keine automatische Ausfuehrung externer Agenten ohne
Freigabe.

Phase 5.0 umfasst keine unkontrollierte Tool-Nutzung.

Phase 5.0 umfasst keine Umgehung von Governance, CAIM, CIM, CMM,
Foundation Decision oder bestehenden Sicherheitspruefungen.

Phase 5.0 baut keine riskanten Agentenketten, keine autonomen Fremdagenten und
keine direkten externen Schreiboperationen.

Orchestrator Core 1.0 darf erst produktiv ausfuehren, wenn Blockieren,
Freigeben, Protokollieren, Review und CMM-Rueckfuehrung getestet und
dokumentiert sind.

## 11. Abschlusskriterien fuer Phase 5.0

Phase 5.0 gilt als abgeschlossen, wenn:

- diese Architekturdefinition vorliegt
- CAIM als kanonische Agentenregistrierung genutzt wird
- bestehende Agenten in CAIM sichtbar sind
- Capabilities als Routinggrundlage definiert sind
- Sicherheits- und Governance-Regeln dokumentiert sind
- Kriterien fuer Spezialagenten verbindlich beschrieben sind
- Chemistry Agent, Research Agent und Tool Agent als Zielagenten abgegrenzt sind
- keine automatische externe Agentenausfuehrung aktiviert wurde
- keine bestehende Agentenlogik gebrochen wurde
- die naechste technische Phase 5.1 klar vorbereitet ist

Phase 5.1 kann danach CAIM Capability Routing vorbereiten, ohne sofort einen
neuen Spezialagenten produktiv zu schalten.

Phase 5.2 priorisiert Orchestrator Core 1.0: Multi-Intent-Planung,
Governance-Check, Agentenkoordination, Review und CMM-Rueckfuehrung. Weitere
Spezialagenten folgen erst nach dieser Steuerungsschicht.
