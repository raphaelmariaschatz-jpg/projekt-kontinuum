# Canonical Code Agent Framework (CODEAF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: IMPLEMENTED_WITH_LIMITATIONS / keine Ausfuehrungsfreigabe
Gueltig ab: 2026-07-18 fuer explizite Auftragsvalidierung
Komponententyp: Code-Agent-Governance-Framework
Runtime-Wirkung: explizite, read-only Auftragsvalidierung
Produktive Aenderungen: keine

## 1. Zweck

Das Canonical Code Agent Framework (CODEAF) 1.0 definiert den verbindlichen Rahmen, nach dem Code-Agenten in Projekt Kontinuum identifiziert, beauftragt, begrenzt, geplant, kontrolliert, geprueft und auditiert werden sollen.

CODEAF ist kein Agent, kein Orchestrator, kein Planner, keine Registry, kein Berechtigungssystem und keine automatische Codeausfuehrung. CODEAF ist die normative Agenten-Governance- und Kontrollschicht fuer Code-Agentenarbeit. Die aktive Komponente validiert nur explizit uebergebene Auftragsvertraege und autorisiert keine Ausfuehrung.

Namensentscheidung: `CODEAF` ist die kanonische Abkuerzung, weil das CMIBF fuer `PK-FW-AGENT-005` bereits `CODEAF | Code Agent Framework | 1.0 | PLANNED | AGENT` fuehrt. `CCAF` war ein Arbeitsname dieses Pruefauftrags und wird nicht als konkurrierende kanonische Benennung verwendet.

Die Architekturposition lautet:

```text
CMIBF / AFP / CDF / CDG
-> CODEAF
-> Agent Registry / CRE / Execution Planner / Orchestrator
-> konkrete Agenten
```

CODEAF verbindet bestehende kanonische Bausteine fuer den Spezialfall automatisierter Codearbeit, ohne ihre Zustaendigkeiten zu uebernehmen.

Grundsatz:

```text
Kein Code-Agent handelt allein aufgrund technischer Moeglichkeit.
Jede Handlung braucht Identitaet, Auftrag, Rolle, Capability, Permission,
Scope, Risikoklasse, Governance-Gate, Nachweis und externe Freigabe.
```

Ein Code-Agent darf seinen eigenen Arbeitsumfang nicht eigenmaechtig erweitern und seine eigene Arbeit nicht allein endgueltig freigeben.

CODEAF 1.0 folgt deny-by-default:

```text
Nicht ausdruecklich erlaubte Aktionen, Pfade, Tools, Befehle, Datenbanken,
Netzwerke, Git-Operationen, Delegationen und Runtime-Modi sind verboten.
```

## 2. Bestandsanker

Die Pruefung zeigt, dass Projekt Kontinuum bereits mehrere CODEAF-relevante Bausteine besitzt:

