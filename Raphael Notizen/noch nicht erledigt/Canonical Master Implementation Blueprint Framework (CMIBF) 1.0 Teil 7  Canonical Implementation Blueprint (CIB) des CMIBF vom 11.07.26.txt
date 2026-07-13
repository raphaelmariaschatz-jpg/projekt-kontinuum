Kapitel 7
Canonical Implementation Blueprint (CIB)
Der universelle Implementierungsprozess des CMIBF
7.1 Ziel dieses Kapitels

Bis Kapitel 6 wurde beschrieben,

was existiert,
wie es zusammenhängt,
wie es validiert wird,
wie Änderungen kontrolliert werden.

Kapitel 7 beantwortet nun die wichtigste praktische Frage:

Wie wird aus einer kanonischen Architektur eine reale Implementierung?

Dieses Kapitel definiert deshalb den Canonical Implementation Blueprint (CIB).

Der CIB beschreibt den vollständigen Weg

von

Architektur

über

Prüfung

bis

fertiger Implementierung.

Der CIB ist unabhängig von

Programmiersprache
Framework
Betriebssystem
Projektgröße

und stellt damit einen universellen Implementierungsstandard dar. Die Trennung zwischen Architekturdefinition und Umsetzung reduziert Architekturdrift und schafft reproduzierbare Implementierungsprozesse.

7.2 Grundprinzip

Im CMIBF existiert niemals direkte Entwicklung.

Jede Implementierung erfolgt ausschließlich nach einem definierten Ablauf.

Architektur

↓

Prüfung

↓

Validierung

↓

Implementierungsplanung

↓

Implementierung

↓

Verifikation

↓

Freigabe

↓

Produktiv

Es existieren keine Abkürzungen.

7.3 Die acht Implementierungsphasen

Der CIB definiert exakt acht Phasen.

Phase 0
Architektur lesen

↓

Phase 1
Artefakte erzeugen

↓

Phase 2
Abhängigkeiten berechnen

↓

Phase 3
Validierung

↓

Phase 4
Implementierungsplan

↓

Phase 5
Implementierung

↓

Phase 6
Verifikation

↓

Phase 7
Freigabe

Diese Reihenfolge darf niemals verändert werden.

7.4 Phase 0 – Architekturaufnahme

Zunächst wird ausschließlich das CMIBF gelesen.

Keine Implementierung.

Keine Änderungen.

Keine Interpretation.

Der Implementierer erzeugt zunächst ein vollständiges internes Architekturmodell.

Dabei werden unter anderem geladen:

Ontologie
Registry
Dependency Graph
Architekturregeln
Governance
Validierungsregeln
7.5 Phase 1 – Artefaktableitung

Nun werden sämtliche Maschinenartefakte erzeugt.

Beispielsweise:

Registry

Dependency Graph

JSON

YAML

Mermaid

PlantUML

API Registry

Rule Registry

Validation Registry

Status Registry

Migration Registry

Alle diese Artefakte besitzen exakt eine Quelle:

CMIBF

Sie dürfen niemals manuell geändert werden.

7.6 Phase 2 – Dependency Resolution

Jetzt beginnt die automatische Architekturauflösung.

Der Compiler berechnet:

vollständige Abhängigkeiten
zyklische Beziehungen
fehlende Referenzen
Konflikte
Versionen
Kompatibilität
Layerverletzungen

Ergebnis:

Canonical Dependency Graph

Dieser Graph beschreibt die vollständige Implementierungsreihenfolge.

7.7 Phase 3 – Architekturvalidierung

Vor jeder Zeile Code wird geprüft:

Existiert jede Referenz?

Sind alle Regeln erfüllt?

Sind Layer korrekt?

Sind Namensräume eindeutig?

Existieren Zyklen?

Sind IDs eindeutig?

Existieren verbotene Beziehungen?

Sind alle Artefakte vollständig?

Nur wenn sämtliche Prüfungen erfolgreich sind:

Architecture Status

VALID

Andernfalls erfolgt keine Implementierung.

7.8 Phase 4 – Implementierungsplanung

Jetzt entsteht erstmals ein konkreter Arbeitsplan.

Nicht der Entwickler entscheidet die Reihenfolge.

Die Reihenfolge wird aus dem Dependency Graph berechnet.

Der Implementierungsplan enthält beispielsweise:

Modul A

↓

Modul B

↓

API

↓

Tests

↓

