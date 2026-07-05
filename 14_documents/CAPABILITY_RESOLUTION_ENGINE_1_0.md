# Capability Resolution Engine 1.0

## Zweck

Die Capability Resolution Engine (CRE) 1.0 ist eine read-only Aufloesungsschicht zwischen Request Router und Agentenausfuehrung. Sie soll nicht weitere Agenten erzeugen, sondern vorhandene und kuenftige Faehigkeiten sauberer finden, priorisieren und fuer Governance, Review und CMM vorbereiten.

CRE 1.0 fuehrt keine Agenten aus. Sie erzeugt Empfehlungen.

## Position in der Architektur

Zielpfad:

```text
User -> Request Router -> Capability Resolution Engine -> Orchestrator Core
     -> Governance -> Agenten -> Review -> CMM / Learning
```

In Version 1.0 ist CRE bereits als Systemkomponente angebunden, bleibt aber eine Empfehlungsschicht. Bestehende Router- und Orchestrator-Pfade werden nicht ersetzt.

## Capability Registry und CAIM

Die Capability Registry `24_config/capability_registry_34_1.json` ist in CRE
1.0 die kanonische Quelle fuer Capability-Definitionen. Jede Capability besitzt
`capability_id`, Name, Beschreibung, unterstuetzte Intents, Prioritaet,
Governance-Level, erlaubte Agenten und Voraussetzungen.

CAIM bleibt die kanonische Quelle fuer Agentenregistrierung und Anbieterstatus.
CRE nutzt CAIM read-only ueber bestehende Methoden wie:

- `find_by_capability`
- `can_execute`
- Agentenfelder wie `capabilities`, `status`, `type`, `governance_required` und `read_only`

CAIM wird nicht umgebaut und keine Capability-Definition wird ueberschrieben.

## Verhaeltnis zu Router, Governance, Agenten, Review und CMM

Der Request Router erkennt weiterhin Anfrageklassen und direkte Agentenrouten. CRE kann daraus eine Capability ableiten, z. B. `file.read`, `diagnostics.run`, `chemistry.lookup` oder `governance.review`.

CRE bereitet folgende Informationen vor:

- passende Capability
- moegliche Agenten aus CAIM
- priorisierte Kandidaten
- empfohlener Agent
- Governance-Pflicht
- menschliche Freigabe
- read-only Status
- Review-Pflicht
- CMM-Relevanz
- Ausfuehrungsempfehlung ohne Ausfuehrung

## Multi-Intent-Kompatibilitaet

CRE 1.0 kann kombinierte Prompts in mehrere Segmente zerlegen und jedes Segment einzeln bewerten.

Beispiel:

`Gib den Projektordner frei, teste danach den FileAgent und erstelle einen Diagnostikbericht.`

Erwartete Aufloesung:

- `project.access`
- `file.status`
- `diagnostics.run`

Damit wird der aktuelle Multi-Intent-Fix architektonisch vorbereitbar: Freigabe und Diagnostik sind dann keine Sonderfall-Ifs mehr, sondern getrennte Capability-Empfehlungen.

## Aktueller Status

Implementiert:

- Modul `kontinuum.core.capability_resolution_engine`
- Capability Registry `24_config/capability_registry_34_1.json` mit 46 vorhandenen CAIM-Capabilities
- Systemanbindung als `system.capability_resolution_engine`
- read-only Statusfunktion und `crestatus`
- Single-Intent-Aufloesung
- Multi-Intent-Aufloesung
- CAIM-Adapter ueber bestehende CAIM-Methoden
- Priorisierung mehrerer Kandidaten
- Governance-, Human-Approval-, Review- und CMM-Hinweise
- Tests fuer Single Intent, Multi Intent, unbekannte Capability, mehrere Agenten, Governance, read-only Diagnose und CAIM-Fallback

## Grenzen von Version 1.0

- CRE fuehrt keine Agenten aus.
- CRE ersetzt den PromptOrchestrator noch nicht.
- Multi-Intent-Ausfuehrung laeuft noch nicht vollstaendig ueber CRE.
- Capability-Erkennung nutzt bewusst einfache Marker, Routerentscheidungen und Registry-Lookup.
- Governance-Gates pruefen Foundation-, CAM-, CCP- und Governance-Voraussetzungen deterministisch; eine vollstaendige Policy-Engine folgt spaeter.
- Review- und CMM-Anbindung werden empfohlen, aber noch nicht automatisch geschrieben.

## Naechste Ausbaustufe 1.1

Empfohlene Schritte:

1. PromptOrchestrator optional CRE-Empfehlungen protokollieren lassen.
2. Multi-Intent-Ausfuehrungsplan einfuehren, der CRE-Ergebnisse sequentiell verarbeitet.
3. FileAgent-Freigabe plus Diagnostikbericht von Sonderlogik auf CRE-Planung migrieren.
4. Governance-Policy als eigene Bewertungsstufe zwischen CRE und Agentenausfuehrung schalten.
5. Review-Queue und CMM-Kandidaten strukturiert aus CRE-Ergebnissen erzeugen.
6. Capability-Marker durch kanonische Capability-Definitionen aus CAIM oder einer separaten Capability Registry ersetzen.
