@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

title Projekt Kontinuum - Analyse Patch Version 1 bis 22

echo ============================================================
echo Projekt Kontinuum - Analyse Patch Version 1 bis 22
echo ============================================================
echo.
echo Dieser Patch analysiert nur. Er kopiert, loescht oder veraendert
echo keine Projektdateien ausserhalb des Analyseordners.
echo.

REM ------------------------------------------------------------
REM Projektordner bestimmen
REM ------------------------------------------------------------
set "DEFAULT_ROOT=E:\Projekt_Kontinuum_Test"
set "PROJECT_ROOT=%~1"

if "%PROJECT_ROOT%"=="" (
    if exist "%DEFAULT_ROOT%" (
        set "PROJECT_ROOT=%DEFAULT_ROOT%"
    ) else (
        set /p PROJECT_ROOT=Bitte Pfad zum Testordner eingeben, z.B. E:\Projekt_Kontinuum_Test: 
    )
)

if not exist "%PROJECT_ROOT%" (
    echo.
    echo [FEHLER] Projektordner nicht gefunden: "%PROJECT_ROOT%"
    echo Starte diese BAT mit Pfad, z.B.:
    echo ANALYSE_PATCH_KONTINUUM_1_BIS_22.bat "E:\Projekt_Kontinuum_Test"
    echo.
    pause
    exit /b 1
)

for /f "tokens=1-4 delims=/-. " %%a in ("%date%") do set "DATE_STAMP=%%d%%c%%b"
for /f "tokens=1-3 delims=:,. " %%a in ("%time%") do set "TIME_STAMP=%%a%%b%%c"
set "TIME_STAMP=%TIME_STAMP: =0%"
set "ANALYSIS_DIR=%PROJECT_ROOT%\_analyse_22_8_vollintegration_%DATE_STAMP%_%TIME_STAMP%"
mkdir "%ANALYSIS_DIR%" >nul 2>nul

set "REPORT=%ANALYSIS_DIR%\integration_analyse_report.txt"
set "VERSION_REPORT=%ANALYSIS_DIR%\versionen_uebersicht.txt"
set "PY_LIST=%ANALYSIS_DIR%\python_dateien.txt"
set "BAT_LIST=%ANALYSIS_DIR%\bat_dateien.txt"
set "SEC_LIST=%ANALYSIS_DIR%\security_dateien.txt"
set "DOC_LIST=%ANALYSIS_DIR%\dokumentations_dateien.txt"
set "DATA_LIST=%ANALYSIS_DIR%\daten_dateien.txt"
set "TREE_FILE=%ANALYSIS_DIR%\ordnerbaum.txt"
set "FILE_LIST=%ANALYSIS_DIR%\vollstaendige_dateiliste.txt"
set "LOGIN_HINTS=%ANALYSIS_DIR%\login_auth_hinweise.txt"
set "MASTER_HINTS=%ANALYSIS_DIR%\master_kandidaten.txt"

(
 echo Projekt Kontinuum - Analyse Patch Version 1 bis 22
 echo Erstellt am: %date% %time%
 echo Projektordner: %PROJECT_ROOT%
 echo Analyseordner: %ANALYSIS_DIR%
 echo.
 echo Zweck:
 echo - Inventur aller vorhandenen Versionen 1 bis 22
 echo - Suche nach Python-, BAT-, Security-, Login-, Dokumentations- und Daten-Dateien
 echo - Vorbereitung fuer eine sichere Vollintegration Version 22.8
 echo.
 echo WICHTIG: Dieser Patch fuehrt keine Integration aus und ueberschreibt keine vorhandenen Projektdateien.
) > "%REPORT%"

echo [1/8] Erzeuge vollstaendige Dateiliste...
dir "%PROJECT_ROOT%" /S /B > "%FILE_LIST%" 2>nul

echo [2/8] Erzeuge Ordnerbaum...
tree "%PROJECT_ROOT%" /F /A > "%TREE_FILE%" 2>nul

echo [3/8] Suche Python-Dateien...
dir "%PROJECT_ROOT%\*.py" /S /B > "%PY_LIST%" 2>nul

echo [4/8] Suche BAT-Dateien...
dir "%PROJECT_ROOT%\*.bat" /S /B > "%BAT_LIST%" 2>nul

echo [5/8] Suche Security- und Login-Dateien...
(
 dir "%PROJECT_ROOT%\security.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\*auth*.py" /S /B 2>nul
 dir "%PROJECT_ROOT%\*login*.py" /S /B 2>nul
 dir "%PROJECT_ROOT%\*user*.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\*benutzer*.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\*recovery*.*" /S /B 2>nul
 dir "%PROJECT_ROOT%\secure_data" /S /B 2>nul
) > "%SEC_LIST%"

echo [6/8] Suche Dokumentation...
(
 dir "%PROJECT_ROOT%\README*" /S /B 2>nul
 dir "%PROJECT_ROOT%\*ARCHITEKTUR*" /S /B 2>nul
 dir "%PROJECT_ROOT%\*ARCHITECTURE*" /S /B 2>nul
 dir "%PROJECT_ROOT%\*HANDBUCH*" /S /B 2>nul
 dir "%PROJECT_ROOT%\*CHANGELOG*" /S /B 2>nul
 dir "%PROJECT_ROOT%\*CHRONIK*" /S /B 2>nul
 dir "%PROJECT_ROOT%\*INTEGRATION*" /S /B 2>nul
) > "%DOC_LIST%"

