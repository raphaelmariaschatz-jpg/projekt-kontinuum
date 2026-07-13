# Projekt Kontinuum 34.1 – Wiedereinstiegspunkt

Stand: 2026-06-25

Kontinuum 34.1 ist der aktive Stand. Foundation 2.2, CAM 1.1, CAM 1.2 und die
Artifact Lifecycle Policy sind Bestandteile der Fundamentebene; das Release
Integrity Framework erzwingt ihre vollständige Freigabekette.

## Verifiziertes Zielbild

- Identitäts- und Rollenblockaden besitzen vollständige Decision-/Answer-Traces
- Erklärungen stammen nur aus gespeicherten Reasoning-Daten
- keine Post-hoc-Regelrekonstruktion
- sichtbare Regelkonflikte mit Gewinnerregel
- Einflusswerte: `ausschlaggebend`, `unterstützend`, `konfliktbehaftet`
- fünf Langzeitziele als aktive Entscheidungsfaktoren
- 48 feste, eindeutige Foundation-Regel-IDs
- FND-ID-048 als eigenständiges Improvement Principle
- Foundation-2.1-Kompatibilitätspfad für ältere Importe
- CAM 1.1 überwacht Archivierung, Freigabebedingungen und signierte Nachweise
- CAM 1.2 überwacht den kanonischen SQLite-Vertrag read-only
- zwölf vorläufige Leitprinzipien weiterhin aktiv

## Start

```text
START_KONTINUUM.bat
16_installation\START_GUI_34_1.bat
16_installation\START_KONTINUUM_34_1.bat
16_installation\RELEASE_GATE_34_1.bat
16_installation\TEST_KONTINUUM_34_1.bat
```

`START_KONTINUUM.bat` ist der kanonische CLI-Start im Projektstamm. Er setzt
`PYTHONPATH` auf `C:\Projekt Kontinuum\01_system` und startet ueber
`python -m kontinuum`. `main.py` und `python -m 01_system.kontinuum` sind
veraltet.

## Aktive Referenzen

- `README.md`
- `14_documents/PROJEKTSTRUKTUR_34_1.md`
- `14_documents/projektstatus/PROJEKTSTATUS_AKTUELL_34_1.md`
- `14_documents/LEITPRINZIPIEN_2026_06_21.md`
- `14_documents/KANONISCHES_ARCHITEKTURMODELL_34_1.md`
- `14_documents/ARBEITSREGEL_ARTEFAKT_LIFECYCLE_34_1.md`
- `24_config/canonical_database_34_1.json`
- `22_project_chronicle/RELEASE_34_1_RELEASE_INTEGRITY_FRAMEWORK.md`
- `14_documents/interne_fehler_und_loesungen/2026_06_21_error_report.md`

Historische Vorversionen bleiben unverändert als Herkunftsnachweis erhalten.

## Wiedereinstieg am 26.06.2026

Heute endet die Umsetzung mit dem vollständig verifizierten Baustein
`CAM 1.2 – Canonical Database Manager`.

Der nächste logische Baustein ist:

`CAM 1.3 – Canonical API Registry`

Der Wiedereinstieg beginnt mit einer read-only Bestandsaufnahme:

1. öffentliche und interne APIs sowie ihre Modulpfade inventarisieren;
2. erlaubte Connectoren und gültige Schnittstellenversionen erfassen;
3. veraltete, doppelte oder unregistrierte Schnittstellen erkennen;
4. einen versionierten API-Vertrag und Abnahmekriterien entwerfen;
5. erst danach Implementierung, Regressionstests und Release-Gate planen.

Keine autonome Schnittstellenänderung und kein Beginn von CAM 1.4 vor
vollständiger Freigabe von CAM 1.3.

## Wiedereinstieg am 30.06.2026

Aktueller Stand: WebAgent 1.0, FileAgent 1.0 und Continuous Canonical Engine
1.0 sind fuer Kontinuum 34.1 diagnostisch/read-only integriert.

Naechster sinnvoller Einstieg:

1. `canonicalenginestatus` in der GUI pruefen;
2. CCE-Logs unter `31_reports/events`, `31_reports/drift` und
   `31_reports/governance` inspizieren;
3. Release-Gate mit CCE-Gate erneut ausfuehren;
4. offene Governance Hooks nur manuell reviewen;
5. danach CKDE-/CDE-Feinabstimmung planen.

Keine automatische Massenaufnahme, keine automatische Archivierung und keine
Gate-Umgehung.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
