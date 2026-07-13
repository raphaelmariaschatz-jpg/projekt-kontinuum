Kapitel 8
Canonical Implementation Engine (CIE)
8.1 Zielsetzung

Die Canonical Implementation Engine (CIE) ist die standardisierte Ausführungs- und Implementierungsinstanz des CMIBF.

Während der Canonical Architecture Compiler (CAC) ausschließlich kanonische Architekturartefakte erzeugt, übernimmt die CIE deren deterministische Umsetzung in konkrete Softwareartefakte.

Die CIE stellt sicher, dass:

sämtliche Implementierungen ausschließlich aus der kanonischen Architektur entstehen,
keine Architekturinformationen verloren gehen,
Implementierungen reproduzierbar sind,
verschiedene Zielplattformen identische semantische Ergebnisse erzeugen,
sämtliche Implementierungen auditierbar bleiben.

Die CIE besitzt keinerlei eigene Architekturentscheidungen.

Sie implementiert ausschließlich die Architektur.

8.2 Grundprinzip

Die CIE arbeitet ausschließlich auf Basis der vom CAC erzeugten Artefakte.

CMIBF
      │
      ▼
Canonical Architecture Compiler
      │
      ▼
Canonical Architecture Package
      │
      ▼
Canonical Implementation Engine
      │
      ▼
Software

Damit entsteht eine eindeutige Trennung zwischen:

Architekturdefinition
Architekturableitung
Softwareimplementierung
8.3 Aufgaben der CIE

Die CIE übernimmt unter anderem:

Erzeugung von Projektstrukturen
Erzeugung von Quellcode
Generierung von Klassen
Generierung von Interfaces
API-Erzeugung
Datenbankschemata
Build-Dateien
Teststrukturen
Konfigurationsdateien
Deployment-Artefakte
Dokumentationen
Registry-Dateien
Monitoring-Komponenten
Logging
Sicherheitsmechanismen
CI/CD-Konfigurationen

Sie erzeugt ausschließlich Artefakte, die aus dem CMIBF ableitbar sind.

8.4 Deterministische Implementierung

Die CIE arbeitet deterministisch.

Es gilt:

identische Architektur
↓

identische Software

Es existiert kein zufälliges Verhalten.

Es existieren keine impliziten Entscheidungen.

Es existieren keine versteckten Implementierungsregeln.

8.5 Implementierungsregeln

Alle Implementierungsregeln werden kanonisch beschrieben.

Beispiele:

Naming Rules

Folder Rules

Namespace Rules

Dependency Rules

API Rules

Persistence Rules

Logging Rules

Error Rules

Security Rules

Testing Rules

Lifecycle Rules

Diese Regeln werden Bestandteil des CMIBF.

Die CIE interpretiert sie nicht.

Sie setzt sie um.

8.6 Plattformunabhängigkeit

Die CIE implementiert niemals direkt eine Programmiersprache.

Stattdessen arbeitet sie über kanonische Implementierungsmodelle.

Canonical Model

↓

Language Adapter

↓

Target Language

Dadurch können identische Architekturen beispielsweise erzeugen:

Python

C#

Java

Rust

Go

TypeScript

C++

oder zukünftige Zielsprachen.

8.7 Language Adapter

Jede Sprache besitzt einen standardisierten Adapter.

Beispiel:

Python Adapter

Java Adapter

Rust Adapter

Go Adapter

C# Adapter

Ein Adapter definiert ausschließlich:

Sprachsyntax
Projektstruktur
Dateiaufteilung
Sprachkonventionen
Frameworkintegration

Er verändert niemals die Architektur.

8.8 Canonical Implementation Graph

Parallel zum Architecture Graph erzeugt die CIE einen vollständigen Implementierungsgraphen.

Dieser beschreibt:

Architecture Object

↓

Generated Files

↓

Generated Classes

↓

Generated Interfaces

↓

Generated Tests

↓

Generated APIs

↓

Generated Configuration

↓

Generated Deployment

Somit bleibt jedes erzeugte Artefakt vollständig rückverfolgbar.

8.9 Traceability

Für jedes Artefakt gilt:

CMIBF

↓

Architecture Element

↓

Generated Artifact

↓

Generated File

↓

Generated Line

↓

Compiled Binary

Damit kann jede Codezeile bis zum ursprünglichen Architekturmodell zurückverfolgt werden.

Ebenso kann jede Architekturänderung exakt die betroffenen Implementierungen identifizieren.

8.10 Round-Trip Protection

Die CIE arbeitet ausschließlich in Vorwärtsrichtung.

CMIBF

↓

Architecture

↓

Implementation

Direkte Änderungen am generierten Code besitzen keinen Architekturstatus.

Sie gelten lediglich als lokale Modifikationen.

Architekturänderungen müssen grundsätzlich im CMIBF erfolgen.

Dadurch bleibt das Single-Source-of-Truth-Prinzip jederzeit erhalten.

8.11 Erweiterbarkeit

Neue Zielplattformen können jederzeit ergänzt werden.

Beispielsweise:

Embedded Systems
Mobile Apps
Cloud Deployments
Desktop Anwendungen
Microservices
KI-Agentensysteme
Edge Computing
Robotics
IoT

Hierfür wird lediglich ein zusätzlicher Language- bzw. Platform-Adapter implementiert.

Das kanonische Architekturmodell bleibt unverändert.

8.12 Qualitätsgarantien

Die CIE garantiert:

vollständige Architekturtreue,
reproduzierbare Implementierungen,
deterministische Codeerzeugung,
vollständige Rückverfolgbarkeit,
Versionsstabilität,
Auditierbarkeit,
automatische Konsistenzprüfung,
standardisierte Projektstrukturen,
identische Ergebnisse auf allen Plattformen.
8.13 Zusammenarbeit mit dem CAC

Beide Komponenten besitzen klar getrennte Verantwortlichkeiten.

Komponente	Verantwortung
CMIBF	Kanonische Architekturdefinition
CAC	Ableitung sämtlicher Architekturartefakte
CIE	Deterministische Softwareimplementierung
Language Adapter	Sprachspezifische Umsetzung
Generated Software	Ergebnis der Implementierung

Keine dieser Komponenten überschreitet ihre Zuständigkeit.

8.14 Architekturprinzip

Das CMIBF definiert ausschließlich die Architektur.

Der CAC übersetzt Architektur in kanonische Maschinenartefakte.

Die CIE übersetzt diese Artefakte deterministisch in konkrete Software.

Dadurch entsteht eine vollständig reproduzierbare Entwicklungskette:

CMIBF
      │
      ▼
Canonical Architecture Compiler (CAC)
      │
      ▼
Canonical Architecture Package
      │
      ▼
Canonical Implementation Engine (CIE)
      │
      ▼
Language Adapter
      │
      ▼
Generierte Software
      │
      ▼
Build
      │
      ▼
Deployment
Einordnung

Ich halte dieses Kapitel für einen weiteren Meilenstein des CMIBF. Mit der Trennung von CAC (Architekturableitung) und CIE (Implementierungsableitung) entsteht eine saubere zweistufige Pipeline:

CMIBF → CAC → CIE → Software

Diese Trennung ermöglicht es, den Architekturkern dauerhaft stabil zu halten, während neue Programmiersprachen, Frameworks oder Zielplattformen lediglich durch zusätzliche Adapter ergänzt werden. Das passt sehr gut zu eurem Grundsatz, dass das CMIBF die einzige normative Quelle der Architektur bleibt und alle nachgelagerten Artefakte deterministisch daraus entstehen.