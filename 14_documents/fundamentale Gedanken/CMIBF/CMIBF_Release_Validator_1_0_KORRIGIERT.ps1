#requires -Version 7.0
<#
.SYNOPSIS
    Prüft die CMIBF-Masterdatei und erstellt einen Markdown- sowie JSON-Bericht.

.DESCRIPTION
    Audit verändert die Eingabedatei nicht.
    Fix erstellt zuerst ein Backup und schreibt eine separate Release-Candidate-Datei.

    Diese Version liest die Datei als vollständigen UTF-8-Text ein und trennt Zeilen
    ausdrücklich an CRLF, LF oder CR. Dadurch werden Windows-, Unix- und gemischte
    Zeilenenden zuverlässig verarbeitet.

.EXAMPLE
    pwsh.exe -ExecutionPolicy Bypass -File ".\CMIBF_Release_Validator_1_0.ps1" `
        -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md" `
        -Mode Audit

.EXAMPLE
    pwsh.exe -ExecutionPolicy Bypass -File ".\CMIBF_Release_Validator_1_0.ps1" `
        -InputPath ".\CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0.md" `
        -Mode Fix
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$InputPath,

    [ValidateSet('Audit', 'Fix')]
    [string]$Mode = 'Audit',

    [string]$OutputPath,

    [string]$ReportDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-Finding {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('ERROR', 'WARNING', 'INFO', 'FIXED')]
        [string]$Severity,

        [Parameter(Mandatory = $true)]
        [string]$Code,

        [int]$Line = 0,

        [Parameter(Mandatory = $true)]
        [string]$Description,

        [string]$Excerpt = ''
    )

    return [pscustomobject]@{
        Severity    = $Severity
        Code        = $Code
        Line        = $Line
        Description = $Description
        Excerpt     = $Excerpt
    }
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

# -----------------------------------------------------------------------------
# Eingabe und Ausgabe vorbereiten
# -----------------------------------------------------------------------------
$resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
if ([IO.Path]::GetExtension($resolvedInput) -ne '.md') {
    throw "Die Eingabedatei muss eine Markdown-Datei (.md) sein: $resolvedInput"
}

$inputDirectory = Split-Path -Parent $resolvedInput
$inputBaseName = [IO.Path]::GetFileNameWithoutExtension($resolvedInput)
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'

if ([string]::IsNullOrWhiteSpace($ReportDirectory)) {
    $ReportDirectory = Join-Path $inputDirectory 'cmibf_release_reports'
}

[void](New-Item -ItemType Directory -Path $ReportDirectory -Force)
$ReportDirectory = (Resolve-Path -LiteralPath $ReportDirectory).Path

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $inputDirectory ($inputBaseName + '_RELEASE_CANDIDATE.md')
}
else {
    $OutputPath = [IO.Path]::GetFullPath($OutputPath)
}

# -----------------------------------------------------------------------------
# Robustes Einlesen: CRLF, LF und CR werden ausdrücklich unterstützt.
# -----------------------------------------------------------------------------
$utf8NoBom = [Text.UTF8Encoding]::new($false, $true)
try {
    $rawText = [IO.File]::ReadAllText($resolvedInput, $utf8NoBom)
}
catch [Text.DecoderFallbackException] {
    throw "Die Datei ist kein gültiger UTF-8-Text: $resolvedInput"
}

# WICHTIG: @() erzwingt ein Array, auch bei nur einer Zeile.
[string[]]$lines = @([regex]::Split($rawText, '\r\n|\n|\r'))

# Eine durch das abschließende Zeilenende erzeugte letzte Leerzeile nicht mitzählen.
$logicalLineCount = $lines.Count
if ($logicalLineCount -gt 0 -and $lines[$logicalLineCount - 1] -eq '') {
    $logicalLineCount--
}

