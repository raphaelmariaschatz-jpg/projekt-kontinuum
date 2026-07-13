param(
    [string]$SourceDirectory = ".",
    [string]$OutputFile = "CANONICAL_MASTER_IMPLEMENTATION_BLUEPRINT_FRAMEWORK_1_0_RAW.md"
)

$ErrorActionPreference = "Stop"

$files = Get-ChildItem -Path $SourceDirectory -Filter "CMIBF_1_0_*.md" |
    Where-Object { $_.Name -notmatch "_RAW\.md$" } |
    Sort-Object Name

if ($files.Count -eq 0) {
    throw "Keine CMIBF-Paketdateien gefunden."
}

if (Test-Path $OutputFile) {
    Remove-Item $OutputFile -Force
}

foreach ($file in $files) {
    Write-Host "Füge hinzu: $($file.Name)"
    Get-Content -Path $file.FullName -Raw -Encoding UTF8 |
        Add-Content -Path $OutputFile -Encoding UTF8
    Add-Content -Path $OutputFile -Value "`r`n" -Encoding UTF8
}

$hash = Get-FileHash -Path $OutputFile -Algorithm SHA256
Write-Host ""
Write-Host "Erstellt: $OutputFile"
Write-Host "SHA-256: $($hash.Hash)"
