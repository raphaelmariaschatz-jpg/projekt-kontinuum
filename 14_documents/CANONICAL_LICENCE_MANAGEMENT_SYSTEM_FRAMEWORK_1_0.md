# Canonical Licence Management System Framework (CLMSF) 1.0

Datum: 2026-07-18
Status: aktiv mit Begrenzungen
Runtime-Wirkung: explizite strukturelle Deklarationspruefung
Produktive Aenderungen: keine
Revision: 1.1 nach fachlicher Gesamtbewertung, GO mit Auflagen

## 1. Zweck

Das Canonical Licence Management System Framework (CLMSF) 1.0 definiert den kanonischen Architekturrahmen fuer zukuenftige Lizenzmechanismen in Projekt Kontinuum. Es ist kein Lizenzmanager, kein DRM-System und kein Authentisierungssystem. Die aktive Komponente prueft nur explizit uebergebene Lizenzdeklarationen strukturell und besitzt keine produktive Durchsetzungswirkung.

CLMSF beschreibt:

- Lizenzidentitaeten,
- Lizenzregistrierung,
- Lizenzlebenszyklus,
- Validierungs- und Auditprinzipien,
- Compliance- und Sicherheitsgrenzen,
- Export- und Erweiterungspunkte,
- Integrationsregeln zu bestehenden kanonischen Frameworks.

## 2. Architekturpruefung

Die bestehende Architektur folgt dem Architecture First Principle:

```text
Idee -> Architekturanalyse -> CMIBF-Definition oder CMIBF-Erweiterung
-> Architekturpruefung -> Freigabe -> CAC -> kanonische Artefakte
-> Implementierung -> Validierung und Tests -> Release -> Betrieb
-> Monitoring -> kontrollierte Evolution
```

CLMSF passt in diese Ordnung nur als kanonisches Framework unterhalb von CMIBF und oberhalb spaeterer Implementierungen. Es darf keine Runtime-Logik vorwegnehmen.

### Relevante Bestandsanker

- `CMIBF 1.0`: normative Architekturquelle und Architekturverfassung.
- `CDF 1.0`: praktischer Entwicklungsrahmen fuer Auftragsbearbeitung, Pruefung und Abschluss.
- `CDG 1.0`: Entwicklungsgovernance mit Architecture-First-Regeln.
- `CAF 1.0`: Identitaet, Authentisierung, Session, Recovery und Audit, aber keine Lizenzierung.
- `CAMap 1.0`: Architekturkarte fuer Layer, Abhaengigkeiten und Status.
- `CAM / ALP / CADP`: Artefaktklassifikation, Lifecycle, aktive kanonische Speicherorte.
- `CCP 1.0`: kontrollierter Aenderungslebenszyklus fuer kanonische Aenderungen.
- `Release Integrity`: spaeteres Release-Gate fuer Implementierungsartefakte, Manifest, Hashes und Reports.
- `CIPL 1.0`: Herkunfts- und Urheberregister; ausdruecklich kein Lizenzsystem.
- bestehende Registry-/Manager-Muster: Canonical API Registry, Canonical Artifact Manager, Canonical Architecture Manager, Canonical Identity Manager.

## 3. Architekturposition

CLMSF gehoert primaer in den Canonical Layer.

```text
CMIBF
  -> AFP / CAWP / CPI / CAC
  -> Governance: AGF, CDG, CDF, CCP
  -> Canonical Layer
       -> CAF
       -> CAM / ALP / CADP
       -> CIPL
       -> CLMSF
  -> Operational Layer
       -> spaeterer Licence Manager / Licence Validation Service
  -> Learning Layer
       -> spaetere Compliance-Evidenz, Audit-Auswertung, Governance-Review
```

CLMSF stellt Architekturvertraege bereit. Spaetere Runtime-Komponenten duerfen diese Vertraege konsumieren, aber nicht selbst die kanonische Lizenzarchitektur definieren.

## 4. Nicht-Ziele

CLMSF 1.0 implementiert nicht:

- produktive Lizenzpruefung,
- Aktivierungsschluessel,
- Lizenzserver,
- Bezahlsysteme,
- DRM,
- Benutzerrechteverwaltung,
- Authentisierung,
- automatische Lizenzvergabe,
- automatische Sperrung,
- Cloud-Synchronisierung,
- juristische Einzelfallbewertung.

