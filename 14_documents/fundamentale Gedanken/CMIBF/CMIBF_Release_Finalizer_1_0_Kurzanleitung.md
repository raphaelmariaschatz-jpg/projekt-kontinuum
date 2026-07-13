# CMIBF Release Finalizer 1.0 – Kurzanleitung

## Zweck

Der Finalizer erstellt aus einer geprüften CMIBF-Masterdatei ein finales,
reproduzierbares Release-Paket. Die Eingabedatei wird niemals verändert.

## Empfohlener Aufruf für den aktuellen Stand

```powershell
pwsh.exe -ExecutionPolicy Bypass `
  -File ".\CMIBF_Release_Finalizer_1_0.ps1" `
  -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0_REPAIRED.md" `
  -ValidatorPath ".\CMIBF_Release_Validator_1_0.ps1" `
  -ReleaseVersion "1.0" `
  -ApprovedBy "Raphael Maria Schatz" `
  -ApproveWarnings `
  -WarningApprovalReason "Die drei Duplicate-Heading-Warnungen wurden redaktionell geprüft und sind aufgrund wiederkehrender Titelblöcke beziehungsweise kontextbezogener Abschnittsüberschriften zulässig." `
  -MarkReadOnly
```

## Ergebnis

Standardmäßig entsteht der Ordner:

```text
cmibf_releases/
└── CMIBF_1_0_YYYYMMDD_HHMMSS/
    ├── CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md
    ├── CMIBF_RELEASE_MANIFEST.json
    ├── CMIBF_RELEASE_FREIGABEBERICHT.md
    ├── CMIBF_RELEASE_NOTES.md
    ├── SHA256SUMS.txt
    └── validation/
        ├── CMIBF_RELEASE_VALIDATION_REPORT.md
        └── CMIBF_RELEASE_VALIDATION_REPORT.json
```

Zusätzlich wird ein gleichnamiges ZIP-Paket erzeugt.

## Sicherheitsregeln

- Jeder Validator-Fehler blockiert die Finalisierung.
- Warnungen blockieren, sofern sie nicht ausdrücklich freigegeben wurden.
- Die finale Masterdatei muss byteidentisch zur validierten Eingabedatei sein.
- SHA-256 und Dateigröße werden vor der Freigabe verglichen.
- Ein unvollständiger Validator-Bericht blockiert die Finalisierung.
- Das Original wird weder überschrieben noch umbenannt.
