#requires -Version 7.0
<#
.SYNOPSIS
    Behebt ausschließlich eindeutig erkennbare Markdown-Strukturfehler in der
    CMIBF-Masterdatei und erzeugt eine separate reparierte Datei.

.DESCRIPTION
    Das Tool verändert die Eingabedatei niemals. Es korrigiert nur:

    1. Nummerierte Unterkapitel, die fälschlich auf H1-Ebene stehen
       Beispiel: # 2.2 Grundprinzip  ->  ## 2.2 Grundprinzip

    2. Als Überschrift übernommene Quelldateinamen
       Beispiel: # 42_Abkuerzungsverzeichnis.md
              -> # 42 – Abkuerzungsverzeichnis

    Andere Befunde, etwa doppelte Titelblöcke oder Merge-Metadaten, werden
    bewusst nicht automatisch verändert.

.EXAMPLE
    pwsh.exe -ExecutionPolicy Bypass -File ".\CMIBF_Release_Repair_Tool_1_0.ps1" `
        -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$InputPath,

    [string]$OutputPath,

    [string]$ReportDirectory,

    [ValidateSet('LF', 'CRLF')]
    [string]$LineEnding = 'LF',

    [switch]$OverwriteOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Excerpt {
    param(
        [AllowEmptyString()][string]$Value,
        [int]$MaximumLength = 180
    )

    if ([string]::IsNullOrEmpty($Value)) {
        return ''
    }

    $singleLine = ($Value -replace '\s+', ' ').Trim()
    if ($singleLine.Length -le $MaximumLength) {
        return $singleLine
    }

    return $singleLine.Substring(0, $MaximumLength) + '...'
}

function Escape-MarkdownCell {
    param([AllowEmptyString()][string]$Value)

    if ($null -eq $Value) {
        return ''
    }

    $result = $Value -replace '\|', '\|'
    $result = $result -replace "`r", ' '
    $result = $result -replace "`n", ' '
    return $result
}

# -----------------------------------------------------------------------------
# Pfade vorbereiten
# -----------------------------------------------------------------------------
$resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path

if ([IO.Path]::GetExtension($resolvedInput) -ne '.md') {
    throw "Die Eingabedatei muss eine Markdown-Datei (.md) sein: $resolvedInput"
}

$inputDirectory = Split-Path -Parent $resolvedInput
$inputBaseName = [IO.Path]::GetFileNameWithoutExtension($resolvedInput)
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $inputDirectory ($inputBaseName + '_REPAIRED.md')
}
else {
    $OutputPath = [IO.Path]::GetFullPath($OutputPath)
}

if ([string]::IsNullOrWhiteSpace($ReportDirectory)) {
    $ReportDirectory = Join-Path $inputDirectory 'cmibf_release_reports'
}

[void](New-Item -ItemType Directory -Path $ReportDirectory -Force)
$ReportDirectory = (Resolve-Path -LiteralPath $ReportDirectory).Path

$resolvedOutput = [IO.Path]::GetFullPath($OutputPath)

if ($resolvedOutput -eq $resolvedInput) {
    throw 'Die Ausgabedatei darf nicht mit der Eingabedatei identisch sein. Die Originaldatei wird aus Sicherheitsgründen niemals überschrieben.'
}

if ((Test-Path -LiteralPath $resolvedOutput) -and -not $OverwriteOutput) {
    throw "Die Ausgabedatei existiert bereits: $resolvedOutput`nVerwende -OverwriteOutput, wenn sie ersetzt werden soll."
}

$outputDirectory = Split-Path -Parent $resolvedOutput
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    [void](New-Item -ItemType Directory -Path $outputDirectory -Force)
}

# -----------------------------------------------------------------------------
# UTF-8 robust einlesen und Zeilen erkennen
# -----------------------------------------------------------------------------
$utf8Strict = [Text.UTF8Encoding]::new($false, $true)
try {
    $rawText = [IO.File]::ReadAllText($resolvedInput, $utf8Strict)
}
catch [Text.DecoderFallbackException] {
    throw "Die Eingabedatei ist kein gültiger UTF-8-Text: $resolvedInput"
}

[string[]]$inputLines = @([regex]::Split($rawText, '\r\n|\n|\r'))
$hadFinalLineEnding = $rawText -match '(\r\n|\n|\r)$'

# Die vom letzten Zeilenende erzeugte technische Leerzeile nicht bearbeiten.
$logicalLineCount = $inputLines.Count
if ($hadFinalLineEnding -and $logicalLineCount -gt 0 -and $inputLines[$logicalLineCount - 1] -eq '') {
    $logicalLineCount--
}

if ($logicalLineCount -le 1 -and $rawText.Length -gt 1000) {
    throw "Die Datei wurde nur als eine Zeile erkannt. Reparatur aus Sicherheitsgründen abgebrochen. Zeichen: $($rawText.Length)"
}

