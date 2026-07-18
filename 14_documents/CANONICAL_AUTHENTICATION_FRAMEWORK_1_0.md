# Canonical Authentication Framework (CAF) 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: teilweise integriert, mit Auflagen
Gueltig ab: 2026-07-16
Komponententyp: Authentication Governance Framework / kanonisches Sicherheitsmodell
Runtime-Wirkung: nicht-autoritative Authentisierungsbeobachtung

## 1. Zweck

Das Canonical Authentication Framework (CAF) 1.0 definiert den verbindlichen Rahmen fuer Identitaet, Authentisierung, Authentisierungsergebnis, Sitzung, Wiederherstellung, Agenten- und Dienstidentitaeten sowie Audit in Projekt Kontinuum.

CAF ist keine neue Login-Implementierung. CAF ersetzt keine produktive Authentisierungslogik und deaktiviert keine historischen Komponenten. CAF ordnet vorhandene Pfade ein und bereitet eine spaetere kontrollierte Migration vor. Die aktive Komponente erzeugt nur nicht-autoritative Beobachtungsobjekte; diese duerfen nicht als Login- oder Autorisierungsnachweis verwendet werden.

Grundsatz:

```text
Identitaet beschreibt, wer oder was eine Entitaet ist.
Authentisierung beweist eine behauptete Identitaet.
Autorisierung entscheidet, was danach erlaubt ist.
Sitzung begrenzt die Gueltigkeit des Nachweises.
Audit belegt den Vorgang datensparsam und pruefbar.
```

## 2. Bestandsbild

Die aktive Authentisierung besteht aus `01_system/kontinuum/core/auth.py`, `01_system/kontinuum/core/password_security.py`, `32_data/auth_config.json`, `10_security/auth_security_master.json` und `27_logs/auth_audit.log`.

Die aktive Desktop-GUI `11_gui/desktop_gui_34_1.py` erzwingt einen Login ueber `AuthManager.verify_login()` und verlangt fuer riskante Systemaenderungen eine erneute Superadmin-Bestaetigung ueber `verify_superadmin_confirmation()`.

Die kanonische Identitaetsverwaltung besteht separat in `01_system/kontinuum/foundation/canonical_identity_manager.py` und `24_config/canonical_identity.json`. Sie modelliert Creator, Assistant, Rollen und Permissions, fuehrt aber keine Authentisierung durch.

`01_system/kontinuum/core/session_context.py` stellt eine Laufzeitsicht des aktiven Benutzers bereit. Dieser Pfad enthaelt eine historische Kompatibilitaetslogik, die Creator- und Authentisierungsstatus aus Namen ableiten kann. CAF bewertet das als Legacy-Verhalten, das nicht Grundlage zukuenftiger Authentisierung sein darf.

Historische Sicherheitsdaten, Backups und fruehere Authentisierungsversionen liegen insbesondere in `02_versions/`, `09_backups/`, `10_security/backups/`, `11_gui/archive/`, `17_tests/archive/` und `32_data/02_versions/`.

## 3. Architekturposition

CAF haengt ab von CMIBF, AFP, CAWP, Foundation, Governance, Canonical Identity, CAM, ALP, Release Integrity und Canonical Glossary.

CAF stellt bereit:

- kanonisches Identitaetsmodell,
- Authentisierungsmethodenmodell,
- Assurance-Level-Modell,
- unveraenderliches Authentisierungsergebnis,
- Session-Modell,
- Recovery-Modell,
- Agenten- und Dienstidentitaetsmodell,
- Migrations- und Teststrategie.

CAF ist nicht zustaendig fuer vollstaendige Autorisierung, Rechtevergabe, Lizenzierung, Deployment-Profile oder produktive Geheimnisrotation. Diese Bereiche muessen CAF-Ergebnisse konsumieren, duerfen sie aber nicht selbst erzeugen.

## 4. Kanonisches Identitaetsmodell

Jede authentisierbare Entitaet muss als Identitaet gefuehrt werden koennen:

| Feld | Bedeutung |
| --- | --- |
| `identity_id` | dauerhafte, eindeutige Identitaets-ID |
| `identity_type` | Identitaetstyp |
| `canonical_name` | kanonischer Name |
| `display_name` | sichtbarer Anzeigename |
| `status` | Lebenszyklusstatus |
| `trust_domain` | Vertrauensbereich |
| `created_at` / `updated_at` | Erzeugung und letzte Aenderung |
| `valid_from` / `valid_until` | zeitliche Gueltigkeit |
| `authentication_methods` | erlaubte Methoden |
| `credential_references` | Referenzen auf Nachweise, keine Secrets |
| `security_state` | Sicherheitszustand |
| `revocation_state` | Widerrufszustand |
| `metadata` | nichtkritische Zusatzdaten |
| `provenance` | Herkunft und Freigabe |
| `schema_version` | Schemafassung |

