#requires -Version 7.0
<#
.SYNOPSIS
    Finalisiert eine geprüfte CMIBF-Masterdatei als reproduzierbares Release-Paket.

.DESCRIPTION
    Der CMIBF Release Finalizer 1.0:

    1. führt den CMIBF Release Validator 1.0 im Audit-Modus aus,
    2. blockiert das Release bei Fehlern,
    3. verlangt bei Warnungen eine ausdrückliche Freigabe,
    4. erstellt eine unveränderte finale Masterdatei,
    5. erzeugt SHA-256-Hashes, Manifest, Freigabebericht und Release Notes,
    6. übernimmt den Validator-Bericht in das Release,
    7. erstellt optional ein ZIP-Paket,
    8. verändert die Eingabedatei niemals.

    Exitcodes:
      0 = Release erfolgreich finalisiert
      1 = Release wegen nicht freigegebener Warnungen abgebrochen
      2 = Release wegen Validierungsfehlern abgebrochen
      3 = Konfigurations-, Integritäts- oder Ausführungsfehler

.EXAMPLE
    pwsh.exe -ExecutionPolicy Bypass -File ".\CMIBF_Release_Finalizer_1_0.ps1" `
        -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0_REPAIRED.md" `
        -ValidatorPath ".\CMIBF_Release_Validator_1_0.ps1" `
        -ApproveWarnings `
        -WarningApprovalReason "Doppelte Titelüberschriften wurden geprüft und sind kontextbedingt zulässig."

