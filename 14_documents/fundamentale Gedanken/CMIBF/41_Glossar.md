# CANONICAL MASTER IMPLEMENTATION BLUEPRINT FRAMEWORK (CMIBF) 1.0

## Teil 41 – Glossar

**Dokument-ID:** CMIBF-1.0-TEIL-41  
**Dokumenttyp:** Kanonisches Glossar  
**Version:** 1.0  
**Status:** Zur Review und Freigabe  
**Datum:** 12.07.2026  
**Normative Quelle:** CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md

---

## 41.1 Zweck und Geltungsbereich

Dieses Glossar definiert die verbindliche Bedeutung zentraler Begriffe des **Canonical Master Implementation Blueprint Framework (CMIBF) 1.0**.

Es dient als gemeinsame sprachliche Grundlage für:

- Architektur und Governance,
- Framework-, Modul- und Artefaktentwicklung,
- Prüfung, Validierung und Zertifizierung,
- Compiler-, Build-, Deployment- und Runtime-Prozesse,
- Dokumentation, Implementierung und Betrieb,
- menschliche Autoren, Prüfer und Entwickler,
- automatisierte Werkzeuge und den Canonical Architecture Compiler.

Die Definitionen dieses Glossars gelten für das gesamte CMIBF und für alle daraus abgeleiteten Artefakte.

---

## 41.2 Normativer Status

1. Jeder kanonische Begriff besitzt innerhalb des CMIBF genau eine verbindliche Bedeutung.
2. Abweichende, konkurrierende oder widersprüchliche Definitionen sind unzulässig.
3. Das Glossar erläutert das CMIBF, ersetzt jedoch keine normative Regel eines Fachkapitels.
4. Bei einem Widerspruch zwischen Glossar und Fachkapitel gilt die präzisere normative Regel des Fachkapitels.
5. Festgestellte Widersprüche müssen im CMIBF korrigiert werden; abgeleitete Artefakte dürfen nicht manuell angepasst werden.
6. Neue Begriffe und Bedeutungsänderungen werden ausschließlich durch eine kontrollierte Änderung des CMIBF eingeführt.
7. Maschinenlesbare Glossarformate werden deterministisch aus dem CMIBF erzeugt.

---

## 41.3 Aufbau eines kanonischen Glossareintrags

Ein vollständiger Glossareintrag kann folgende Merkmale besitzen:

- **Begriff-ID**
- **Bezeichnung**
- **Kurzbezeichnung oder Akronym**
- **Definition**
- **Kategorie**
- **Normativer Status**
- **Verwandte Begriffe**
- **Referenzierte CMIBF-Kapitel**
- **Version**
- **Lifecycle-Status**

Die nachfolgenden Einträge bilden die menschenlesbare Fassung des Glossars.

---

# 41.4 Kanonische Begriffe

## A

### Abgeleitetes Artefakt

Ein durch den **Canonical Architecture Compiler** oder einen anderen ausdrücklich autorisierten Generator aus dem CMIBF erzeugtes Ergebnis.

Abgeleitete Artefakte können unter anderem sein:

- Registries,
- Dependency Graphs,
- Ontologien,
- Validierungsregeln,
- Implementierungsregeln,
- Blueprints,
- Konfigurationsdateien,
- Statusmodelle,
- Reports,
- Maschinenlesbare Kataloge.

Abgeleitete Artefakte sind nicht selbst die normative Architekturquelle und dürfen nicht direkt als Ersatz für eine Änderung des CMIBF bearbeitet werden.

**Kategorie:** Artefakt, Compiler, Governance  
**Verwandte Begriffe:** CMIBF, CAC, Single Source of Truth, Reproduzierbarkeit

---

### Abhängigkeit

Eine explizit beschriebene Beziehung, bei der eine Architekturkomponente, ein Artefakt, ein Framework, ein Modul, ein Dienst oder ein Prozess eine andere Einheit benötigt, voraussetzt, verwendet oder beeinflusst.

Jede Abhängigkeit muss mindestens Quelle, Ziel, Typ, Richtung, Status und Versionsbezug eindeutig beschreiben.

**Kategorie:** Architekturbeziehung  
**Verwandte Begriffe:** Dependency Graph, Dependency Resolution, Referenzintegrität

---

### Abwärtskompatibilität

Eigenschaft einer neuen Version, bestehende zulässige Verwendungen, Verträge, Daten oder Integrationen einer früheren Version weiterhin zu unterstützen.

Abwärtskompatibilität ist anzustreben, darf jedoch nicht stillschweigend angenommen werden.

**Kategorie:** Versionierung, Lifecycle  
**Verwandte Begriffe:** Breaking Change, Deprecation, Migration

---

### Agent

Eine eindeutig identifizierte, registrierte und kontrollierte Ausführungseinheit, die innerhalb definierter Fähigkeiten, Werkzeuge, Rechte, Policies und Governance-Grenzen Aufgaben bearbeitet.

Ein Agent darf keine nicht autorisierten Fähigkeiten, Schnittstellen oder Selbstfreigaben verwenden.

**Kategorie:** Runtime, Ausführung  
**Verwandte Begriffe:** Capability, Orchestrierung, Governance, Tool

---

### Änderungsantrag

Ein formal dokumentierter Vorschlag zur Änderung, Erweiterung, Korrektur oder Ablösung eines normativen Bestandteils des CMIBF.

Ein Änderungsantrag führt nicht automatisch zu einer Architekturänderung. Er muss geprüft, bewertet, freigegeben oder abgelehnt werden.

**Kategorie:** Governance  
**Verwandte Begriffe:** ADR, Freigabe, Evolution

---

### Anhang

Ein ergänzender Bestandteil des CMIBF, der vertiefende Informationen, Beispiele, Vorlagen, Referenzen, Tabellen oder technische Zusatzinformationen enthält.

Ein Anhang ist nur dann normativ, wenn sein normativer Status ausdrücklich gekennzeichnet ist.

**Kategorie:** Dokumentation  
**Verwandte Begriffe:** Normativ, Informativ, Referenzartefakt

---

### API

Eine formal beschriebene Programmierschnittstelle, über die Komponenten, Module, Dienste oder externe Systeme kontrolliert miteinander interagieren.

Jede kanonische API muss auf einem versionierten Interface Contract beruhen.

**Kategorie:** Integration, Schnittstelle  
**Verwandte Begriffe:** Interface Contract, Integration, Provider, Consumer

---

### Architektur

Die strukturierte, nachvollziehbare und versionierte Beschreibung eines Systems, seiner Komponenten, Verantwortlichkeiten, Beziehungen, Regeln, Informationsflüsse, Zustände und Lebenszyklen.

Im CMIBF umfasst Architektur sowohl normative Beschreibungen als auch die kontrollierte Ableitung maschinenlesbarer Artefakte.

**Kategorie:** Grundbegriff  
**Verwandte Begriffe:** Architekturmodell, Framework, Blueprint

---

### Architekturartefakt

Ein eindeutig identifiziertes Ergebnis der Architekturarbeit.

Dazu gehören beispielsweise:

- Kapitel,
- Modelle,
- Diagramme,
- Entscheidungen,
- Verträge,
- Registries,
- Blueprints,
- Templates,
- Reports,
- Ontologien.

Jedes offizielle Architekturartefakt muss versionierbar, referenzierbar und nachvollziehbar sein.

**Kategorie:** Artefakt  
**Verwandte Begriffe:** Artifact Identity, Lineage, Referenzkatalog

---

### Architecture Decision Record

Ein versioniertes Dokument zur nachvollziehbaren Erfassung einer wesentlichen Architekturentscheidung.

Ein ADR enthält mindestens:

- eine eindeutige ID,
- Titel und Kontext,
- Entscheidung,
- Begründung,
- betrachtete Alternativen,
- Auswirkungen,
- Status,
- Datum und Verantwortlichkeit.

**Kurzbezeichnung:** ADR  
**Kategorie:** Governance, Dokumentation  
**Verwandte Begriffe:** Änderungsantrag, Architekturentscheidung, Audit

---

### Architekturentscheidung

Eine kontrolliert getroffene und dokumentierte Festlegung, die Struktur, Regeln, Beziehungen, Verantwortlichkeiten oder Lebenszyklen der Architektur beeinflusst.

Wesentliche Architekturentscheidungen werden als ADR dokumentiert.

**Kategorie:** Governance  
**Verwandte Begriffe:** ADR, Freigabe, Governance

---

### Architekturkomponente

Eine logisch abgrenzbare Einheit innerhalb eines Architekturmodells.

Eine Architekturkomponente kann beispielsweise ein Framework, Modul, Dienst, Agent, Registry, Compiler, Vertrag oder Runtime-Bestandteil sein.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Modul, Framework, Service

---

### Architekturmodell

Eine strukturierte Darstellung ausgewählter Eigenschaften und Beziehungen einer Architektur.

Ein Architekturmodell kann menschenlesbar, grafisch oder maschinenlesbar dargestellt werden, darf aber der normativen Quelle nicht widersprechen.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Meta-Modell, Referenzmodell, Ontologie

---

### Architekturprinzip

Eine grundlegende, langfristig gültige Leitregel für Architekturentscheidungen und Implementierungen.

Architekturprinzipien besitzen Vorrang vor lokalen Bequemlichkeitsentscheidungen und müssen im gesamten Geltungsbereich konsistent angewendet werden.

**Kategorie:** Governance, Architektur  
**Verwandte Begriffe:** Constraint, Policy, Konvention

---

### Archivierung

Die kontrollierte Überführung nicht mehr aktiver, ersetzter oder historischer Artefakte in einen dauerhaft nachvollziehbaren Aufbewahrungszustand.

Archivierung darf weder Identität noch Historie eines Artefakts zerstören.

**Kategorie:** Lifecycle  
**Verwandte Begriffe:** Archived, Historisierung, Lineage

---

### Artefaktidentität

Die stabile, eindeutige und vom Dateinamen oder Speicherort unabhängige Identität eines Artefakts.

Eine Umbenennung, Verschiebung oder Formatänderung erzeugt keine neue Artefaktidentität, solange die fachliche Identität fortbesteht.

**Kategorie:** Artefaktverwaltung  
**Verwandte Begriffe:** Artifact-ID, Lineage, Version

---

### Artifact-ID

Eine dauerhaft eindeutige Kennung eines Architektur- oder Implementierungsartefakts.

Die Artifact-ID bleibt über Umbenennungen, Verschiebungen und zulässige Versionierungen hinweg stabil, sofern keine neue fachliche Identität entsteht.

**Kategorie:** Identifikation  
**Verwandte Begriffe:** Artefaktidentität, Reference-ID, Framework-ID

---

### Audit

Eine systematische und nachvollziehbare Prüfung von Architektur, Artefakten, Prozessen, Regeln, Entscheidungen oder Laufzeitereignissen.

Ein Audit bewertet insbesondere Vollständigkeit, Integrität, Regelkonformität, Nachvollziehbarkeit und Reproduzierbarkeit.

**Kategorie:** Governance, Prüfung  
**Verwandte Begriffe:** Audit Trail, Compliance, Validation

---

### Audit Trail

Eine lückenlose, zeitlich geordnete und gegen unkontrollierte Veränderung geschützte Aufzeichnung relevanter Ereignisse, Entscheidungen, Zustandsänderungen und Freigaben.

**Kategorie:** Audit, Historisierung  
**Verwandte Begriffe:** Provenance, Lineage, Log

---

## B

### Baseline

Ein eindeutig identifizierter, freigegebener und reproduzierbarer Referenzstand einer Architektur, Konfiguration, Implementierung oder eines Artefaktsatzes.

Eine Baseline dient als Vergleichs-, Prüf- und Wiederherstellungsgrundlage.

**Kategorie:** Versionierung, Release  
**Verwandte Begriffe:** Release, Version, Snapshot

---

### Blueprint

Eine aus der normativen Architektur abgeleitete, strukturierte und implementierungsnahe Beschreibung zur Erstellung, Prüfung oder Konfiguration eines Systems oder Systembestandteils.

Ein Blueprint darf keine eigenständige, dem CMIBF widersprechende Architektur erfinden.

**Kategorie:** Implementierung  
**Verwandte Begriffe:** CAC, Implementierungsregel, Template

---

### Breaking Change

Eine Änderung, durch die bisher zulässige Verwendungen, Schnittstellen, Datenformate, Abhängigkeiten oder Verhaltensweisen nicht mehr ohne Anpassung funktionieren.

Breaking Changes müssen ausdrücklich gekennzeichnet, begründet, versioniert und durch einen Migrationspfad begleitet werden.

**Kategorie:** Versionierung  
**Verwandte Begriffe:** Abwärtskompatibilität, Deprecation, Migration

---

### Build

Ein kontrollierter Prozess zur Erzeugung definierter Architektur-, Konfigurations- oder Softwareartefakte aus eindeutig versionierten Eingaben.

Ein kanonischer Build muss nachvollziehbar und reproduzierbar sein.

**Kategorie:** Build, Implementierung  
**Verwandte Begriffe:** Build-ID, Reproducible Build, Release

---

### Build-ID

Eine eindeutige Kennung eines konkreten Build-Vorgangs oder Build-Ergebnisses.

Sie verbindet mindestens Eingabeversionen, Compiler-Version, Build-Konfiguration und erzeugte Artefakte.

**Kategorie:** Identifikation, Build  
**Verwandte Begriffe:** Version, Hash, Release-ID

---

## C

### Canonical Architecture Compiler

Die zentrale, deterministische Transformationsinstanz des CMIBF.

Der CAC liest die normative Architektur und erzeugt daraus definierte maschinenlesbare Architektur- und Implementierungsartefakte. Er darf keine Architektur erfinden, ergänzen oder eigenständig verändern.

**Kurzbezeichnung:** CAC  
**Kategorie:** Compiler, Architektur  
**Verwandte Begriffe:** CMIBF, deterministisch, abgeleitetes Artefakt

---

### Canonical Architecture Compilation

Der kontrollierte Prozess, bei dem das CMIBF eingelesen, semantisch geprüft, in ein internes kanonisches Modell überführt und in definierte Ausgabeformate transformiert wird.

**Kategorie:** Compiler  
**Verwandte Begriffe:** CAC, Parsing, Semantic Validation, Blueprint Generation

---

### Canonical Architecture Glossary

Das verbindliche terminologische System des CMIBF.

Es definiert Begriffe eindeutig und bildet die sprachliche Grundlage für Dokumentation, Implementierung, Prüfung und maschinelle Verarbeitung.

**Kurzbezeichnung:** CAGL  
**Kategorie:** Terminologie  
**Verwandte Begriffe:** Glossar, Normative Terminologie

---

### Canonical Dependency Graph

Die vollständige, gerichtete und maschinenlesbare Darstellung aller relevanten kanonischen Abhängigkeiten zwischen Architekturentitäten.

Der Graph wird aus dem CMIBF erzeugt und darf keine unabhängige normative Quelle bilden.

**Kurzbezeichnung:** CDG  
**Kategorie:** Architekturbeziehung  
**Verwandte Begriffe:** Abhängigkeit, Dependency Resolution, Impact Analysis

---

### Canonical Framework Registry