# -----------------------------------------------------------------------------
# Ausschließlich sichere Reparaturen ausführen
# -----------------------------------------------------------------------------
$outputLines = [Collections.Generic.List[string]]::new()
$changes = [Collections.Generic.List[object]]::new()
$insideFence = $false
$fenceMarker = ''

for ($index = 0; $index -lt $logicalLineCount; $index++) {
    $lineNumber = $index + 1
    $before = $inputLines[$index]
    $after = $before
    $changeCode = ''
    $changeDescription = ''

    if ($before -match '^\s*(```|~~~)') {
        $marker = $Matches[1]
        if (-not $insideFence) {
            $insideFence = $true
            $fenceMarker = $marker
        }
        elseif ($marker -eq $fenceMarker) {
            $insideFence = $false
            $fenceMarker = ''
        }
    }
    elseif (-not $insideFence) {
        # 1. Als H1 übernommene Quelldateinamen.
        if ($before -match '^#\s+(\d+)_([^#]+?)\.md\s*$') {
            $number = $Matches[1]
            $title = ($Matches[2] -replace '_', ' ').Trim()
            $after = "# $number – $title"
            $changeCode = 'REPAIR-FILENAME-HEADING'
            $changeDescription = 'Quelldateiname in eine reguläre Kapitelüberschrift umgewandelt.'
        }
        # 2. Nummerierte Unterkapitel auf H1-Ebene.
        elseif ($before -match '^#\s+(\d+\.\d+)\s+(.+?)\s*$') {
            $number = $Matches[1]
            $title = $Matches[2]
            $after = "## $number $title"
            $changeCode = 'REPAIR-H1-SUBSECTION'
            $changeDescription = 'Nummeriertes Unterkapitel von H1 auf H2 korrigiert.'
        }
    }

    [void]$outputLines.Add($after)

    if ($after -ne $before) {
        [void]$changes.Add([pscustomobject]@{
            Line        = $lineNumber
            Code        = $changeCode
            Description = $changeDescription
            Before      = $before
            After       = $after
        })
    }
}

# -----------------------------------------------------------------------------
# Ergebnis vor dem Schreiben intern validieren
# -----------------------------------------------------------------------------
$remainingH1Subsections = [Collections.Generic.List[object]]::new()
$remainingFilenameHeadings = [Collections.Generic.List[object]]::new()
$insideFence = $false
$fenceMarker = ''

for ($index = 0; $index -lt $outputLines.Count; $index++) {
    $line = $outputLines[$index]

    if ($line -match '^\s*(```|~~~)') {
        $marker = $Matches[1]
        if (-not $insideFence) {
            $insideFence = $true
            $fenceMarker = $marker
        }
        elseif ($marker -eq $fenceMarker) {
            $insideFence = $false
            $fenceMarker = ''
        }
        continue
    }

    if ($insideFence) {
        continue
    }

    if ($line -match '^#\s+\d+\.\d+\s+.+$') {
        [void]$remainingH1Subsections.Add([pscustomobject]@{
            Line = $index + 1
            Text = $line
        })
    }

    if ($line -match '^#\s+\d+_[^#]+\.md\s*$') {
        [void]$remainingFilenameHeadings.Add([pscustomobject]@{
            Line = $index + 1
            Text = $line
        })
    }
}

if ($remainingH1Subsections.Count -gt 0 -or $remainingFilenameHeadings.Count -gt 0) {
    throw "Die interne Nachprüfung ist fehlgeschlagen. Verbliebene H1-Unterkapitel: $($remainingH1Subsections.Count); verbliebene Dateinamen-Überschriften: $($remainingFilenameHeadings.Count). Es wurde keine Datei geschrieben."
}

if ($changes.Count -eq 0) {
    throw 'Es wurden keine eindeutig reparierbaren Fehler gefunden. Es wurde keine Ausgabedatei geschrieben.'
}

# -----------------------------------------------------------------------------
# UTF-8 ohne BOM schreiben; Original bleibt unverändert
# -----------------------------------------------------------------------------
$newLine = if ($LineEnding -eq 'CRLF') { "`r`n" } else { "`n" }
$outputText = [string]::Join($newLine, $outputLines)
if ($hadFinalLineEnding) {
    $outputText += $newLine
}

