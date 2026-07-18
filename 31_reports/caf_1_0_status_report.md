# CAF 1.0 Pruef- und Statusbericht

Stand: 2026-07-18
Auftrag: Canonical Authentication Framework (CAF) 1.0
Status: PARTIALLY_INTEGRATED_WITH_CONDITIONS
Runtime-Wirkung: nicht-autoritative Authentisierungsbeobachtung

## 1. Zusammenfassung

Projekt Kontinuum besitzt bereits einen aktiven lokalen Login-Pfad mit `AuthManager`, Argon2id-Passwortschutz, Sicherheits-Master, GUI-Login und Superadmin-Reauth fuer riskante Aktionen. Daneben existieren kanonische Identitaetsartefakte, Session-Kontextlogik, Rollen-/Permission-Dateien, Authorization-Gates und viele historische Sicherheitsdaten.

CAF 1.0 ist als kanonischer Rahmen erforderlich, weil Identitaet, Authentisierung, Autorisierung, Sitzung und Audit aktuell noch nicht durch ein gemeinsames, unveraenderliches Ergebnisobjekt verbunden sind. Die produktive Authentisierung darf nicht ersetzt werden; empfohlen ist eine additive CAF-Schicht.

## 2. Untersuchte Dateien und Komponenten

- `01_system/kontinuum/core/auth.py`
- `01_system/kontinuum/core/password_security.py`
- `01_system/kontinuum/core/session_context.py`
- `01_system/kontinuum/core/identity_router.py`
- `01_system/kontinuum/foundation/canonical_identity_manager.py`
- `01_system/kontinuum/core/foundation_integrity.py`
- `01_system/kontinuum/tools/oracle_cloud_tools.py`
- `01_system/kontinuum/tools/development_tools.py`
- `11_gui/desktop_gui_34_1.py`
- `11_gui/archive/32_4`, `11_gui/archive/33_0`, `11_gui/archive/34_0`
- `10_security/auth_security_master.json`
- `10_security/roles_permissions.json`
- `10_security/PASSWORT_ZURUECKSETZEN_23.ps1`
- `10_security/backups/`
- `24_config/canonical_identity.json`
- `24_config/canonical_identity_34_1.json`
- `24_config/oracle_cloud.json`
- `32_data/auth_config.json`
- `32_data/admin_command_audit.json`
- `17_tests/test_auth_23.py`
- `17_tests/test_architecture_v24_23.py`
- `17_tests/test_canonical_identity_manager_1_0.py`
- `17_tests/test_development_sandbox_23.py`
- historische Sicherheits- und Auditflaechen in `02_versions/`, `09_backups/`, `17_tests/archive/` und `32_data/02_versions/`

## 3. Bestehende Authentisierungspfade

Aktiver Pfad: GUI ruft `require_login()` auf, erstellt `AuthManager`, prueft `auth.status()` und authentisiert ueber `verify_login(username, password)`.

Privilegierter Pfad: riskante GUI-Aktionen fragen erneut das Superadmin-Passwort ab und rufen `verify_superadmin_confirmation(identity, password, purpose)` auf.

Migrationspfad: `AuthManager` akzeptiert Argon2id und historische SHA-256-Hashes. Bei erfolgreicher Legacy-Anmeldung migriert er den Hash nach Argon2id in aktive Auth-Datei und Sicherheits-Master.

Recovery-/Reset-Pfad: `10_security/PASSWORT_ZURUECKSETZEN_23.ps1` kann den Superadmin-Hash neu setzen und schreibt Backups sowie Audit-Eintraege. Der Lifecycle des Recovery Keys ist noch nicht CAF-vollstaendig.

Session-Pfad: `SessionContext` bindet ein User-Dictionary und kann bei fehlenden Daten aus Namen Creator/Auth-Status ableiten.

## 4. Erkannte Duplikate

- aktive Auth-Daten liegen in `32_data/auth_config.json` und gespiegelt im Sicherheits-Master `10_security/auth_security_master.json`;
- Rollen/Permissions existieren sowohl in Auth-Dateien als auch in `10_security/roles_permissions.json` und in `24_config/canonical_identity.json`;
- GUI-Login-Implementierungen sind in aktiver GUI und archivierten GUI-Versionen mehrfach vorhanden;
- historische `security.json`- und `audit_log.json`-Dateien sind vielfach in Versionen und Backups vorhanden.

Diese Duplikate sind nicht automatisch falsch, aber ohne CAF-Lifecycle riskant, weil Quelle, Gueltigkeit und Reaktivierungsverbot nicht ueberall maschinenlesbar getrennt sind.

## 5. Erkannte Sicherheitsrisiken

Hoch: `SessionContext` kann `authenticated=True`, `is_creator=True` und `SUPERADMIN` aus Namen ableiten. Das darf nur als Legacy-Kompatibilitaet gelten.