Das zentrale, kanonisch abgeleitete Verzeichnis aller Frameworks, ihrer Identitäten, Versionen, Statuswerte, Verantwortungsbereiche, Fähigkeiten und Abhängigkeiten.

**Kurzbezeichnung:** CFR  
**Kategorie:** Registry  
**Verwandte Begriffe:** Framework-ID, Framework Discovery, CAC

---

### Canonical Interface Contract

Ein verbindlicher, versionierter Vertrag für die Interaktion zwischen Komponenten, Modulen, Diensten, Frameworks oder externen Systemen.

Er definiert mindestens beteiligte Parteien, Eingaben, Ausgaben, Vorbedingungen, Nachbedingungen, Fehlerfälle und Kompatibilitätsregeln.

**Kategorie:** Schnittstelle  
**Verwandte Begriffe:** API, Provider, Consumer, Contract-ID

---

### Canonical Layer

Die Architekturebene, die verbindliche Identitäten, Modelle, Regeln, Verträge und Beziehungen bereitstellt.

Der Canonical Layer steht unter Governance und bildet die kontrollierte Grundlage für abgeleitete Implementierungs- und Runtime-Artefakte.

**Kategorie:** Architekturebene  
**Verwandte Begriffe:** Foundation Layer, Governance Layer, Operational Layer

---

### Canonical Master Implementation Blueprint Framework

Das übergeordnete, normative und versionierte Architekturhandbuch zur Beschreibung, Steuerung, Ableitung, Prüfung, Implementierung und Evolution komplexer Systeme.

Das CMIBF ist die einzige normative Quelle für die von ihm geregelte Architektur.

**Kurzbezeichnung:** CMIBF  
**Kategorie:** Meta-Framework  
**Verwandte Begriffe:** Single Source of Truth, CAC, Blueprint

---

### Canonical Model

Die eindeutige, konsistente und intern normalisierte Darstellung aller im CMIBF definierten Entitäten, Beziehungen, Regeln, Zustände und Constraints.

Das Canonical Model bildet die Grundlage der Compiler-Ausgaben.

**Kategorie:** Compiler, Meta-Modell  
**Verwandte Begriffe:** Parsing, Semantic Validation, Ontologie

---

### Capability

Eine explizit definierte, registrierte und überprüfbare Fähigkeit einer Komponente, eines Frameworks, Agenten oder Dienstes.

Eine Capability beschreibt, was eine Einheit leisten darf und unter welchen Bedingungen sie verwendet werden kann.

**Kategorie:** Registry, Ausführung  
**Verwandte Begriffe:** Agent, Framework Discovery, Policy

---

### Certification

Die formale Bestätigung, dass ein definierter Prüfgegenstand festgelegte Anforderungen, Standards und Validierungsregeln erfüllt.

Eine Zertifizierung setzt eine erfolgreich abgeschlossene und nachvollziehbare Prüfung voraus.

**Kategorie:** Qualitätssicherung  
**Verwandte Begriffe:** Validation, Compliance, Release Gate

---

### Checksum

Ein aus Daten berechneter Prüfwert zur Erkennung unbeabsichtigter oder unzulässiger Veränderungen.

**Kategorie:** Integrität  
**Verwandte Begriffe:** Hash, Signatur, Build

---

### Compliance

Die nachweisbare Übereinstimmung mit verbindlichen Regeln, Policies, Standards, Verträgen oder gesetzlichen Anforderungen.

**Kategorie:** Governance, Prüfung  
**Verwandte Begriffe:** Audit, Validation, Certification

---

### Component

Siehe **Architekturkomponente**.

---

### Constraint

Eine verbindliche Einschränkung, Bedingung oder Grenze, die eine Architektur, Implementierung, Konfiguration oder Ausführung einhalten muss.

Constraints müssen eindeutig, prüfbar und nach Möglichkeit maschinenlesbar formuliert sein.

**Kategorie:** Regel  
**Verwandte Begriffe:** Policy, Validation Rule, Vorbedingung

---

### Consumer

Eine Komponente oder ein System, das eine von einem Provider bereitgestellte Schnittstelle, Capability, Ressource oder Information verwendet.

**Kategorie:** Integration  
**Verwandte Begriffe:** Provider, Interface Contract, API

---

### Contract-ID

Eine eindeutige Kennung eines kanonischen Interface Contracts.

**Kategorie:** Identifikation  
**Verwandte Begriffe:** Canonical Interface Contract, Reference-ID

---

### Controlled Architecture Evolution

Die ausschließlich über definierte Governance-, Prüf-, Freigabe-, Versionierungs- und Compiler-Prozesse erfolgende Weiterentwicklung der Architektur.

Kontrollierte Evolution schließt autonome Selbständerungen und Selbstfreigaben aus.

**Kategorie:** Evolution, Governance  
**Verwandte Begriffe:** Änderungsantrag, CSEA, Freigabe

---

## D

### Datenabhängigkeit

Eine Abhängigkeit, bei der eine Einheit Daten, Datenstrukturen, Datenqualität, Zustände oder Datenverfügbarkeit einer anderen Einheit voraussetzt.

**Kategorie:** Abhängigkeit  
**Verwandte Begriffe:** Abhängigkeit, Schema, Interface Contract

---

### Deployment

Der kontrollierte Prozess zur Überführung freigegebener und validierter Artefakte in eine definierte Zielumgebung.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Release, Runtime, Rollback

---

### Deprecated

Ein Lifecycle-Status für einen weiterhin vorhandenen, aber zur Ablösung vorgesehenen Bestandteil.

Deprecated-Komponenten dürfen nicht ohne definierte Übergangsphase entfernt werden.

**Kategorie:** Lifecycle-Status  
**Verwandte Begriffe:** Deprecation, Archived, Migration

---

### Deprecation

Der kontrollierte Prozess zur Kennzeichnung, Übergangsverwaltung und späteren Ablösung eines veralteten Architektur- oder Implementierungsbestandteils.

**Kategorie:** Lifecycle  
**Verwandte Begriffe:** Deprecated, Breaking Change, Migration

---

### Dependency Graph

Siehe **Canonical Dependency Graph**, sofern der Graph den Geltungsbereich des CMIBF betrifft.

---

### Dependency Resolution

Die regelbasierte Analyse und deterministische Auflösung explizit definierter Abhängigkeiten.

Sie umfasst insbesondere Referenzprüfung, Versionskompatibilität, Konflikterkennung, Zyklenerkennung und Reihenfolgenbildung.

**Kategorie:** Architekturbeziehung  
**Verwandte Begriffe:** Abhängigkeit, CDG, Topologische Ordnung

---

### Deterministisch

Eigenschaft eines Prozesses, bei identischen gültigen Eingaben und identischen relevanten Rahmenbedingungen reproduzierbar dasselbe Ergebnis zu erzeugen.

**Kategorie:** Qualitätsprinzip  
**Verwandte Begriffe:** Reproduzierbarkeit, CAC, Build

---

### Discovery

Der kontrollierte Prozess zum Auffinden registrierter Frameworks, Module, Capabilities, Dienste oder Artefakte anhand kanonischer Metadaten.

**Kategorie:** Registry  
**Verwandte Begriffe:** Framework Registry, Capability, Registry

---

## E

### Ecosystem

Die Gesamtheit der miteinander verbundenen Frameworks, Module, Dienste, Werkzeuge, Integrationen, Nutzerrollen und externen Systeme innerhalb eines definierten Geltungsbereichs.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Integration, Registry, Plattform

---

### Entität

Ein eindeutig identifizierbares fachliches oder technisches Objekt des kanonischen Modells.

Beispiele sind Frameworks, Module, Artefakte, Verträge, Rollen, Zustände oder Beziehungen.

**Kategorie:** Meta-Modell  
**Verwandte Begriffe:** Identität, Beziehung, Ontologie

---

