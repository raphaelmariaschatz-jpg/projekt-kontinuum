# Canonical Deployment Framework (CDFX) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Konzept geprueft, Architekturbaustein empfohlen
Gueltig ab: 2026-07-16
Komponententyp: Deployment Governance Framework / deklaratives Profilmodell
Runtime-Wirkung: keine

## 1. Zweck

Das Canonical Deployment Framework (CDFX) 1.0 definiert, wie aus genau einer Canonical Architecture kontrollierte, reproduzierbare und governance-konforme Bereitstellungsvarianten abgeleitet werden koennen.

CDFX ist kein Produktmodell, keine Edition-Codebasis und keine Runtime-Migration. Es ist ein deklaratives Architektur- und Governance-Framework fuer Deployment-Profile.

Grundsatz:

```text
Eine Canonical Architecture.
Ein Canonical Core.
Mehrere validierte Deployment-Profile.
Keine Forks.
```

## 2. Bestandsanalyse

Projekt Kontinuum besitzt bereits die relevanten Grundlagen fuer ein kanonisches Deployment-Modell:

- CMIBF ist die normative Architekturquelle und Single Source of Truth.
- AFP legt fest, dass Architektur jeder Implementierung vorausgeht.
- CAWP regelt KI-Arbeitsverhalten und Architekturdisziplin.
- CAC ist als kuenftiger Compiler und Validator vorgesehen, darf aber keine Architekturprinzipien erfinden.
- CAMap beschreibt Beziehungen, besitzt aber keine eigene Architekturautoritaet.
- Framework Registry und CDG dokumentieren Identitaeten und Abhaengigkeiten.
- Foundation, Governance, CAM, ALP, CDF, CDG, CRE, Execution Planner, Orchestrator Core und Release Integrity bilden bereits eine tragfaehige Kernstruktur.
- CEF, CAICF, CMLF, CIF, CCP-Cognitive, CHIF, CVF und Meta-Reasoning sind als fachliche oder kognitive Erweiterungen anschlussfaehig.

Es existiert bisher kein eigenstaendiges Deployment-Profilmodell, das Profile, Rollen, Ressourcen, Lizenzbedingungen, Integrationen und Konfliktregeln kanonisch zusammenfuehrt. CDFX schliesst diese Luecke, ohne eine neue Architekturquelle zu bilden.

## 3. Namens- und Abkuerzungskollisionen

CDFX ist als Kuerzel geeignet, weil `CDF` bereits fuer das Canonical Development Framework reserviert ist. `CDFX` muss dauerhaft als Canonical Deployment Framework gefuehrt werden und darf nicht mit CDF, CDG oder CDFW verwechselt werden.

Die Bezeichnung "Edition" ist fuer Benutzerkommunikation moeglich, aber architektonisch riskant. Kanonisch sollten die Varianten als Deployment-Profile bezeichnet werden:

- Personal Deployment Profile
- Enterprise Deployment Profile
- Research Deployment Profile

Damit bleibt klar, dass keine getrennten Produkte entstehen.

## 4. Architektur-Einordnung

CDFX ist ein abgeleitetes kanonisches Framework unterhalb von CMIBF, AFP, CAWP und CAC. Es darf keine normative Architekturquelle sein.

Empfohlene Hierarchie:

```text
CMIBF
  |
AFP
  |
CAWP
  |
CAC / Validatoren
  |
Kanonische Artefakte
  |
CDFX Deployment Profiles
  |
Validierte Bereitstellung
```

CDFX beschreibt, welche Profile zulaessig sind und welche Frameworks, Capabilities, Rollen, Ressourcen, Lizenzen, Integrationen und Konfigurationen ein Profil aktivieren darf. CDFX entscheidet nicht eigenmaechtig ueber Architektur. Jede profilrelevante Regel muss auf CMIBF, Framework Registry, CDG, CAM, Governance oder eine spaeter freigegebene Architekturentscheidung rueckfuehrbar sein.

## 5. Kanonisches Deployment-Modell

Das empfohlene Modell lautet:

```text
Canonical Architecture
        |
        v
Canonical Core
        |
        v
Deployment Profile
        |
        +-- aktivierte Capabilities
        +-- aktivierte Frameworks
        +-- Governance-Regeln
        +-- Rollen- und Rechteprofil
        +-- Ressourcenprofil
        +-- Lizenzprofil
        +-- Integrationsprofil
        +-- Konfiguration
        |
        v
Validierung
        |
        v
Bereitstellung
```

Profile enthalten grundsaetzlich Referenzen, Aktivierungsregeln und Grenzwerte. Vollstaendige Fachkonfigurationen duerfen nur eingebettet werden, wenn sie stabil, versioniert und validierbar sind. Profilvererbung ist in CDFX 1.0 nicht empfohlen. Profilkombinationen sind nur als explizit freigegebene Composite Profiles zulaessig.

## 6. Canonical Core

Der Canonical Core ist der unveraenderliche Mindestkern, der in allen Deployment-Profilen erhalten bleiben muss. Nicht jede Core-Komponente muss in jeder Bereitstellung fuer Benutzer sichtbar sein, aber ihre Architekturrolle darf nicht entfernt werden.

| Komponente | Core | Runtime aktiv | Governance aktiv | Mindestfunktion |
| --- | --- | --- | --- | --- |
| CMIBF | Ja | Nein | Ja | Normative Architekturquelle |
| Foundation | Ja | Ja | Ja | technische und semantische Grundregeln |
| Governance Layer | Ja | Teilweise | Ja | Regeln, Freigabe, Pruefung |
| Canonical Architecture / CAMap | Ja | Nein | Ja | Architekturkarte und Einordnung |
| CAM | Ja | Teilweise | Ja | Artefaktidentitaet und Lifecycle-Bezug |
| ALP | Ja | Nein | Ja | Archivierung, Historisierung, Abloesung |
| CDF | Ja | Nein | Ja | Entwicklungsrahmen |
| CDG | Ja | Nein | Ja | Entwicklungs- und Abhaengigkeitsgovernance |
| CDFX | Ja | Nein | Ja | Deployment-Profilmodell |
| Canonical Glossary | Ja | Nein | Ja | eindeutige Begriffe |
| Canonical History Index / Projektchronik | Ja | Nein | Ja | Nachvollziehbarkeit |
| Canonical Memory | Ja | Ja | Ja | kontrollierte Wissens- und Erinnerungsbasis |
| CRE | Ja | Ja | Ja | Faehigkeitsauswahl ohne direkte Ausfuehrung |
| Execution Planner | Ja | Ja | Ja | validierte Planung |
| Orchestrator Core | Ja | Ja | Ja | Ausfuehrung validierter Plaene |
| Release Integrity | Ja | Teilweise | Ja | Integritaet und Reproduzierbarkeit |
| Identitaets- und Provenienzmechanismen | Ja | Ja | Ja | Identitaet, Herkunft, Verantwortlichkeit |
| Sicherheits- und Auditgrundlagen | Ja | Ja | Ja | Mindestschutz und Nachweisbarkeit |
| Validierungsmechanismen | Ja | Teilweise | Ja | Profil- und Release-Pruefung |

Niemals durch ein Deployment-Profil deaktivierbar sind CMIBF-Bezug, Foundation, Governance, Core-Identitaet, Core-Provenienz, Mindest-Audit, Release-Integrity-Bezug, Orchestrator-Grenzen, CRE/Planner/Orchestrator-Trennung und die Rueckfuehrbarkeit auf kanonische Artefakte.

## 7. Deployment-Profile

### 7.1 Personal Deployment Profile

Zielgruppe: Privatanwender.

Bewertung: sinnvoll als schlankes Standardprofil mit lokaler Nutzung, reduziert sichtbarer Administration, Einzelbenutzerbetrieb und Datenschutzfokus.

Deployment-Merkmale:

- Einzelbenutzerbetrieb
- lokale oder persoenliche Installation
- einfache Standardkonfiguration
- reduzierte Administrationsoberflaeche
- geringe Ressourcenanforderungen
- optionale Medien-, Lern- und Dokumentfunktionen

