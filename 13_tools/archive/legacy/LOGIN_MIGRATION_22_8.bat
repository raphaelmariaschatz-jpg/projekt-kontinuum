@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

title Projekt Kontinuum 22.8 - Login Migration

echo ============================================================
echo Projekt Kontinuum 22.8 - LOGIN_MIGRATION
echo ============================================================
echo.
echo Diese Datei analysiert und sammelt Login-/Security-Dateien.
echo Sie ueberschreibt KEINE bestehenden Projektdateien automatisch.
echo.

set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%CD%"

if not exist "%PROJECT_ROOT%" (
    echo [FEHLER] Projektordner nicht gefunden: "%PROJECT_ROOT%"
    echo Nutzung: LOGIN_MIGRATION_22_8.bat "E:\Projekt_Kontinuum_Test"
    pause
    exit /b 1
)

for /f "tokens=1-4 delims=.:-/ " %%a in ("%date% %time%") do set "STAMP=%%c%%b%%a_%%d"
set "STAMP=%STAMP: =0%"
set "OUT=%PROJECT_ROOT%\_migration_22_8_login_%STAMP%"
set "BACKUP=%OUT%\backup_security_originale"
mkdir "%OUT%" >nul 2>nul
mkdir "%BACKUP%" >nul 2>nul

echo Projektordner: %PROJECT_ROOT% > "%OUT%\LOGIN_MIGRATION_REPORT.txt"
echo Analyseordner: %OUT% >> "%OUT%\LOGIN_MIGRATION_REPORT.txt"
echo Erstellt: %date% %time% >> "%OUT%\LOGIN_MIGRATION_REPORT.txt"
echo. >> "%OUT%\LOGIN_MIGRATION_REPORT.txt"

echo [1/5] Suche Security/Login-Dateien...
(
 echo Security- und Login-Kandidaten
 echo ============================================================
 dir "%PROJECT_ROOT%\*security*.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*auth*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*login*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*password*.*" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*passwort*.*" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*recovery*.*" /s /b 2^>nul
) > "%OUT%\security_login_kandidaten.txt"

echo [2/5] Suche bevorzugte Master-Kandidaten...
(
 echo Empfohlene Master-Kandidaten
 echo ============================================================
 echo [Version 6.3 Sicherheitsedition]
 dir "%PROJECT_ROOT%\02_versions\version_06\*6_3*\*\data\security.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\02_versions\version_06\*6_3*\*\continuum_v6_3.py" /s /b 2^>nul
 echo.
 echo [Version 9 Cross Platform]
 dir "%PROJECT_ROOT%\02_versions\version_09\*\*\data\security.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\02_versions\version_09\*\*\secure_data" /s /b /ad 2^>nul
 dir "%PROJECT_ROOT%\02_versions\version_09\*\*\continuum_v9.py" /s /b 2^>nul
 echo.
 echo [Version 22.x Auth]
 dir "%PROJECT_ROOT%\02_versions\version_22\*auth*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\02_versions\version_22\*security*.json" /s /b 2^>nul
) > "%OUT%\login_master_kandidaten.txt"

echo [3/5] Kopiere Security/Login-Dateien in Analyse-Backup...
for /f "usebackq delims=" %%F in ("%OUT%\security_login_kandidaten.txt") do (
    if exist "%%F" (
        set "REL=%%F"
        set "REL=!REL:%PROJECT_ROOT%=!"
        set "REL=!REL:\=_!"
        copy /Y "%%F" "%BACKUP%\!REL!" >nul 2>nul
    )
)

echo [4/5] Erzeuge Migrationsplan...
(
 echo LOGIN_MIGRATION_22_8 - Migrationsplan
 echo ============================================================
 echo.
 echo Ziel:
 echo - Raphael Schatz als Superadmin erhalten/wiederherstellen.
 echo - Bestehende Passwortdaten aus Version 6.3/9/22 sichern.
 echo - Keine automatische Ueberschreibung ohne spaetere manuelle Pruefung.
 echo.
 echo Empfohlene Reihenfolge:
 echo 1. Version 6.3 Sicherheitsedition als Sicherheitslogik pruefen.
 echo 2. Version 9 security.json als altes Passwort-/Login-Referenzsystem pruefen.
 echo 3. Version 22.x auth.py NICHT blind als Master nutzen, wenn dort ein Default-Passwort steht.
 echo 4. Erst nach Codepruefung eine neue auth.py fuer 22.8 erzeugen.
 echo.
 echo Ausgabe-Dateien:
 echo - security_login_kandidaten.txt
 echo - login_master_kandidaten.txt
 echo - backup_security_originale\
 echo.
 echo Wichtig:
 echo Diese BAT migriert noch nicht produktiv. Sie bereitet die sichere Migration vor.
) > "%OUT%\LOGIN_MIGRATIONSPLAN.txt"

echo [5/5] Fertig.
echo Bericht: %OUT%
echo.
echo LOGIN_MIGRATION_22_8 abgeschlossen. >> "%OUT%\LOGIN_MIGRATION_REPORT.txt"
echo Ausgabeordner: %OUT% >> "%OUT%\LOGIN_MIGRATION_REPORT.txt"

echo Bitte sende den Ordner zur Pruefung oder pruefe die TXT-Berichte.
pause
exit /b 0