### Ereignis

Eine eindeutig beschriebene, zeitlich einordenbare Feststellung oder Zustandsänderung, die für Architektur, Ausführung, Monitoring, Audit oder Lifecycle relevant ist.

**Kategorie:** Runtime, Audit  
**Verwandte Begriffe:** Event-ID, Zustandsübergang, Audit Trail

---

### Erweiterung

Ein zusätzlicher, klar abgegrenzter Funktions- oder Architekturbaustein, der den kanonischen Kern ergänzt, ohne ihn unkontrolliert zu verändern.

**Kategorie:** Erweiterbarkeit  
**Verwandte Begriffe:** Plug-in, Extension Point, Kompatibilität

---

### Extension Point

Eine ausdrücklich definierte Stelle, an der zulässige Erweiterungen eingebunden werden können.

Extension Points müssen Verträge, Grenzen, Kompatibilitätsregeln und Governance-Anforderungen festlegen.

**Kategorie:** Erweiterbarkeit  
**Verwandte Begriffe:** Plug-in, Interface Contract, Policy

---

## F

### Failure

Ein Ausführungs- oder Prüfzustand, in dem ein definierter erwarteter Erfolg nicht erreicht wurde.

Ein Failure muss klassifiziert, protokolliert und entsprechend festgelegter Regeln behandelt werden.

**Kategorie:** Ausführung  
**Verwandte Begriffe:** Error, Failed, Recovery

---

### Foundation Layer

Die grundlegende Architekturebene für Identität, Basiskonfiguration, Kernverträge, elementare Dienste und unverzichtbare Systemvoraussetzungen.

Höhere Ebenen dürfen die Foundation nicht unkontrolliert umgehen.

**Kategorie:** Architekturebene  
**Verwandte Begriffe:** Canonical Layer, Governance Layer, Operational Layer

---

### Framework

Ein versionierter, eindeutig identifizierter und abgegrenzter Ordnungs- und Regelrahmen für einen definierten Verantwortungsbereich.

Ein Framework beschreibt unter anderem Zweck, Geltungsbereich, Bestandteile, Regeln, Schnittstellen, Abhängigkeiten und Lifecycle.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Framework-ID, Modul, Registry

---

### Framework Discovery

Das automatisierte oder manuelle Auffinden geeigneter registrierter Frameworks anhand kanonischer Metadaten, Kategorien, Tags, Versionen, Abhängigkeiten und Capabilities.

**Kategorie:** Registry  
**Verwandte Begriffe:** CFR, Discovery, Capability

---

### Framework-ID

Eine dauerhaft eindeutige Kennung eines Frameworks.

**Kategorie:** Identifikation  
**Verwandte Begriffe:** Framework, Registry, Version

---

### Freigabe

Eine dokumentierte Governance-Entscheidung, durch die ein geprüfter Gegenstand einen definierten zulässigen Status erhält.

Eine Freigabe muss Verantwortlichkeit, Zeitpunkt, Gegenstand, Version und Prüfergebnis nachvollziehbar machen.

**Kategorie:** Governance  
**Verwandte Begriffe:** Approval, Release Gate, Validation

---

## G

### Geltungsbereich

Der ausdrücklich festgelegte fachliche, technische, organisatorische oder zeitliche Bereich, in dem eine Regel, ein Framework, ein Vertrag oder ein Artefakt verbindlich gilt.

**Kategorie:** Governance  
**Verwandte Begriffe:** Scope, Normativ, Verantwortungsbereich

---

### Generator

Eine kontrollierte Komponente zur Erzeugung definierter Ausgabeformate aus kanonischen, validierten Eingaben.

Ein Generator darf keine eigenständige Architektur erfinden.

**Kategorie:** Compiler  
**Verwandte Begriffe:** CAC, Plug-in, Blueprint

---

### Glossar

Ein strukturiertes Verzeichnis verbindlich definierter Begriffe.

Im CMIBF ist das Glossar Teil der normativen Terminologie.

**Kategorie:** Terminologie  
**Verwandte Begriffe:** CAGL, Abkürzungsverzeichnis

---

### Governance

Das Gesamtsystem aus Regeln, Rollen, Verantwortlichkeiten, Prüfungen, Entscheidungen, Freigaben, Kontrollen und Nachweisen zur kontrollierten Steuerung der Architektur.

**Kategorie:** Governance  
**Verwandte Begriffe:** Policy, Audit, Freigabe

---

### Governance Gate

Ein definierter Kontrollpunkt, an dem ein Vorgang nur bei erfüllten Voraussetzungen fortgesetzt werden darf.

**Kategorie:** Governance  
**Verwandte Begriffe:** Release Gate, Validation, Approval

---

### Governance Layer

Die Architekturebene für Policies, Berechtigungen, Kontrollen, Prüfungen, Freigaben, Auditierung und kontrollierte Evolution.

**Kategorie:** Architekturebene  
**Verwandte Begriffe:** Foundation Layer, Canonical Layer, Operational Layer

---

## H

### Hash

Ein deterministisch berechneter digitaler Fingerabdruck von Daten.

Hashes unterstützen Integritätsprüfung, Vergleich, Reproduzierbarkeit und eindeutige Zuordnung von Artefaktständen.

**Kategorie:** Integrität  
**Verwandte Begriffe:** Checksum, Signatur, Build

---

### Historisierung

Die dauerhafte, geordnete und nachvollziehbare Aufbewahrung früherer Zustände, Versionen, Entscheidungen und Ereignisse.

Historisierung darf bestehende Historie nicht nachträglich verfälschen.

**Kategorie:** Lifecycle  
**Verwandte Begriffe:** Lineage, Provenance, Archivierung

---

## I

### Identität

Die stabile und eindeutige Zuordnung einer Entität unabhängig von ihrer Darstellung, Bezeichnung oder ihrem Speicherort.

**Kategorie:** Meta-Modell  
**Verwandte Begriffe:** ID, Artefaktidentität, Framework-ID

---

### Impact Analysis

Die systematische Ermittlung der Auswirkungen einer geplanten oder eingetretenen Änderung auf abhängige Entitäten, Verträge, Builds, Deployments, Runtime-Komponenten und Dokumentation.

**Kategorie:** Analyse  
**Verwandte Begriffe:** Dependency Graph, Änderung, Risiko

---

### Implementierung

Die kontrollierte technische Realisierung einer freigegebenen Architektur oder eines daraus erzeugten Blueprints.

Eine Implementierung darf normative Architekturregeln nicht stillschweigend verändern.

**Kategorie:** Entwicklung  
**Verwandte Begriffe:** Blueprint, Build, Validation

---

### Implementierungsregel

Eine aus der Architektur abgeleitete, prüfbare Vorgabe für die technische Umsetzung.

**Kategorie:** Implementierung  
**Verwandte Begriffe:** Blueprint, Constraint, Validation Rule

---

### Implementierungs-Roadmap

Eine priorisierte, phasenweise und abhängigkeitsbewusste Planung zur Umsetzung der durch das CMIBF beschriebenen Architektur.

Die Roadmap muss Governance Gates, Voraussetzungen, Abhängigkeiten, Ergebnisse und Prüfpunkte berücksichtigen.

**Kategorie:** Planung  
**Verwandte Begriffe:** Dependency Graph, Meilenstein, Phase

---

### Informativ

Kennzeichnung eines Inhalts, der erläutert, begründet, beispielhaft darstellt oder Orientierung bietet, ohne selbst eine verbindliche Regel festzulegen.

**Kategorie:** Dokumentation  
**Verwandte Begriffe:** Normativ, Beispiel, Anhang

---

### Integration

Die kontrollierte Verbindung interner oder externer Komponenten über definierte Schnittstellen, Verträge, Registrierungen und Governance-Regeln.

