Teil 3 – Kapitel 3
Kanonische Architekturartefakte und Architekturontologie
3. Kanonische Architekturartefakte und Architekturontologie
3.1 Zielsetzung

Dieses Kapitel definiert die kanonische Ontologie des Canonical Master Implementation Blueprint Framework (CMIBF).

Die Ontologie beschreibt nicht die Implementierung eines Systems.

Sie beschreibt die formalen Objekte, aus denen jede kanonische Architektur besteht.

Damit entsteht ein gemeinsames Architekturvokabular, welches für sämtliche zukünftigen Frameworks verpflichtend ist.

Beispiele:

CAF
CAM
CSPF
CLMSF
CDF
CRE
Execution Planner
Governance Framework
zukünftige Erweiterungen

Alle verwenden dieselbe Ontologie.

3.2 Grundprinzip

Ein Architekturmodell besteht niemals ausschließlich aus Dokumenten.

Es besteht aus Architekturartefakten.

Ein Artefakt besitzt:

Identität
Verantwortung
Beziehungen
Lebenszyklus
Versionierung
Historie
Semantik

Nicht Dateien bilden die Architektur.

Architekturartefakte bilden die Architektur.

Dateien sind lediglich deren physische Repräsentation.

3.3 Definition eines Architekturartefakts

Ein Architekturartefakt ist jede eindeutig identifizierbare Einheit der kanonischen Architektur.

Beispiele:

Framework

Modul

API

Registry

Policy

Regel

Datenmodell

Workflow

Governance-Regel

Capability

Service

Komponente

Interface

Konfiguration

Manifest

Dokument

Testdefinition

Migration

Adapter

Connector

Runtime-Komponente

Auditdefinition

Deploymentbeschreibung

Blueprint

3.4 Eigenschaften eines Artefakts

Jedes Architekturartefakt besitzt mindestens folgende Eigenschaften.

Identität

globale Artifact-ID

kanonischer Name

Kurzname

Typ

Version

Status

Besitzer

Verantwortliche Ebene

Semantik

Beschreibung

Zweck

Verantwortung

Eingaben

Ausgaben

Nebenwirkungen

Garantien

Nichtziele

Beziehungen

Parent

Children

Dependencies

Required By

Implements

Extends

Uses

References

Produces

Consumes

Governance

Owner

Reviewer

Freigabestatus

Änderungsverlauf

Verifikationsstatus

Compliance-Status

Lebenszyklus

Entwurf

Review

Freigegeben

Implementiert

Validiert

Aktiv

Deprecated

Archiviert

3.5 Architekturontologie

Die Ontologie beschreibt sämtliche Objekttypen der Architektur.

Mindestens folgende Klassen existieren.

Framework

oberste logische Architektur

Beispiele:

CMIBF

CAF

CAM

CDF

CLMSF

CSPF

Blueprint

Implementierungsbeschreibung

Beinhaltet

Architektur

Regeln

Prozesse

Roadmaps

Governance

Layer

Architekturebene

Beispiele

Foundation

Canonical

Operational

Implementation

Governance

Documentation

Component

funktionale Einheit

Beispiele

Registry

Validator

Resolver

Manager

Orchestrator

Engine

Planner

Service

stellt Funktionalität bereit

Beispiele

Validation Service

Audit Service

Planning Service

Runtime Service

Policy

verbindliche Architekturregel

Beispiele

Naming Policy

Dependency Policy

Lifecycle Policy

Security Policy

Rule

konkrete prüfbare Einzelregel

Beispiele

FND-ID-001

CAM-ID-034

CSP-ID-121

Contract

definiert Schnittstellen

API

Schema

Datenaustausch

Versionierung

Registry

verwaltet kanonische Objekte

Beispiele

Artifact Registry

API Registry

Capability Registry

Rule Registry

Manifest

beschreibt Bestandteile

Versionen

Abhängigkeiten

Hashes

Kompatibilität

Model

formale Beschreibung

Datenmodell

Objektmodell

Architekturmodell

Semantisches Modell

Workflow

Ablaufdefinition

Review

Implementierung

Migration

Freigabe

Deployment

Capability

beschreibt Fähigkeiten

Nicht Implementierungen.

Test

Validierung

Unit-Test

Integrationstest

Compliance-Test

Architekturtest

Report

Ergebnisse

Status

Audit

Compliance

Historie

3.6 Beziehungen zwischen Artefakten

Artefakte existieren niemals isoliert.

Zwischen ihnen bestehen definierte Beziehungen.

Typische Beziehungstypen:

contains

implements

extends

requires

depends_on

references

generates

consumes

inherits

validates

tests

documents

governs

replaces

supersedes

archives

3.7 Architekturgraph

Aus den Beziehungen entsteht ein vollständiger Architekturgraph.

Dieser besitzt folgende Eigenschaften:

gerichteter Graph

zyklusfreie Kernabhängigkeiten

mehrfache Referenzen erlaubt

Versionsbeziehungen

Historienbeziehungen

Governance-Beziehungen

Implementierungsbeziehungen

Der Architekturgraph bildet die objektive Wahrheit der Architektur.

3.8 Semantische Eindeutigkeit

Jedes Objekt besitzt exakt eine kanonische Bedeutung.

Synonyme dürfen existieren.

Die Semantik darf jedoch niemals mehrdeutig sein.

Damit wird verhindert:

uneinheitliche Begriffe

verschiedene Interpretationen

doppelte Verantwortlichkeiten

semantische Konflikte

3.9 Trennung von Semantik und Implementierung

Die Architektur beschreibt:

was existiert.

Die Implementierung beschreibt:

wie etwas umgesetzt wird.

Diese Trennung ist verpflichtend.

Dadurch bleibt die Architektur dauerhaft stabil.

Implementierungen können sich verändern.

Die Architektur bleibt unverändert.

3.10 Kanonische Architekturartefakte als Single Source of Truth

Jedes Architekturartefakt besitzt genau eine kanonische Definition.

Alle weiteren Darstellungen sind davon abzuleiten.

Beispiele:

JSON

YAML

Markdown

Diagramme

Code

Dokumentation

Statusberichte

Visualisierungen

Registry-Einträge

dürfen ausschließlich aus dem kanonischen Artefakt erzeugt werden.

3.11 Architekturontologie als Grundlage aller zukünftigen Frameworks

Die hier definierte Ontologie ist frameworkübergreifend verbindlich.

Kein zukünftiges Framework darf eigene grundlegende Architekturbegriffe definieren, wenn diese bereits Bestandteil dieser Ontologie sind.

Neue Begriffsklassen dürfen ausschließlich durch Erweiterung der Ontologie eingeführt werden.

Die Ontologie bildet damit den semantischen Kern des gesamten Projekt-Kontinuum-Ökosystems.

Abschluss von Kapitel 3

Mit Kapitel 3 ist der objektorientierte Architekturkern des CMIBF definiert. Während Kapitel 2 die formale Meta-Architektur mit Ebenen, Verantwortlichkeiten und Informationsflüssen festgelegt hat, beschreibt Kapitel 3 die grundlegenden Bausteine dieser Architektur: die kanonischen Architekturartefakte, ihre Eigenschaften, Beziehungen und ihre gemeinsame Ontologie. Damit verfügen alle zukünftigen Frameworks über ein einheitliches semantisches Fundament.