Zulaessige Identitaetstypen in CAF 1.0:

- `CREATOR`
- `SUPERADMIN`
- `HUMAN_USER`
- `ENTERPRISE_USER`
- `RESEARCH_USER`
- `AGENT`
- `SYSTEM_SERVICE`
- `CONNECTOR`
- `DEVICE`
- `EXTERNAL_APPLICATION`

## 5. Architekturentscheidung Creator / Superadministrator

Creator und Superadministrator sollen in CAF 1.0 nicht als dieselbe Rolle behandelt werden.

Entscheidung:

```text
Creator ist ein dauerhafter geschuetzter Vertrauensanker.
Superadministrator ist eine privilegierte Rolle bzw. Autorisierungszuordnung.
In der aktuellen Personal-Installation koennen beide auf dieselbe menschliche Person zeigen.
Kanonisch bleiben sie getrennt.
```

Begruendung:

- Creator-Identitaet ist Foundation- und Provenienz-relevant.
- Superadministrator ist ein operatives Rechteprofil.
- Rollen duerfen keine Authentisierung behaupten.
- Eine spaetere Enterprise- oder Research-Nutzung kann weitere Superadmins benoetigen, ohne die Creator-Identitaet zu vervielfaeltigen.
- Kritische Foundation-Aenderungen koennen beide Bedingungen verlangen: Creator-Identitaet plus Superadmin-Rolle plus erneute Authentisierung.

## 6. Authentisierungsmethoden

CAF 1.0 definiert eine Methode als austauschbaren Nachweistyp. Jede Methode muss mindestens beschreiben:

- `method_id`
- `method_class`
- `supported_identity_types`
- `assurance_level`
- `required_inputs`
- `allowed_scopes`
- `validity_duration`
- `lock_state`
- `renewal_rules`
- `revocation_rules`
- `audit_requirements`
- `fallback_rules`
- `failure_behavior`

In CAF 1.0 sind folgende Methodenklassen vorgesehen:

| Klasse | Status | Hinweis |
| --- | --- | --- |
| `PASSWORD_ARGON2ID` | aktiv anschlussfaehig | heutiger bevorzugter lokaler Pfad |
| `PASSWORD_LEGACY_SHA256` | deprecated | nur kontrollierte Migration, keine neue Nutzung |
| `RECOVERY_KEY` | entdeckt / Auflage | muss neu bewertet und widerrufbar werden |
| `LOCAL_DEVICE_CONTEXT` | geplant | darf Passwort nicht ersetzen |
| `CRYPTOGRAPHIC_KEY` | geplant | fuer Agenten, Dienste und Connectoren |
| `CERTIFICATE` | geplant | fuer spaetere Dienst- und Enterprise-Nutzung |
| `TIME_LIMITED_TOKEN` | geplant | nur mit Ablauf, Bindung und Widerruf |
| `OPERATING_SYSTEM_ACCOUNT` | geplant | externer Nachweis, nicht alleiniger Creator-Beweis |
| `EXTERNAL_IDENTITY_SOURCE` | spaeter | keine Cloud-Abhaengigkeit in CAF 1.0 |
| `MFA` | spaeter | erhoeht Assurance, ersetzt Identitaetsmodell nicht |

## 7. Assurance Levels

CAF 1.0 verwendet folgende Authentisierungsstufen:

| Level | Bedeutung | Beispiele |
| --- | --- | --- |
| `AAL-0` | nicht authentisiert | anonyme Anfrage, reine Anzeige |
| `AAL-1` | einfacher lokaler Nachweis | einfacher Benutzerlogin |
| `AAL-2` | starker lokaler Nachweis | Argon2id-Passwort mit gueltiger Identitaet und Audit |
| `AAL-3` | privilegierte erneute Authentisierung | Superadmin-Bestaetigung fuer riskante Aktion |
| `AAL-4` | Creator-/Systemkern-Zugriff | Creator-Vertrauensanker plus Superadmin plus explizite Freigabe plus Governance-Nachweis |