Direkte undokumentierte Kopplungen sind unzulässig.

**Kategorie:** Architektur  
**Verwandte Begriffe:** API, Interface Contract, Provider, Consumer

---

### Integrität

Eigenschaft eines Artefakts, Systems oder Prozesses, vollständig, unverfälscht, konsistent und gegen unkontrollierte Veränderung geschützt zu sein.

**Kategorie:** Qualität  
**Verwandte Begriffe:** Hash, Signatur, Validation

---

### Interface

Eine definierte Grenze, über die zwei oder mehr Einheiten Informationen, Aufrufe, Ereignisse oder Ressourcen austauschen.

**Kategorie:** Schnittstelle  
**Verwandte Begriffe:** API, Interface Contract, Integration

---

### Interface Contract

Siehe **Canonical Interface Contract**.

---

### Interoperabilität

Fähigkeit unterschiedlicher Systeme, Komponenten oder Frameworks, auf Grundlage gemeinsamer Verträge, Formate und Bedeutungen korrekt zusammenzuarbeiten.

**Kategorie:** Integration  
**Verwandte Begriffe:** Interface Contract, Kompatibilität, Semantik

---

## K

### Kanonisch

Verbindlich, eindeutig, autorisiert und innerhalb des definierten Geltungsbereichs maßgeblich.

Ein kanonischer Inhalt bildet die Referenz, aus der zulässige Darstellungen und Artefakte abgeleitet werden.

**Kategorie:** Grundbegriff  
**Verwandte Begriffe:** Normativ, Single Source of Truth

---

### Kanonischer Kern

Die Gesamtheit der grundlegenden, normativen Identitäten, Prinzipien, Regeln, Modelle und Beziehungen, die nur durch kontrollierte Governance geändert werden darf.

**Kategorie:** Architektur  
**Verwandte Begriffe:** CMIBF, Controlled Architecture Evolution

---

### Kompatibilität

Die nachgewiesene Fähigkeit verschiedener Versionen, Komponenten oder Systeme, gemäß definierter Verträge und Regeln korrekt zusammenzuarbeiten.

**Kategorie:** Versionierung, Integration  
**Verwandte Begriffe:** Abwärtskompatibilität, Interface Contract, Version

---

### Komponente

Siehe **Architekturkomponente**.

---

### Konfiguration

Eine versionierbare Menge von Einstellungen und Parametern, die zulässiges Verhalten innerhalb der Architektur konkretisiert.

Konfiguration darf keine normative Architekturregel umgehen oder ersetzen.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Runtime Configuration, Policy, Version

---

### Konsistenz

Widerspruchsfreiheit zwischen Definitionen, Regeln, Beziehungen, Versionen, Referenzen und daraus abgeleiteten Artefakten.

**Kategorie:** Qualität  
**Verwandte Begriffe:** Validation, Referenzintegrität, Semantic Validation

---

### Kontext

Die für Interpretation, Planung, Ausführung oder Bewertung relevanten Informationen und Rahmenbedingungen.

Kontext muss eindeutig abgegrenzt und darf nicht mit normativen Regeln verwechselt werden.

**Kategorie:** Ausführung, Semantik  
**Verwandte Begriffe:** Scope, State, Environment

---

### Konvention

Eine verbindlich festgelegte Regel für Benennung, Strukturierung, Darstellung, Modellierung, Versionierung oder Dokumentation.

**Kategorie:** Standardisierung  
**Verwandte Begriffe:** Naming Convention, Template, Policy

---

## L

### Lifecycle

Die definierte Folge zulässiger Zustände und Übergänge einer Entität von ihrer Erstellung bis zu Ablösung oder Archivierung.

**Kategorie:** Zustandsmodell  
**Verwandte Begriffe:** State, Transition, Deprecation

---

### Lineage

Die nachvollziehbare Abstammungs- und Entwicklungskette eines Artefakts.

Lineage beschreibt, aus welchen Quellen ein Artefakt entstand, wie es verändert wurde und welche Nachfolger oder Ableitungen existieren.

**Kategorie:** Provenance  
**Verwandte Begriffe:** Artifact Identity, Historisierung, Provenance

---

### Log

Eine zeitlich geordnete Aufzeichnung technischer oder fachlicher Ereignisse.

Logs müssen hinsichtlich Quelle, Zeitbezug, Kontext und Integrität ausreichend nachvollziehbar sein.

**Kategorie:** Observability  
**Verwandte Begriffe:** Audit Trail, Event, Trace

---

### Lose Kopplung

Architekturprinzip, nach dem Komponenten nur über klar definierte, stabile Verträge voneinander abhängen und interne Details nicht gegenseitig voraussetzen.

**Kategorie:** Architekturprinzip  
**Verwandte Begriffe:** Interface Contract, Integration, Modularität

---

## M

### Maschinenlesbar

In einer formal strukturierten und eindeutig interpretierbaren Form vorliegend, die automatisierte Verarbeitung und Validierung ermöglicht.

**Kategorie:** Darstellung  
**Verwandte Begriffe:** Schema, Parser, Registry

---

### Manifest

Ein strukturiertes Verzeichnis der zu einem Build, Release, Paket oder Artefaktsatz gehörenden Bestandteile und Metadaten.

**Kategorie:** Artefaktverwaltung  
**Verwandte Begriffe:** Registry, Build, Release

---

### Meta-Architektur

Eine Architektur, die Regeln, Modelle und Strukturen zur Beschreibung anderer Architekturen definiert.

**Kategorie:** Meta-Modell  
**Verwandte Begriffe:** CMIBF, Meta-Modell, Framework

---

### Meta-Modell

Ein Modell, das zulässige Arten von Entitäten, Beziehungen, Eigenschaften, Regeln und Strukturen anderer Modelle beschreibt.

**Kategorie:** Meta-Architektur  
**Verwandte Begriffe:** Ontologie, Schema, Canonical Model

---

### Migration

Der kontrollierte Übergang von einem bestehenden Architektur-, Daten-, Schnittstellen- oder Implementierungsstand zu einem neuen Stand.

Eine Migration muss Voraussetzungen, Transformationen, Prüfungen, Risiken und Rollback-Möglichkeiten dokumentieren.

**Kategorie:** Lifecycle  
**Verwandte Begriffe:** Breaking Change, Deprecation, Rollback

---

### Modul

Eine abgegrenzte, versionierbare Architektur- oder Implementierungseinheit mit definierter Verantwortung, Schnittstellen und Abhängigkeiten.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Framework, Service, Komponente

---

### Modularität

Architekturprinzip zur Zerlegung eines Systems in klar abgegrenzte, verständliche und kontrolliert kombinierbare Einheiten.

**Kategorie:** Architekturprinzip  
**Verwandte Begriffe:** Modul, Lose Kopplung, Interface Contract

---

### Monitoring

Die fortlaufende Überwachung bekannter Zustände, Ereignisse, Grenzwerte, Verfügbarkeiten und Fehlerbedingungen.

Monitoring beantwortet primär, ob definierte erwartete oder bekannte Bedingungen eingehalten werden.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Observability, Metrik, Alert

---

## N

### Namenskonvention

Eine verbindliche Regel zur einheitlichen Benennung von Dateien, IDs, Frameworks, Modulen, Klassen, Schnittstellen oder anderen Entitäten.

**Kategorie:** Konvention  
**Verwandte Begriffe:** ID-Schema, Dokumentationsstandard

---

### Normativ

Verbindlich und innerhalb des festgelegten Geltungsbereichs einzuhalten.

Normative Aussagen verwenden im CMIBF insbesondere die Schlüsselwörter **muss**, **darf nicht**, **soll**, **soll nicht**, **kann** und **empfohlen** entsprechend ihrer definierten Stärke.