## 5. Komponentenmodell

### 5.1 Canonical Licence Identity

Eine Lizenzidentitaet beschreibt eine dauerhaft referenzierbare Lizenz als kanonisches Objekt.

Pflichtfelder:

- `licence_id`: stabile eindeutige ID, z. B. `LIC-KONTINUUM-YYYY-NNNN`.
- `licence_type`: z. B. `PRIVATE`, `RESEARCH`, `ENTERPRISE`, `INTERNAL`, `OPEN_SOURCE_COMPATIBILITY`, `TRIAL`.
- `schema_version`: Version des Lizenzschemas.
- `licence_version`: Version der konkreten Lizenzdefinition.
- `owner_reference`: Referenz auf Identitaet oder Organisation, kein Authentisierungsnachweis.
- `issuer_reference`: Herausgeber oder Governance-Quelle.
- `licensed_subject`: kanonischer Bezugspunkt der Lizenz.
- `origin`: Herkunft, z. B. manuelle Freigabe, Vertrag, Forschungsvereinbarung.
- `status`: Lebenszyklusstatus.
- `valid_from`, `valid_until`: zeitliche Gueltigkeit.
- `licence_profile_reference`: Verweis auf ein kanonisches Lizenzprofil.
- `scope`: erlaubter Nutzungsbereich.
- `constraints`: Einschraenkungen.
- `provenance`: Bezug auf CIPL, Governance-Entscheidung oder Projektchronik.
- `history_reference`: Verweis auf Audit-/Historienkette.
- `integrity`: Hash-/Signatur-Metadaten, keine Secrets.

`licensed_subject` beantwortet die Frage, worauf sich eine Lizenz konkret bezieht. Zulaessige Subject-Klassen koennen sein:

- Benutzer,
- Organisation,
- Geraet,
- Installation,
- API,
- Connector,
- Forschungseinheit,
- Deployment,
- Produkt- oder Modulgruppe.

`owner_reference` beschreibt den Inhaber oder Verantwortlichen. `licensed_subject` beschreibt das lizenzierte Zielobjekt. Beide Felder duerfen identisch referenzieren, muessen es aber nicht.

Lizenztypen bleiben ausdruecklich offen erweiterbar. Die oben genannten Typen sind Startklassen, keine abgeschlossene Enumeration. Neue Lizenztypen muessen spaeter ueber Registry-, Policy- oder Profilkonfiguration ergaenzbar sein, ohne die CLMSF-Architektur selbst zu aendern.

Abgrenzung zu CAF: CAF beweist Identitaet; CLMSF referenziert Identitaeten nur. Lizenzbesitz darf nicht als Authentisierung gelten.

### 5.2 Canonical Licence Registry

Die Registry ist die kanonische Quelle fuer Lizenzmetadaten, nicht zwingend fuer vollstaendige Lizenztexte.

Aufgaben:

- Registrierung von Lizenzdatensaetzen,
- eindeutige Identitaet und Duplikatschutz,
- Versionierung,
- Such- und Referenzmodell,
- Status- und Lifecycle-Nachvollziehbarkeit,
- Integritaetspruefung,
- Verknuepfung mit Audit, CIPL, CAF-Identitaeten und Governance.

Registry-Regeln:

- append-only Historie fuer relevante Statuswechsel,
- keine stillen Ueberschreibungen,
- jeder aktive Datensatz besitzt genau einen kanonischen Speicherort,
- jede Aenderung benoetigt CCP-konformen Kontext,
- Hashes werden ueber kanonisch serialisierte Nutzdaten gebildet,
- Secrets, private Schluessel und Zahlungsdaten gehoeren nicht in die Registry.

### 5.3 Canonical Licence Lifecycle

Empfohlenes Statusmodell:

```text
Draft
  -> Proposed
  -> Approved
  -> Active
  -> Suspended
  -> Reinstated
  -> Expiring
  -> Expired
  -> Revoked
  -> Archived
```

Bewertung der Zusatzstatus:

- `Proposed`: sinnvoll, weil Projekt Kontinuum zwischen Entwurf und Governance-Freigabe unterscheidet.
- `Approved`: sinnvoll, weil eine Lizenz vorbereitet und freigegeben sein kann, bevor sie aktiv wird.
- `Reinstated`: sinnvoll, um Wiederaktivierung nach Suspendierung auditierbar zu machen.
- `Expiring`: optionaler Warnzustand, rein abgeleitet, nicht zwingend persistiert.

