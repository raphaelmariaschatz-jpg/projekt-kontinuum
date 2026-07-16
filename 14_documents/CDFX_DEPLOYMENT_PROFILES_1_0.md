# CDFX Deployment Profiles 1.0

> (c) 2026 Raphael Maria Schatz - Projekt Kontinuum. Alle Rechte vorbehalten.

Status: Profilkonzept / deklarative Ausgangsprofile
Gueltig ab: 2026-07-16
Runtime-Wirkung: keine

## 1. Zweck

Dieses Dokument beschreibt die ersten CDFX Deployment Profiles fuer Projekt Kontinuum. Die Profile sind keine Produkte, keine Edition-Codebasen und keine Forks. Sie sind deklarative Aktivierungs-, Begrenzungs- und Validierungsprofile fuer eine gemeinsame Canonical Architecture.

Kanonische Bezeichnung:

- Personal Deployment Profile
- Enterprise Deployment Profile
- Research Deployment Profile

Die Bezeichnung "Edition" kann spaeter fuer externe Kommunikation verwendet werden, soll aber nicht die kanonische Architekturbezeichnung sein.

## 2. Gemeinsame Regeln

Alle Profile muessen:

- den Canonical Core unveraendert erhalten,
- dieselbe Foundation verwenden,
- auf CMIBF, AFP, CAWP, CAM, CDG und Release Integrity rueckfuehrbar sein,
- Frameworks und Capabilities nur referenzieren,
- Core-Deaktivierungen blockieren,
- Abhaengigkeiten und Konflikte validierbar machen,
- eine eindeutige Profil-ID und Version besitzen,
- ohne Forks reproduzierbar bereitstellbar sein.

Profilvererbung ist in CDFX 1.0 nicht vorgesehen. Profilkombinationen sind nur als explizit freigegebene Composite Profiles zulaessig.

## 3. Personal Deployment Profile

Profil-ID: CDFX-PROFILE-PERSONAL-1-0
Status: recommended-concept
Zielgruppe: Privatanwender

Schwerpunkte:

- persoenlicher Assistent
- Lernen
- Wissensmanagement
- Alltag
- Medien
- Kreativitaet
- Planung
- Dokumente
- Sprache
- Bildung

Deployment-Merkmale:

- Einzelbenutzerbetrieb
- lokale oder persoenliche Installation
- reduzierte sichtbare Administration
- Datenschutzfokus
- geringe Ressourcenanforderungen
- verstaendliche Standardkonfiguration

Empfohlene optionale Frameworks:

- CAICF
- CMLF
- CHIF
- CVF optional
- CIF sichtbar reduziert

Nicht empfohlen:

- Mandantenfaehigkeit
- komplexe Enterprise-Rollen
- experimentelle Core-nahe Module ohne Research-Governance

## 4. Enterprise Deployment Profile

Profil-ID: CDFX-PROFILE-ENTERPRISE-1-0
Status: recommended-concept
Zielgruppe: Unternehmen und groessere Organisationen

Schwerpunkte:

- Wissensmanagement
- Unternehmensprozesse
- Governance
- Audit
- Dokumentation
- Compliance
- Teams
- Rollen
- Unternehmensarchitektur
- Reporting

Deployment-Merkmale:

- Mehrbenutzerbetrieb
- erweitertes Rollenmodell
- Rechteverwaltung
- organisationsbezogene Konfiguration
- Auditierbarkeit
- Monitoring
- kontrollierte Administration
- freigegebene Integrationen

Empfohlene optionale Frameworks:

- CEF
- Observability
- Evaluation Center
- Capability Discovery
- Meta-Reasoning mit Governance
- CHIF
- CIF

Abgrenzung:

CEF ist ein aktivierbares Enterprise-Framework, nicht das Deployment-Profil selbst.

## 5. Research Deployment Profile

Profil-ID: CDFX-PROFILE-RESEARCH-1-0
Status: recommended-concept
Zielgruppe: Forschung, Hochschulen, wissenschaftliche Entwicklung

Schwerpunkte:

- Exploration
- Experimente
- Simulation
- Wissenschaft
- Datenanalyse
- Framework-Entwicklung
- Capability-Entwicklung
- Modellvergleich
- Evaluation

Deployment-Merkmale:

- kontrollierte Experimentierraeume
- hohe Konfigurierbarkeit
- Forschungsprotokolle
- Reproduzierbarkeit
- Visualisierung
- Trennung von canonical, experimental und rejected

Empfohlene optionale Frameworks:

- CAICF
- CMLF
- Meta-Reasoning
- Evaluation Center
- Capability Discovery
- Observability
- Adaptive Strategy Engine nur spaeter und governance-pflichtig

Schutzregel:

Experimentelle Komponenten duerfen nie direkt in den Canonical Core uebergehen. Jede Uebernahme benoetigt Architekturentscheidung, Dokumentationspflege, Glossar, Querverweispruefung, Konsistenzpruefung, Freigabe und erst danach Implementierung.

## 6. Erweiterung fuer kuenftige Profile

Neue Profile duerfen nur eingefuehrt werden, wenn sie:

- eine eindeutige Profil-ID besitzen,
- keine bestehende Profilsemantik duplizieren,
- den Canonical Core unveraendert lassen,
- ihre Abhaengigkeiten deklarieren,
- Konflikte und Ausschluesse benennen,
- einen Freigabestatus besitzen,
- in CAM/ALP/Release Integrity nachweisbar werden.

Moegliche spaetere Profile:

- Education Deployment Profile
- Public Sector Deployment Profile
- Offline Deployment Profile
- Developer Deployment Profile
- Evaluation Deployment Profile

Diese Profile sind noch nicht freigegeben.