**Kategorie:** Governance, Terminologie  
**Verwandte Begriffe:** Informativ, Muss, Soll, Kann

---

## O

### Observability

Fähigkeit, den inneren Zustand eines Systems anhand erzeugter Metriken, Logs, Traces, Ereignisse und Kontextinformationen nachvollziehen und analysieren zu können.

Observability ergänzt Monitoring insbesondere bei unbekannten Fehlerbildern und Ursachenanalysen.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Monitoring, Trace, Root Cause Analysis

---

### Ontologie

Eine formal strukturierte Beschreibung von Begriffen, Entitäten, Kategorien, Eigenschaften und Beziehungen eines Wissens- oder Architekturbereichs.

Die CMIBF-Ontologie wird aus der normativen Architektur abgeleitet.

**Kategorie:** Wissen, Meta-Modell  
**Verwandte Begriffe:** Glossar, Semantic Model, Canonical Model

---

### Operational Layer

Die Architekturebene für Planung, Orchestrierung, Ausführung, Runtime, Monitoring, Observability, Fehlerbehandlung und Betrieb.

Sie verwendet ausschließlich freigegebene und validierte Artefakte der vorgelagerten Ebenen.

**Kategorie:** Architekturebene  
**Verwandte Begriffe:** Foundation Layer, Canonical Layer, Governance Layer

---

### Orchestrierung

Die kontrollierte Koordination definierter Ausführungseinheiten auf Grundlage eines validierten Plans, festgelegter Abhängigkeiten, Verträge und Zustände.

Orchestrierung führt aus; strategische Planung ist getrennt zu behandeln.

**Kategorie:** Ausführung  
**Verwandte Begriffe:** Execution Model, Planner, Runtime

---

## P

### Parsing

Das strukturierte Einlesen und Zerlegen einer Quelle in formal erkennbare Bestandteile.

Canonical Parsing extrahiert aus dem CMIBF unter anderem Kapitel, Entitäten, Regeln, Beziehungen, Identitäten und Constraints.

**Kategorie:** Compiler  
**Verwandte Begriffe:** CAC, Canonical Model, Semantic Validation

---

### Phase

Ein klar abgegrenzter Abschnitt eines Lifecycle-, Build-, Prüf-, Implementierungs- oder Evolutionsprozesses mit definierten Voraussetzungen, Aktivitäten, Ergebnissen und Abschlusskriterien.

**Kategorie:** Prozess  
**Verwandte Begriffe:** Gate, Meilenstein, Roadmap

---

### Planner

Eine Komponente, die auf Grundlage von Ziel, Kontext, Policies, Capabilities und Abhängigkeiten einen ausführbaren Plan erstellt.

Der Planner trifft Planungsentscheidungen; der Orchestrator führt validierte Pläne aus.

**Kategorie:** Ausführung  
**Verwandte Begriffe:** Orchestrierung, Execution Plan, Capability

---

### Plattform

Eine technische und organisatorische Grundlage, auf der Frameworks, Dienste, Module oder Anwendungen bereitgestellt und betrieben werden.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Runtime, Ecosystem, Deployment

---

### Plug-in

Eine versionierte Erweiterung, die über einen ausdrücklich definierten Extension Point eingebunden wird.

Ein Plug-in darf den kanonischen Kern nicht unkontrolliert verändern.

**Kategorie:** Erweiterbarkeit  
**Verwandte Begriffe:** Extension Point, Generator, Capability

---

### Policy

Eine verbindliche, prüfbare Regel zur Steuerung zulässiger Entscheidungen, Zugriffe, Ausführungen oder Änderungen.

**Kategorie:** Governance  
**Verwandte Begriffe:** Constraint, Governance, Berechtigung

---

### Postcondition

Siehe **Nachbedingung**: Eine Bedingung, die nach erfolgreicher Ausführung eines Vorgangs erfüllt sein muss.

**Kategorie:** Vertrag  
**Verwandte Begriffe:** Precondition, Interface Contract, Validation

---

### Precondition

Siehe **Vorbedingung**: Eine Bedingung, die vor Ausführung eines Vorgangs erfüllt sein muss.

**Kategorie:** Vertrag  
**Verwandte Begriffe:** Postcondition, Interface Contract, Validation

---

### Provenance

Die dokumentierte Herkunft eines Artefakts oder Datensatzes einschließlich Quellen, Transformationen, erzeugender Komponenten, Validierungen und Freigaben.

**Kategorie:** Nachvollziehbarkeit  
**Verwandte Begriffe:** Lineage, Audit Trail, Historisierung

---

### Provider

Eine Komponente oder ein System, das eine Schnittstelle, Capability, Ressource oder Information bereitstellt.

**Kategorie:** Integration  
**Verwandte Begriffe:** Consumer, Interface Contract, API

---

## R

### Recovery

Der kontrollierte Prozess zur Wiederherstellung eines zulässigen und konsistenten Zustands nach einem Fehler oder Ausfall.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Failure, Rollback, Resilience

---

### Reference-ID

Eine eindeutige Kennung eines normativen oder registrierten Referenzobjekts.

**Kategorie:** Identifikation  
**Verwandte Begriffe:** Artifact-ID, Contract-ID, Framework-ID

---

### Referenzartefakt

Ein offiziell registriertes Artefakt, das als verbindliche oder informative Referenz für Architektur, Implementierung, Prüfung oder Betrieb dient.

**Kategorie:** Artefakt  
**Verwandte Begriffe:** Referenzkatalog, Normativ, Informativ

---

### Referenzintegrität

Eigenschaft, dass alle Referenzen eindeutig auf existierende, zulässige und versionskompatible Ziele verweisen.

**Kategorie:** Qualität  
**Verwandte Begriffe:** Validation, Dependency Resolution, ID

---

### Referenzmodell

Ein wiederverwendbares und normativ oder informativ klassifiziertes Modell für einen definierten Architektur- oder Anwendungsbereich.

**Kategorie:** Architekturmodell  
**Verwandte Begriffe:** Pattern, Template, Blueprint

---

### Registry

Ein strukturiertes, versioniertes und maschinenlesbares Verzeichnis eindeutig identifizierter Entitäten und ihrer Metadaten.

Eine aus dem CMIBF erzeugte Registry ist ein abgeleitetes Artefakt.

**Kategorie:** Artefaktverwaltung  
**Verwandte Begriffe:** CFR, Discovery, Manifest

---

### Release

Ein eindeutig identifizierter, freigegebener und reproduzierbarer Stand eines Artefaktsatzes zur definierten Nutzung oder Bereitstellung.

**Kategorie:** Lifecycle  
**Verwandte Begriffe:** Baseline, Build, Deployment

---

### Release Gate

Ein Governance- und Qualitätssicherungspunkt, der vor Veröffentlichung oder Deployment erfüllt sein muss.

**Kategorie:** Governance  
**Verwandte Begriffe:** Validation, Certification, Freigabe

---

### Reproduzierbarkeit

Eigenschaft, einen definierten Prozess oder ein Ergebnis unter gleichen dokumentierten Bedingungen erneut mit übereinstimmendem Resultat herstellen zu können.

**Kategorie:** Qualitätsprinzip  
**Verwandte Begriffe:** Deterministisch, Build, CAC

---

### Resilience

Fähigkeit eines Systems, Störungen zu verkraften, kontrolliert zu reagieren und einen zulässigen Betriebszustand aufrechtzuerhalten oder wiederherzustellen.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Recovery, Failure, Availability

---

### Rollback

Die kontrollierte Rückkehr zu einem zuvor freigegebenen und konsistenten Stand.

**Kategorie:** Lifecycle, Betrieb  
**Verwandte Begriffe:** Migration, Recovery, Baseline

---

### Root Cause Analysis