Verbotene Abkuerzungen:

- `Draft -> Active` ohne Governance-Kontext,
- `Revoked -> Active` ohne neue Lizenzversion oder expliziten Reinstatement-Prozess,
- Loeschung statt Archivierung.

### 5.4 Canonical Licence Validation

CLMSF definiert nur Validierungsarten, keine Implementierung.

Zukuenftige Validierungsdimensionen:

- Identitaet: Existiert die Lizenz-ID?
- Integritaet: Stimmen Hash, Signatur und Registry-Referenz?
- Zeit: Liegt die Nutzung innerhalb des Gueltigkeitsfensters?
- Status: Ist die Lizenz aktiv oder gesperrt?
- Scope: Passt die angefragte Nutzung zum Lizenzumfang?
- Kompatibilitaet: Passt die Lizenz zu Produkt, Deployment, Nutzerklasse und Policy?
- Vertrauen: Ist die Herkunft genehmigt und nicht widerrufen?
- Compliance: Stimmen interne Richtlinien und externe Lizenzbedingungen?

Validierungsergebnisse sollen unveraenderliche Ergebnisobjekte sein, analog zum CAF-Muster:

- `validation_id`,
- `licence_id`,
- `checked_at`,
- `checker_reference`,
- `result`,
- `assurance_level`,
- `licence_assurance_level`,
- `findings`,
- `audit_reference`,
- `schema_version`.

CLMSF sollte ein eigenes Vertrauensmodell vorbereiten. Empfohlene `licence_assurance_level`:

- `LOW`: unvollstaendige oder nur lokal bekannte Lizenzmetadaten.
- `MEDIUM`: formal gueltiger Datensatz mit nachvollziehbarer Herkunft.
- `HIGH`: integritaetsgepruefter und governance-gepruefter Datensatz.
- `CANONICAL`: kanonisch freigegebene, auditierte und releasefaehige Lizenzreferenz.

Dieses Level beschreibt das Vertrauen in den Lizenzdatensatz. Es ersetzt weder CAF-Assurance noch Benutzerrechte.

### 5.5 Canonical Licence Policies

CLMSF sollte Policy-Bereiche definieren, aber keine konkreten Vertragsregeln erfinden.

Policy-Gruppen:

- `issuance_policy`: Vergabe und Freigabe.
- `usage_policy`: erlaubte Nutzungsarten.
- `transfer_policy`: Uebertragung, Mandantenwechsel, Besitzwechsel.
- `renewal_policy`: Verlaengerung und Reaktivierung.
- `suspension_policy`: temporaere Sperrung.
- `revocation_policy`: endgueltiger Widerruf.
- `archive_policy`: Archivierung und Evidenzerhalt.
- `export_policy`: erlaubte Exportformate.
- `compliance_policy`: Kompatibilitaets- und Reviewpflichten.

### 5.6 Canonical Licence Profile

Ein Licence Profile beschreibt wiederverwendbare Lizenzparameter, die nicht jedes Mal als freie `scope`- oder `constraints`-Felder dupliziert werden sollen.

Moegliche Profilfelder:

- `profile_id`,
- `profile_name`,
- `profile_version`,
- `allowed_licence_types`,
- `runtime_duration`,
- `activation_model`,
- `connector_rights`,
- `api_rights`,
- `deployment_model`,
- `offline_allowed`,
- `cloud_allowed`,
- `export_rights`,
- `transfer_rules`,
- `compliance_requirements`,
- `audit_requirements`,
- `schema_version`.

Licence Profiles verhindern, dass spaetere Lizenzmodelle als unstrukturierte Sonderfaelle wachsen. Sie sind Architekturbausteine, keine Runtime-Entscheider.

### 5.7 Canonical Licence Audit

Lizenzereignisse muessen revisionssicher dokumentierbar sein.

Audit-Felder:

- `event_id`,
- `timestamp`,
- `actor_reference`,
- `action`,
- `licence_id`,
- `previous_status`,
- `new_status`,
- `source`,
- `reason`,
- `result`,
- `hash_before`,
- `hash_after`,
- `governance_reference`,
- `release_reference`,
- `schema_version`.

