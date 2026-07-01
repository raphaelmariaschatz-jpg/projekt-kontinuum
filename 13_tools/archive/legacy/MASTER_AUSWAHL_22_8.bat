@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

title Projekt Kontinuum 22.8 - Master Auswahl

echo ============================================================
echo Projekt Kontinuum 22.8 - MASTER_AUSWAHL
echo ============================================================
echo.
echo Diese Datei bestimmt Master-Kandidaten fuer die Vollintegration.
echo Sie kopiert nichts in eine Zielversion und ueberschreibt nichts.
echo.

set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%CD%"

if not exist "%PROJECT_ROOT%" (
    echo [FEHLER] Projektordner nicht gefunden: "%PROJECT_ROOT%"
    echo Nutzung: MASTER_AUSWAHL_22_8.bat "E:\Projekt_Kontinuum_Test"
    pause
    exit /b 1
)

for /f "tokens=1-4 delims=.:-/ " %%a in ("%date% %time%") do set "STAMP=%%c%%b%%a_%%d"
set "STAMP=%STAMP: =0%"
set "OUT=%PROJECT_ROOT%\_masterauswahl_22_8_%STAMP%"
mkdir "%OUT%" >nul 2>nul

set "REPORT=%OUT%\MASTER_AUSWAHL_REPORT.txt"

echo Projektordner: %PROJECT_ROOT% > "%REPORT%"
echo Analyseordner: %OUT% >> "%REPORT%"
echo Erstellt: %date% %time% >> "%REPORT%"
echo. >> "%REPORT%"

echo [1/8] Suche Hauptversionen...
dir "%PROJECT_ROOT%\02_versions\version_*" /b /ad > "%OUT%\versionen.txt" 2>nul

echo [2/8] Suche GUI/Web-Kandidaten...
(
 echo GUI/Web-Kandidaten
 echo ============================================================
 dir "%PROJECT_ROOT%\*desktop_gui.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*web_app.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*gui*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*main.py" /s /b 2^>nul
) > "%OUT%\kandidaten_gui_web.txt"

echo [3/8] Suche Agenten-Kandidaten...
(
 echo Agenten-Kandidaten
 echo ============================================================
 dir "%PROJECT_ROOT%\*agents*" /s /b /ad 2^>nul
 dir "%PROJECT_ROOT%\*agent*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*orchestrator*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*planner*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*research*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*reflection*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*dialog*.py" /s /b 2^>nul
) > "%OUT%\kandidaten_agenten.txt"

echo [4/8] Suche Internet/Connector-Kandidaten...
(
 echo Internet-/Connector-Kandidaten
 echo ============================================================
 dir "%PROJECT_ROOT%\*internet*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*connector*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*web*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*research*.py" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*sources*.json" /s /b 2^>nul
) > "%OUT%\kandidaten_internet_connectoren.txt"

echo [5/8] Suche Memory/Wissens-Kandidaten...
(
 echo Memory-/Wissens-Kandidaten
 echo ============================================================
 dir "%PROJECT_ROOT%\*memory*.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*knowledge*.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*knowledge_graph*.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*master_index*.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*questions*.json" /s /b 2^>nul
 dir "%PROJECT_ROOT%\*learning*.json" /s /b 2^>nul
) > "%OUT%\kandidaten_memory_wissen.txt"

echo [6/8] Suche BAT-/Installer-Kandidaten...
(
 echo BAT-/Installer-Kandidaten
 echo ============================================================
 dir "%PROJECT_ROOT%\*.bat" /s /b 2^>nul
 dir "%PROJECT_ROOT%\requirements*.txt" /s /b 2^>nul
) > "%OUT%\kandidaten_bat_install.txt"

echo [7/8] Schreibe empfohlene Master-Regeln...
(
 echo MASTER_AUSWAHL_22_8 - Empfohlene Master-Regeln
 echo ============================================================
 echo.
 echo 1. Technische Basis:
 echo    Version 18.x / 18.7, falls vorhanden: GUI, Web, Agenten, Tests, Internetstatus.
 echo.
 echo 2. Login/Security:
 echo    Version 6.3 fuer robuste Superadmin-Logik.
 echo    Version 9 fuer altes Passwort-/Cross-Platform-System.
 echo.
 echo 3. Startdateien:
 echo    Version 18.x fuer START_GUI/START_WEB/START_KONTINUUM.
 echo    Version 9 fuer START_WINDOWS/START_CONSOLE_WINDOWS als Legacy.
 echo.
 echo 4. Wissen/Memory:
 echo    Nicht ueberschreiben, sondern alle JSON-Dateien unter legacy_data sammeln.
 echo.
 echo 5. Version 22.x:
 echo    Nur als Zielarchitektur/Connector-/Superadmin-/Projektprinzip-Erweiterung nutzen.
 echo    Nicht als alleinige technische Basis verwenden, wenn weniger Dateien vorhanden sind.
 echo.
 echo 6. Schutzregel:
 echo    Niemals produktive security.json/auth.py ohne Backup ersetzen.
) > "%OUT%\MASTER_REGELN_22_8.txt"

echo [8/8] Fertig.
(
 echo.
 echo Ergebnisdateien:
 echo - versionen.txt
 echo - kandidaten_gui_web.txt
 echo - kandidaten_agenten.txt
 echo - kandidaten_internet_connectoren.txt
 echo - kandidaten_memory_wissen.txt
 echo - kandidaten_bat_install.txt
 echo - MASTER_REGELN_22_8.txt
 echo.
 echo Diese BAT hat nichts ueberschrieben.
) >> "%REPORT%"

echo Bericht: %OUT%
echo Bitte sende den Ordner zur Pruefung oder pruefe die TXT-Berichte.
pause
exit /b 0
