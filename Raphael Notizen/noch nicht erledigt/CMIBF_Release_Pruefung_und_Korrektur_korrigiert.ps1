#requires -Version 7.0
<#!
.SYNOPSIS
  Prüft und korrigiert die zusammengeführte CMIBF-1.0-Markdown-Datei.

.DESCRIPTION
  Audit: rein lesende Prüfung mit Markdown- und JSON-Bericht.
  Fix:   erstellt ein Backup und korrigiert nur eindeutig erkennbare Strukturfehler.

  Das Skript verändert in Fix nur konservativ:
  - Dateinamen als Überschriften, z. B. "# 42_Abkuerzungsverzeichnis.md"
  - nummerierte Unterkapitel auf H1-Ebene, z. B. "# 2.2 ..." -> "## 2.2 ..."
  - Unter-Unterkapitel, z. B. "# 2.2.1 ..." -> "### 2.2.1 ..."
  - Leerzeichen am Zeilenende und überzählige Leerzeilen

  Mehrdeutige Befunde (doppelte Titelblöcke, Paketmetadaten, unklare H1-Struktur,
  Querverweise) werden dokumentiert, aber nicht automatisch entfernt.

.EXAMPLE
  .\CMIBF_Release_Pruefung_und_Korrektur.ps1 `
    -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md" `
    -Mode Audit

.EXAMPLE
  .\CMIBF_Release_Pruefung_und_Korrektur.ps1 `
    -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md" `
    -Mode Fix
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$InputPath,

    [ValidateSet('Audit', 'Fix')]
    [string]$Mode = 'Audit',

    [string]$OutputPath,

    [string]$ReportDirectory,

    [switch]$FailOnWarning
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-Issue {
    param(
        [ValidateSet('ERROR','WARNING','INFO','FIXED')]
        [string]$Severity,
        [string]$Code,
        [int]$Line,
        [string]$Message,
        [string]$Text = ''
    )
    [pscustomobject]@{
        Severity = $Severity
        Code     = $Code
        Line     = $Line
        Message  = $Message
        Text     = $Text
    }
}

function ConvertTo-SafeFileName {
    param([string]$Name)
    $invalid = [IO.Path]::GetInvalidFileNameChars()
    foreach ($char in $invalid) { $Name = $Name.Replace([string]$char, '_') }
    return $Name
}

$resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
if ([IO.Path]::GetExtension($resolvedInput) -ne '.md') {
    throw "Eingabedatei muss eine Markdown-Datei (.md) sein: $resolvedInput"
}

$inputDirectory = Split-Path -Parent $resolvedInput
$inputBaseName  = [IO.Path]::GetFileNameWithoutExtension($resolvedInput)
$timestamp      = Get-Date -Format 'yyyyMMdd_HHmmss'

if (-not $ReportDirectory) {
    $ReportDirectory = Join-Path $inputDirectory 'cmibf_release_reports'
}
$null = New-Item -ItemType Directory -Force -Path $ReportDirectory
$ReportDirectory = (Resolve-Path -LiteralPath $ReportDirectory).Path

if (-not $OutputPath) {
    if ($Mode -eq 'Fix') {
        $OutputPath = Join-Path $inputDirectory ($inputBaseName + '_RELEASE_CANDIDATE.md')
    }
    else {
        $OutputPath = $resolvedInput
    }
}
else {
    $OutputPath = [IO.Path]::GetFullPath($OutputPath)
}

$raw = [IO.File]::ReadAllText($resolvedInput, [Text.UTF8Encoding]::new($false))
# Vereinheitlichung nur im Arbeitsspeicher; Original bleibt im Audit unverändert.
$normalized = $raw -replace "`r`n?", "`n"
$lines = [Collections.Generic.List[string]]::new()
foreach ($line in ($normalized -split "`n", -1)) { $lines.Add($line) }

$issues = [Collections.Generic.List[object]]::new()
$changes = [Collections.Generic.List[object]]::new()
$titlePattern = '^#\s+CANONICAL MASTER IMPLEMENTATION BLUEPRINT FRAMEWORK \(CMIBF\) 1\.0\s*$'

