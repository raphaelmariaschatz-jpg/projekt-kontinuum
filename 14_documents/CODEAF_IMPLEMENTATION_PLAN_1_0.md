# CODEAF Implementation Plan 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Phase 1 und begrenzter Teil von Phase 2 umgesetzt
Gueltig ab: 2026-07-18
Runtime-Wirkung: explizite, read-only Auftragsvalidierung

## 1. Ziel

CODEAF wird schrittweise als Kontrollrahmen aktiviert. Agentenlaufzeit,
Schreibrechte, Git-Automation, Orchestrierung und finale Freigabe bleiben
getrennt und nicht freigegeben.

## 2. Phasen

### Phase 1 - Architektur und Abgrenzung

- Bestand und produktiven read-only CodeAgent dokumentieren.
- Rollen, Capabilities, Permissions, Modi, Risiken und Gates definieren.
- CODEAF als kanonische Benennung gegen den Arbeitsnamen CCAF sichern.

Status: umgesetzt.

### Phase 2 - Konsolidierter Auftragsvertrag

- minimales Framework-Metamanifest bereitstellen,
- kanonische Task-Felder und kontrollierte Enumerationen validieren,
- strukturelle Task-Reviews ohne Ausfuehrungswirkung erzeugen.

Status: begrenzt umgesetzt.

### Phase 3 - Spezialisierte Konfigurationen und Schemas

- Rollen-, Capability-, Permission-, Risiko-, Modus- und Gate-Dateien trennen,
- Task-, Report- und Registry-Schemas nach Governance-Freigabe einfuehren.

Status: offen.

### Phase 4 - Registry und Identity

- CAIM-Registry-Gaps kontrolliert pruefen,
- CAF- und CLMSF-Referenzen validieren,
- Agenten- und Laufidentitaeten attestieren.

Status: nicht freigegeben.

### Phase 5 - Kontrollierte Integration

- CRE-, Planner- und Orchestrator-Vertraege separat freigeben,
- unabhaengige Verifikation und Audit anbinden,
- produktive Pilotauftraege erst nach Security- und Release-Gate.

Status: nicht freigegeben.

## 3. Aktive Artefakte

- `14_documents/CANONICAL_CODE_AGENT_FRAMEWORK_1_0.md`
- `14_documents/CODEAF_IMPLEMENTATION_PLAN_1_0.md`
- `24_config/canonical_code_agent_framework_1_0.json`
- `01_system/kontinuum/core/code_agent_framework.py`
- `17_tests/test_code_agent_framework_1_0.py`
- `31_reports/codeaf_1_0_status_report.md`

## 4. Grenzen

- keine Agentenlaufzeit oder Auftragsausfuehrung
- keine autonomen Schreibrechte
- keine automatische Selbstfreigabe
- keine Aenderung des produktiven CodeAgent
- keine stille Registry-Korrektur
- keine Aenderung an CRE, Planner oder Orchestrator
- keine automatische Git-, Audit- oder Memory-Schreibung

## 5. Empfehlung

GO fuer den aktiven Task-Validator; SPAETER fuer Registry-Konsolidierung,
attestierte Identitaet, Runtime-Gates und produktive Ausfuehrung.