Audit-Regel: Lizenzereignisse duerfen nicht direkt in Learning oder Memory uebernommen werden. Sie koennen spaeter als Evidenz fuer Governance-Review referenziert werden.

### 5.8 Canonical Licence Security

CLMSF-Sicherheitsanforderungen:

- manipulationssichere Hashes fuer kanonische Datensaetze,
- optionale digitale Signaturen fuer spaetere Phasen,
- Duplikatschutz ueber ID, Owner, Scope, Fingerprint und Herkunft,
- Revocation Chain fuer widerrufene Lizenzen,
- Licence Assurance Level fuer Vertrauen in Herkunft, Integritaet und Freigabe,
- Trennung von Metadaten, Secrets und privaten Schluesseln,
- keine Lizenzentscheidung allein aus Dateinamen oder UI-Text,
- keine automatische Rechteeskalation durch Lizenzbesitz.

### 5.9 Canonical Licence Compliance

Compliance soll als Review- und Regelmodell vorbereitet werden.

Zu pruefende Klassen:

- Projektinterne Nutzung,
- private Nutzung,
- Forschungslizenz,
- Unternehmenslizenz,
- Open-Source-Kompatibilitaet,
- Connector-/API-Nutzung,
- Cloud-/Offline-Nutzung,
- Export- oder Weitergabebeschraenkungen.

CLMSF sollte Compliance-Bewertungen als eigene Evidenzobjekte fuehren, nicht als Teil des reinen Lizenzstatus.

### 5.10 Canonical Licence Export

Erlaubte Exportformen:

- JSON fuer maschinenlesbare Lizenzmetadaten,
- Markdown fuer Governance- und Architekturberichte,
- Audit-Protokolle fuer Release Evidence,
- zusammenfassende Reports fuer Review und Freigabe.

Exportregeln:

- keine Secrets,
- keine privaten Schluessel,
- Datenschutzpruefung vor personenbezogenen Exporten,
- Hash-/Signaturinformationen duerfen exportiert werden,
- Export selbst wird auditierbar.

## 6. Beziehungen zu bestehenden Frameworks

### CMIBF

CLMSF muss im CMIBF als kanonisches Framework definiert oder dort referenziert werden, bevor eine Implementierung entsteht.

### CDF / CDG

Jede spaetere Umsetzung folgt dem CDF-Arbeitszyklus und CDG-Regeln: Orientierung, Konsistenzpruefung, kanonische Einordnung, kontrollierte Aenderung, Dokumentation, Tests, Release.

### CAF

CAF stellt authentisierte Identitaeten und Assurance bereit. CLMSF konsumiert diese Informationen, erzeugt sie aber nicht. Lizenzvalidierung darf niemals Login ersetzen.

### CAM / ALP / CADP

CLMSF-Artefakte muessen eindeutige Artefaktklassen und Speicherorte erhalten. Historische Lizenzreports sind Release Evidence; aktive Framework-Dokumente sind Canonical; spaetere Runtime-Komponenten koennen Runtime Required sein.

### CCP

Lizenzstatuswechsel und Registry-Aenderungen sind kanonische Aenderungen, sobald sie verbindliche Wirkung haben. Sie benoetigen Change Proposal, Pre-Audit, Governance Review, kontrolliertes Update, Dokumentationssync und Release Integrity Gate.

### CIPL

CIPL dokumentiert Herkunft und Urheber. CLMSF kann CIPL-Referenzen verwenden, ersetzt CIPL aber nicht. CIPL bleibt kein Lizenzsystem.

### Release Integrity

Release Integrity sollte spaeter pruefen:

- Vorhandensein der CLMSF-Dokumente,
- Gueltigkeit der Registry-Konfiguration,
- Hash-Integritaet der kanonischen Lizenzdatensaetze,
- Audit-Snapshot,
- Testabdeckung spaeterer Implementierungen,
- keine unregistrierten aktiven Lizenzkomponenten.

### Canonical Dependencies

CLMSF sollte in CAMap und spaeter im kanonischen Dependency Graph als eigener Architekturbaustein gefuehrt werden.

Empfohlenes Abhaengigkeitsmodell:

```text
CLMSF
  depends on CMIBF
  depends on AFP / CAWP / CPI / CAC
  depends on AGF / CDG / CDF
  depends on CCP
  depends on CAM / ALP / CADP
  depends on CIPL
  depends on Release Integrity
  optionally consumes CAF identity and assurance references
  optionally informs Canonical Glossary, CAMap and CKS
```