# ---------- Automatische, konservative Korrekturen ----------
if ($Mode -eq 'Fix') {
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $original = $lines[$i]
        $newLine = $original.TrimEnd()

        # Unter-Unterkapitel vor Unterkapiteln prüfen.
        if ($newLine -match '^#\s+(\d+\.\d+\.\d+(?:\.\d+)*)\s+(.+)$') {
            $depth = [Math]::Min(6, 1 + (($Matches[1] -split '\.').Count))
            $newLine = ('#' * $depth) + ' ' + $Matches[1] + ' ' + $Matches[2]
        }
        elseif ($newLine -match '^#\s+(\d+\.\d+)\s+(.+)$') {
            $newLine = '## ' + $Matches[1] + ' ' + $Matches[2]
        }
        elseif ($newLine -match '^#\s+(\d+)_([A-Za-zÄÖÜäöüß][^#]*?)\.md\s*$') {
            $number = $Matches[1]
            $name = ($Matches[2] -replace '_', ' ').Trim()
            $newLine = "# $number – $name"
        }

        if ($newLine -ne $original) {
            $lines[$i] = $newLine
            $changes.Add([pscustomobject]@{
                Line   = $i + 1
                Before = $original
                After  = $newLine
            })
        }
    }

    # Mehr als zwei aufeinanderfolgende Leerzeilen auf maximal zwei reduzieren.
    $cleanLines = [Collections.Generic.List[string]]::new()
    $blankCount = 0
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            $blankCount++
            if ($blankCount -le 2) { $cleanLines.Add('') }
        }
        else {
            $blankCount = 0
            $cleanLines.Add($line)
        }
    }
    $lines = $cleanLines
}

# ---------- Prüfungen auf dem aktuellen Arbeitsstand ----------
$headings = [Collections.Generic.List[object]]::new()
$headingCounts = @{}
$inFence = $false
$fenceMarker = ''

for ($i = 0; $i -lt $lines.Count; $i++) {
    $lineNo = $i + 1
    $line = $lines[$i]

    if ($line -match '^\s*(```|~~~)') {
        $marker = $Matches[1]
        if (-not $inFence) { $inFence = $true; $fenceMarker = $marker }
        elseif ($marker -eq $fenceMarker) { $inFence = $false; $fenceMarker = '' }
        continue
    }
    if ($inFence) { continue }

    if ($line -match '^(#{1,6})\s+(.+?)\s*$') {
        $level = $Matches[1].Length
        $text = $Matches[2].Trim()
        $headings.Add([pscustomobject]@{ Line = $lineNo; Level = $level; Text = $text })
        $key = "$level|$($text.ToLowerInvariant())"
        if (-not $headingCounts.ContainsKey($key)) { $headingCounts[$key] = @() }
        $headingCounts[$key] += $lineNo

        if ($text -match '\.md$') {
            $issues.Add((New-Issue WARNING 'MD-FILENAME-HEADING' $lineNo 'Dateiname wurde als Überschrift übernommen.' $line))
        }
        if ($level -eq 1 -and $text -match '^\d+\.\d+(?:\.\d+)*\s+') {
            $issues.Add((New-Issue WARNING 'MD-H1-NUMBERED-SUBSECTION' $lineNo 'Nummeriertes Unterkapitel steht noch auf H1-Ebene.' $line))
        }
    }

    if ($line -match '\b(TODO|TBD|FIXME|XXX)\b') {
        $issues.Add((New-Issue WARNING 'CONTENT-PLACEHOLDER' $lineNo 'Möglicher offener Platzhalter gefunden.' $line.Trim()))
    }
    if ($line -match '^\*\*Paket:\*\*' -or $line -match '^\*\*Enthaltene Bestandteile:\*\*' -or $line -match 'Konsolidierungsbaustein') {
        $issues.Add((New-Issue INFO 'MERGE-PACKAGE-METADATA' $lineNo 'Paketbezogene Metadaten aus einer Quelldatei sind im Gesamtwerk enthalten.' $line.Trim()))
    }
}

if ($inFence) {
    $issues.Add((New-Issue ERROR 'MD-UNCLOSED-FENCE' $lines.Count 'Ein Markdown-Codeblock wurde nicht geschlossen.'))
}

# Überschriften-Sprünge prüfen.
for ($i = 1; $i -lt $headings.Count; $i++) {
    $previous = $headings[$i - 1]
    $current = $headings[$i]
    if ($current.Level -gt ($previous.Level + 1)) {
        $issues.Add((New-Issue WARNING 'MD-HEADING-JUMP' $current.Line "Überschriftenebene springt von H$($previous.Level) auf H$($current.Level)." $current.Text))
    }
}