$lfCount = ([regex]::Matches($rawText, '(?<!\r)\n')).Count
$crlfCount = ([regex]::Matches($rawText, '\r\n')).Count
$crCount = ([regex]::Matches($rawText, '\r(?!\n)')).Count

$findings = @()
$changes = @()

if ($logicalLineCount -le 1 -and $rawText.Length -gt 1000) {
    $findings += New-Finding -Severity ERROR -Code 'INPUT-LINE-PARSING' -Line 0 `
        -Description 'Die große Eingabedatei wurde nur als eine Zeile erkannt. Die Prüfung wurde aus Sicherheitsgründen abgebrochen.' `
        -Excerpt "Zeichen: $($rawText.Length); LF: $lfCount; CRLF: $crlfCount; CR: $crCount"
}

# -----------------------------------------------------------------------------
# Optionale konservative Korrekturen
# -----------------------------------------------------------------------------
if ($Mode -eq 'Fix' -and -not (@($findings | Where-Object Code -eq 'INPUT-LINE-PARSING').Count -gt 0)) {
    $workingLines = [Collections.Generic.List[string]]::new()
    foreach ($line in $lines) {
        [void]$workingLines.Add($line)
    }

    for ($index = 0; $index -lt $workingLines.Count; $index++) {
        $before = $workingLines[$index]
        $after = $before.TrimEnd()

        # Als Überschrift übernommene Quelldateinamen.
        if ($after -match '^#\s+(\d+)_([^#]+?)\.md\s*$') {
            $number = $Matches[1]
            $title = ($Matches[2] -replace '_', ' ').Trim()
            $after = "# $number – $title"
        }
        # Nummerierte Unterkapitel auf H1-Ebene.
        elseif ($after -match '^#\s+(\d+(?:\.\d+){2,})\s+(.+)$') {
            $number = $Matches[1]
            $title = $Matches[2]
            $depth = [Math]::Min(6, ($number -split '\.').Count)
            $after = ('#' * $depth) + " $number $title"
        }
        elseif ($after -match '^#\s+(\d+\.\d+)\s+(.+)$') {
            $after = "## $($Matches[1]) $($Matches[2])"
        }

        if ($after -ne $before) {
            $workingLines[$index] = $after
            $changes += [pscustomobject]@{
                Line   = $index + 1
                Before = $before
                After  = $after
            }
        }
    }

    # Mehr als zwei aufeinanderfolgende Leerzeilen reduzieren.
    $cleanLines = [Collections.Generic.List[string]]::new()
    $blankRun = 0
    foreach ($line in $workingLines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            $blankRun++
            if ($blankRun -le 2) {
                [void]$cleanLines.Add('')
            }
        }
        else {
            $blankRun = 0
            [void]$cleanLines.Add($line)
        }
    }

    [string[]]$lines = $cleanLines.ToArray()
    $logicalLineCount = $lines.Count
    if ($logicalLineCount -gt 0 -and $lines[$logicalLineCount - 1] -eq '') {
        $logicalLineCount--
    }
}

# -----------------------------------------------------------------------------
# Markdown-Struktur prüfen
# -----------------------------------------------------------------------------
$headings = @()
$headingIndex = @{}
$insideFence = $false
$fenceMarker = ''