Die systematische Ermittlung der grundlegenden Ursache eines Fehlers, einer Abweichung oder eines unerwarteten Zustands.

**Kurzbezeichnung:** RCA  
**Kategorie:** Observability  
**Verwandte Begriffe:** Trace, Log, Impact Analysis

---

### Runtime

Die kontrollierte Laufzeitumgebung und Gesamtheit der aktiven Komponenten, Zustände, Konfigurationen und Ausführungsprozesse eines Systems.

Die Runtime darf ausschließlich validierte und freigegebene Artefakte verwenden.

**Kategorie:** Betrieb  
**Verwandte Begriffe:** Deployment, Execution Model, Runtime Governance

---

### Runtime Governance

Die Anwendung von Governance-, Policy-, Berechtigungs-, Audit- und Validierungsregeln während des laufenden Betriebs.

**Kategorie:** Governance, Runtime  
**Verwandte Begriffe:** Runtime, Policy, Audit Trail

---

## S

### Schema

Eine formale Beschreibung der zulässigen Struktur, Datentypen, Pflichtfelder, Beziehungen und Constraints eines maschinenlesbaren Artefakts.

**Kategorie:** Datenmodell  
**Verwandte Begriffe:** Validation, Meta-Modell, Parser

---

### Semantic Validation

Die Prüfung, ob Inhalte nicht nur strukturell korrekt, sondern auch bedeutungsbezogen konsistent, eindeutig und widerspruchsfrei sind.

**Kategorie:** Compiler, Prüfung  
**Verwandte Begriffe:** CAC, Konsistenz, Ontologie

---

### Semantik

Die verbindliche Bedeutung eines Begriffs, Symbols, Datenfelds, Zustands oder Modells.

**Kategorie:** Terminologie  
**Verwandte Begriffe:** Glossar, Ontologie, Semantic Validation

---

### Service

Eine abgegrenzte, über definierte Verträge nutzbare Funktionseinheit.

**Kategorie:** Architektur  
**Verwandte Begriffe:** Modul, API, Provider

---

### Signatur

Ein kryptografischer oder formal kontrollierter Nachweis zur Bestätigung von Herkunft und Integrität eines Artefakts.

**Kategorie:** Integrität  
**Verwandte Begriffe:** Hash, Provenance, Release

---

### Single Source of Truth

Das Prinzip, dass für einen definierten Sachverhalt genau eine autorisierte normative Quelle existiert.

Für die durch das CMIBF geregelte Architektur ist das CMIBF die Single Source of Truth. Abgeleitete Artefakte dürfen diese Quelle nicht ersetzen oder ihr widersprechen.

**Kurzbezeichnung:** SSOT  
**Kategorie:** Architekturprinzip  
**Verwandte Begriffe:** CMIBF, kanonisch, abgeleitetes Artefakt

---

### Snapshot

Eine zeitpunktbezogene, unveränderlich referenzierbare Darstellung eines Zustands oder Artefaktsatzes.

**Kategorie:** Historisierung  
**Verwandte Begriffe:** Baseline, Version, Archivierung

---

### State

Der zu einem bestimmten Zeitpunkt eindeutig definierte Zustand einer Entität.

**Kategorie:** Zustandsmodell  
**Verwandte Begriffe:** State Machine, Transition, Lifecycle

---

### State Machine

Ein formales Modell zulässiger Zustände und Zustandsübergänge.

Nicht definierte Zustandsübergänge sind unzulässig.

**Kategorie:** Zustandsmodell  
**Verwandte Begriffe:** State, Transition, Vorbedingung

---

### Status

Ein eindeutig definierter Kennwert zur Einordnung des aktuellen Lifecycle-, Prüf-, Freigabe- oder Ausführungszustands einer Entität.

**Kategorie:** Zustandsmodell  
**Verwandte Begriffe:** State, Lifecycle, Registry

---

## T

### Task

Eine eindeutig beschriebene, planbare und ausführbare Arbeitseinheit mit Ziel, Eingaben, Voraussetzungen, Verantwortlichkeit und erwartetem Ergebnis.

**Kategorie:** Ausführung  
**Verwandte Begriffe:** Workflow, Planner, Execution Model

---

### Technologieunabhängigkeit

Architekturprinzip, nach dem normative Regeln, Modelle und Verträge nicht unnötig an eine konkrete Programmiersprache, Plattform, Bibliothek oder einen Anbieter gebunden werden.

Technologiespezifische Ableitungen sind über kontrollierte Generatoren oder Profile zulässig.

**Kategorie:** Architekturprinzip  
**Verwandte Begriffe:** Portabilität, Generator, Interface Contract

---

### Template

Eine versionierte Standardvorlage für die einheitliche Erstellung eines bestimmten Artefakttyps.

**Kategorie:** Standardisierung  
**Verwandte Begriffe:** Blueprint, Pattern, Pflichtfeld

---

### Tool

Ein registriertes und kontrolliertes Hilfsmittel, das einer Komponente oder einem Agenten definierte Funktionen bereitstellt.

Werkzeugzugriff muss durch Capabilities, Berechtigungen und Policies begrenzt sein.

**Kategorie:** Ausführung  
**Verwandte Begriffe:** Agent, Capability, Governance

---

### Trace

Eine zusammenhängende Aufzeichnung des Ablaufs einer Anfrage, Transaktion oder Ausführung über mehrere Komponenten hinweg.

**Kategorie:** Observability  
**Verwandte Begriffe:** Log, Event, Root Cause Analysis

---

### Transition

Ein zulässiger, definierter Übergang von einem Ausgangszustand in einen Zielzustand.

Jede Transition besitzt Auslöser, Vorbedingungen, Nachbedingungen und Verantwortlichkeit.

**Kategorie:** Zustandsmodell  
**Verwandte Begriffe:** State, State Machine, Lifecycle

---

## V

### Validation

Die systematische Prüfung, ob ein Artefakt, Modell, Prozess, Build oder System definierte Anforderungen und Regeln erfüllt.

**Kategorie:** Prüfung  
**Verwandte Begriffe:** Verification, Compliance, Certification

---

### Validation Rule

Eine formal definierte und prüfbare Regel, anhand derer Gültigkeit, Konsistenz oder Konformität festgestellt wird.

**Kategorie:** Prüfung  
**Verwandte Begriffe:** Constraint, Schema, Semantic Validation

---

### Validator

Eine autorisierte Komponente oder Rolle, die definierte Validierungsregeln ausführt und Prüfergebnisse nachvollziehbar dokumentiert.

Ein Validator darf normative Regeln nicht eigenständig verändern.

**Kategorie:** Prüfung, Rolle  
**Verwandte Begriffe:** Validation, Governance, CAC

---

### Verifikation

Die Prüfung, ob ein Artefakt oder System entsprechend seiner spezifizierten Vorgaben erstellt wurde.

**Kategorie:** Prüfung  
**Verwandte Begriffe:** Validation, Test, Compliance

---

### Version

Ein eindeutig identifizierter Entwicklungsstand einer Entität oder eines Artefakts.

Versionen müssen nachvollziehbar, referenzierbar und mit ihrer Änderungshistorie verbunden sein.

**Kategorie:** Versionierung  
**Verwandte Begriffe:** Semantische Versionierung, Baseline, Release

---

### Versionskompatibilität

Die definierte Verträglichkeit zwischen bestimmten Versionen voneinander abhängiger Entitäten.

**Kategorie:** Versionierung  
**Verwandte Begriffe:** Kompatibilität, Dependency Resolution, Breaking Change

---

### Vorbedingung

Eine Bedingung, die erfüllt sein muss, bevor ein Vorgang, Zustandsübergang oder Interface-Aufruf zulässig ausgeführt werden darf.