# Doppelte Überschriften gleicher Ebene.
foreach ($entry in $headingCounts.GetEnumerator()) {
    if ($entry.Value.Count -gt 1) {
        $parts = $entry.Key -split '\|', 2
        $issues.Add((New-Issue WARNING 'MD-DUPLICATE-HEADING' $entry.Value[0] "Überschrift H$($parts[0]) kommt mehrfach vor; Zeilen: $($entry.Value -join ', ')." $parts[1]))
    }
}

# Titelblock-Wiederholungen.
$titleLines = @($headings | Where-Object { $_.Level -eq 1 -and ('# ' + $_.Text) -match $titlePattern } | ForEach-Object Line)
if ($titleLines.Count -gt 1) {
    $issues.Add((New-Issue WARNING 'MERGE-DUPLICATE-TITLE' $titleLines[1] "Der CMIBF-Haupttitel kommt $($titleLines.Count)-mal vor; Zeilen: $($titleLines -join ', '). Die zusätzlichen Titelblöcke sollten manuell bewertet werden."))
}

# Wichtige Abschlussbestandteile.
$requiredPatterns = [ordered]@{
    'Präambel'                   = '^Präambel$'
    'Versionshistorie'           = '^Versionshistorie$'
    'Glossar / Teil 41'          = '^(Teil\s+)?41\b|Glossar'
    'Abkürzungsverzeichnis'      = '^42\b.*Abk'
    'Framework Registry'         = '^43\b.*Framework Registry|Framework Registry'
    'Canonical Dependency Graph' = 'Canonical Dependency Graph'
    'Implementierungs-Roadmap'   = '^45\b.*Implementierungs.*Roadmap|Implementierungs-Roadmap'
    'Anhänge'                    = '^46\b.*Anhänge|Anhänge$'
}
foreach ($required in $requiredPatterns.GetEnumerator()) {
    if (-not (@($headings | ForEach-Object { $_.Text }) -match $required.Value)) {
        $issues.Add((New-Issue ERROR 'CONTENT-MISSING-SECTION' 0 "Erwarteter Bestandteil fehlt: $($required.Key)."))
    }
}

# Grobe Link-/Bildsyntaxprüfung (keine vollständige Markdown-Parser-Validierung).
for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if (($line -split '\]\(').Count -ne ($line -split '\)').Count -and $line -match '\[[^\]]+\]\(') {
        $issues.Add((New-Issue INFO 'MD-LINK-CHECK' ($i + 1) 'Markdown-Link möglicherweise unvollständig; bitte manuell prüfen.' $line.Trim()))
    }
}

# ---------- Schreiben im Fix-Modus ----------
$backupPath = $null
if ($Mode -eq 'Fix') {
    $backupPath = Join-Path $inputDirectory ($inputBaseName + ".backup_$timestamp.md")
    Copy-Item -LiteralPath $resolvedInput -Destination $backupPath -Force

    $parent = Split-Path -Parent $OutputPath
    if ($parent) { $null = New-Item -ItemType Directory -Force -Path $parent }
    $outputText = ($lines -join "`r`n").TrimEnd() + "`r`n"
    [IO.File]::WriteAllText($OutputPath, $outputText, [Text.UTF8Encoding]::new($false))

    foreach ($change in $changes) {
        $issues.Add((New-Issue FIXED 'AUTO-CORRECTION' $change.Line 'Eindeutige Formatkorrektur ausgeführt.' ("{0}  =>  {1}" -f $change.Before, $change.After)))
    }
}

# ---------- Berichte ----------
$severityOrder = @{ ERROR = 0; WARNING = 1; INFO = 2; FIXED = 3 }
$sortedIssues = @($issues | Sort-Object @{Expression={ $severityOrder[$_.Severity] }}, Line, Code)
$counts = [ordered]@{
    Errors   = @($sortedIssues | Where-Object Severity -eq 'ERROR').Count
    Warnings = @($sortedIssues | Where-Object Severity -eq 'WARNING').Count
    Info     = @($sortedIssues | Where-Object Severity -eq 'INFO').Count
    Fixed    = @($sortedIssues | Where-Object Severity -eq 'FIXED').Count
}

$reportBase = ConvertTo-SafeFileName("CMIBF_RELEASE_PRUEFBERICHT_$timestamp")
$markdownReport = Join-Path $ReportDirectory ($reportBase + '.md')
$jsonReport = Join-Path $ReportDirectory ($reportBase + '.json')