if (-not (@($findings | Where-Object Code -eq 'INPUT-LINE-PARSING').Count -gt 0)) {
    for ($index = 0; $index -lt $logicalLineCount; $index++) {
        $lineNumber = $index + 1
        $line = $lines[$index]

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

        if ($line -match '^(#{1,6})\s+(.+?)\s*$') {
            $level = $Matches[1].Length
            $headingText = $Matches[2].Trim()
            $heading = [pscustomobject]@{
                Line  = $lineNumber
                Level = $level
                Text  = $headingText
            }
            $headings += $heading

            $key = "$level|$($headingText.ToLowerInvariant())"
            if (-not $headingIndex.ContainsKey($key)) {
                $headingIndex[$key] = @()
            }
            $headingIndex[$key] += $lineNumber

            if ($headingText -match '\.md$') {
                $findings += New-Finding -Severity ERROR -Code 'MD-FILENAME-HEADING' -Line $lineNumber `
                    -Description 'Ein Quelldateiname wurde als Überschrift übernommen.' -Excerpt (Get-Excerpt $line)
            }

            if ($level -eq 1 -and $headingText -match '^\d+\.\d+(?:\.\d+)*\s+') {
                $findings += New-Finding -Severity ERROR -Code 'MD-H1-SUBSECTION' -Line $lineNumber `
                    -Description 'Ein nummeriertes Unterkapitel steht auf H1-Ebene.' -Excerpt (Get-Excerpt $line)
            }
        }

        if ($line -match '\b(TODO|TBD|FIXME|XXX)\b') {
            $findings += New-Finding -Severity WARNING -Code 'CONTENT-PLACEHOLDER' -Line $lineNumber `
                -Description 'Möglicher offener Platzhalter gefunden.' -Excerpt (Get-Excerpt $line)
        }

        if ($line -match '^\*\*Paket:\*\*' -or
            $line -match '^\*\*Enthaltene Bestandteile:\*\*' -or
            $line -match 'Konsolidierungsbaustein') {
            $findings += New-Finding -Severity INFO -Code 'MERGE-PACKAGE-METADATA' -Line $lineNumber `
                -Description 'Paketbezogene Metadaten aus einer Quelldatei sind im Gesamtwerk enthalten.' `
                -Excerpt (Get-Excerpt $line)
        }
    }

    if ($insideFence) {
        $findings += New-Finding -Severity ERROR -Code 'MD-UNCLOSED-FENCE' -Line $logicalLineCount `
            -Description 'Ein Markdown-Codeblock wurde nicht geschlossen.'
    }

    # Sprünge in der Überschriftenhierarchie.
    for ($index = 1; $index -lt $headings.Count; $index++) {
        $previous = $headings[$index - 1]
        $current = $headings[$index]
        if ($current.Level -gt ($previous.Level + 1)) {
            $findings += New-Finding -Severity WARNING -Code 'MD-HEADING-JUMP' -Line $current.Line `
                -Description "Die Überschriftenebene springt von H$($previous.Level) auf H$($current.Level)." `
                -Excerpt (Get-Excerpt $current.Text)
        }
    }

    # Doppelte Überschriften gleicher Ebene.
    foreach ($key in $headingIndex.Keys) {
        $occurrences = @($headingIndex[$key])
        if ($occurrences.Count -gt 1) {
            $parts = $key -split '\|', 2
            $findings += New-Finding -Severity WARNING -Code 'MD-DUPLICATE-HEADING' -Line $occurrences[0] `
                -Description "Die H$($parts[0])-Überschrift kommt mehrfach vor. Zeilen: $($occurrences -join ', ')." `
                -Excerpt (Get-Excerpt $parts[1])
        }
    }

    # Erwartete Bestandteile im Gesamttext suchen.
    $requiredSections = @(
        @{ Name = 'Präambel'; Pattern = '(?im)^#{1,6}\s+.*Präambel.*$' },
        @{ Name = 'Versionshistorie'; Pattern = '(?im)^#{1,6}\s+.*Versionshistorie.*$' },
        @{ Name = 'Glossar / Teil 41'; Pattern = '(?im)^#{1,6}\s+(?:41\b.*Glossar|.*Glossar.*)$' },
        @{ Name = 'Abkürzungsverzeichnis'; Pattern = '(?im)^#{1,6}\s+.*Abk(?:ü|ue)rzungsverzeichnis.*$' },
        @{ Name = 'Framework Registry'; Pattern = '(?im)^#{1,6}\s+.*Framework[ _-]*Registry.*$' },
        @{ Name = 'Canonical Dependency Graph'; Pattern = '(?im)^#{1,6}\s+.*(?:Canonical\s+)?Dependency\s+Graph.*$' },
        @{ Name = 'Implementierungs-Roadmap'; Pattern = '(?im)^#{1,6}\s+.*Implementierungs[ _-]*Roadmap.*$' },
        @{ Name = 'Anhänge'; Pattern = '(?im)^#{1,6}\s+.*Anh(?:ä|ae)nge.*$' }
    )

    $currentText = [string]::Join("`n", $lines)
    foreach ($section in $requiredSections) {
        if (-not [regex]::IsMatch($currentText, $section.Pattern)) {
            $findings += New-Finding -Severity ERROR -Code 'CONTENT-MISSING-SECTION' -Line 0 `
                -Description "Erwarteter Bestandteil fehlt: $($section.Name)."
        }
    }
}

# Änderungen als Befunde aufnehmen.
foreach ($change in $changes) {
    $findings += New-Finding -Severity FIXED -Code 'AUTO-CORRECTION' -Line $change.Line `
        -Description 'Eine eindeutige Formatkorrektur wurde durchgeführt.' `
        -Excerpt (Get-Excerpt "$($change.Before) -> $($change.After)")
}

# -----------------------------------------------------------------------------
# Fix-Ausgabe und Backup
# -----------------------------------------------------------------------------
$backupPath = $null
if ($Mode -eq 'Fix' -and -not (@($findings | Where-Object Code -eq 'INPUT-LINE-PARSING').Count -gt 0)) {
    $backupDirectory = Join-Path $inputDirectory 'cmibf_release_backups'
    [void](New-Item -ItemType Directory -Path $backupDirectory -Force)
    $backupPath = Join-Path $backupDirectory ($inputBaseName + '_BACKUP_' + $timestamp + '.md')
    Copy-Item -LiteralPath $resolvedInput -Destination $backupPath -Force

    $outputDirectory = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($outputDirectory)) {
        [void](New-Item -ItemType Directory -Path $outputDirectory -Force)
    }

    $outputText = [string]::Join("`n", $lines)
    if (-not $outputText.EndsWith("`n")) {
        $outputText += "`n"
    }
    [IO.File]::WriteAllText($OutputPath, $outputText, [Text.UTF8Encoding]::new($false))
}

# -----------------------------------------------------------------------------
# Bericht erstellen
# -----------------------------------------------------------------------------
$errorCount = @($findings | Where-Object Severity -eq 'ERROR').Count
$warningCount = @($findings | Where-Object Severity -eq 'WARNING').Count
$infoCount = @($findings | Where-Object Severity -eq 'INFO').Count
$fixedCount = @($findings | Where-Object Severity -eq 'FIXED').Count

$reportMdPath = Join-Path $ReportDirectory ("CMIBF_RELEASE_PRUEFBERICHT_$timestamp.md")
$reportJsonPath = Join-Path $ReportDirectory ("CMIBF_RELEASE_PRUEFBERICHT_$timestamp.json")

$reportLines = [Collections.Generic.List[string]]::new()
[void]$reportLines.Add('# CMIBF Release-Prüfbericht')
[void]$reportLines.Add('')
[void]$reportLines.Add("- **Zeitpunkt:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$reportLines.Add("- **Validator:** CMIBF Release Validator 1.0")
[void]$reportLines.Add("- **Modus:** $Mode")
[void]$reportLines.Add("- **Eingabe:** ``$resolvedInput``")
[void]$reportLines.Add("- **Zeichen:** $($rawText.Length)")
[void]$reportLines.Add("- **Zeilen:** $logicalLineCount")
[void]$reportLines.Add("- **Zeilenenden:** LF=$lfCount, CRLF=$crlfCount, CR=$crCount")
[void]$reportLines.Add("- **Überschriften:** $($headings.Count)")
[void]$reportLines.Add("- **Fehler:** $errorCount")
[void]$reportLines.Add("- **Warnungen:** $warningCount")
[void]$reportLines.Add("- **Hinweise:** $infoCount")
[void]$reportLines.Add("- **Automatisch korrigiert:** $fixedCount")
if ($null -ne $backupPath) {
    [void]$reportLines.Add("- **Backup:** ``$backupPath``")
    [void]$reportLines.Add("- **Ausgabe:** ``$OutputPath``")
}
[void]$reportLines.Add('')
[void]$reportLines.Add('## Befunde')
[void]$reportLines.Add('')

if ($findings.Count -eq 0) {
    [void]$reportLines.Add('Keine Befunde.')
}
else {
    [void]$reportLines.Add('| Schweregrad | Code | Zeile | Beschreibung | Fundstelle |')
    [void]$reportLines.Add('|---|---|---:|---|---|')
    foreach ($finding in $findings) {
        $severity = Escape-MarkdownCell $finding.Severity
        $code = Escape-MarkdownCell $finding.Code
        $description = Escape-MarkdownCell $finding.Description
        $excerpt = Escape-MarkdownCell $finding.Excerpt
        [void]$reportLines.Add("| $severity | ``$code`` | $($finding.Line) | $description | $excerpt |")
    }
}

[void]$reportLines.Add('')
[void]$reportLines.Add('## Bewertung')
[void]$reportLines.Add('')
if ($errorCount -gt 0) {
    [void]$reportLines.Add('**NICHT FREIGABEFÄHIG:** Mindestens ein Fehler muss behoben werden.')
}
elseif ($warningCount -gt 0) {
    [void]$reportLines.Add('**BEDINGT FREIGABEFÄHIG:** Keine Fehler, aber Warnungen müssen geprüft werden.')
}
else {
    [void]$reportLines.Add('**FREIGABEFÄHIG:** Keine Fehler oder Warnungen erkannt.')
}

[IO.File]::WriteAllLines($reportMdPath, $reportLines, [Text.UTF8Encoding]::new($false))

$jsonReport = [pscustomobject]@{
    validator          = 'CMIBF Release Validator 1.0'
    timestamp          = (Get-Date).ToString('o')
    mode               = $Mode
    input              = $resolvedInput
    output             = if ($Mode -eq 'Fix') { $OutputPath } else { $null }
    backup             = $backupPath
    character_count    = $rawText.Length
    line_count         = $logicalLineCount
    line_endings       = [pscustomobject]@{
        lf   = $lfCount
        crlf = $crlfCount
        cr   = $crCount
    }
    heading_count      = $headings.Count
    error_count        = $errorCount
    warning_count      = $warningCount
    info_count         = $infoCount
    fixed_count        = $fixedCount
    findings           = $findings
}

$jsonReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportJsonPath -Encoding utf8NoBOM

Write-Host ''
Write-Host '===== CMIBF Release Validator 1.0 ====='
Write-Host ("Modus:         {0}" -f $Mode)
Write-Host ("Eingabe:       {0}" -f $resolvedInput)
Write-Host ("Zeilen:        {0}" -f $logicalLineCount)
Write-Host ("Überschriften: {0}" -f $headings.Count)
Write-Host ("Fehler:        {0}" -f $errorCount)
Write-Host ("Warnungen:     {0}" -f $warningCount)
Write-Host ("Hinweise:      {0}" -f $infoCount)
Write-Host ("Korrigiert:    {0}" -f $fixedCount)
Write-Host ("Bericht MD:    {0}" -f $reportMdPath)
Write-Host ("Bericht JSON:  {0}" -f $reportJsonPath)
if ($Mode -eq 'Fix') {
    Write-Host ("Backup:        {0}" -f $backupPath)
    Write-Host ("Ausgabe:       {0}" -f $OutputPath)
}

if ($errorCount -gt 0) {
    exit 2
}
elseif ($warningCount -gt 0) {
    exit 1
}
else {
    exit 0
}