Wichtig: `depends on CAF` darf nur als optionale Konsum-Beziehung verstanden werden. CLMSF benoetigt fuer Lizenzmetadaten eine Identitaetsreferenz, erzeugt aber keine Authentisierung und ist nicht Teil des CAF-Vertrauensnachweises.

## 7. Erweiterungspunkte

CLMSF 1.0 sollte folgende Erweiterungen ausdruecklich vorbereiten:

- digitale Signaturen,
- externe Lizenzserver,
- Offline-Lizenzen,
- Mehrmandantenfaehigkeit,
- Unternehmenslizenzen,
- Forschungslizenzen,
- Privatlizenzen,
- API- und Connector-Lizenzen,
- Cloud-Deployment,
- Device-Binding,
- Trust-Chain-Modelle,
- offene Lizenztypen ohne Architekturumbau,
- Licence Profiles fuer wiederverwendbare Nutzungs-, Deployment-, Connector-, Offline-, Cloud- und Exportregeln,
- Compliance-Profile,
- maschinenlesbare Lizenzbedingungen,
- Export- und Audit-Profile.

## 8. Moegliche Dateistruktur

Nur als Zielbild fuer spaetere freigegebene Umsetzung:

```text
14_documents/
  CANONICAL_LICENCE_MANAGEMENT_SYSTEM_FRAMEWORK_1_0.md
  CLMSF_IMPLEMENTATION_PLAN_1_0.md

24_config/
  canonical_licence_management_system_framework_1_0.json
  canonical_licence_registry_1_0.json
  canonical_licence_policy_1_0.json

31_reports/
  clmsf/
    CLMSF_ARCHITECTURE_REVIEW_1_0.md
    CLMSF_RELEASE_READINESS_REPORT_1_0.md

32_data/
  licence_registry/
    audit/
    exports/
    history/

01_system/kontinuum/core/
  canonical_licence_registry.py        # spaeter, nicht in CLMSF 1.0
  canonical_licence_validation.py      # spaeter, nicht in CLMSF 1.0

17_tests/
  test_canonical_licence_registry_1_0.py       # spaeter
  test_canonical_licence_validation_1_0.py     # spaeter
  test_clmsf_release_integrity_1_0.py          # spaeter
```

## 9. Erforderliche Dokumente

Fuer eine spaetere kanonische Umsetzung werden empfohlen:

1. `CANONICAL_LICENCE_MANAGEMENT_SYSTEM_FRAMEWORK_1_0.md`
2. `CLMSF_IMPLEMENTATION_PLAN_1_0.md`
3. `CLMSF_POLICY_MODEL_1_0.md`
4. `CLMSF_REGISTRY_SCHEMA_1_0.md`
5. `CLMSF_AUDIT_MODEL_1_0.md`
6. `CLMSF_SECURITY_AND_COMPLIANCE_MODEL_1_0.md`
7. `CLMSF_RELEASE_INTEGRITY_PROFILE_1_0.md`
8. `CLMSF_STATUS_REPORT_1_0.md`

## 10. Risiken

### Verantwortlichkeitsvermischung

Groesstes Risiko ist die Vermischung von Lizenzierung mit Authentisierung, Autorisierung, CIPL oder Runtime-Rechten. Gegenmassnahme: CLMSF referenziert Identitaeten und Policies, erzeugt aber keine Authentisierung oder Berechtigungen.

### Verdeckte Runtime-Implementierung

Ein Lizenzframework koennte unbewusst als produktiver Lizenzmanager gebaut werden. Gegenmassnahme: CLMSF 1.0 bleibt Dokumentation und Konfiguration ohne Runtime-Wirkung.

### Juristische Scheingenauigkeit

Technische Lizenzmetadaten ersetzen keine Rechtspruefung. Gegenmassnahme: Compliance als Review- und Evidenzmodell, nicht als automatische Rechtsentscheidung.

### Duplikate und parallele Wahrheiten

Mehrere Lizenzlisten oder verstreute Lizenzdaten wuerden CADP/ALP verletzen. Gegenmassnahme: genau eine aktive Registry pro Zweck.

### Datenschutz und Secrets

Lizenzdaten koennen personenbezogen sein. Gegenmassnahme: Datensparsamkeit, Referenzen statt Klartextdaten, keine Secrets in Registry oder Export.