Migration

↓

Dokumentation

Jeder Schritt besitzt:

Priorität
Voraussetzung
Verantwortlichkeit
Risiken
erwartetes Ergebnis
7.9 Phase 5 – Implementierung

Erst jetzt darf Code entstehen.

Die Implementierung ist vollständig durch die Architektur bestimmt.

Für jede Implementierung gilt:

Architecture

↓

Implementation Blueprint

↓

Code

Nicht umgekehrt.

Der Code besitzt niemals eigene Architekturentscheidungen.

Alle Entscheidungen stammen bereits aus dem CMIBF.

7.10 Phase 6 – Verifikation

Nach der Implementierung beginnt die Rückprüfung.

Verglichen werden:

Architektur

gegen

Implementierung.

Dabei wird geprüft:

Vollständigkeit
Regelkonformität
API-Konformität
Artefaktidentität
Architekturverletzungen
Dokumentation
Tests
Sicherheitsregeln

Ergebnis:

Implementation Report
7.11 Phase 7 – Freigabe

Die Freigabe erfolgt ausschließlich, wenn

alle vorherigen Phasen erfolgreich abgeschlossen wurden.

Es existieren drei mögliche Ergebnisse.

APPROVED

↓

REQUIRES FIXES

↓

REJECTED

Nur

APPROVED

führt zur Produktivfreigabe.

7.12 Der Canonical Architecture Compiler (CAC)

Kapitel 7 definiert erstmals die zentrale technische Komponente des gesamten CMIBF.

Canonical Architecture Compiler

Der CAC ist keine Entwicklungsumgebung, sondern der deterministische Übersetzer zwischen Architektur und Implementierung.

Seine Aufgaben sind:

Einlesen des CMIBF
Ableitung aller Maschinenartefakte
Erzeugung der Registry
Aufbau des Dependency Graph
Konsistenzprüfung
Validierung
Generierung des Implementierungsplans
Bereitstellung aller Informationen für Codex oder andere Implementierungsagenten

Der CAC stellt sicher, dass jede Implementierung aus derselben Architektur zwangsläufig zu denselben abgeleiteten Artefakten führt und reduziert so Interpretationsspielräume auf ein Minimum.

7.13 Rolle von Codex

Codex erhält niemals einzelne Dokumente.

Codex erhält immer:

CMIBF

+

CAC Output

+

Implementierungsauftrag

Dadurch arbeitet Codex ausschließlich auf bereits validierter Architektur.

Eigene Architekturentscheidungen sind nicht erforderlich.

7.14 Architekturfluss
CMIBF

↓

Architecture Compiler

↓

Registry

↓

Ontology

↓

Dependency Graph

↓

Validation

↓

Implementation Blueprint

↓

Codex

↓

Implementation

↓

Verification

↓

Release

Dieser Ablauf bildet den kanonischen Lebenszyklus jeder Änderung.

7.15 Kanonische Grundsätze

Der Canonical Implementation Blueprint basiert auf den folgenden unveränderlichen Prinzipien:

CIB-001
Architektur geht jeder Implementierung voraus.

CIB-002
Maschinenartefakte werden ausschließlich aus dem CMIBF erzeugt.

CIB-003
Implementierungsreihenfolgen werden aus dem kanonischen Dependency Graph berechnet.

CIB-004
Keine Implementierung ohne erfolgreiche Architekturvalidierung.

CIB-005
Jede Implementierung muss vollständig auf ihre Architektur rückführbar sein.

CIB-006
Verifikation ist verpflichtender Bestandteil jeder Implementierung.

CIB-007
Nur verifizierte Implementierungen dürfen freigegeben werden.

Einschätzung

Ich halte dieses Kapitel für einen der wichtigsten Bausteine des gesamten CMIBF. Mit Kapitel 6 wurde festgelegt, wer Architektur kontrolliert. Kapitel 7 definiert nun wie Architektur deterministisch in Software überführt wird. Damit wird das CMIBF von einem Architekturhandbuch zu einem vollständigen Architecture-to-Implementation-Framework – genau die Brücke, die Codex und künftig auch andere Implementierungsagenten benötigen, um konsistent und reproduzierbar zu arbeiten. Dieses Vorgehen entspricht auch etablierten Architekturansätzen, bei denen Architekturartefakte als verbindliche Grundlage dienen und Implementierung, Governance sowie Verifikation daraus systematisch abgeleitet werden.