| Bereich | Vorhandener Anker | Bewertung |
| --- | --- | --- |
| Projektstruktur | `14_documents/PROJEKTSTRUKTUR_34_1.md` | aktiv und kanonisch |
| Entwicklungsrahmen | `14_documents/CANONICAL_DEVELOPMENT_FRAMEWORK_1_0.md` | aktiv |
| Entwicklungsgovernance | `14_documents/CANONICAL_DEVELOPMENT_GOVERNANCE_34_1.md` | aktiv |
| KI-Arbeitsprotokoll | `14_documents/CANONICAL_AI_WORKING_PROTOCOL_1_0.md` | freigegeben |
| Architekturgovernance | `14_documents/ARCHITECTURE_GOVERNANCE_FRAMEWORK_1_0.md` | aktiv |
| Authentisierung | `14_documents/CANONICAL_AUTHENTICATION_FRAMEWORK_1_0.md` | geprueft, mit Auflagen freigabefaehig |
| Lizenzierung | `14_documents/CANONICAL_LICENCE_MANAGEMENT_SYSTEM_FRAMEWORK_1_0.md` | Architekturvorschlag, GO mit Auflagen |
| Agent Registry | `24_config/canonical_agents.json` | aktiv, aber fuer Code-Agenten-Governance unvollstaendig |
| Agentenhistorie | `24_config/history/canonical_agent_history/` | vorhanden |
| CodeAgent | `01_system/kontinuum/core/code_agent.py`, `14_documents/code_agent_1_0_umsetzung_2026-07-01.md` | produktiv als read-only Analyseagent dokumentiert |
| Capability Registry | `24_config/capability_registry_34_1.json` | aktiv, CAIM-basiert |
| CRE | `01_system/kontinuum/core/capability_resolution_engine.py`, `14_documents/CAPABILITY_RESOLUTION_ENGINE_1_0.md` | read-only Empfehlungsschicht |
| Execution Planner | `01_system/kontinuum/core/execution_planner.py`, `24_config/execution_plan_schema_34_1.json` | plant, fuehrt nicht aus |
| Orchestrator Core | `01_system/kontinuum/core/orchestrator_core.py`, `24_config/orchestrator_runtime_schema_34_1.json` | fuehrt nur validierte Plaene aus |
| Release Integrity | `24_config/release_integrity_34_1.json` | Gate- und Nachweisanker |
| Audit/Reports | `27_logs/`, `31_reports/`, `31_reports/events`, `31_reports/governance` | vorhanden, aber nicht CODEAF-spezifisch |

Wichtiger Befund: Die vorhandene Agent Registry enthaelt fuer mehrere Agenten read-only-Beschreibungen, aber technisch `read_only: false`. Dieser Befund ist in diesem Auftrag ausschliesslich ein dokumentierter Gap. Eine Korrektur bestehender Runtime- oder Registry-Dateien darf erst nach abgeschlossener CODEAF-Architekturdefinition, Pruefung und ausdruecklicher Implementierungsfreigabe erfolgen.

## 3. Definition

Ein Code-Agent ist eine identifizierbare, regelgebundene Software- oder Modellinstanz, die innerhalb eines ausdruecklich freigegebenen Auftrags Quellcode, Konfigurationen, Tests, Dokumentation oder zugehoerige Entwicklungsartefakte analysiert, plant, erzeugt, veraendert, prueft oder verwaltet.

Diese Definition ist fuer CODEAF 1.0 geeignet, wenn drei Praezisierungen gelten:

- Ein Code-Agent kann intern, lokal, extern, modellbasiert oder regelbasiert sein.
- Analyse-, Planungs-, Implementierungs-, Test-, Review-, Security-, Migrations-, Dokumentations- und Release-Agenten sind Rollen, nicht zwingend separate Produkte.
- Technische Faehigkeit ist keine Erlaubnis; Permission entsteht nur aus Auftrag, Rolle, Scope, Risikoklasse und Freigabe.

## 4. Abgrenzung

| Komponente | Zustaendigkeit | CODEAF-Abgrenzung |
| --- | --- | --- |
| CMIBF | normative Architekturquelle | CODEAF darf CMIBF nicht ersetzen; CODEAF benoetigt CMIBF-Abdeckung vor Implementierung |
| CDF | Entwicklungsarbeitszyklus | CODEAF konkretisiert Code-Agent-Auftraege innerhalb des CDF |
| CDG | Entwicklungsregeln | CODEAF konsumiert CDG-Regeln und erzeugt keine neue Entwicklungsverfassung |
| CAWP | Arbeitsverhalten aller KI-Systeme | CODEAF spezialisiert CAWP auf Code-Agenten |
| CAF | Identitaet, Authentisierung, Session, Audit | CODEAF referenziert CAF fuer Agenten- und Laufidentitaet |
| CLMSF | Lizenzidentitaet und Nutzung | CODEAF referenziert Lizenz-/Provider-/Modellnutzung |
| CAIM | Agentenregistrierung | CODEAF definiert zusaetzliche Anforderungen an Code-Agenten-Registrierung |
| CRE | Capability-Aufloesung | CODEAF definiert zulaessige Code-Agent-Capabilities; CRE loest sie auf |
| Execution Planner | Planerstellung | CODEAF definiert Plan-Gates; Planner erstellt validierte Plaene |
| Orchestrator Core | regelgebundene Ausfuehrung | CODEAF begrenzt Ausfuehrung; Orchestrator entscheidet keine Entwicklungsfreigabe |
| CAM | Artefaktklassifikation und Lifecycle | CODEAF meldet erzeugte/geaenderte Artefakte an CAM |
| Release Integrity | Freigabefaehigkeit | CODEAF liefert Nachweise fuer Release-Gates |
| Audit/Provenienz | Nachvollziehbarkeit | CODEAF definiert agentenspezifische Pflichtfelder |