$utf8NoBom = [Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllText($resolvedOutput, $outputText, $utf8NoBom)

# Hashes erst nach erfolgreichem Schreiben bilden.
$inputHash = (Get-FileHash -LiteralPath $resolvedInput -Algorithm SHA256).Hash
$outputHash = (Get-FileHash -LiteralPath $resolvedOutput -Algorithm SHA256).Hash

# -----------------------------------------------------------------------------
# Berichte erstellen
# -----------------------------------------------------------------------------
$reportMdPath = Join-Path $ReportDirectory "CMIBF_REPAIR_BERICHT_$timestamp.md"
$reportJsonPath = Join-Path $ReportDirectory "CMIBF_REPAIR_BERICHT_$timestamp.json"

$h1FixCount = @($changes | Where-Object { $_.Code -eq 'REPAIR-H1-SUBSECTION' }).Count
$filenameFixCount = @($changes | Where-Object { $_.Code -eq 'REPAIR-FILENAME-HEADING' }).Count

$reportLines = [Collections.Generic.List[string]]::new()
[void]$reportLines.Add('# CMIBF Repair-Bericht')
[void]$reportLines.Add('')
[void]$reportLines.Add("- **Zeitpunkt:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$reportLines.Add('- **Tool:** CMIBF Release Repair Tool 1.0')
[void]$reportLines.Add("- **Eingabe:** ``$resolvedInput``")
[void]$reportLines.Add("- **Ausgabe:** ``$resolvedOutput``")
[void]$reportLines.Add("- **Zeilen:** $logicalLineCount")
[void]$reportLines.Add("- **Zeilenenden der Ausgabe:** $LineEnding")
[void]$reportLines.Add("- **Korrekturen insgesamt:** $($changes.Count)")
[void]$reportLines.Add("- **H1-Unterkapitel korrigiert:** $h1FixCount")
[void]$reportLines.Add("- **Dateinamen-Überschriften korrigiert:** $filenameFixCount")
[void]$reportLines.Add("- **SHA-256 Eingabe:** ``$inputHash``")
[void]$reportLines.Add("- **SHA-256 Ausgabe:** ``$outputHash``")
[void]$reportLines.Add('')
[void]$reportLines.Add('## Durchgeführte Korrekturen')
[void]$reportLines.Add('')
[void]$reportLines.Add('| Zeile | Code | Vorher | Nachher |')
[void]$reportLines.Add('|---:|---|---|---|')

foreach ($change in $changes) {
    $beforeCell = Escape-MarkdownCell (Get-Excerpt $change.Before)
    $afterCell = Escape-MarkdownCell (Get-Excerpt $change.After)
    [void]$reportLines.Add("| $($change.Line) | ``$($change.Code)`` | $beforeCell | $afterCell |")
}

[void]$reportLines.Add('')
[void]$reportLines.Add('## Interne Nachprüfung')
[void]$reportLines.Add('')
[void]$reportLines.Add('- Verbliebene nummerierte Unterkapitel auf H1-Ebene: **0**')
[void]$reportLines.Add('- Verbliebene Dateinamen als H1-Überschrift: **0**')
[void]$reportLines.Add('- Originaldatei verändert: **Nein**')
[void]$reportLines.Add('')
[void]$reportLines.Add('## Nicht automatisch verändert')
[void]$reportLines.Add('')
[void]$reportLines.Add('Doppelte Titelblöcke, Merge-Metadaten und redaktionelle Wiederholungen wurden bewusst nicht automatisch verändert und müssen anschließend erneut mit dem CMIBF Release Validator geprüft werden.')

[IO.File]::WriteAllLines($reportMdPath, $reportLines, $utf8NoBom)

$jsonReport = [ordered]@{
    Timestamp = (Get-Date).ToString('o')
    Tool = 'CMIBF Release Repair Tool 1.0'
    InputPath = $resolvedInput
    OutputPath = $resolvedOutput
    LogicalLineCount = $logicalLineCount
    OutputLineEnding = $LineEnding
    ChangeCount = $changes.Count
    H1SubsectionFixCount = $h1FixCount
    FilenameHeadingFixCount = $filenameFixCount
    RemainingH1Subsections = 0
    RemainingFilenameHeadings = 0
    OriginalModified = $false
    InputSha256 = $inputHash
    OutputSha256 = $outputHash
    Changes = @($changes)
}

$jsonText = $jsonReport | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText($reportJsonPath, $jsonText, $utf8NoBom)

# -----------------------------------------------------------------------------
# Konsolenausgabe
# -----------------------------------------------------------------------------
Write-Host ''
Write-Host '===== CMIBF Release Repair Tool 1.0 ====='
Write-Host "Eingabe:                    $resolvedInput"
Write-Host "Ausgabe:                    $resolvedOutput"
Write-Host "Zeilen:                     $logicalLineCount"
Write-Host "Korrekturen insgesamt:      $($changes.Count)"
Write-Host "H1-Unterkapitel korrigiert: $h1FixCount"
Write-Host "Dateinamen korrigiert:       $filenameFixCount"
Write-Host 'Interne Nachprüfung:         BESTANDEN'
Write-Host "Bericht MD:                 $reportMdPath"
Write-Host "Bericht JSON:               $reportJsonPath"
