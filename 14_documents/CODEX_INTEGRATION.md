# Codex-Integration in Kontinuum 23.0

Stand: 2026-06-10

Kontinuum besitzt einen eigenen `CodexAgent` und ein kontrolliertes
`CodexTools`-Gateway.

## Kanonische Architekturbindung

Fuer alle Codex-Arbeiten an Projekt Kontinuum gilt:

- Das CMIBF 1.0 ist die einzige normative Architekturquelle und Architekturverfassung.
- Das Canonical Architecture First Principle (AFP) ist verbindlich.
- Das Canonical AI Working Protocol (CAWP) 1.0 ist fuer Codex als KI-Arbeitsprotokoll verbindlich.
- Codex darf keine Implementierung, kein Framework, keinen Agenten, kein Modul, keine Registry, kein Datenmodell, keine Dokumentation und keinen Build erzeugen, wenn die zugrunde liegende Architektur nicht zuvor im CMIBF definiert, geprueft und freigegeben wurde.
- Code besitzt keine normative Architekturautoritaet.
- Architektur darf nicht aus bestehendem Code rekonstruiert und ungeprueft als kanonisch behandelt werden.
- Erkenntnisse aus Implementierung, Tests, Betrieb oder Monitoring muessen als Architekturanalyse in den AFP-Zyklus zurueckgefuehrt werden.
- Codex muss Annahmen, Risiken, Pruefungen, Testgrenzen, Traceability und Abschlussbefunde nach CAWP transparent machen.

Verbindliche Reihenfolge:

```text
Idee
-> Architekturanalyse
-> CMIBF-Definition oder CMIBF-Erweiterung
-> Architekturpruefung
-> Freigabe
-> CAC
-> kanonische Artefakte
-> Implementierung
-> Validierung und Tests
-> Release
-> Betrieb
-> Monitoring
-> kontrollierte Evolution
```

Der Canonical Architecture Compiler (CAC) ist als Compiler zu behandeln, nicht als freier Artefaktgenerator oder eigenstaendiger Architekt. Er liest das CMIBF, prueft Syntax, Semantik, Regeln, Inkonsistenzen und AFP-Konformitaet, erzeugt ausschliesslich deterministische Ableitungen und muss ungueltige Architektur-Builds verweigern.

Kanonische Governance-Hierarchie fuer Codex:

```text
CMIBF
-> AFP
-> CAWP
-> CAC
```

## Befehle

```text
codexstatus
codex: Prüfe die Python-Dateien auf Syntaxfehler
```

## Sicherheit

- Standardmodus: `read-only`
- Prompts und Codex-Antworten werden nicht dauerhaft gespeichert.
- Codex läuft als separater Prozess im Projektwurzelverzeichnis.
- Eine Schreibfreigabe muss bewusst über `KONTINUUM_CODEX_SANDBOX` gesetzt werden.

## Aktive CLI

```text
C:\Projekt Kontinuum\13_tools\codex_cli\codex.exe
```

Die integrierte CLI wird automatisch erkannt. Für eine andere CLI-Version kann
optional `KONTINUUM_CODEX_COMMAND` gesetzt werden.

Statusprüfung:

```text
16_installation\START_KONTINUUM_23.bat codexstatus
```


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