## 5. Zielarchitektur

CODEAF 1.0 soll folgende Verarbeitungskette festschreiben:

```text
Canonical Agent Task
-> Agent Identity Validation
-> Role and Permission Resolution
-> Capability Resolution
-> Risk Classification
-> Governance Gate
-> Execution Plan
-> Controlled Execution
-> Independent Verification
-> Audit and Provenance
-> Human or Authorized Final Approval
```

Zustaendigkeiten:

- CODEAF definiert Regeln, Vertrage, Pflichtfelder, Gates und Grenzen.
- CAF bestaetigt Identitaet und Sitzung.
- CLMSF bestaetigt spaeter zulaessige Nutzung, Provider, Modell und Edition.
- CAIM registriert Agenten.
- CRE loest Capabilities auf.
- Execution Planner plant.
- Orchestrator Core fuehrt nur validierte Plaene aus.
- CAM klassifiziert Artefakte.
- Release Integrity prueft Freigabefaehigkeit.
- Raphael oder eine ausdruecklich autorisierte Instanz behaelt die finale Kontrolle.

## 6. Agentenidentitaet

CODEAF 1.0 benoetigt zwei Identitaetsebenen:

1. dauerhafte Agentenidentitaet,
2. konkrete Lauf-/Sitzungsidentitaet.

Pflichtfelder der dauerhaften Identitaet:

```text
agent_id
agent_name
agent_version
agent_type
provider
model_name
model_version
runtime
trust_level
status
registered_roles
registered_capabilities
permission_profile
authentication_reference
licence_reference
created_at
updated_at
valid_from
valid_until
```

Pflichtfelder der Laufidentitaet:

```text
agent_run_id
session_id
task_id
execution_id
started_at
initiated_by
active_role
active_permission_profile
active_scope
risk_class
approval_reference
```

## 7. Rollenmodell

CODEAF 1.0 sollte folgende Rollen normativ aufnehmen:

| Rolle | CODEAF-1.0-Status | Kernrechte | harte Grenze |
| --- | --- | --- | --- |
| Analysis Agent | zwingend | lesen, analysieren, berichten | keine Schreibaktion |
| Planning Agent | zwingend | Plaene, Risiken, Tests, Rueckfallstrategie | fuehrt Plan nicht selbst aus |
| Implementation Agent | zwingend | freigegebene Aenderungen im Scope | keine Scope-Erweiterung |
| Review Agent | zwingend | Architektur-, Scope-, Qualitaetspruefung | keine finale Selbstfreigabe |
| Test Agent | zwingend | Tests finden, ausfuehren, bewerten | keine Codefreigabe allein |
| Security Agent | zwingend fuer R3+ | Auth, Permission, Secrets, Pfade, Injection, Privilegien | keine Risikoabsenkung |
| Documentation Agent | zwingend | Dokumentation und Reports | keine Runtime-Aenderung |
| Migration Agent | optional in 1.0, vorbereitet | Verschieben/Migration nach Sonderfreigabe | keine stille Migration |
| Release Agent | optional in 1.0, vorbereitet | Release-Integritaet pruefen | kein Release ohne Gate |

Rollen duerfen bei niedrigen Risiken kombiniert werden. Ab R3 muss mindestens Review oder Test getrennt dokumentiert werden. Ab R4 ist unabhaengige Kontrolle Pflicht. R5 bleibt ohne ausdrueckliche Sonderfreigabe ausserhalb produktiver CODEAF-1.0-Ausfuehrung.