## 11. Empfehlungen

1. CLMSF 1.0 als eigenes kanonisches Framework im Canonical Layer fuehren.
2. Vor Implementierung CMIBF-Abdeckung und Governance-Freigabe herstellen.
3. CAF, CIPL, CAM und Release Integrity nur anbinden, nicht duplizieren.
4. Lizenzidentitaet, Registry, Lifecycle, Validation Result und Audit Event als getrennte Architekturkonzepte definieren.
5. `licensed_subject` als Pflichtbezug jeder Lizenz aufnehmen.
6. Lizenztypen offen erweiterbar halten und nicht als abgeschlossene Enumeration behandeln.
7. Licence Assurance Level und Licence Profiles in der Spezifikation vorbereiten.
8. In CLMSF 1.0 keine produktive Lizenzvalidierung und keinen Lizenzmanager implementieren.
9. Eine spaetere Implementierung erst nach CLMSF Implementation Plan, Schemafreigabe, Tests und Release-Integrity-Profil beginnen.

## 12. Integrationsstrategie

### Phase 0 - Architekturannahme

- CLMSF-Bericht pruefen.
- Entscheidung treffen, ob CLMSF als eigenstaendiges Framework in CMIBF aufgenommen wird.
- Begriffe in Canonical Glossary ergaenzen.

### Phase 1 - Kanonische Spezifikation

- CLMSF-Hauptdokument erstellen.
- Registry-, Policy-, Audit- und Security-Modelle beschreiben.
- CAMap-Beziehung und Dependency Graph ergaenzen.

### Phase 2 - Konfigurationsentwurf

- Maschinenlesbare Framework-Konfiguration aktivieren.
- Registry- und Policy-Schemas spaeter separat vorbereiten.
- Noch keine produktiven Datensaetze und keine Runtime-Integration.

### Phase 3 - Implementierungsplan

- Spaeteren `CanonicalLicenceRegistryManager` nur planen.
- Schnittstellen zu CAF, CAM, Release Integrity und Governance formal beschreiben.
- Tests und Release-Gates definieren.

### Phase 4 - Kontrollierte Umsetzung

- Erst nach separatem Auftrag.
- Manager, Tests, Statuscheck und Release Integrity Profil implementieren.
- Keine Migration ohne Audit und Freigabe.

## 13. Statusbericht

Pruefstatus:

- Auftrag gelesen: ja.
- Bestehende Architektur geprueft: ja, mit Schwerpunkt auf CMIBF/CDF/CAF/CAMap/CDG/ALP/CADP/CCP/CIPL/Release Integrity und Manager-Mustern.
- Produktive Dateien geaendert: nein.
- Runtime-Komponenten erstellt: ja, begrenzte read-only Strukturpruefung.
- Implementierung begonnen: ja, ohne Lizenzdurchsetzung.
- CLMSF-Zielarchitektur vorgeschlagen: ja.
- Fachliche Gesamtbewertung eingearbeitet: ja, GO mit Auflagen.
- Ergaenzt: `licensed_subject`, offene Lizenztypen, Licence Assurance Level, Canonical Dependencies und Licence Profiles.

Bewertung:

CLMSF 1.0 ist architektonisch sinnvoll und als begrenzte, nicht
rechtsverbindliche Strukturpruefung aktiv. Die sauberste Einordnung ist der
Canonical Layer mit Governance-Anbindung an CMIBF, CDF, CDG, CCP,
CAM/ALP/CADP, CAF, CIPL und Release Integrity.

## 14. Aktiver Umfang

`CanonicalLicenceManagementSystemFramework` validiert die neue
maschinenlesbare CLMSF-Definition und prueft explizit uebergebene
Lizenzdeklarationen auf Pflichtfelder, registrierte Starttypen, Lifecycle,
Zeitfenster, Subject-Struktur und Secret-Freiheit.

Die Komponente:

- wird im zentralen Systemstatus registriert,
- erzeugt deterministische strukturelle Review-Ergebnisse,
- stellt keine Lizenz aus und aktiviert keine Lizenz,
- erteilt keine Rechte und authentisiert keine Identitaet,
- trifft keine juristische oder Compliance-Einzelfallentscheidung,
- mutiert keine Registry und schreibt kein Memory,
- fuehrt keine Sperre, Zahlung oder DRM-Funktion aus.
