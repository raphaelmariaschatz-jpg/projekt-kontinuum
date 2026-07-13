Kapitel 4
Architekturbeziehungen, Abhängigkeitsmodell und kanonischer Dependency Graph
4.1 Zielsetzung

Eine kanonische Architektur besteht nicht ausschließlich aus Artefakten.

Sie besteht aus den formalen Beziehungen zwischen diesen Artefakten.

Das CMIBF definiert daher:

zulässige Architekturbeziehungen
Abhängigkeitsregeln
Informationsfluss
Verantwortungsfluss
Änderungsfluss
Vererbungsregeln
Konsistenzbedingungen

Dadurch entsteht ein vollständiges Architekturmodell.

4.2 Grundprinzip

Jedes Architekturartefakt besitzt Beziehungen.

Keine Komponente existiert isoliert.

Jede Beziehung besitzt:

Quelle
Ziel
Beziehungstyp
Richtung
Semantik
Änderungsregeln

Formal:

Relationship

ID
Source
Target
RelationshipType
Direction
Strength
Version
Status
Constraints
4.3 Kanonische Beziehungstypen

CMIBF definiert ausschließlich kanonische Beziehungsklassen.

Structural Relationship

Beschreibt Struktur.

Beispiele:

contains
owns
consists_of
belongs_to
Dependency Relationship

Beschreibt technische Abhängigkeiten.

Beispiele

depends_on
requires
imports
references
uses
Information Relationship

Beschreibt Informationsfluss.

Beispiele

produces
consumes
transforms
reads
writes
Responsibility Relationship

Beschreibt Verantwortlichkeiten.

Beispiele

managed_by
owned_by
approved_by
reviewed_by
Runtime Relationship

Beschreibt Laufzeitverhalten.

Beispiele

calls
invokes
executes
triggers
Lifecycle Relationship

Beschreibt Evolution.

Beispiele

supersedes
replaces
extends
deprecates
inherits
4.4 Architekturbeziehungen besitzen Semantik

Eine Beziehung ist niemals lediglich ein Pfeil.

Sie besitzt Bedeutung.

Beispiel

Foundation

defines

Canonical Layer

bedeutet:

Die Foundation definiert die zulässigen Regeln.

Nicht:

Die Foundation implementiert den Canonical Layer.

Ebenso

Canonical Layer

governs

Operational Layer

bedeutet:

Die Operational Layer darf ausschließlich innerhalb der kanonischen Regeln arbeiten.

4.5 Informationsfluss

CMIBF unterscheidet Informationsfluss strikt von Steuerungsfluss.

Informationsfluss:

Data

↓

Transformation

↓

Knowledge

↓

Decision

Steuerungsfluss:

Governance

↓

Policies

↓

Validation

↓

Execution

Diese beiden Flüsse dürfen nicht vermischt werden.

4.6 Verantwortungsfluss

Verantwortung fließt ausschließlich nach unten.

Creator

↓

Architecture Board

↓

Framework Owner

↓

Module Owner

↓

Implementation

↓

Runtime

Implementierungen besitzen keine Architekturhoheit.

Architekturentscheidungen entstehen ausschließlich oberhalb.

4.7 Änderungsfluss

Änderungen beginnen niemals im Code.

Sie beginnen immer in der Architektur.

Architecture

↓

Blueprint

↓

Specification

↓

Implementation

↓

Deployment

↓

Runtime

Dadurch entsteht vollständige Rückverfolgbarkeit.

4.8 Dependency-Modell

Das CMIBF beschreibt sämtliche Architekturabhängigkeiten explizit.

Jede Komponente besitzt:

Incoming Dependencies

Outgoing Dependencies

Beispiel

Canonical Registry

Incoming

← Foundation

← Architecture

Outgoing

→ Validation

→ Governance

→ Runtime

Damit wird jede Auswirkung einer Änderung berechenbar.

4.9 Direkte und indirekte Abhängigkeiten

CMIBF unterscheidet zwei Klassen.