## 8. Capability-Modell

Capabilities beschreiben technische Faehigkeiten. Sie sind keine Erlaubnis.

CODEAF 1.0 sollte folgende Capability-Gruppen definieren:

```text
code.read
code.search
code.analyze
code.plan
code.create
code.modify
code.delete
code.move
code.archive
config.read
config.modify
schema.read
schema.validate
schema.modify
tests.discover
tests.create
tests.execute
tests.evaluate
git.inspect
git.diff
git.branch
git.stage
git.commit
git.reset
database.inspect
database.read
database.write
database.migrate
documentation.read
documentation.update
architecture.inspect
architecture.validate
architecture.modify
security.inspect
security.audit
release.inspect
release.verify
release.prepare
audit.write
provenance.write
report.create
```

Kritische Capabilities duerfen nicht standardmaessig vergeben werden:

```text
code.delete
code.move
git.commit
git.reset
database.write
database.migrate
architecture.modify
release.prepare
```

## 9. Berechtigungsmodell

CODEAF trennt Capability und Permission:

```text
Capability = Agent kann es technisch.
Permission = Agent darf es in diesem Auftrag, in diesem Scope, unter diesen Gates.
```

Ein Permission Profile muss mindestens enthalten:

```text
allowed_paths
denied_paths
allowed_files
denied_files
allowed_file_types
allowed_operations
denied_operations
allowed_commands
denied_commands
max_files_changed
max_total_diff_lines
network_access
database_access
git_access
requires_human_approval
requires_independent_verification
```

Explizite Verbote haben Vorrang vor allgemeinen Erlaubnissen.

CODEAF 1.0 unterscheidet vier technische Grenzbereiche:

| Grenze | Bedeutung | Standard |
| --- | --- | --- |
| Read-only | Lesen, Analysieren, Berichten | erlaubt nur bei passendem Auftrag |
| Write | Dateien, Konfigurationen, Tests oder Dokumentation veraendern | verboten ohne explizite Permission |
| Execute | Befehle, Tests, Skripte, Tools oder Agenten ausfuehren | verboten ohne explizite Permission |
| Administrative | Git-Schreiboperationen, Rechte, Auth, Lizenz, Datenbank, Release, Migration | verboten ohne Sonderfreigabe |

Runtime-Konfiguration darf CODEAF-Grenzen nicht erweitern. Bei Konflikt zwischen Beschreibung, Registry, Permission Profile und Runtime-Konfiguration gilt die strengste Grenze.

## 10. Kanonischer Code-Agentenauftrag

Ein Canonical Agent Task muss mindestens enthalten:

```text
task_id
title
goal
rationale
initial_state
requester
agent_role
allowed_capabilities
permission_profile
allowed_scope
excluded_scope
canonical_rules
risk_class
required_prechecks
planned_workflow
test_requirements
documentation_requirements
audit_requirements
abort_conditions
rollback_point
expected_results
approval_process
final_report
status
```

Statuswerte fuer CODEAF 1.0:

```text
DRAFT
UNDER_REVIEW
APPROVED
READY
IN_PROGRESS
PAUSED
BLOCKED
ABORTED
FAILED
COMPLETED
VERIFIED
REJECTED
RELEASED
```

## 11. Arbeitszyklus

CODEAF 1.0 verwendet den technischen Zyklus:

```text
Identify -> Inspect -> Plan -> Authorize -> Execute -> Verify -> Report
```

Dieser Zyklus ist kompatibel mit "Erkennen - Schaffen - Vollenden":

| Leitformel | Technische Phasen |
| --- | --- |
| Erkennen | Identify, Inspect, Plan |
| Schaffen | Authorize, Execute |
| Vollenden | Verify, Report, Final Approval |

Die poetische Leitformel darf keine Pruefschritte ersetzen.

## 12. Betriebsmodi

CODEAF 1.0 sollte aufnehmen:

| Modus | CODEAF-1.0-Status |
| --- | --- |
| Read-only Mode | aktiv definieren |
| Proposal Mode | aktiv definieren |
| Controlled Write Mode | definieren, aber nur nach Freigabe nutzbar |
| Migration Mode | vorbereiten, Sonderfreigabe erforderlich |
| Emergency Repair Mode | vorbereiten, eng begrenzen |
| Autonomous Maintenance Mode | nur konzeptionell, nicht aktivieren |

## 13. Risikoklassen

| Klasse | Bedeutung | Mindestanforderung |
| --- | --- | --- |
| CODEAF-R0 | reine Analyse | kein Schreiben, Bericht |
| CODEAF-R1 | geringes Risiko | Scope, Diff-Pruefung, Dokumentation |
| CODEAF-R2 | begrenzte Codeaenderung | lokale Tests, Rueckfallpunkt |
| CODEAF-R3 | erhoehtes Risiko | Plan-Gate, Review/Test getrennt dokumentieren |
| CODEAF-R4 | kritische Aenderung | Security-Pruefung, Raphael-/Sonderfreigabe, Release-Impact |
| CODEAF-R5 | systemweit oder irreversibel | in 1.0 nicht produktiv automatisieren |

## 14. Kontroll-Gates

CODEAF 1.0 definiert zehn Gates:

1. Identity Gate
2. Task Gate
3. Role Gate
4. Capability Gate
5. Permission Gate
6. Risk Gate
7. Plan Gate
8. Execution Gate
9. Verification Gate
10. Final Approval Gate

Kein Agent darf ein fehlgeschlagenes Gate selbststaendig umgehen.

## 14.1 Delegation und Unteragenten

Delegation ist in CODEAF 1.0 nur zulaessig, wenn sie im Auftrag ausdruecklich erlaubt ist.

Mindestregeln:

- jede delegierte Einheit braucht eine eigene Agenten- oder Laufidentitaet,
- delegierte Rollen und Capabilities muessen im Auftrag oder Plan enthalten sein,
- Unteragenten duerfen den Scope nicht erweitern,
- der delegierende Agent bleibt fuer Bericht und Nachweis verantwortlich, darf aber keine fremde Pruefung ersetzen,
- kritische Pruefrollen duerfen nicht verdeckt an denselben Implementierungsagenten zurueckdelegiert werden,
- jede Delegation muss auditiert werden.

Ungeplante Unteragenten, freie Agentensuche und automatische Agentenketten bleiben in CODEAF 1.0 verboten.

## 14.2 Konfliktregeln

Bei Widerspruch zwischen Beschreibung, Registry, Konfiguration, Runtime-Verhalten, Auftrag oder beobachtetem Verhalten gelten folgende Regeln:

1. Sicherheit und Deny-by-default haben Vorrang.
2. Explizite Verbote haben Vorrang vor Erlaubnissen.
3. Der engere Scope hat Vorrang vor dem weiteren Scope.
4. Registry- oder Runtime-Abweichungen werden als Gap dokumentiert, nicht still korrigiert.
5. Schreibende oder administrative Aktionen werden bis zur Klaerung blockiert.
6. Konflikte mit CMIBF, AFP, CDF, CDG oder CAWP blockieren produktive Ausfuehrung.

## 15. Vier-Augen-Prinzip

Selbstpruefung darf eine unabhaengige Pruefung ergaenzen, aber bei kritischen Aenderungen nicht ersetzen.

Minimalregel:

- R0 bis R1: Selbstpruefung zulaessig, Abschlussbericht Pflicht.
- R2: Review oder Test dokumentieren.
- R3: getrennte Review- oder Testrolle erforderlich.
- R4: Security- oder Governance-Pruefung plus Raphael-/Sonderfreigabe.
- R5: keine produktive CODEAF-1.0-Autonomie.

## 16. Verbote

CODEAF 1.0 verbietet:

- eigenmaechtige Scope-Erweiterung,
- stille Architekturaenderung,
- Loeschung ohne ausdrueckliche Erlaubnis,
- Veraenderung auftragsfremder Dateien,
- automatischen Git-Commit ohne ausdrueckliche Erlaubnis,
- automatischen Reset,
- Ueberschreiben fremder uncommitteter Aenderungen,
- Vermischung aktiver und historischer Artefakte,
- Ersetzen kanonischer Artefakte durch nicht kanonische Kopien,
- Aenderung von Authentifizierung oder Berechtigungen ohne Sonderfreigabe,
- Annahme erfolgreicher Ausfuehrung ohne Nachweis,
- Verschweigen fehlgeschlagener Tests,
- Erfinden nicht gepruefter Projektzustaende,
- automatische Selbstfreigabe,
- Umgehen von Governance-Gates,
- verdeckte Nebenaenderungen,
- unkontrollierten Netzwerkzugriff,
- Verarbeitung von Geheimnissen ausserhalb freigegebener Grenzen,
- Aktivierung autonomer Wartung durch CODEAF 1.0.

## 17. Audit und Provenienz

Jede Code-Agenten-Ausfuehrung muss mindestens protokollieren:

```text
task_id
agent_id
agent_run_id
agent_version
model_name
model_version
role
capabilities_used
permission_profile
risk_class
start_time
end_time
input_artifacts
read_artifacts
created_artifacts
modified_artifacts
moved_artifacts
deleted_artifacts
commands_executed
tools_used
tests_executed
test_results
warnings
errors
denied_actions
approvals
git_commit_before
git_commit_after
diff_reference
report_reference
final_status
```

Secrets, rohe Tokens, Passwoerter, private Schluessel und sensible Nutzdaten duerfen nicht vollstaendig gespeichert werden. Wo moeglich sind Hashes, Referenzen oder reduzierte Metadaten zu verwenden.

## 18. Abbruchregeln

Ein Code-Agent muss abbrechen oder auf Analyse begrenzen, wenn:

- Scope unklar ist,
- Identitaet nicht gueltig ist,
- Berechtigung fehlt,
- Risikoklasse nicht bestimmbar ist,
- Rueckfallpunkt fehlt,
- unerwartete Arbeitsbaumveraenderungen auftreten,
- ein Konflikt mit kanonischen Regeln besteht,
- Tests nicht ausfuehrbar sind und keine Testgrenze erlaubt ist,
- kritische Sicherheitsbefunde auftreten,
- erforderliche Freigabe fehlt,
- Auftrag und Projektzustand widersprechen.

Bei Abbruch duerfen keine weiteren schreibenden Aktionen erfolgen. Bereits vorgenommene Aenderungen, Risiken und offene Punkte sind zu dokumentieren.

Laufzeitbegrenzungen muessen je Auftrag festgelegt werden:

```text
max_runtime_seconds
max_commands
max_files_read
max_files_changed
max_diff_lines
max_network_requests
max_delegated_agents
```

Ueberschreitungen fuehren mindestens zu Pause oder Abbruch und muessen im Bericht erscheinen.

## 19. Artefaktplan

Empfohlene Folgeartefakte nach Governance-/CMIBF-Klaerung:

| Pfad | Zweck | Format | Status |
| --- | --- | --- | --- |
| `14_documents/CANONICAL_CODE_AGENT_FRAMEWORK_1_0.md` | normativer CODEAF-Rahmen | Markdown | vorbereitet |
| `24_config/canonical_code_agent_framework_1_0.json` | maschinenlesbares Framework-Metamanifest | JSON | aktiv mit Begrenzungen |
| `24_config/canonical_code_agent_roles_1_0.json` | Rollen und Grenzen | JSON | geplant |
| `24_config/canonical_code_agent_capabilities_1_0.json` | Capability-Katalog | JSON | geplant |
| `24_config/canonical_code_agent_permission_profiles_1_0.json` | Permission-Profile | JSON | geplant |
| `24_config/canonical_code_agent_risk_classes_1_0.json` | Risikoklassen | JSON | geplant |
| `24_config/canonical_code_agent_operating_modes_1_0.json` | Betriebsmodi | JSON | geplant |
| `24_config/canonical_code_agent_control_gates_1_0.json` | Gate-Katalog | JSON | geplant |
| `schemas/canonical_code_agent_task_1_0.schema.json` | Auftragsschema | JSON Schema | geplant |
| `schemas/canonical_code_agent_report_1_0.schema.json` | Berichtsschema | JSON Schema | geplant |
| `schemas/canonical_code_agent_registry_1_0.schema.json` | Registry-Erweiterung | JSON Schema | geplant |
| `31_reports/codeaf_1_0_status_report.md` | Pruef- und Abschlussbericht | Markdown | aktiv |