Keine eigene Produktarchitektur. Erweiterungen muessen als aktivierbare Capabilities oder Frameworks referenziert werden.

### 7.2 Enterprise Deployment Profile

Zielgruppe: Unternehmen und groessere Organisationen.

Bewertung: sinnvoll, aber stark governance- und rollenabhaengig. Mehrbenutzerbetrieb, Rollen, Rechte, Mandantenfaehigkeit, Audit, Monitoring und API-Integration sind teils Deployment-Merkmale, teils eigenstaendige Capabilities.

Deployment-Merkmale:

- Organisationskonfiguration
- erweitertes Rollen- und Rechteprofil
- Audit- und Compliance-Anforderungen
- zentrale Richtlinien
- freigegebene Integrationen
- Monitoring- und Reporting-Anforderungen

CEF ist dabei nicht das Deployment-Profil selbst, sondern ein optional aktivierbares Enterprise-Framework innerhalb eines Enterprise-Profils.

### 7.3 Research Deployment Profile

Zielgruppe: Forschung, Hochschulen, wissenschaftliche Entwicklung.

Bewertung: sinnvoll, wenn experimentelle Komponenten strikt von kanonischen Komponenten getrennt werden.

Deployment-Merkmale:

- kontrollierte Experimentierraeume
- hohe Konfigurierbarkeit
- Forschungsprotokolle
- Reproduzierbarkeit
- Visualisierung und Evaluation
- explizite Trennung zwischen canonical, experimental und rejected

Experimentelle Module duerfen den Canonical Core nicht veraendern. Uebernahme in die Canonical Architecture erfordert separaten Governance-Zyklus.

## 8. Aktivierbare Frameworks und Capabilities

| Element | Funktion | Zulaessige Profile | Bedingungen |
| --- | --- | --- | --- |
| CAICF | KI-Kompetenzaufbau | Personal, Research, Enterprise | Governance- und Lernbezug vorhanden |
| CMLF | Medienlernen | Personal, Research | Datenschutz, Quellen- und Mediengovernance |
| CEF | Unternehmensmodell | Enterprise, Research | Rollen-, Audit- und Organisationskontext |
| CIF | Intelligenzdefinition | alle, sichtbar je nach Profil | darf CCP/CRE nicht ersetzen |
| CCP-Cognitive | Denk- und Verarbeitungspipeline | alle | Core-nahe, nicht als Produktfeature duplizieren |
| CHIF | Mensch-System-Interaktion | alle | UI-spezifische Sichtbarkeit profilierbar |
| CVF | visuelle Verarbeitung | Personal, Research, Enterprise optional | Datenschutz, Mediengovernance, Ressourcen |
| Meta-Reasoning | Reflexions- und Begruendungspruefung | Research, Enterprise, optional Personal | klare Grenzen zu Runtime-Entscheidung |
| Observability | Monitoring und Nachvollziehbarkeit | Enterprise, Research | Datenschutz, Audit, Rollenrechte |
| Capability Discovery | Faehigkeitserkennung | Research, Enterprise, optional Personal | CRE- und Registry-Anbindung |
| Evaluation Center | Bewertung und Vergleich | Research, Enterprise | Evidenz, Reproduzierbarkeit, Audit |
| Adaptive Strategy Engine | Strategieanpassung | Research, spaeter Enterprise | hohe Governance, keine autonome Architekturentscheidung |

Jedes Element behaelt unabhaengig vom Profil seine kanonische Identitaet. Profile aktivieren, begrenzen oder verbergen; sie duplizieren nicht.

## 9. Rollen-, Rechte- und Lizenzmodell

CDFX 1.0 empfiehlt ein dreistufiges Rollenmodell:

- Core Governance Roles: Owner, Architect, Release Reviewer, Auditor.
- Deployment Roles: Personal User, Enterprise Admin, Enterprise User, Research Lead, Research Contributor.
- System Roles: Orchestrator, Planner, Capability Resolver, Validator, Audit Writer.