Hoch: Oracle Cloud, Self-Extension und Foundation Integrity pruefen mutable Dictionary-Felder wie `authenticated`, `is_superadmin`, `role` und Permissions. Zukuenftig muss ein unveraenderliches CAF-Ergebnis mit Frische und Assurance geprueft werden.

Mittel: Legacy-SHA-256 wird noch akzeptiert. Das ist als Migration vertretbar, darf aber nicht neu erzeugt werden.

Mittel: Recovery-Key-Hash ist entdeckt, aber Ablauf, Rotation, Sperrung und erneute Identitaetspruefung sind nicht als kanonischer Lifecycle definiert.

Mittel: Backups enthalten historische Hashwerte. Im Bericht wurden keine realen Secrets ausgegeben; die Dateien muessen aber durch ALP/CAM klar als historisch und nicht aktiv markiert bleiben.

## 6. Aktive und historische Komponenten

Aktiv:

- `AuthManager`
- `PasswordSecurity`
- `desktop_gui_34_1.py`
- `canonical_identity_manager.py`
- `session_context.py`
- `foundation_integrity.py`
- `oracle_cloud_tools.py`
- `development_tools.py`

Historisch oder Archiv:

- `11_gui/archive/*`
- `17_tests/archive/*`
- `10_security/backups/*`
- `02_versions/*`
- `32_data/02_versions/*`
- historische `security.json`- und `audit_log.json`-Artefakte

## 7. Vorgeschlagenes Identitaetsmodell

CAF fuehrt `identity_id`, `identity_type`, `canonical_name`, `display_name`, `status`, `trust_domain`, Zeitfelder, `authentication_methods`, `credential_references`, `security_state`, `revocation_state`, `metadata`, `provenance` und `schema_version` ein.

Creator und Superadministrator werden kanonisch getrennt: Creator ist ein dauerhafter Vertrauensanker; Superadministrator ist eine privilegierte Rolle. In der Personal-Installation koennen beide auf dieselbe Person zeigen.

## 8. Vorgeschlagene Authentisierungsmethoden

- `PASSWORD_ARGON2ID`: aktiv anschlussfaehig
- `PASSWORD_LEGACY_SHA256`: deprecated, nur Migration
- `RECOVERY_KEY`: entdeckt, Lifecycle-Auflage
- `LOCAL_DEVICE_CONTEXT`: geplant
- `CRYPTOGRAPHIC_KEY`: geplant fuer Agenten/Dienste/Connectoren
- `CERTIFICATE`: geplant
- `TIME_LIMITED_TOKEN`: geplant, nur mit Ablauf und Widerruf
- `OPERATING_SYSTEM_ACCOUNT`: spaeter integrierbar
- `EXTERNAL_IDENTITY_SOURCE`: spaeter, keine CAF-1.0-Cloud-Abhaengigkeit
- `MFA`: spaeter als Assurance-Erhoehung

## 9. Assurance-Level-Modell

- `AAL-0`: nicht authentisiert
- `AAL-1`: einfacher Identitaetsnachweis
- `AAL-2`: starker lokaler Nachweis
- `AAL-3`: privilegierte erneute Authentisierung
- `AAL-4`: Creator-/Systemkern-Zugriff mit Governance-Nachweis

Assurance entsteht aus Methode, Kontext, Frische und Widerrufszustand, nicht aus Rollenbezeichnung oder Namen.

## 10. Session-Modell

Eine Sitzung referenziert ein Authentisierungsergebnis und enthaelt `session_id`, `identity_id`, `authentication_event_id`, `assurance_level`, `created_at`, `last_used_at`, `valid_until`, `reauthentication_after`, `security_context`, `revocation_state`, `downgrade_state` und `logout_state`.

CAF empfiehlt zuerst einen Compatibility Wrapper um die heutige Session-Dictionary-Struktur.

## 11. Recovery-Modell

Recovery muss ein eigener, widerrufbarer Pfad sein. Voraussetzungen sind Identitaetspruefung, Ablauf, Rotation, Audit, Hash-/Key-Referenzen statt Klartext, keine Rechteausweitung und kontrollierte Sperrung nach Nutzung oder Kompromittierung.

## 12. Agenten- und Dienstidentitaeten

Agenten, Dienste, Connectoren, Geraete und externe Anwendungen erhalten eigene Identitaeten. Sie duerfen nicht implizit als Creator oder Superadmin handeln. Privilegierte Aktionen muessen eine menschliche oder systemische Authentisierung referenzieren.

## 13. Integrationsmatrix