Die spezialisierten Rollen-, Capability-, Permission-, Risiko-, Modus-, Gate-
und Schemaartefakte bleiben geplant. Der aktive Umfang konsolidiert die
minimalen Definitionen in genau einem validierten Framework-Metamanifest.

## 20. Teststrategie

CODEAF-Implementierung benoetigt spaeter:

- Schema-Tests fuer gueltige und ungueltige Agentenauftraege,
- Permission-Tests fuer erlaubte und verbotene Aktionen,
- Gate-Tests fuer fehlende Identitaet, Permission, Freigabe, Rueckfallpunkt und Verifikation,
- Rollen-Tests fuer Schreibverbote und Rollentrennung,
- Audit-Tests fuer vollstaendige Nachweise und verweigerte Aktionen,
- Integrationstests mit CAF, CLMSF, CAIM, CRE, Execution Planner, Orchestrator, CAM, Release Integrity und Audit.

## 21. Minimaler Scope 1.0

Zwingend:

- Begriffsdefinition,
- Agentenidentitaet,
- Rollen,
- Capabilities,
- Permissions,
- Canonical Agent Task,
- Betriebsmodi,
- Risikoklassen,
- Kontroll-Gates,
- Audit- und Berichtspflichten,
- Integrationsvertraege,
- Abbruchregeln.

Zurueckstellen:

- dynamische Agentenauswahl,
- Agentenreputation,
- autonome Wartung,
- selbststaendige Aufgabenzerlegung,
- lernende Code-Agenten,
- formale Verifikation,
- produktive R5-Automation.

## 22. Architekturentscheidung

Empfehlung: GO MIT EINSCHRAENKUNGEN.

Begruendung:

- Nutzen und Bedarf sind klar.
- Wiederverwendbare Bausteine sind vorhanden.
- CODEAF kann als verbindende Governance-Schicht eingefuehrt werden.
- Es darf keine neue Runtime und keine parallele Agentenarchitektur entstehen.
- Vor produktiver Maschinenlesbarkeit sind CMIBF-/AFP-Abdeckung, Schema-Freigabe und Registry-Konsolidierung erforderlich.

CODEAF 1.0 ist als Dokumentations-, Auftrags- und Pruefrahmen aktiv.
Produktive Ausfuehrungsrechte, autonome Schreibrechte oder automatische
Freigaben sind nicht Teil dieser Freigabe.

## 23. Aktiver Umfang

`CanonicalCodeAgentFramework` laedt und validiert das konsolidierte
CODEAF-Metamanifest. Ein Aufrufer kann einen kanonischen Code-Agentenauftrag
explizit auf Pflichtfelder, Rolle, Capabilities, Permission Profile,
Betriebsmodus, Risikoklasse und zehn Kontroll-Gates pruefen.

Die Komponente:

- wird im zentralen Systemstatus registriert,
- wendet Deny-by-default und den Vorrang expliziter Verbote an,
- markiert autonome Wartung und R5-Automation als unzulaessig,
- gibt `execution_authorized` und `final_approval_granted` immer als `false`
  aus,
- aktiviert keinen Agenten und fuehrt keinen Auftrag aus,
- veraendert weder `CodeAgentService` noch CRE, Planner oder Orchestrator,
- korrigiert den dokumentierten Registry-Gap nicht stillschweigend,
- schreibt weder Auditdaten noch Memory.
