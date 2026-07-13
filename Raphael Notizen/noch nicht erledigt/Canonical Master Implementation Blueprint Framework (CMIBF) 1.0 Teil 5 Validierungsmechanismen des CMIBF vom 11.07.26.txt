Kapitel 5 – Validierungsmechanismen
5.1 Zielsetzung

Das CANONICAL MASTER IMPLEMENTATION BLUEPRINT FRAMEWORK (CMIBF) definiert nicht nur die kanonische Architektur eines Softwaresystems, sondern auch die Regeln, nach denen deren korrekte Umsetzung überprüft werden kann.

Jede Implementierung muss objektiv validierbar sein.

Dazu definiert das CMIBF einen mehrstufigen Validierungsprozess.

Dieser stellt sicher, dass

Architekturvorgaben eingehalten werden,
Beziehungen vollständig sind,
Artefakte konsistent bleiben,
Abhängigkeiten korrekt modelliert werden,
Implementierungen reproduzierbar sind,
spätere Erweiterungen keine Architekturverletzungen erzeugen.

Validierung ist somit Bestandteil der Architektur selbst.

5.2 Architekturvalidierung als kontinuierlicher Prozess

Im CMIBF erfolgt Validierung nicht ausschließlich vor einem Release.

Sie begleitet den gesamten Lebenszyklus.

Architekturdefinition
        │
        ▼
Implementierung
        │
        ▼
Strukturprüfung
        │
        ▼
Konsistenzprüfung
        │
        ▼
Semantische Prüfung
        │
        ▼
Dependency-Prüfung
        │
        ▼
Governance-Prüfung
        │
        ▼
Release-Freigabe

Dadurch werden Fehler möglichst früh erkannt.

5.3 Validierungsebenen

Das CMIBF definiert mehrere unabhängige Validierungsschichten.

Ebene 1
Strukturvalidierung

Prüft:

Existenz aller Pflichtartefakte
Vollständigkeit
Verzeichnisstruktur
Namenskonventionen
Versionierung
Identifier

Fragestellung:

Existiert die Architektur vollständig?

Ebene 2
Konsistenzvalidierung

Prüft:

doppelte Definitionen
widersprüchliche Modelle
Mehrdeutigkeiten
inkonsistente Beziehungen
unzulässige Referenzen

Fragestellung:

Ist die Architektur widerspruchsfrei?

Ebene 3
Semantische Validierung

Prüft:

Bedeutung aller Beziehungen
Rollen
Verantwortlichkeiten
erlaubte Verwendung

Beispielsweise:

Service
    nutzt
Datenbank

ist erlaubt.

Datenbank
    kontrolliert
Service

ist semantisch falsch.

Ebene 4
Dependency-Validierung

Prüft:

Zyklen
verbotene Richtungen
Layerverletzungen
fehlende Abhängigkeiten
redundante Kanten

Hier wird der kanonische Dependency Graph analysiert.

Ebene 5
Governance-Validierung

Prüft:

Richtlinien
Freigaben
Verantwortlichkeiten
Reviews
Änderungsprozesse
Ebene 6
Integritätsvalidierung

Prüft

Hashwerte
Signaturen
Versionshistorie
Herkunft
Provenienz
5.4 Validierungsobjekte

Validiert werden sämtliche kanonischen Architekturartefakte.

Dazu gehören insbesondere:

Dokumente
Meta-Modelle
Ontologien
Registry-Dateien
Dependency Graph
API-Definitionen
Konfigurationen
Statusmodelle
Policies
Regeln
Glossare
Roadmaps
Migrationsdefinitionen
Governance-Artefakte

Jedes Artefakt besitzt eigene Validierungsregeln.

5.5 Kanonische Validierungsregeln

Das CMIBF unterscheidet zwischen verschiedenen Regelklassen.

Pflichtregeln (Mandatory)

Müssen erfüllt sein.

Verletzung

→ Architektur ungültig.

Soll-Regeln (Recommended)

Sollten erfüllt werden.

Verletzung

→ Warnung.

Optionale Regeln

Erhöhen Qualität.

Verletzung

→ Information.

Erweiterungsregeln

Gelten ausschließlich für optionale Framework-Erweiterungen.

5.6 Regelhierarchie

Alle Regeln besitzen Prioritäten.

CRITICAL