Assurance entsteht aus Methode, Sicherheitskontext, Frische des Nachweises und Revocation-Status. Sie darf nicht aus Rolle, Anzeigename oder Dialoginhalt abgeleitet werden.

## 8. Kanonisches Authentisierungsergebnis

Ein CAF-Authentisierungsergebnis ist unveraenderlich und nur von CAF-akzeptierten Ausstellern erzeugbar:

```json
{
  "authentication_event_id": "caf-auth-...",
  "identity_id": "creator_001",
  "identity_type": "CREATOR",
  "authentication_method_id": "local-password-argon2id",
  "assurance_level": "AAL-2",
  "authenticated_at": "2026-07-16T00:00:00Z",
  "valid_until": "2026-07-16T01:00:00Z",
  "session_id": "caf-session-...",
  "security_context": {
    "trust_domain": "local_personal_runtime",
    "reauthentication_required_for": ["admin_command", "foundation_change"]
  },
  "device_context": {
    "device_id": null,
    "binding_state": "not_bound"
  },
  "origin": {
    "component": "AuthManager",
    "path": "01_system/kontinuum/core/auth.py"
  },
  "result": "success",
  "schema_version": "1.0"
}
```

Das Ergebnis darf keine Passwoerter, Recovery Keys, Tokens oder rohen Hashwerte enthalten.

## 9. Session-Modell

Eine CAF-Sitzung ist ein zeitlich begrenzter Sicherheitskontext. Sie muss mindestens enthalten:

- `session_id`
- `identity_id`
- `authentication_event_id`
- `assurance_level`
- `created_at`
- `last_used_at`
- `valid_until`
- `reauthentication_after`
- `security_context`
- `revocation_state`
- `downgrade_state`
- `logout_state`

CAF 1.0 empfiehlt fuer die erste Integration einen Compatibility Wrapper um die heutige Session-Dictionary-Struktur. Zukuenftig duerfen Berechtigungspruefungen nicht mehr frei veraenderbare Felder wie `role` oder `authenticated` allein akzeptieren, sondern muessen ein gueltiges CAF-Ergebnis pruefen.

## 10. Recovery-Modell

Recovery ist ein eigener Authentisierungspfad mit hoeherem Risiko. CAF 1.0 verlangt:

- getrennte Identitaetspruefung,
- Hash- oder Key-Referenzen statt Klartext,
- zeitliche Begrenzung,
- Widerruf,
- Audit,
- keine automatische Rechteausweitung,
- keine Umgehung des regulaeren Authentisierungspfads,
- kontrollierte Rotation nach Nutzung.

Der vorhandene Recovery-Key-Bezug im Sicherheits-Master bleibt entdeckt, aber nicht abschliessend freigegeben.

## 11. Agenten- und Dienstidentitaeten

Agenten, Dienste, Connectoren und Geraete muessen eigene Identitaeten erhalten. Sie duerfen nicht implizit als Creator, Superadmin oder menschlicher Benutzer handeln.

Mindestregeln:

- jeder Agent besitzt `identity_id`, `identity_type=AGENT`, `canonical_name`, `trust_domain` und `allowed_scopes`;
- jeder Dienst besitzt `identity_type=SYSTEM_SERVICE`;
- Connectoren besitzen `identity_type=CONNECTOR` und Herkunftsnachweis;
- interne Komponenten duerfen einander nicht allein aufgrund lokalen Prozesskontexts vertrauen;
- privilegierte Werkzeugaufrufe muessen den menschlichen oder System-Nachweis referenzieren.

## 12. Audit

CAF-Audit muss datensparsam, manipulationsbewusst und trennbar von Nutzungslogs sein.

Zu protokollieren:

- Authentisierungserfolg und -fehlschlag,
- Konfigurationsfehler,
- Passwort-Hash-Migration,
- Recovery-Nutzung,
- Session-Erstellung, Ablauf, Logout, Downgrade,
- erneute Authentisierung,
- Widerruf,
- Ausgabe und Annahme von CAF-Ergebnissen.

Nicht zu protokollieren:

- Passwoerter,
- Recovery Keys,
- Tokens,
- rohe Hashwerte,
- vollstaendige geheime Konfigurationen.

## 13. Integrationsmatrix

