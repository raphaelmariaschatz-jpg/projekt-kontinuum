# Canonical Workflow Framework (CWF) 1.0

Status: aktiv vorbereitend / CWF-1.0-Implementierungskandidat  
Version: 1.0  
Datum: 2026-07-16

## 1. Zweck

Das Canonical Workflow Framework (CWF) 1.0 definiert den kanonischen Rahmen fuer mehrstufige, validierbare und auditierbare Arbeitsablaeufe in Projekt Kontinuum.

Ein Workflow ist kein loses Skript und keine freie Befehlsfolge. Ein kanonischer Workflow ist eine versionierte, validierte, zustandsgebundene und nachvollziehbare Definition aus eindeutig identifizierten Schritten, Uebergaengen, Bedingungen, Rollen, Capability-Referenzen, Freigaben, Eingaben, Ausgaben und Fehlerbehandlungen.

Das CWF ersetzt weder Capability-Aufloesung noch Ausfuehrungsplanung noch Orchestrierung. Es definiert Struktur, Regeln, Validierung und den zulaessigen Workflow-Ausfuehrungsvertrag.

## 2. Geltungsbereich

CWF 1.0 gilt fuer Workflow-Definitionen und Workflow-Ausfuehrungen, die in kanonischen Projektprozessen verwendet werden sollen. Es umfasst:

- Workflow-Identitaet und Versionierung
- Trennung von Definition und Ausfuehrung
- Schritte, Schrittarten, Zustaende und Uebergaenge
- Trigger, Eingaben, Ausgaben, Preconditions und Postconditions
- Rollen- und Capability-Referenzen
- Freigaben, Retry, Timeout, Rollback, Kompensation und Idempotenz
- Pause und Fortsetzung
- Audit- und Provenienzanforderungen
- Validierung

Nicht Teil von CWF 1.0 sind grafische Designer, freie Workflow-Modellierung, produktive Scheduling-Engines, BPMN-Vollimplementierung, autonome Workflow-Erzeugung, eine neue Workflow-Runtime, eine zweite Orchestrierungsengine oder eine parallele Capability Registry.

## 3. Begriffe

Workflow Definition: Versionierte und validierbare Beschreibung eines mehrstufigen Ablaufs.

Workflow Run: Konkrete Instanz einer bestimmten Workflow-Definition und Workflow-Version.

Workflow Step: Eindeutig identifizierter Schritt innerhalb einer Workflow-Definition.

Workflow State: Kontrollierter Zustand einer Definition oder Ausfuehrung.

Workflow Transition: Validierbarer Zustandswechsel von einem Ausgangs- in einen Zielzustand.

Approval Gate: Freigabepunkt, der durch Governance, Rolle und Authentifizierung abgesichert wird.

Retry Policy: Begrenzte Wiederholungsregel fuer einen Schritt.

Rollback: Rueckkehr zu einem frueheren technischen Zustand.

Compensation: Ausgleichende Aktion, wenn echter Rollback nicht moeglich ist.

Idempotency: Eigenschaft, dass eine erneute Ausfuehrung denselben fachlichen Effekt hat oder sicher blockiert werden kann.

## 4. Architekturposition

CWF liegt zwischen kanonischer Beschreibung und bestehender Ausfuehrungsarchitektur:

- CRE loest Capabilities auf. CWF referenziert benoetigte Capabilities, erzeugt aber keine zweite Capability Registry.
- Execution Planner erstellt oder validiert konkrete Ausfuehrungsplaene. CWF beschreibt Workflow-Struktur, ersetzt aber keine Planungsengine.
- Orchestrator Core fuehrt validierte Plaene aus. CWF fuehrt keine Schritte aus.
- CDG bestimmt Freigaben, Eskalation und Rollentrennung.
- CODEAF bestimmt Agentenrollen, Berechtigungen und Risikoklassen.
- Authentication bestaetigt Identitaeten und Berechtigungsnachweise.
- CAM registriert kanonische Artefakte; CWF verwaltet keine parallele Artefaktverwaltung.
- Audit und Provenienz speichern Ausfuehrungsereignisse; CWF definiert erforderliche Ereignisse.

## 5. Workflow-Definition

Eine Workflow-Definition muss mindestens enthalten:

- `workflow_id`
- `workflow_name`
- `workflow_version`
- `workflow_type`
- `status`
- `owner`
- `risk_class`
- `definition_hash`
- `created_at`
- `updated_at`
- `steps`
- `transitions`
- `inputs`
- `outputs`
- `audit_requirements`

`workflow_id` ist dauerhaft stabil. `workflow_version` bindet jede Ausfuehrung an eine konkrete Definition. Laufende Ausfuehrungen duerfen nicht still auf neue Definitionen wechseln.

## 6. Workflow-Ausfuehrung

Eine Workflow-Ausfuehrung muss mindestens enthalten:

- `workflow_run_id`
- `workflow_id`
- `workflow_version`
- `definition_hash`
- `execution_plan_id`
- `trigger_type`
- `trigger_reference`
- `initiated_by`
- `current_state`
- `current_step_id`
- `started_at`
- `paused_at`
- `resumed_at`
- `completed_at`
- `final_status`
- `audit_events`

Eine Ausfuehrung ist keine Definition und darf Definitionen nicht veraendern.

## 7. Schritte