$md = [Text.StringBuilder]::new()
[void]$md.AppendLine('# CMIBF Release-Prüfbericht')
[void]$md.AppendLine()
[void]$md.AppendLine("- **Zeitpunkt:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$md.AppendLine("- **Modus:** $Mode")
[void]$md.AppendLine("- **Eingabe:** ``$resolvedInput``")
if ($Mode -eq 'Fix') {
    [void]$md.AppendLine("- **Ausgabe:** ``$OutputPath``")
    [void]$md.AppendLine("- **Backup:** ``$backupPath``")
}
[void]$md.AppendLine("- **Zeilen:** $($lines.Count)")
[void]$md.AppendLine("- **Überschriften:** $($headings.Count)")
[void]$md.AppendLine("- **Fehler:** $($counts.Errors)")
[void]$md.AppendLine("- **Warnungen:** $($counts.Warnings)")
[void]$md.AppendLine("- **Hinweise:** $($counts.Info)")
[void]$md.AppendLine("- **Automatisch korrigiert:** $($counts.Fixed)")
[void]$md.AppendLine()

if ($sortedIssues.Count -eq 0) {
    [void]$md.AppendLine('## Ergebnis')
    [void]$md.AppendLine()
    [void]$md.AppendLine('Keine Auffälligkeiten gefunden.')
}
else {
    [void]$md.AppendLine('## Befunde')
    [void]$md.AppendLine()
    [void]$md.AppendLine('| Schweregrad | Code | Zeile | Beschreibung | Fundstelle |')
    [void]$md.AppendLine('|---|---|---:|---|---|')
    foreach ($issue in $sortedIssues) {
        $text = ($issue.Text -replace '\|','\|' -replace "`r?`n", ' ').Trim()
        if ($text.Length -gt 180) { $text = $text.Substring(0,177) + '...' }
        $message = $issue.Message -replace '\|','\|'
        [void]$md.AppendLine("| $($issue.Severity) | ``$($issue.Code)`` | $($issue.Line) | $message | $text |")
    }
}

[void]$md.AppendLine()
[void]$md.AppendLine('## Bewertung')
[void]$md.AppendLine()
if ($counts.Errors -gt 0) {
    [void]$md.AppendLine('**NICHT FREIGABEFÄHIG:** Mindestens ein Fehler muss behoben werden.')
}
elseif ($counts.Warnings -gt 0) {
    [void]$md.AppendLine('**RELEASE CANDIDATE MIT PRÜFBEDARF:** Keine harten Fehler, aber Warnungen müssen bewertet werden.')
}
else {
    [void]$md.AppendLine('**STRUKTURELL FREIGABEFÄHIG:** Keine Fehler oder Warnungen gefunden.')
}

[IO.File]::WriteAllText($markdownReport, $md.ToString(), [Text.UTF8Encoding]::new($false))

$reportObject = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    mode = $Mode
    input_path = $resolvedInput
    output_path = if ($Mode -eq 'Fix') { $OutputPath } else { $null }
    backup_path = $backupPath
    statistics = [ordered]@{
        lines = $lines.Count
        headings = $headings.Count
        errors = $counts.Errors
        warnings = $counts.Warnings
        info = $counts.Info
        fixed = $counts.Fixed
    }
    issues = $sortedIssues
    changes = @($changes)
}
[IO.File]::WriteAllText($jsonReport, ($reportObject | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))

Write-Host ''
Write-Host '===== CMIBF Release-Prüfung =====' -ForegroundColor Cyan
Write-Host "Modus:       $Mode"
Write-Host "Eingabe:     $resolvedInput"
if ($Mode -eq 'Fix') {
    Write-Host "Ausgabe:     $OutputPath"
    Write-Host "Backup:      $backupPath"
}
Write-Host "Fehler:      $($counts.Errors)"
Write-Host "Warnungen:   $($counts.Warnings)"
Write-Host "Hinweise:    $($counts.Info)"
Write-Host "Korrigiert:  $($counts.Fixed)"
Write-Host "Bericht MD:  $markdownReport"
Write-Host "Bericht JSON:$jsonReport"

if ($counts.Errors -gt 0) { exit 2 }
if ($FailOnWarning -and $counts.Warnings -gt 0) { exit 1 }
exit 0