**Kategorie:** Vertrag, Zustandsmodell  
**Verwandte Begriffe:** Nachbedingung, Constraint, Interface Contract

---

## W

### Workflow

Eine geordnete Folge von Tasks, Entscheidungen, Zuständen und Übergängen zur Erreichung eines definierten Ergebnisses.

**Kategorie:** Prozess  
**Verwandte Begriffe:** Task, Orchestrierung, Execution Model

---

## Z

### Zertifizierung

Siehe **Certification**.

---

### Zustand

Siehe **State**.

---

### Zustandsintegrität

Eigenschaft, dass ein System oder Artefakt sich ausschließlich in zulässigen, konsistenten und nachvollziehbaren Zuständen befindet.

**Kategorie:** Zustandsmodell  
**Verwandte Begriffe:** State Machine, Validation, Runtime

---

### Zustandsübergang

Siehe **Transition**.

---

### Zyklische Abhängigkeit

Eine Abhängigkeitsstruktur, bei der eine Entität direkt oder indirekt wieder von sich selbst abhängt.

Zyklische Kernabhängigkeiten sind grundsätzlich zu vermeiden und müssen durch Dependency Resolution erkannt und bewertet werden.

**Kategorie:** Abhängigkeit  
**Verwandte Begriffe:** Dependency Graph, Topologische Ordnung, Konflikt

---

# 41.5 Normative Schlüsselwörter

Die folgenden Schlüsselwörter werden im CMIBF verbindlich verwendet:

### MUSS

Kennzeichnet eine zwingende Anforderung. Eine Abweichung ist ohne formale Änderung oder ausdrücklich definierte Ausnahme unzulässig.

### DARF NICHT

Kennzeichnet ein verbindliches Verbot.

### SOLL

Kennzeichnet eine starke Anforderung. Eine Abweichung ist nur mit dokumentierter, fachlich tragfähiger Begründung zulässig.

### SOLL NICHT

Kennzeichnet eine starke negative Empfehlung. Eine Abweichung erfordert eine dokumentierte Begründung.

### KANN

Kennzeichnet eine zulässige Option.

### EMPFOHLEN

Kennzeichnet eine bevorzugte, aber nicht zwingende Vorgehensweise.

### OPTIONAL

Kennzeichnet einen nicht verpflichtenden Bestandteil, dessen Verwendung dennoch alle geltenden Regeln erfüllen muss.

---

# 41.6 Kanonische Lifecycle-Statuswerte

Die folgenden Statuswerte bilden einen allgemeinen, erweiterbaren Grundbestand:

| Status | Bedeutung |
|---|---|
| `Proposed` | Vorgeschlagen, noch nicht geprüft oder freigegeben |
| `Defined` | Fachlich beschrieben |
| `Registered` | In einer kanonischen Registry erfasst |
| `In Review` | In formaler Prüfung |
| `Validated` | Erfolgreich validiert |
| `Approved` | Durch zuständige Governance freigegeben |
| `Ready` | Für den vorgesehenen nächsten Schritt vorbereitet |
| `Active` | Aktiv gültig oder in Betrieb |
| `Suspended` | Vorübergehend ausgesetzt |
| `Deprecated` | Zur Ablösung vorgesehen |
| `Rejected` | Nicht freigegeben |
| `Failed` | Vorgang oder Prüfung fehlgeschlagen |
| `Completed` | Ordnungsgemäß abgeschlossen |
| `Archived` | Historisch aufbewahrt und nicht mehr aktiv |
| `Retired` | Kontrolliert außer Betrieb genommen |

Fachspezifische Zustandsmodelle dürfen zusätzliche Statuswerte definieren, sofern sie mit dem Canonical State Model konsistent bleiben.

---

# 41.7 Begriffsregeln

1. Begriffe müssen eindeutig, knapp und prüfbar definiert werden.
2. Synonyme dürfen zur Lesbarkeit verwendet werden, müssen jedoch auf den kanonischen Begriff verweisen.
3. Abkürzungen werden im separaten Abkürzungsverzeichnis geführt.
4. Deutsche und englische Bezeichnungen dürfen parallel verwendet werden, sofern ihre kanonische Bedeutung identisch bleibt.
5. Neue Begriffe benötigen eine eindeutige Einordnung und Referenz.
6. Mehrdeutige Alltagsbegriffe müssen im Architekturkontext präzisiert werden.
7. Produkt-, Hersteller- und Technologiewörter dürfen keine technologieunabhängigen Architekturbegriffe ersetzen.
8. Veraltete Begriffe werden nicht kommentarlos gelöscht, sondern kontrolliert als deprecated markiert und gegebenenfalls auf Nachfolgebegriffe verwiesen.
9. Maschinenlesbare Begriff-IDs bleiben über reine Sprach- oder Schreibweisenänderungen hinweg stabil.
10. Das Glossar muss vor jeder offiziellen CMIBF-Freigabe auf Vollständigkeit, Eindeutigkeit und Referenzintegrität geprüft werden.

---

# 41.8 Compiler- und Registry-Integration

Der Canonical Architecture Compiler soll aus den normativen Glossardefinitionen mindestens folgende Artefakte erzeugen können:

- ein maschinenlesbares Glossar,
- eine Begriff-ID-Registry,
- Synonym- und Alias-Zuordnungen,
- Kapitelreferenzen,
- Begriffsbeziehungen,
- Deprecation-Hinweise,
- mehrsprachige Darstellungen,
- Validierungsregeln für Begriffsverwendung,
- Konsistenz- und Konfliktberichte.

Manuelle Änderungen an diesen abgeleiteten Glossarartefakten sind unzulässig.

---

# 41.9 Validierungskriterien

Vor der Freigabe dieses Glossars müssen mindestens folgende Prüfungen erfolgreich sein:

- keine widersprüchlichen Definitionen,
- keine mehrfach vergebenen Begriff-IDs,
- keine unaufgelösten Referenzen,
- keine unzulässigen Synonymkonflikte,
- konsistente Groß- und Kleinschreibung,
- konsistente Verwendung von Akronymen,
- Übereinstimmung mit den Fachkapiteln 1 bis 40,
- Übereinstimmung mit Framework Registry und Dependency Graph,
- korrekte Lifecycle- und Governance-Begriffe,
- Eignung zur maschinenlesbaren Ableitung.

---

# 41.10 Pflege und Evolution

Das Glossar ist ein kontrolliert weiterentwickelter Bestandteil des CMIBF.

Änderungen erfolgen ausschließlich durch:

1. Ermittlung eines Änderungsbedarfs,
2. dokumentierten Änderungsvorschlag,
3. Prüfung fachlicher Auswirkungen,
4. Governance-Freigabe,
5. Aktualisierung des CMIBF,
6. erneute Architekturkompilierung,
7. Validierung der erzeugten Glossarartefakte,
8. Veröffentlichung einer neuen Version.

Die historische Bedeutung früherer Begriffe und Versionen muss nachvollziehbar bleiben.

---

# 41.11 Zusammenfassung

Teil 41 definiert die gemeinsame und verbindliche Begriffswelt des **Canonical Master Implementation Blueprint Framework (CMIBF) 1.0**.

Das Glossar gewährleistet:

- terminologische Eindeutigkeit,
- konsistente Architekturkommunikation,
- nachvollziehbare Governance,
- maschinenlesbare Ableitung,
- zuverlässige Validierung,
- langfristige Wartbarkeit,
- kontrollierte internationale und technologische Erweiterbarkeit.

Es bildet gemeinsam mit dem Abkürzungsverzeichnis, der Framework Registry, dem Canonical Dependency Graph und den weiteren Abschlussartefakten die Referenzbasis des vollständigen CMIBF 1.0.

---

**Ende von Teil 41 – Glossar**
