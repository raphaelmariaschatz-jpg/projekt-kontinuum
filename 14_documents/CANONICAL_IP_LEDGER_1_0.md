# Canonical Intellectual Property Ledger (CIPL) 1.0

> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

## Zweck

Der Canonical Intellectual Property Ledger (CIPL) 1.0 ist das kanonische Herkunfts- und Urheberregister fuer Projekt Kontinuum. Er dokumentiert nachvollziehbar, wie wesentliche Architekturentscheidungen, Konzepte und Kernartefakte entstanden sind.

CIPL ergaenzt Git, Projektchronik und Governance um eine Herkunftsebene. Er veraendert keine Architektur, keine Runtime und keine Datenfluesse.

## Scope

CIPL dokumentiert zukuenftig fuer wesentliche Architekturartefakte:

- Ursprung
- Urheber
- Zeitpunkt
- Begruendung
- Version
- Zusammenhang
- optionale Git-Referenz
- historische Entwicklung
- Projektchronik- und Governance-Bezug

Die kanonische Creator Identity lautet:

```text
Creator: Raphael Maria Schatz
Creator-ID: RMS-0001
```

Die Creator-ID ist ausschliesslich eine interne kanonische Referenz innerhalb von Projekt Kontinuum. Sie ersetzt keine juristischen Identitaetsnachweise.

## Nicht-Ziele

CIPL ist kein Lizenzsystem, kein DRM, keine Rechteverwaltung und kein Sicherheitssystem. CIPL prueft keine Benutzerrechte, verschluesselt keine Artefakte, bewertet keine juristischen Ansprueche und fuehrt keine automatische Git-Auswertung durch.

## Single Source of Truth

Das kanonische Manifest liegt unter:

```text
24_config/canonical_ip_ledger_1_0.json
```

Dieses Manifest definiert Ledger-Version, Creator Identity, Projektinhaber, Copyright-Halter, Governance-Referenzen, Projektchronik-Referenzen und das vorbereitete Herkunftsdatenschema.

## Herkunftsdatensatz

Ein CIPL-Herkunftsdatensatz kann fuer zukuenftige Architekturartefakte folgende Felder aufnehmen:

- `artifact_id`
- `artifact_name`
- `artifact_type`
- `origin`
- `creator_id`
- `author`
- `created_at`
- `version`
- `rationale`
- `context`
- `related_components`
- `git_reference`
- `historical_development`
- `chronicle_reference`
- `governance_reference`
- `migration_required`

Bestehende Historien muessen nicht migriert werden. CIPL bereitet die strukturierte Erfassung fuer zukuenftige Architekturarbeit vor.

## Vorbereitete Architekturartefakte

CIPL ist fuer die Herkunftsdokumentation folgender Artefaktgruppen vorbereitet:

- CAM
- CRE
- Execution Planner
- Orchestrator Core
- CCP
- CDF
- CDG
- Foundation
- Governance
- Canonical Lifecycle

Diese Eintraege sind vorbereitende Metadatenplaetze. Sie aktivieren keine Runtime-Logik und aendern keine bestehenden Module.

## Integration

### Git

CIPL kann manuelle Git-Referenzen aufnehmen, etwa erster Commit, Architektur-Commit oder Referenz-Hash. Es gibt keine automatische Git-Auswertung.

### Projektchronik

CIPL verweist auf bestehende Projektchroniken. Chroniken werden nicht veraendert und nicht migriert.

### CAM

CIPL ist ein dokumentiertes Governance-Artefakt fuer die kanonische Architektur. CAM wird nicht funktional erweitert.

### Release Integrity

CIPL kann zukuenftig als dokumentarischer Release-Integrity-Pruefpunkt betrachtet werden. In CIPL 1.0 wird kein Release-Gate veraendert.

### Canonical Governance

CIPL ist eine Governance-Komponente fuer Herkunft, Urheberschaft und Entstehungskontext. Er erweitert die Nachvollziehbarkeit, aber nicht die bestehenden Governance-Regeln.

## Schutzgrenzen

- keine Runtime-Aenderung
- keine API-Aenderung
- keine Datenmigration
- keine automatische Rechtepruefung
- keine automatische Git-Auswertung
- keine Aenderung an CAM, CRE, Foundation oder Orchestrator
- keine juristische Bewertung
