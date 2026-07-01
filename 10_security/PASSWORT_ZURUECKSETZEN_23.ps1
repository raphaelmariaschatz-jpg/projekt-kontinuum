$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Root = "C:\Projekt Kontinuum"
$ActiveFile = Join-Path $Root "32_data\auth_config.json"
$MasterFile = Join-Path $Root "10_security\auth_security_master.json"
$BackupDir = Join-Path $Root "10_security\backups"
$AuditFile = Join-Path $Root "27_logs\auth_audit.log"
$Username = "Raphael Schatz"
$PythonExe = Join-Path $env:LOCALAPPDATA "Python\pythoncore-3.14-64\python.exe"

function Get-Argon2id([string]$Value) {
    if (-not (Test-Path -LiteralPath $PythonExe)) {
        throw "Signierte Python-Laufzeit für Argon2id wurde nicht gefunden."
    }
    $script = "import sys; from argon2 import PasswordHasher, Type; value=sys.stdin.read().rstrip('\r\n'); print(PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2,hash_len=32,salt_len=16,type=Type.ID).hash(value))"
    $hash = $Value | & $PythonExe -c $script
    if ($LASTEXITCODE -ne 0 -or -not $hash.StartsWith('$argon2id$')) {
        throw "Argon2id-Passwortableitung ist fehlgeschlagen."
    }
    return $hash.Trim()
}

function Write-JsonAtomic([string]$Path, $Data) {
    $temp = "$Path.tmp"
    $json = $Data | ConvertTo-Json -Depth 20
    [IO.File]::WriteAllText($temp, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Write-Audit([string]$EventName, [bool]$Success, [string]$Detail) {
    $directory = Split-Path -Parent $AuditFile
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
    $safeDetail = ($Detail -replace "[\r\n]", " ")
    Add-Content -LiteralPath $AuditFile -Encoding UTF8 -Value "$([DateTime]::UtcNow.ToString('o')) | $EventName | success=$Success | $safeDetail"
}

function Reset-Password([string]$Password) {
    $active = Get-Content -LiteralPath $ActiveFile -Raw | ConvertFrom-Json
    $master = Get-Content -LiteralPath $MasterFile -Raw | ConvertFrom-Json
    if ($active.username -ne $Username -or $active.role -ne "SUPERADMIN") {
        throw "Aktiver Superadmin-Eintrag wurde nicht gefunden."
    }
    $matching = @($master.security_entries | Where-Object {
        $_.username -eq $Username -and $_.password_hash -and $_.password_hash -ne "created_on_first_start"
    })
    if ($matching.Count -ne 1) {
        throw "Der Sicherheits-Master enthält keinen eindeutigen Superadmin-Eintrag."
    }

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    Copy-Item -LiteralPath $ActiveFile -Destination (Join-Path $BackupDir "auth_config_before_password_reset_$stamp.json")
    Copy-Item -LiteralPath $MasterFile -Destination (Join-Path $BackupDir "auth_security_master_before_password_reset_$stamp.json")

    $newHash = Get-Argon2id $Password
    $active.password_hash = $newHash
    $matching[0].password_hash = $newHash
    Write-JsonAtomic $ActiveFile $active
    Write-JsonAtomic $MasterFile $master
    Write-Audit "superadmin_password_reset" $true $Username
}

$form = New-Object Windows.Forms.Form
$form.Text = "Projekt Kontinuum 23.0 - Superadmin-Passwort zurücksetzen"
$form.Size = New-Object Drawing.Size(540, 310)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

$title = New-Object Windows.Forms.Label
$title.Text = "Superadmin-Passwort zurücksetzen"
$title.Font = New-Object Drawing.Font("Segoe UI", 14, [Drawing.FontStyle]::Bold)
$title.AutoSize = $true
$title.Location = New-Object Drawing.Point(105, 20)
$form.Controls.Add($title)

$user = New-Object Windows.Forms.Label
$user.Text = "Benutzer: Raphael Schatz"
$user.AutoSize = $true
$user.Location = New-Object Drawing.Point(175, 58)
$form.Controls.Add($user)

$label1 = New-Object Windows.Forms.Label
$label1.Text = "Neues Passwort"
$label1.AutoSize = $true
$label1.Location = New-Object Drawing.Point(35, 100)
$form.Controls.Add($label1)

$password1 = New-Object Windows.Forms.TextBox
$password1.UseSystemPasswordChar = $true
$password1.Size = New-Object Drawing.Size(300, 25)
$password1.Location = New-Object Drawing.Point(190, 96)
$form.Controls.Add($password1)

$label2 = New-Object Windows.Forms.Label
$label2.Text = "Passwort wiederholen"
$label2.AutoSize = $true
$label2.Location = New-Object Drawing.Point(35, 140)
$form.Controls.Add($label2)

$password2 = New-Object Windows.Forms.TextBox
$password2.UseSystemPasswordChar = $true
$password2.Size = New-Object Drawing.Size(300, 25)
$password2.Location = New-Object Drawing.Point(190, 136)
$form.Controls.Add($password2)

$status = New-Object Windows.Forms.Label
$status.Text = "Mindestens 12 Zeichen."
$status.AutoSize = $true
$status.Location = New-Object Drawing.Point(190, 172)
$form.Controls.Add($status)

$submit = New-Object Windows.Forms.Button
$submit.Text = "Passwort zurücksetzen"
$submit.Size = New-Object Drawing.Size(300, 32)
$submit.Location = New-Object Drawing.Point(190, 200)
$form.Controls.Add($submit)

$cancel = New-Object Windows.Forms.Button
$cancel.Text = "Abbrechen"
$cancel.Size = New-Object Drawing.Size(120, 32)
$cancel.Location = New-Object Drawing.Point(35, 200)
$cancel.Add_Click({ $form.Close() })
$form.Controls.Add($cancel)

$submit.Add_Click({
    if ($password1.Text.Length -lt 12) {
        $status.Text = "Das Passwort muss mindestens 12 Zeichen enthalten."
        return
    }
    if ($password1.Text -cne $password2.Text) {
        $status.Text = "Die Passwörter stimmen nicht überein."
        return
    }
    try {
        Reset-Password $password1.Text
        $password1.Clear()
        $password2.Clear()
        [Windows.Forms.MessageBox]::Show("Das Superadmin-Passwort wurde erfolgreich zurückgesetzt.", "Passwort-Reset", "OK", "Information") | Out-Null
        $form.Close()
    }
    catch {
        Write-Audit "superadmin_password_reset" $false $_.Exception.Message
        [Windows.Forms.MessageBox]::Show("Reset fehlgeschlagen:`n$($_.Exception.Message)", "Passwort-Reset", "OK", "Error") | Out-Null
    }
})

$form.AcceptButton = $submit
$form.CancelButton = $cancel
$form.Add_Shown({ $password1.Focus() })
[void]$form.ShowDialog()