Direkt

A

depends_on

B

Indirekt

A

depends_on

B

depends_on

C

Somit besitzt

A

indirectly depends_on

C

Diese Beziehungen werden automatisch berechnet.

4.10 Zyklische Abhängigkeiten

Kanonische Architekturen vermeiden Zyklen.

Unzulässig:

A

depends_on

B

depends_on

A

Zulässig ausschließlich wenn

formal dokumentiert
explizit freigegeben
technisch begründet

Standardregel:

Keine zyklischen Abhängigkeiten.

4.11 Dependency-Ebenen

Nicht jede Ebene darf jede andere Ebene referenzieren.

Zulässig:

Foundation

↓

Canonical

↓

Operational

↓

Runtime

Unzulässig:

Runtime

↓

Foundation

Ebenso

Implementation

↓

Architecture

Eine Implementierung darf Architektur nicht definieren.

4.12 Architekturgraph

Alle Beziehungen bilden gemeinsam einen gerichteten Graphen.

                Foundation

                     │

                     ▼

             Canonical Layer

           ┌─────────┼──────────┐

           ▼         ▼          ▼

      Governance  Registry  Meta Model

           │         │          │

           └─────────┼──────────┘

                     ▼

           Operational Layer

                     ▼

             Runtime Layer

                     ▼

              Monitoring

                     ▼

                Feedback

                     ▼

              Improvement

Dieser Graph beschreibt die vollständige Architektur.

4.13 Kanonischer Dependency Graph (CDG)

Das CMIBF führt den Canonical Dependency Graph (CDG) als zentrales Architekturartefakt ein.

Der CDG ist die maschinenlesbare Repräsentation aller Architekturbeziehungen.

Er enthält:

sämtliche Knoten (Nodes)
sämtliche Beziehungen (Edges)
Beziehungstypen
Richtungen
Gültigkeitsbereiche
Versionen
Status
Konsistenzinformationen
Prüfergebnisse

Der CDG bildet die Grundlage für automatisierte Architekturvalidierung, Impact-Analysen und konsistente Implementierungsplanung.

4.14 Impact Analysis

Vor jeder Änderung kann der CDG automatisch bestimmen:

welche Artefakte betroffen sind,
welche Komponenten indirekt beeinflusst werden,
welche Architekturregeln überprüft werden müssen,
welche Regressionstests erforderlich sind,
welche Dokumente aktualisiert werden müssen.

Architekturänderungen werden dadurch planbar und nachvollziehbar.

4.15 Architekturregeln

Für sämtliche Beziehungen gelten folgende kanonische Regeln:

Regel 1 – Explizite Beziehungen: Jede Architekturbeziehung muss formal definiert sein.

Regel 2 – Typisierung: Jede Beziehung besitzt genau einen kanonischen Beziehungstyp.

Regel 3 – Richtungsprinzip: Beziehungen sind grundsätzlich gerichtet.

Regel 4 – Schichtenintegrität: Beziehungen dürfen keine definierten Architekturschichten verletzen.

Regel 5 – Zyklusfreiheit: Zyklische Abhängigkeiten sind nur in ausdrücklich begründeten Ausnahmefällen zulässig.

Regel 6 – Rückverfolgbarkeit: Änderungen müssen über den CDG bis zu ihren Auswirkungen auf Implementierung und Laufzeit nachvollziehbar sein.

Regel 7 – Maschinenlesbarkeit: Alle Beziehungen müssen in strukturierter Form exportierbar und automatisiert validierbar sein.

Kapitelzusammenfassung

Mit Kapitel 4 erhält das CMIBF seine relationale Architektur. Während Kapitel 3 die Artefakte selbst definiert hat, beschreibt dieses Kapitel deren formale Verknüpfungen. Der Canonical Dependency Graph (CDG) wird als zentrales Architekturartefakt eingeführt und ermöglicht vollständige Abhängigkeitsanalysen, Änderungsplanung und automatisierte Konsistenzprüfungen.