Berechtigungen muessen deklarativ im Profil referenziert werden. Rollen duerfen den Canonical Core nicht umgehen.

Lizenzprofile sollten getrennt von Deployment-Profilen modelliert werden. Ein Deployment-Profil kann ein Lizenzprofil voraussetzen, aber die Lizenz darf keine Architekturvariante erzeugen. Empfohlene Lizenzprofile:

- personal-local
- enterprise-governed
- research-lab
- evaluation-only

## 10. Ressourcen- und Integrationsmodell

Ressourcenprofile beschreiben Mindest- und Zielressourcen, zum Beispiel Speicher, lokale Modelle, Netzwerkzugriff, Benutzerzahl, Audit-Speicher, Integrationslimits und Monitoring.

Integrationsprofile beschreiben erlaubte externe Systeme, API-Zugriffe, Connectoren, Import/Export, Authentifizierung und Auditpflicht. Integrationen sind immer optional und governance-pflichtig.

## 11. Abhaengigkeiten und Schnittstellen

| Beziehung | Richtung | Art | Regel |
| --- | --- | --- | --- |
| CMIBF -> CDFX | normativ | Architekturquelle | CDFX darf CMIBF nicht widersprechen |
| AFP -> CDFX | normativ | Reihenfolge | keine Implementierung ohne Architekturentscheidung |
| CAWP -> CDFX | governance | KI-Arbeit | Konzept, Pruefung und Bericht folgen CAWP |
| CAC -> CDFX | validierend | spaeter | CAC validiert Profile, erfindet sie nicht |
| CAM -> CDFX | governance | Artefakte | CDFX-Artefakte muessen klassifizierbar sein |
| ALP -> CDFX | lifecycle | Historisierung | Profile brauchen Versionierung und Abloesung |
| CDG -> CDFX | governance | Abhaengigkeiten | ungueltige Kombis muessen blockierbar sein |
| CRE -> Profile | operational | Capability-Auswahl | nur freigegebene Capabilities |
| Execution Planner -> Profile | operational | Planbarkeit | Ressourcen und Rechte muessen planbar sein |
| Orchestrator Core -> Profile | operational | Ausfuehrung | nur validierte Plaene |
| Release Integrity -> Profile | governance | Reproduzierbarkeit | Profile werden Teil des Release-Nachweises |
| Canonical Glossary -> CDFX | semantisch | Begriffe | Abkuerzungen und Begriffe eindeutig halten |
| Projektchronik -> CDFX | historisch | Nachweis | Profilentscheidungen dokumentieren |

## 12. Konflikt- und Validierungsregeln

Ein Deployment-Profil ist ungueltig, wenn es:

- eine Core-Komponente deaktiviert,
- eine Framework-Identitaet dupliziert,
- eine nicht freigegebene Abhaengigkeit erzwingt,
- Rollenrechte ohne Auditpflicht erweitert,
- Lizenz- oder Sicherheitsgrenzen umgeht,
- experimentelle Komponenten als kanonisch markiert,
- eine eigene Architekturquelle bildet,
- nicht reproduzierbar ist.

CDFX 1.0 empfiehlt, Profile als flache, versionierte Deklarationen zu modellieren. Profilkombinationen sind nur ueber explizite Composite Profiles erlaubt. Profilvererbung bleibt bis zu einer spaeteren Freigabe ausgeschlossen.

## 13. Risiken und offene Fragen

Risiken:

- "Edition" koennte als Produktlinie statt als Profil verstanden werden.
- Enterprise- und Research-Anforderungen koennen unbemerkt Runtime- oder Sicherheitsframeworks voraussetzen.
- Experimentelle Forschungsfunktionen koennen den Core kontaminieren, wenn keine Quarantaene besteht.
- Lizenzprofile koennen faelschlich Architekturentscheidungen ersetzen.
- Zu komplexe Profilkombinationen koennen Validierung erschweren.

Offene Fragen:

- Soll CDFX im CMIBF als neues Framework registriert werden, und welche Framework-ID erhaelt es?
- Welche Minimalvalidierung soll der CAC zuerst uebernehmen?
- Welche Rollenrechte gehoeren in CDFX und welche in ein spaeteres Security- oder Authentication-Framework?
- Wann werden Lizenzprofile durch CLMSF verbindlich?
- Soll ein erstes Pilotprofil Personal oder Research sein?

## 14. Empfehlung

Empfehlung: GO fuer die kanonische Konzept- und Dokumentationsvorbereitung; SPAETER fuer technische Implementierung, CAC-Anbindung, Deployment-Resolver und produktive Profilaktivierung.

Begruendung:

- CDFX erhaelt eine gemeinsame Codebasis.
- CDFX setzt genau eine Canonical Architecture voraus.
- CDFX laesst den Canonical Core unveraendert.
- Deployment wird deklarativ ueber Profile, Regeln und Konfigurationen gesteuert.
- Frameworks und Capabilities werden referenziert, nicht dupliziert.
- Zukuenftige Varianten koennen ohne Architekturbruch vorbereitet werden.

## 15. Kanonischer Implementierungsplan

| Phase | Voraussetzung | Ergebnis | Risiko | Abnahmekriterium |
| --- | --- | --- | --- | --- |
| 1 Architekturfreigabe | CDFX-Konzept liegt vor | Entscheidung GO/SPAETER | unklare Autoritaet | Raphael/CMIBF-Freigabe dokumentiert |
| 2 Dokumentationspflege | Freigabe | CDFX-Dokumente final | Begriffsabweichung | Querverweise geprueft |
| 3 Glossarpflege | Namensentscheidung | CDFX-Begriff im Glossar | Kollision mit CDF | CDFX eindeutig definiert |
| 4 Querverweispruefung | Dokumente stabil | Beziehungen in CAMap/CDG erfasst | veraltete Referenzen | keine widerspruechlichen Links |
| 5 JSON-Schema-Finalisierung | Profilmodell stabil | verbindliches Schema | zu fruehe Festlegung | Schema validiert |
| 6 Profilregistrierung | Schema final | Profile registriert | Produktdenken | Profile als Deployment Profiles markiert |
| 7 Konfliktvalidierung | Abhaengigkeiten erfasst | Validator-Regeln | Kombinationskomplexitaet | Core-Deaktivierung blockiert |
| 8 Rollenintegration | Rollenmodell freigegeben | Rechteprofile | Sicherheitsluecken | Auditpflicht definiert |
| 9 Ressourcen/Lizenz | CLMSF/CSF-Abgleich | Ressourcen- und Lizenzprofile | Lizenz als Architekturquelle | Lizenz nur als Bedingung |
| 10 CAC-Anbindung | CAC bereit | Profilvalidierung | Compiler ueberdehnt | CAC validiert nur |
| 11 Deployment-Resolver | Profile validiert | Resolver-Konzept | Runtime-Effekt zu frueh | keine produktive Aktivierung ohne Auftrag |
| 12 Release Integrity | RI-Regeln bereit | Profilnachweis im Release | unvollstaendige Evidence | reproduzierbare Profil-ID |
| 13 Tests | Validator vorhanden | Testmatrix | Testluecken | ungueltige Profile fallen durch |
| 14 Pilotprofil | Freigabe | erstes Pilotprofil | zu breiter Scope | ein Profil kontrolliert pilotiert |
| 15 Freigabe | Pilot bestanden | kontrollierte Nutzung | Schattenprofile | Freigabestatus dokumentiert |
| 16 Evolution | Betriebserfahrung | Profilversionierung | Profilwildwuchs | ALP/CAM-Historie vorhanden |

## 16. Abschlussstatus

CONCEPT_COMPLETE

Es wurde keine produktive Implementierung vorgenommen. CDFX 1.0 ist als Konzept- und Governance-Schicht geeignet, benoetigt aber vor technischer Aktivierung eine formale Architekturfreigabe und spaetere Validator-/CAC-Anbindung.