| Bereich | Heutiger Stand | CAF-Ziel |
| --- | --- | --- |
| GUI Login | `AuthManager.verify_login()` | CAF-Result erzeugen und Session binden |
| Superadmin-Bestaetigung | Passwort erneut via AuthManager | `AAL-3` Reauth-Event |
| Foundation-Aenderung | Auth-Dict plus Creator-Name | `AAL-4` mit Creator-Anker und Governance |
| Oracle Cloud Change | Session-Dict-Gate | CAF-Result plus Autorisierung |
| Self-Extension | Session-Dict-Gate | CAF-Result plus Policy Gate |
| Canonical Identity | getrennt von Auth | Identitaetsquelle, keine Passwortpruefung |
| Legacy SHA-256 | akzeptiert und migriert | deprecated, messbar ausphasen |
| Recovery | vorhanden, unvollstaendig bewertet | gesondertes widerrufbares Verfahren |

## 14. Migrationsstrategie

Phase 1: CAF als Konzept und Statusbericht einfuehren. Keine Runtime-Aenderung.

Phase 2: CAF-Datenschema und Ergebnisobjekt additiv implementieren. Bestehender Login bleibt fuehrend.

Phase 3: `AuthManager.verify_login()` gibt zusaetzlich ein CAF-Ergebnis aus. Bestehende GUI-Dictionaries bleiben kompatibel.

Phase 4: GUI, Oracle Cloud, Development Self-Extension und Foundation Integrity akzeptieren CAF-Ergebnisse als zusaetzliche Pruefung.

Phase 5: Legacy-Namensableitungen und direkte Session-Dict-Vertrauensannahmen werden als deprecated markiert.

Phase 6: Alte Pfade erst nach Tests, Release Integrity, Backup und expliziter Freigabe stilllegen.

## 15. Teststrategie

Pflichttestklassen:

- gueltige und ungueltige Authentisierung,
- gesperrte Identitaet,
- abgelaufener oder widerrufener Nachweis,
- Session-Erstellung, Ablauf, Logout und Downgrade,
- erneute Authentisierung,
- Recovery,
- Brute-Force- und Replay-Schutz,
- Session-Invalidierung,
- Privilegienanhebung,
- Token- und Recovery-Widerruf,
- manipulierte Authentisierungsergebnisse,
- Agentenidentitaetsfaelschung,
- Downgrade-Versuch,
- Schema-Validierung,
- Audit-Vollstaendigkeit,
- keine Secrets in Logs,
- keine direkten CAF-Umgehungen,
- Kompatibilitaet mit bestehendem Creator-Login und GUI.

## 16. Statusmodell

CAF-Statuswerte:

- `NOT_PRESENT`
- `DISCOVERED`
- `ANALYZED`
- `DEFINED`
- `PARTIALLY_INTEGRATED`
- `VERIFIED`
- `ACTIVE`
- `DEGRADED`
- `BLOCKED`
- `REVOKED`

CAF 1.0 selbst steht nach der additiven Aktivierung auf `PARTIALLY_INTEGRATED`.
Die produktive Authentisierung und Autorisierung stehen weiterhin nicht auf
`ACTIVE` unter CAF.

## 17. Freigabeempfehlung

CAF 1.0 ist konzeptionell mit Auflagen freigabefaehig.

Auflagen:

- kein produktiver Auth-Refactor ohne gesonderten Auftrag,
- keine neue Geheimnisspeicherung ohne Schema- und Security-Review,
- Legacy-SHA-256 nur als Migrationspfad,
- Creator-Status nie mehr aus Namen ableiten,
- Berechtigungsgates muessen mittelfristig CAF-Ergebnisse statt frei veraenderbarer Dicts pruefen,
- Recovery-Key-Lifecycle muss vor Aktivierung vollstaendig definiert werden.

## 18. Aktiver Umfang

`CanonicalAuthenticationFramework` laedt und validiert Identitaetstypen,
Methodenklassen, Assurance Levels und das kanonische Ergebnisfeldmodell. Ein
Aufrufer kann einen bereits extern beobachteten Authentisierungsvorgang als
deterministisches, frozen CAF-Objekt strukturieren.

Die Komponente:

- wird im zentralen Systemstatus registriert,
- prueft Identitaetstyp, Methode, Mindest-Assurance und Zeitgrenzen,
- weist Passwoerter, Hashes, Tokens, Recovery Keys und private Schluessel ab,
- authentisiert niemanden und erstellt keine Sitzung,
- setzt `issuer_attested`, `authentication_performed` und
  `authorization_usable` immer auf `false`,
- aendert weder `AuthManager` noch GUI oder privilegierte Verbraucher,
- schreibt weder Auditdateien noch Memory.