echo [7/8] Suche Daten- und Wissensdateien...
(
 dir "%PROJECT_ROOT%\memory.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\knowledge_graph.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\master_index.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\sources.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\settings.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\learning_tasks.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\research_reports.json" /S /B 2>nul
 dir "%PROJECT_ROOT%\*.db" /S /B 2>nul
 dir "%PROJECT_ROOT%\*.sqlite" /S /B 2>nul
) > "%DATA_LIST%"

echo [8/8] Erzeuge Versionsuebersicht...
(
 echo Versionsuebersicht Projekt Kontinuum
 echo Projektordner: %PROJECT_ROOT%
 echo.
 for /L %%V in (1,1,22) do (
     set "N=0%%V"
     set "N=!N:~-2!"
     echo ------------------------------------------------------------
     echo Version %%V / Ordnersuche version_!N!, version_%%V, v%%V
     echo ------------------------------------------------------------
     dir "%PROJECT_ROOT%\*version_!N!*" /S /B /AD 2>nul
     dir "%PROJECT_ROOT%\*version_%%V*" /S /B /AD 2>nul
     dir "%PROJECT_ROOT%\*v%%V*" /S /B /AD 2>nul
     echo.
 )
) > "%VERSION_REPORT%"

REM Kandidaten fuer Master-Komponenten
(
 echo Master-Kandidaten fuer spaetere Version 22.8
 echo.
 echo [Login/Security-Kandidaten]
 findstr /I /C:"version_09" "%SEC_LIST%" 2>nul
 findstr /I /C:"security.json" "%SEC_LIST%" 2>nul
 findstr /I /C:"auth" "%SEC_LIST%" 2>nul
 echo.
 echo [GUI/Web-Kandidaten]
 findstr /I /C:"desktop_gui.py" "%PY_LIST%" 2>nul
 findstr /I /C:"web_app.py" "%PY_LIST%" 2>nul
 findstr /I /C:"gui" "%PY_LIST%" 2>nul
 echo.
 echo [Agenten-Kandidaten]
 findstr /I /C:"agents" "%PY_LIST%" 2>nul
 findstr /I /C:"orchestrator" "%PY_LIST%" 2>nul
 findstr /I /C:"dialog" "%PY_LIST%" 2>nul
 findstr /I /C:"research" "%PY_LIST%" 2>nul
 echo.
 echo [Startdateien]
 type "%BAT_LIST%"
) > "%MASTER_HINTS%"

REM Login Hinweise mit Textsuche in Python/JSON, ohne Dateien zu veraendern
(
 echo Login- und Authentifizierungs-Hinweise
 echo.
 echo Suche nach Begriffen: password, passwort, login, auth, Raphael, Superadmin, recovery
 echo.
 for /f "usebackq delims=" %%F in ("%PY_LIST%") do (
     findstr /I /N /C:"password" /C:"passwort" /C:"login" /C:"auth" /C:"Raphael" /C:"superadmin" /C:"recovery" "%%F" >nul 2>nul
     if not errorlevel 1 (
         echo ------------------------------------------------------------
         echo %%F
         findstr /I /N /C:"password" /C:"passwort" /C:"login" /C:"auth" /C:"Raphael" /C:"superadmin" /C:"recovery" "%%F" 2>nul
     )
 )
 for /f "usebackq delims=" %%F in ("%SEC_LIST%") do (
     echo ------------------------------------------------------------
     echo %%F
 )
) > "%LOGIN_HINTS%"

REM Zahlen ermitteln
for /f %%A in ('type "%PY_LIST%" ^| find /C /V ""') do set PY_COUNT=%%A
for /f %%A in ('type "%BAT_LIST%" ^| find /C /V ""') do set BAT_COUNT=%%A
for /f %%A in ('type "%SEC_LIST%" ^| find /C /V ""') do set SEC_COUNT=%%A
for /f %%A in ('type "%DOC_LIST%" ^| find /C /V ""') do set DOC_COUNT=%%A
for /f %%A in ('type "%DATA_LIST%" ^| find /C /V ""') do set DATA_COUNT=%%A
for /f %%A in ('type "%FILE_LIST%" ^| find /C /V ""') do set FILE_COUNT=%%A

(
 echo.
 echo ============================================================
 echo Zusammenfassung
 echo ============================================================
 echo Dateien gesamt: %FILE_COUNT%
 echo Python-Dateien: %PY_COUNT%
 echo BAT-Dateien: %BAT_COUNT%
 echo Security/Login-Fundstellen: %SEC_COUNT%
 echo Dokumentationsdateien: %DOC_COUNT%
 echo Daten-/Wissensdateien: %DATA_COUNT%
 echo.
 echo Erzeugte Berichte:
 echo - %VERSION_REPORT%
 echo - %PY_LIST%
 echo - %BAT_LIST%
 echo - %SEC_LIST%
 echo - %DOC_LIST%
 echo - %DATA_LIST%
 echo - %TREE_FILE%
 echo - %FILE_LIST%
 echo - %LOGIN_HINTS%
 echo - %MASTER_HINTS%
 echo.
 echo Naechster Schritt:
 echo Bitte den Ordner "%ANALYSIS_DIR%" als ZIP packen und zur Pruefung senden.
) >> "%REPORT%"

echo.
echo ============================================================
echo Analyse abgeschlossen.
echo ============================================================
echo Analyseordner:
echo %ANALYSIS_DIR%
echo.
echo Wichtig: Bitte diesen Analyseordner als ZIP packen und hochladen.
echo.
pause
exit /b 0