.EXAMPLE
    pwsh.exe -ExecutionPolicy Bypass -File ".\CMIBF_Release_Finalizer_1_0.ps1" `
        -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0_REPAIRED.md" `
        -ValidatorPath ".\CMIBF_Release_Validator_1_0.ps1" `
        -ReleaseRoot ".\cmibf_releases" `
        -ReleaseVersion "1.0" `
        -ApprovedBy "Raphael Maria Schatz" `
        -ApproveWarnings `
        -WarningApprovalReason "Die drei Duplicate-Heading-Warnungen wurden redaktionell geprüft."
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ValidatorPath,

    [string]$ReleaseRoot,

    [ValidatePattern('^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?$')]
    [string]$ReleaseVersion = '1.0',

    [string]$ApprovedBy = 'Raphael Maria Schatz',

    [switch]$ApproveWarnings,

    [string]$WarningApprovalReason,

    [string[]]$ApprovedWarningCodes = @(),

    [switch]$NoZip,

    [switch]$MarkReadOnly,

    [switch]$OverwriteRelease
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ToolName = 'CMIBF Release Finalizer 1.0'
$CanonicalFileName = 'CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md'
$Utf8NoBom = [Text.UTF8Encoding]::new($false)
$stagingDirectory = $null

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content
    )
    [IO.File]::WriteAllText($Path, $Content, $script:Utf8NoBom)
}

function Escape-MarkdownCell {
    param([AllowEmptyString()][string]$Value)
    if ($null -eq $Value) { return '' }
    return (($Value -replace '\|', '\|') -replace "`r|`n", ' ')
}

function Get-SafeFileName {
    param([Parameter(Mandatory = $true)][string]$Value)
    $invalid = [IO.Path]::GetInvalidFileNameChars()
    $result = $Value
    foreach ($char in $invalid) {
        $result = $result.Replace([string]$char, '_')
    }
    return $result
}

function Stop-Finalizer {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [ValidateSet(1,2,3)][int]$ExitCode = 3
    )
    Write-Error $Message
    exit $ExitCode
}

try {
    # -------------------------------------------------------------------------
    # Pfade und Grundvoraussetzungen
    # -------------------------------------------------------------------------
    $resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
    $resolvedValidator = (Resolve-Path -LiteralPath $ValidatorPath).Path

    if ([IO.Path]::GetExtension($resolvedInput) -ne '.md') {
        Stop-Finalizer "Die Eingabedatei muss eine Markdown-Datei sein: $resolvedInput"
    }

    if ([IO.Path]::GetExtension($resolvedValidator) -ne '.ps1') {
        Stop-Finalizer "Der Validator muss eine PowerShell-Datei sein: $resolvedValidator"
    }

    if ([string]::IsNullOrWhiteSpace($ApprovedBy)) {
        Stop-Finalizer 'ApprovedBy darf nicht leer sein.'
    }

    if ($ApproveWarnings -and [string]::IsNullOrWhiteSpace($WarningApprovalReason)) {
        Stop-Finalizer 'Bei -ApproveWarnings muss -WarningApprovalReason angegeben werden.'
    }

    $inputDirectory = Split-Path -Parent $resolvedInput
    if ([string]::IsNullOrWhiteSpace($ReleaseRoot)) {
        $ReleaseRoot = Join-Path $inputDirectory 'cmibf_releases'
    }
    $ReleaseRoot = [IO.Path]::GetFullPath($ReleaseRoot)
    [void](New-Item -ItemType Directory -Path $ReleaseRoot -Force)

    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $releaseId = "CMIBF_$($ReleaseVersion.Replace('.', '_'))_$timestamp"
    $releaseDirectory = Join-Path $ReleaseRoot $releaseId
    $stagingDirectory = Join-Path $ReleaseRoot ('.staging_' + $releaseId + '_' + [guid]::NewGuid().ToString('N'))

    if (Test-Path -LiteralPath $releaseDirectory) {
        if (-not $OverwriteRelease) {
            Stop-Finalizer "Das Release-Verzeichnis existiert bereits: $releaseDirectory"
        }
        Remove-Item -LiteralPath $releaseDirectory -Recurse -Force
    }

    [void](New-Item -ItemType Directory -Path $stagingDirectory -Force)
    $validationDirectory = Join-Path $stagingDirectory 'validation'
    [void](New-Item -ItemType Directory -Path $validationDirectory -Force)

    # -------------------------------------------------------------------------
    # Validator im Audit-Modus ausführen
    # -------------------------------------------------------------------------
    Write-Host ''
    Write-Host "===== $ToolName ====="
    Write-Host "Eingabe:      $resolvedInput"
    Write-Host "Validator:    $resolvedValidator"
    Write-Host "Release:      $ReleaseVersion"
    Write-Host ''

    & pwsh.exe -NoProfile -ExecutionPolicy Bypass -File $resolvedValidator `
        -InputPath $resolvedInput `
        -Mode Audit `
        -ReportDirectory $validationDirectory

    $validatorExitCode = $LASTEXITCODE

    $jsonReportFile = Get-ChildItem -LiteralPath $validationDirectory -File `
        -Filter 'CMIBF_RELEASE_PRUEFBERICHT_*.json' |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1

    $mdReportFile = Get-ChildItem -LiteralPath $validationDirectory -File `
        -Filter 'CMIBF_RELEASE_PRUEFBERICHT_*.md' |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1

    if ($null -eq $jsonReportFile -or $null -eq $mdReportFile) {
        Stop-Finalizer 'Der Validator hat keinen vollständigen Markdown-/JSON-Bericht erzeugt.'
    }

    $validatorReport = Get-Content -LiteralPath $jsonReportFile.FullName -Raw -Encoding utf8 |
        ConvertFrom-Json -Depth 20

    $errorCount = [int]$validatorReport.error_count
    $warningCount = [int]$validatorReport.warning_count
    $infoCount = [int]$validatorReport.info_count
    $headingCount = [int]$validatorReport.heading_count
    $lineCount = [int]$validatorReport.line_count

    if ($validatorExitCode -eq 2 -or $errorCount -gt 0) {
        $failedDirectory = Join-Path $ReleaseRoot ("FAILED_$releaseId")
        Move-Item -LiteralPath $stagingDirectory -Destination $failedDirectory
        Write-Host ''
        Write-Host 'RELEASE BLOCKIERT: Der Validator meldet Fehler.'
        Write-Host "Fehler:        $errorCount"
        Write-Host "Warnungen:     $warningCount"
        Write-Host "Prüfberichte:  $failedDirectory"
        exit 2
    }

    if ($validatorExitCode -notin @(0,1)) {
        Stop-Finalizer "Der Validator wurde mit einem unerwarteten Exitcode beendet: $validatorExitCode"
    }

    # -------------------------------------------------------------------------
    # Warnungsfreigabe
    # -------------------------------------------------------------------------
    $warningFindings = @($validatorReport.findings | Where-Object {
        $_.Severity -eq 'WARNING'
    })

    $unapprovedWarnings = @()

    if ($warningCount -gt 0) {
        if ($ApproveWarnings) {
            $unapprovedWarnings = @()
        }
        elseif ($ApprovedWarningCodes.Count -gt 0) {
            $unapprovedWarnings = @($warningFindings | Where-Object {
                $ApprovedWarningCodes -notcontains [string]$_.Code
            })
        }
        else {
            $unapprovedWarnings = $warningFindings
        }
    }

    if ($unapprovedWarnings.Count -gt 0) {
        $failedDirectory = Join-Path $ReleaseRoot ("PENDING_WARNING_APPROVAL_$releaseId")
        Move-Item -LiteralPath $stagingDirectory -Destination $failedDirectory
        Write-Host ''
        Write-Host 'RELEASE NICHT FINALISIERT: Warnungen wurden nicht vollständig freigegeben.'
        Write-Host "Warnungen:     $warningCount"
        Write-Host "Offen:         $($unapprovedWarnings.Count)"
        Write-Host "Prüfberichte:  $failedDirectory"
        Write-Host ''
        Write-Host 'Verwende -ApproveWarnings zusammen mit -WarningApprovalReason,'
        Write-Host 'oder gib einzelne Codes mit -ApprovedWarningCodes frei.'
        exit 1
    }

    # -------------------------------------------------------------------------
    # Finale Datei unverändert übernehmen und Integrität prüfen
    # -------------------------------------------------------------------------
    $finalDocumentPath = Join-Path $stagingDirectory $CanonicalFileName
    Copy-Item -LiteralPath $resolvedInput -Destination $finalDocumentPath -Force

    $inputHash = (Get-FileHash -LiteralPath $resolvedInput -Algorithm SHA256).Hash.ToUpperInvariant()
    $finalHash = (Get-FileHash -LiteralPath $finalDocumentPath -Algorithm SHA256).Hash.ToUpperInvariant()

    if ($inputHash -ne $finalHash) {
        Stop-Finalizer 'Integritätsfehler: Eingabe- und Release-Datei besitzen unterschiedliche SHA-256-Hashes.'
    }

    $inputLength = (Get-Item -LiteralPath $resolvedInput).Length
    $finalLength = (Get-Item -LiteralPath $finalDocumentPath).Length

    if ($inputLength -ne $finalLength) {
        Stop-Finalizer 'Integritätsfehler: Eingabe- und Release-Datei besitzen unterschiedliche Dateigrößen.'
    }

    # Validator-Berichte kanonisch benennen
    $releaseValidationMd = Join-Path $validationDirectory 'CMIBF_RELEASE_VALIDATION_REPORT.md'
    $releaseValidationJson = Join-Path $validationDirectory 'CMIBF_RELEASE_VALIDATION_REPORT.json'
    Move-Item -LiteralPath $mdReportFile.FullName -Destination $releaseValidationMd -Force
    Move-Item -LiteralPath $jsonReportFile.FullName -Destination $releaseValidationJson -Force

    # -------------------------------------------------------------------------
    # Manifest
    # -------------------------------------------------------------------------
    $releaseTimestamp = (Get-Date).ToString('o')
    $warningApprovalMode = if ($warningCount -eq 0) {
        'NOT_REQUIRED'
    }
    elseif ($ApproveWarnings) {
        'ALL_WARNINGS_EXPLICITLY_APPROVED'
    }
    else {
        'APPROVED_BY_WARNING_CODE'
    }

    $manifest = [ordered]@{
        schema = 'projekt-kontinuum.cmibf.release-manifest.v1'
        tool = $ToolName
        release_id = $releaseId
        release_version = $ReleaseVersion
        release_status = 'FINAL'
        timestamp = $releaseTimestamp
        approved_by = $ApprovedBy
        source = [ordered]@{
            path = $resolvedInput
            file_name = [IO.Path]::GetFileName($resolvedInput)
            size_bytes = $inputLength
            sha256 = $inputHash
        }
        canonical_artifact = [ordered]@{
            artifact_id = 'PK-FW-META-001'
            canonical_name = 'Canonical Master Implementation Blueprint Framework'
            abbreviation = 'CMIBF'
            version = $ReleaseVersion
            file_name = $CanonicalFileName
            size_bytes = $finalLength
            sha256 = $finalHash
            encoding = 'UTF-8'
            immutable_copy = $true
        }
        validation = [ordered]@{
            validator = [string]$validatorReport.validator
            validator_exit_code = $validatorExitCode
            errors = $errorCount
            warnings = $warningCount
            information = $infoCount
            lines = $lineCount
            headings = $headingCount
            result = if ($warningCount -gt 0) { 'APPROVED_WITH_WARNINGS' } else { 'PASSED' }
            report_markdown = 'validation/CMIBF_RELEASE_VALIDATION_REPORT.md'
            report_json = 'validation/CMIBF_RELEASE_VALIDATION_REPORT.json'
        }
        warning_approval = [ordered]@{
            required = ($warningCount -gt 0)
            mode = $warningApprovalMode
            approved_codes = @($ApprovedWarningCodes)
            reason = if ($warningCount -gt 0) { $WarningApprovalReason } else { $null }
            approved_by = if ($warningCount -gt 0) { $ApprovedBy } else { $null }
            approved_at = if ($warningCount -gt 0) { $releaseTimestamp } else { $null }
        }
        package = [ordered]@{
            zip_created = (-not $NoZip)
            read_only_requested = [bool]$MarkReadOnly
        }
    }

    $manifestJsonPath = Join-Path $stagingDirectory 'CMIBF_RELEASE_MANIFEST.json'
    $manifestJson = $manifest | ConvertTo-Json -Depth 12
    Write-Utf8NoBom -Path $manifestJsonPath -Content ($manifestJson + "`n")

    # -------------------------------------------------------------------------
    # Lesbarer Freigabebericht
    # -------------------------------------------------------------------------
    $warningRows = @()
    foreach ($warning in $warningFindings) {
        $warningRows += "| $([int]$warning.Line) | ``$(Escape-MarkdownCell ([string]$warning.Code))`` | $(Escape-MarkdownCell ([string]$warning.Description)) | $(Escape-MarkdownCell ([string]$warning.Excerpt)) |"
    }

    $reportLines = [Collections.Generic.List[string]]::new()
    [void]$reportLines.Add('# CMIBF Release-Freigabebericht')
    [void]$reportLines.Add('')
    [void]$reportLines.Add("- **Release-ID:** ``$releaseId``")
    [void]$reportLines.Add("- **Version:** $ReleaseVersion")
    [void]$reportLines.Add("- **Status:** **FINAL**")
    [void]$reportLines.Add("- **Finalisiert am:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')")
    [void]$reportLines.Add("- **Freigegeben durch:** $ApprovedBy")
    [void]$reportLines.Add("- **Kanonische Datei:** ``$CanonicalFileName``")
    [void]$reportLines.Add("- **SHA-256:** ``$finalHash``")
    [void]$reportLines.Add("- **Dateigröße:** $finalLength Bytes")
    [void]$reportLines.Add('')
    [void]$reportLines.Add('## Validierung')
    [void]$reportLines.Add('')
    [void]$reportLines.Add("- Fehler: **$errorCount**")
    [void]$reportLines.Add("- Warnungen: **$warningCount**")
    [void]$reportLines.Add("- Hinweise: **$infoCount**")
    [void]$reportLines.Add("- Zeilen: **$lineCount**")
    [void]$reportLines.Add("- Überschriften: **$headingCount**")
    [void]$reportLines.Add("- Ergebnis: **$(if ($warningCount -gt 0) { 'FREIGEGEBEN MIT GEPRÜFTEN WARNUNGEN' } else { 'BESTANDEN' })**")
    [void]$reportLines.Add('')

    if ($warningCount -gt 0) {
        [void]$reportLines.Add('## Freigegebene Warnungen')
        [void]$reportLines.Add('')
        [void]$reportLines.Add("| Zeile | Code | Beschreibung | Fundstelle |")
        [void]$reportLines.Add('|---:|---|---|---|')
        foreach ($row in $warningRows) {
            [void]$reportLines.Add($row)
        }
        [void]$reportLines.Add('')
        [void]$reportLines.Add("- **Freigabebegründung:** $WarningApprovalReason")
        [void]$reportLines.Add("- **Freigegeben durch:** $ApprovedBy")
        [void]$reportLines.Add('')
    }

    [void]$reportLines.Add('## Integritätsaussage')
    [void]$reportLines.Add('')
    [void]$reportLines.Add('Die finale Masterdatei wurde byteidentisch aus der validierten Eingabedatei übernommen.')
    [void]$reportLines.Add('Eingabe und Release-Artefakt besitzen denselben SHA-256-Hash. Die Eingabedatei wurde nicht verändert.')
    [void]$reportLines.Add('')
    [void]$reportLines.Add('## Kanonische Wirkung')
    [void]$reportLines.Add('')
    [void]$reportLines.Add('Dieses Release bildet die freigegebene kanonische Fassung des CMIBF 1.0.')
    [void]$reportLines.Add('Abgeleitete Architekturartefakte dürfen dem CMIBF nicht widersprechen und sind aus dieser Fassung abzuleiten.')

    $releaseReportPath = Join-Path $stagingDirectory 'CMIBF_RELEASE_FREIGABEBERICHT.md'
    Write-Utf8NoBom -Path $releaseReportPath -Content (($reportLines -join "`n") + "`n")

    # -------------------------------------------------------------------------
    # Release Notes
    # -------------------------------------------------------------------------
    $releaseNotes = @"
