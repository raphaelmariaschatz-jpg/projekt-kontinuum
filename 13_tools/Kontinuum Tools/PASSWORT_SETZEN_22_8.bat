@echo off
setlocal
cd /d "%~dp0"

echo.
echo Projekt Kontinuum 22.8 - Passwort setzen
echo Benutzer: Raphael / Raphael Schatz
echo.

if not exist "kontinuum\auth_master.py" (
    echo [FEHLER] Datei fehlt: kontinuum\auth_master.py
    echo Bitte auth_master.py zuerst nach runtime_22_8\kontinuum kopieren.
    pause
    exit /b 1
)

set /p NEWPASS=Neues Passwort eingeben: 

python -c "from kontinuum.auth_master import create_or_reset_superadmin_password; create_or_reset_superadmin_password(r'%NEWPASS%'); print('Passwort fuer Raphael Schatz wurde gesetzt.')"

echo.
echo Fertig. Du kannst dich danach mit Benutzername Raphael oder Raphael Schatz anmelden.
echo.
pause