HIGH

MEDIUM

LOW

INFO

CRITICAL-Regeln blockieren Releases.

HIGH-Regeln verhindern Architekturfreigaben.

MEDIUM-Regeln erzeugen Korrekturmaßnahmen.

LOW-Regeln erzeugen Empfehlungen.

INFO dient ausschließlich der Dokumentation.

5.7 Validierungsworkflow

Der vollständige Workflow lautet:

Start

↓

Artefakte laden

↓

Schema validieren

↓

Meta-Modell prüfen

↓

Ontologie prüfen

↓

Dependency Graph prüfen

↓

Governance prüfen

↓

Policies prüfen

↓

Integrität prüfen

↓

Validierungsbericht erzeugen

↓

Releaseentscheidung
5.8 Validierungsberichte

Jede Validierung erzeugt einen vollständigen Report.

Ein Report enthält mindestens:

Zeitpunkt
Version
Validator
geprüfte Artefakte
Anzahl Regeln
Fehler
Warnungen
Empfehlungen
Status
Signatur

Beispiel:

Validation Report

Version:
1.0

Checked Artifacts:
318

Rules:
1742

Critical:
0

High:
0

Medium:
2

Low:
8

Info:
15

Status:
PASSED
5.9 Kanonischer Architekturstatus

Jede Architektur besitzt einen offiziellen Status.

DRAFT

REVIEW

VALIDATED

CERTIFIED

RELEASED

DEPRECATED

ARCHIVED

Nur

CERTIFIED

darf als kanonische Referenz verwendet werden.

5.10 Architekturzertifizierung

Eine Zertifizierung bestätigt,

dass

alle Pflichtregeln erfüllt sind,
keine kritischen Fehler existieren,
sämtliche Artefakte konsistent sind,
Governance vollständig ist,
Integrität nachgewiesen wurde.

Erst danach erhält eine Architektur den Status

CERTIFIED
5.11 Architektur-Compliance

Compliance beschreibt die Übereinstimmung einer Implementierung mit dem CMIBF.

Es werden drei Konformitätsstufen definiert:

Stufe	Bedeutung
Level 1	Strukturell konform
Level 2	Architektonisch konform
Level 3	Vollständig kanonisch konform

Level 3 stellt die höchste Qualitätsstufe dar.

5.12 Automatisierte Validierung

Alle Prüfungen sollen vollständig automatisierbar sein.

Hierfür definiert das CMIBF standardisierte Validatoren.

Beispiele:

Schema Validator
Dependency Validator
Ontology Validator
Registry Validator
Policy Validator
Governance Validator
Integrity Validator
Consistency Validator

Diese Validatoren bilden gemeinsam die Canonical Validation Engine (CVE) als zentrale Prüfkomponente des CMIBF. Die CVE führt alle Validierungsschritte reproduzierbar aus und erzeugt einen einheitlichen, maschinenlesbaren Validierungsbericht. Dadurch wird sichergestellt, dass dieselbe Architektur unabhängig von Zeitpunkt oder Ausführungsumgebung stets zu identischen Prüfergebnissen führt.

5.13 Architektur als beweisbares System

Das CMIBF versteht Architektur nicht als statische Dokumentation, sondern als formales, überprüfbares System. Jede Aussage über den Zustand einer Architektur muss sich durch definierte Regeln, nachvollziehbare Validierungsprozesse und reproduzierbare Nachweise belegen lassen.

Damit wird die Architektur selbst zu einem qualitätsgesicherten Artefakt. Änderungen, Erweiterungen oder Migrationen können objektiv bewertet werden, ohne von individuellen Interpretationen abhängig zu sein. Validierung ist somit kein nachgelagerter Qualitätsschritt, sondern ein integraler Bestandteil der kanonischen Architektur.

Abschluss von Kapitel 5

Mit diesem Kapitel etabliert das CMIBF einen formalen Nachweis der Architekturkonformität. Während die vorherigen Kapitel beschrieben haben, was eine kanonische Architektur ist und wie ihre Elemente zusammenhängen, definiert Kapitel 5 nun wie ihre Korrektheit bewiesen wird. Damit entsteht die Grundlage für reproduzierbare Zertifizierung, automatisierte Qualitätssicherung und langfristige Wartbarkeit komplexer Softwaresysteme.