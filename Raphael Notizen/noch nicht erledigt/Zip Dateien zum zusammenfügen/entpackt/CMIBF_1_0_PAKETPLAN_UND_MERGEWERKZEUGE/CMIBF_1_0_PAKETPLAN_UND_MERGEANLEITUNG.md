# CMIBF 1.0 – Verbindlicher Paket- und Zusammenführungsplan

**Zieldatei:** `CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md`  
**Projekt:** Projekt Kontinuum  
**Stand:** 11.07.2026  
**Status:** Arbeits- und Zusammenführungsplan

## 1. Ziel

Das vollständige Werk wird in einzeln herunterladbare ZIP-Pakete aufgeteilt.  
Jedes ZIP enthält genau eine fortlaufend nummerierte Markdown-Hauptdatei.  
Nach Abschluss werden die Dateien in numerischer Reihenfolge ohne inhaltliche Umformatierung zusammengeführt.

## 2. Verbindliche Pakete

| Paket | Dateiname im ZIP | Inhalt |
|---:|---|---|
| 00 | `CMIBF_1_0_00_FRONTMATTER.md` | Titelblatt, Dokumentkontrolle, Präambel, Versionshistorie, Lese- und Geltungsregeln |
| 01 | `CMIBF_1_0_01_ARCHITEKTURPRINZIPIEN_KAPITEL_01_04.md` | Architekturprinzipien sowie Kapitel 1–4 |
| 02 | `CMIBF_1_0_02_KAPITEL_05_08.md` | Kapitel 5–8 |
| 03 | `CMIBF_1_0_03_KAPITEL_09_12.md` | Kapitel 9–12 |
| 04 | `CMIBF_1_0_04_KAPITEL_13_16.md` | Kapitel 13–16 |
| 05 | `CMIBF_1_0_05_KAPITEL_17_20.md` | Kapitel 17–20 |
| 06 | `CMIBF_1_0_06_KAPITEL_21_24.md` | Kapitel 21–24 |
| 07 | `CMIBF_1_0_07_KAPITEL_25_28.md` | Kapitel 25–28 |
| 08 | `CMIBF_1_0_08_KAPITEL_29_32.md` | Kapitel 29–32 |
| 09 | `CMIBF_1_0_09_KAPITEL_33_36.md` | Kapitel 33–36 |
| 10 | `CMIBF_1_0_10_KAPITEL_37_40.md` | Kapitel 37–40 |
| 11 | `CMIBF_1_0_11_GLOSSAR_ABKUERZUNGEN.md` | Glossar und Abkürzungsverzeichnis |
| 12 | `CMIBF_1_0_12_FRAMEWORK_REGISTRY.md` | Vollständige Framework Registry |
| 13 | `CMIBF_1_0_13_CANONICAL_DEPENDENCY_GRAPH.md` | Canonical Dependency Graph einschließlich Mermaid und Regeln |
| 14 | `CMIBF_1_0_14_IMPLEMENTIERUNGS_ROADMAP.md` | Implementierungs-Roadmap, Phasen, Gates und Reihenfolge |
| 15 | `CMIBF_1_0_15_ANHAENGE.md` | Anhänge, Matrizen, Vorlagen, Prüf- und Ableitungsregeln |
| 16 | `CMIBF_1_0_16_SCHLUSSTEIL.md` | Schlussbestimmungen, Freigabevermerk, Dokumentintegrität |

## 3. ZIP-Namensschema

```text
CMIBF_1_0_PAKET_00_FRONTMATTER.zip
CMIBF_1_0_PAKET_01_ARCHITEKTURPRINZIPIEN_KAPITEL_01_04.zip
...
CMIBF_1_0_PAKET_16_SCHLUSSTEIL.zip
```

## 4. Regeln für jedes Paket

Jede Markdown-Datei muss:

1. UTF-8-kodiert sein.
2. genau einen definierten Abschnitt des Gesamtwerks enthalten.
3. mit einem Paket-Metadatenblock beginnen.
4. keine zweite Dokument-Titelseite enthalten.
5. keine eigenständige Versionsnummer besitzen, die der CMIBF-Version widerspricht.
6. am Ende eine eindeutige Fortsetzungsmarke enthalten.
7. Überschriftennummern des Gesamtwerks unverändert bewahren.
8. Querverweise auf die endgültige Gesamtdatei ausrichten.
9. keine Inhalte nur zusammenfassen, wenn der vollständige Inhalt erforderlich ist.
10. nach Review unverändert in die Gesamtdatei übernommen werden können.

## 5. Paket-Metadatenblock

```yaml
---
document_id: CMIBF-1.0
package_id: CMIBF-1.0-PXX
package_sequence: XX
canonical_target: CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md
status: draft-for-review
encoding: UTF-8
merge_order: XX
---
```

Der Metadatenblock bleibt zunächst in den Einzeldateien. Bei der endgültigen kanonischen Zusammenführung werden die Paket-Metadaten entfernt; nur der zentrale Metadatenblock des Gesamtwerks bleibt bestehen.

## 6. Fortsetzungsmarke

Am Ende jeder Paketdatei außer Paket 16:

```text
<!-- CMIBF_PACKAGE_END: PXX | NEXT: PYY -->
```

Am Ende von Paket 16:

```text
<!-- CMIBF_COMPLETE_END -->
```

## 7. Manuelle Zusammenführung

1. Alle ZIP-Dateien in einen gemeinsamen Ordner entpacken.
2. Die `.md`-Dateien nach Namen sortieren.
3. Die Dateien von `00` bis `16` in dieser Reihenfolge zusammenfügen.
4. Die Paket-Metadatenblöcke der Pakete `01` bis `16` entfernen.
5. Fortsetzungsmarken entfernen.
6. Ergebnis speichern als:

```text
CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md
```

7. Abschließend Inhaltsverzeichnis, interne Links und Kapitelnummern prüfen.
8. SHA-256-Prüfsumme erzeugen und in die Dokumentkontrolle eintragen.

## 8. Automatische Zusammenführung unter Windows PowerShell

Die mitgelieferte Datei `MERGE_CMIBF_1_0.ps1` verbindet die Markdown-Dateien in Namensreihenfolge.  
Sie führt zunächst eine Rohzusammenführung durch. Die Bereinigung der Paket-Metadaten erfolgt bei der kanonischen Abschlussprüfung.

## 9. Vorgehen in neuen Chats

Für jeden neuen Chat genügt beispielsweise:

```text
Argos, bitte erstelle jetzt CMIBF 1.0 Paket 03 gemäß dem verbindlichen
Paketplan: Kapitel 9–12. Erstelle die vollständige Markdown-Datei und
stelle sie als ZIP-Datei zum Download bereit.
```

Dabei sollte der zuletzt freigegebene Paketplan hochgeladen oder der genaue Paketname genannt werden.  
Bei Kapiteln, deren exakter Originaltext geprüft werden soll, sollten außerdem die betreffenden bisherigen Kapiteldateien bereitgestellt werden.

## 10. Wichtiger Integritätshinweis

Die Paketierung löst das Größen- und Downloadproblem. Sie ersetzt jedoch nicht die spätere Gesamtprüfung.  
Erst nach Zusammenführung, Review, Querverweisprüfung und Freigabe wird die Datei zur offiziellen:

`CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md`