| Bereich | Ist | CAF-Ziel |
| --- | --- | --- |
| GUI Login | AuthManager-Dict | CAF-Result plus Kompatibilitaet |
| Superadmin-Reauth | Passwortpruefung | `AAL-3` Reauth-Event |
| Foundation-Aenderung | Auth-Dict + Creator-Name | `AAL-4` + Governance |
| Oracle Cloud | Session-Dict-Gate | CAF-Result + Policy |
| Self-Extension | Session-Dict-Gate | CAF-Result + Policy |
| Canonical Identity | Identitaetsgovernance | Quelle fuer Identitaeten, nicht Passwortpruefung |
| Legacy-Daten | viele Archive | ALP/CAM-Lifecycle und Reaktivierungsverbot |

## 14. Migrationsstrategie

1. CAF-Dokument, CAF-Konzept-JSON und Statusbericht einfuehren.
2. CAF-Ergebnisobjekt additiv implementieren.
3. `AuthManager` erweitert ein erfolgreiches Login um ein CAF-Ergebnis.
4. GUI und privilegierte Tools akzeptieren CAF-Ergebnis zusaetzlich zur alten Struktur.
5. Tests fuer Ablauf, Widerruf, Manipulation, Recovery und Reauth ergaenzen.
6. Legacy-Namensableitung und direkte Session-Dict-Vertrauensannahmen deprecaten.
7. Alte Pfade erst nach Release Integrity, Backup und Freigabe stilllegen.

## 15. Teststrategie

Erforderlich sind funktionale Tests, Sicherheitstests, Integritaetstests, Kompatibilitaetstests und Regressionstests. Bestehende Tests fuer Auth, Argon2id-Migration, Canonical Identity, Oracle Cloud, Development Self-Extension, Foundation Integrity, Runtime, Governance und Release Integrity muessen erhalten bleiben.

## 16. Neu erstellte Artefakte

- `14_documents/CANONICAL_AUTHENTICATION_FRAMEWORK_1_0.md`
- `24_config/canonical_authentication_framework_1_0.json`
- `31_reports/caf_1_0_status_report.md`
- `01_system/kontinuum/core/authentication_framework.py`
- `17_tests/test_authentication_framework_1_0.py`

## 17. Offene Fragen

- Welche Komponente soll langfristig als einziger CAF-Result-Aussteller gelten?
- Soll der Sicherheits-Master aktiv bleiben oder spaeter in eine kanonische Credential Registry ueberfuehrt werden?
- Wie wird Recovery konkret freigegeben, rotiert und widerrufen?
- Welche Agenten benoetigen eigene kryptografische Identitaeten zuerst?
- Wie wird CAF in Release Integrity und CAM vollstaendig referenziert, ohne bestehende Framework-Artefakte ungeprueft zu ueberschreiben?

## 18. Blocker

Kein technischer Blocker fuer die additive Beobachtungsschicht. Blocker fuer produktive Aktivierung:

- fehlendes CAF-Ergebnisobjekt,
- fehlende Session-Ablauf-/Widerrufslogik,
- mutable Session-Dict-Gates,
- Recovery-Lifecycle unvollstaendig,
- historische Sicherheitsdaten noch nicht vollstaendig lifecycle-klassifiziert.

## 19. Restrisiken

Die aktive Beobachtungsschicht reduziert die produktiven Legacy-Risiken nicht
automatisch. Das groesste Restrisiko bleibt die Verwechslung von Identitaet,
Rolle und Authentisierung in Legacy-Kompatibilitaetspfaden.

## 20. Klare Empfehlung

Empfehlung: **CAF 1.0 mit Auflagen freigabefaehig**.

Begruendung:

- die aktive Login-Logik ist erkennbar und testgedeckt;
- Argon2id ist vorhanden;
- historische SHA-256-Migration ist kontrollierbar;
- die Trennung von Identitaet, Authentisierung und Autorisierung ist konzeptionell sauber definierbar;
- Risiken sind bekannt und ohne sofortigen Runtime-Umbau adressierbar;
- produktive Aenderungen waeren aktuell zu frueh und muessen in einem gesonderten Implementierungsauftrag erfolgen.

## 21. Aktiver Umfang und Validierung

Aktiviert wurden ein frozen, nicht-autoritativer CAF-Beobachtungsvertrag und
die zentrale Statusregistrierung. Die Komponente validiert die kanonischen
Felder, Identity Types, Method Classes, Assurance-Mindestwerte, Zeitgrenzen und
verbietet Secret-Felder.

Explizit unveraendert blieben:

- `AuthManager` und `PasswordSecurity`
- GUI-Login und Superadmin-Reauth
- `SessionContext` und dessen dokumentiertes Legacy-Risiko
- Oracle-, Self-Extension- und Foundation-Authorization-Gates
- Credential-, Recovery-, Session- und Audit-Speicherung

Das Ergebnis setzt `issuer_attested=false`, `authentication_performed=false`
und `authorization_usable=false`. Es darf daher keinen bestehenden
Sicherheitsentscheid ersetzen.