# CMIBF $ReleaseVersion – Release Notes

- **Release-ID:** ``$releaseId``
- **Status:** FINAL
- **Freigabe:** $ApprovedBy
- **Datum:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')
- **Masterdatei:** ``$CanonicalFileName``
- **SHA-256:** ``$finalHash``

## Inhalt

Dieses Paket enthält die finale, validierte und integritätsgesicherte Fassung des
Canonical Master Implementation Blueprint Framework (CMIBF) $ReleaseVersion.

## Paketbestandteile

- ``$CanonicalFileName``
- ``CMIBF_RELEASE_MANIFEST.json``
- ``CMIBF_RELEASE_FREIGABEBERICHT.md``
- ``CMIBF_RELEASE_NOTES.md``
- ``SHA256SUMS.txt``
- ``validation/CMIBF_RELEASE_VALIDATION_REPORT.md``
- ``validation/CMIBF_RELEASE_VALIDATION_REPORT.json``

## Validierungsstatus

- Fehler: $errorCount
- Warnungen: $warningCount
- Hinweise: $infoCount
- Ergebnis: $(if ($warningCount -gt 0) { 'Freigegeben mit dokumentierter Warnungsprüfung' } else { 'Bestanden ohne Warnungen' })
"@
    $releaseNotesPath = Join-Path $stagingDirectory 'CMIBF_RELEASE_NOTES.md'
    Write-Utf8NoBom -Path $releaseNotesPath -Content ($releaseNotes.TrimEnd() + "`n")

    # -------------------------------------------------------------------------
    # Hashliste aller Paketdateien
    # -------------------------------------------------------------------------
    $hashListPath = Join-Path $stagingDirectory 'SHA256SUMS.txt'
    $packageFiles = Get-ChildItem -LiteralPath $stagingDirectory -File -Recurse |
        Where-Object { $_.FullName -ne $hashListPath } |
        Sort-Object FullName

    $hashLines = foreach ($file in $packageFiles) {
        $relative = [IO.Path]::GetRelativePath($stagingDirectory, $file.FullName).Replace('\', '/')
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $relative"
    }
    Write-Utf8NoBom -Path $hashListPath -Content (($hashLines -join "`n") + "`n")

    # Staging atomar zum finalen Release-Verzeichnis machen
    Move-Item -LiteralPath $stagingDirectory -Destination $releaseDirectory

    # -------------------------------------------------------------------------
    # ZIP erstellen
    # -------------------------------------------------------------------------
    $zipPath = $null
    if (-not $NoZip) {
        $zipPath = Join-Path $ReleaseRoot ($releaseId + '.zip')
        if (Test-Path -LiteralPath $zipPath) {
            if ($OverwriteRelease) {
                Remove-Item -LiteralPath $zipPath -Force
            }
            else {
                Stop-Finalizer "Das ZIP-Paket existiert bereits: $zipPath"
            }
        }
        Compress-Archive -LiteralPath (Join-Path $releaseDirectory '*') `
            -DestinationPath $zipPath `
            -CompressionLevel Optimal
    }

    # Optional: Release-Dateien schreibschützen
    if ($MarkReadOnly) {
        Get-ChildItem -LiteralPath $releaseDirectory -File -Recurse | ForEach-Object {
            $_.IsReadOnly = $true
        }
    }

    # -------------------------------------------------------------------------
    # Abschluss
    # -------------------------------------------------------------------------
    Write-Host ''
    Write-Host "===== $ToolName ====="
    Write-Host 'Status:        FINALISIERT'
    Write-Host "Release-ID:    $releaseId"
    Write-Host "Version:       $ReleaseVersion"
    Write-Host "Fehler:        $errorCount"
    Write-Host "Warnungen:     $warningCount"
    Write-Host "Hinweise:      $infoCount"
    Write-Host "SHA-256:       $finalHash"
    Write-Host "Release-Pfad:  $releaseDirectory"
    if ($null -ne $zipPath) {
        Write-Host "ZIP-Paket:     $zipPath"
    }
    Write-Host ''
    exit 0
}
catch {
    if (-not [string]::IsNullOrWhiteSpace($stagingDirectory) -and (Test-Path -LiteralPath $stagingDirectory -ErrorAction SilentlyContinue)) {
        Remove-Item -LiteralPath $stagingDirectory -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Error "$ToolName ist fehlgeschlagen: $($_.Exception.Message)"
    exit 3
}