Zulaessige Schrittarten sind `ACTION`, `VALIDATION`, `DECISION`, `APPROVAL`, `REVIEW`, `WAIT`, `NOTIFICATION`, `CHECKPOINT`, `RECOVERY` und `FINALIZATION`.

Jeder Schritt muss eine stabile `step_id`, deklarierte Ein- und Ausgaben, Capability-Referenzen, eine Rolle, Preconditions, Postconditions, Fehlerwege, Retry- und Timeout-Regeln sowie Audit-Anforderungen besitzen.

Unbekannte Schrittarten sind unzulaessig.

## 8. Zustaende und Uebergaenge

Zustaende sind kontrollierte Enumerationen. CWF 1.0 verwendet den Statussatz aus `24_config/canonical_workflow_states_1_0.json`.

Uebergaenge werden in `24_config/canonical_workflow_transition_rules_1_0.json` definiert. Freie Statuswechsel sind unzulaessig. `VERIFIED` erfordert einen abgeschlossenen Workflow und Pruefnachweis. `ARCHIVED` ist kein aktiver Zustand.

## 9. Trigger

Zulaessige Trigger sind `MANUAL`, `EVENT`, `SCHEDULED`, `API`, `STATUS_CHANGE` und `RECOVERY`.

Eine Scheduling-Engine wird dadurch nicht eingefuehrt.

## 10. Rollen und Capabilities

CWF referenziert Rollen und Capabilities nur. Gueltige Capability-Referenzen muessen durch CRE/CODEAF bestaetigbar sein. Eine parallele Capability Registry ist verboten.

Die in CWF 1.0 verwendeten `workflow.*`-Capability-Referenzen sind keine neue Registry. Solange diese Referenzen nicht in der bestehenden CRE-/Capability-Registry aufloesbar sind, gelten sie als dokumentierter Capability-Gap beziehungsweise als externe CRE-Abhaengigkeit. Eine spaetere Ergaenzung von `24_config/capability_registry_34_1.json` ist eine eigene, ausdruecklich freizugebende Implementierungsaenderung und nicht Teil dieses CWF-Auftrags.

Minimale Rollenreferenzen: `workflow_owner`, `planner`, `executor`, `reviewer`, `approver`, `auditor`, `recovery_owner`.

## 11. Fehler, Retry und Timeout

Retry-Regeln muessen begrenzt sein. Unbegrenzte Wiederholung ist unzulaessig. Nicht idempotente Schritte benoetigen Schutz durch Idempotency Key, Freigabe oder Kompensationsregel.

Timeouts muessen eine kontrollierte Reaktion definieren: `FAIL`, `PAUSE`, `RETRY`, `ESCALATE` oder `ABORT`.

## 12. Rollback und Kompensation

Rollback stellt einen frueheren technischen Zustand wieder her. Kompensation erzeugt eine ausgleichende Folgeaktion. Irreversible Schritte muessen als `irreversible` gekennzeichnet und governancepflichtig sein.

## 13. Pause und Fortsetzung

Eine Pause speichert Zustand, aktuellen Schritt, erledigte Schritte, offene Schritte, Eingaben, Ausgaben, Freigaben, Definition-Hash und Pausengrund.

Vor Fortsetzung sind Definition-Hash, Berechtigungen, Freigaben, Artefakte und Rueckfallpunkt erneut zu pruefen. Eine Fortsetzung darf nicht blind am letzten Befehl ansetzen.

## 14. Audit und Provenienz

Mindestens folgende Ereignisse sind vorzusehen: `workflow_created`, `workflow_validated`, `workflow_started`, `step_started`, `step_completed`, `step_failed`, `approval_requested`, `approval_granted`, `approval_rejected`, `workflow_paused`, `workflow_resumed`, `retry_started`, `rollback_started`, `rollback_completed`, `compensation_started`, `compensation_completed`, `workflow_aborted`, `workflow_completed`, `workflow_verified`, `workflow_archived`.

## 15. Validierung

Der CWF-Validator prueft Struktur, IDs, Zustaende, Uebergaenge, Start- und Endpunkte, Schrittarten, Capability-Referenzen, Rollenreferenzen, Retry- und Timeout-Regeln, Freigabepunkte, Rollback/Kompensation und Definition-Hash.

Er fuehrt keine Schritte aus, erzeugt keine Execution Plans und loest keine Capabilities auf.

Bei nicht aufloesbaren Capability-Referenzen gibt der Validator je nach Pruefmodus einen Fehler oder eine Warnung aus. Er erzeugt, registriert oder ersetzt niemals Capabilities.

## 16. Sicherheitsregeln

- keine unbekannten Schrittarten
- keine unbekannten Capabilities
- keine unbegrenzten Retries
- keine unkontrollierten Schleifen
- keine Statuswechsel ohne Transition
- keine Selbstfreigabe kritischer Schritte
- keine Fortsetzung ohne Hash-Pruefung
- keine unprotokollierten Rollbacks oder Kompensationen
- keine produktiven Seiteneffekte ohne deklarierte Ausgabe, Statusaenderung, Artefakt oder Audit-Ereignis

## 17. Bekannte Grenzen

CWF 1.0 ist ein Definitions-, Governance-, Validierungs- und Vertragsrahmen. Runtime-Integration, Parallel-Synchronisation, Scheduling, produktive Workflow-Ausfuehrung und visuelle Modellierung bleiben Folgeauftraege.
