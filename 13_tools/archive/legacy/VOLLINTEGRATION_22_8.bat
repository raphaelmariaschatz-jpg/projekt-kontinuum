@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

title Projekt Kontinuum 22.8 - Vollintegration Vorbereitung

echo ============================================================
echo Projekt Kontinuum 22.8 - VOLLINTEGRATION
echo ============================================================
echo.
echo Sicherheitsmodus: Diese BAT erstellt eine 22.8-Arbeitskopie,
echo sammelt Legacy-Versionen und Berichte, aber ersetzt keine
 echo produktiven Login-Dateien ohne separate Freigabe.
echo.

set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%CD%"

if not exist "%PROJECT_ROOT%" (
    echo [FEHLER] Projektordner nicht gefunden: "%PROJECT_ROOT%"
    echo Nutzung: VOLLINTEGRATION_22_8.bat "E:\Projekt_Kontinuum_Test"
    pause
    exit /b 1
)

set "VERSIONS_ROOT=%PROJECT_ROOT%\02_versions"
if not exist "%VERSIONS_ROOT%" (
    echo [FEHLER] 02_versions nicht gefunden unter: "%PROJECT_ROOT%"
    pause
    exit /b 1
)

for /f "tokens=1-4 delims=.:-/ " %%a in ("%date% %time%") do set "STAMP=%%c%%b%%a_%%d"
set "STAMP=%STAMP: =0%"
set "OUT=%PROJECT_ROOT%\_vollintegration_22_8_%STAMP%"
set "TARGET=%VERSIONS_ROOT%\version_22\Projekt_Kontinuum_22_8_Vollintegration_1_bis_22"
set "BACKUP=%OUT%\backup_vor_vollintegration"

mkdir "%OUT%" >nul 2>nul
mkdir "%BACKUP%" >nul 2>nul
mkdir "%TARGET%" >nul 2>nul
mkdir "%TARGET%\legacy_versions" >nul 2>nul
mkdir "%TARGET%\legacy_data" >nul 2>nul
mkdir "%TARGET%\legacy_security" >nul 2>nul
mkdir "%TARGET%\docs" >nul 2>nul
mkdir "%TARGET%\logs" >nul 2>nul
mkdir "%TARGET%\scripts" >nul 2>nul
mkdir "%TARGET%\kontinuum" >nul 2>nul

set "REPORT=%OUT%\VOLLINTEGRATION_REPORT.txt"
echo Projektordner: %PROJECT_ROOT% > "%REPORT%"
echo Zielordner: %TARGET% >> "%REPORT%"
echo Erstellt: %date% %time% >> "%REPORT%"
echo. >> "%REPORT%"

echo WICHTIG: Diese Version ist eine Arbeitskopie/Vorbereitung. >> "%REPORT%"
echo Produktive Sicherheit/Login-Dateien werden nur gesammelt, nicht aktiv ersetzt. >> "%REPORT%"
echo. >> "%REPORT%"

echo [SICHERHEITSFRAGE]
echo Zielordner:
echo "%TARGET%"
echo.
echo Diese BAT erstellt/ergaenzt diesen Zielordner.
echo Sie kopiert viele Dateien, loescht aber nichts.
echo.
choice /C JN /M "Fortfahren? J=Ja, N=Nein"
if errorlevel 2 (
    echo Abgebrochen durch Benutzer. >> "%REPORT%"
    echo Abgebrochen.
    pause
    exit /b 0
)

echo [1/7] Sichere vorhandenen Zielordner, falls vorhanden...
if exist "%TARGET%" (
    xcopy "%TARGET%" "%BACKUP%\Projekt_Kontinuum_22_8_Vollintegration_1_bis_22" /E /I /H /Y >nul 2>nul
)

echo [2/7] Kopiere alle Versionen 1 bis 22 als Legacy-Archiv...
for /d %%D in ("%VERSIONS_ROOT%\version_*") do (
    set "NAME=%%~nxD"
    echo Kopiere !NAME! ...
    echo Legacy: !NAME! >> "%REPORT%"
    xcopy "%%D" "%TARGET%\legacy_versions\!NAME!" /E /I /H /Y >nul 2>nul
)

echo [3/7] Sammle Daten-/Wissensdateien separat...
for /r "%VERSIONS_ROOT%" %%F in (*.json) do (
    set "REL=%%F"
    set "REL=!REL:%VERSIONS_ROOT%=!"
    set "REL=!REL:\=_!"
    copy /Y "%%F" "%TARGET%\legacy_data\!REL!" >nul 2>nul
)

echo [4/7] Sammle Security/Login-Dateien separat...
for /r "%VERSIONS_ROOT%" %%F in (*security*.json *auth*.py *login*.py *password*.* *passwort*.* *recovery*.*) do (
    if exist "%%F" (
        set "REL=%%F"
        set "REL=!REL:%VERSIONS_ROOT%=!"
        set "REL=!REL:\=_!"
        copy /Y "%%F" "%TARGET%\legacy_security\!REL!" >nul 2>nul
    )
)

echo [5/7] Erzeuge Startdateien fuer 22.8-Arbeitskopie...
(
 echo @echo off
 echo cd /d "%%~dp0"
 echo echo Starte Projekt Kontinuum 22.8 Vollintegration...
 echo if exist main.py ^(
 echo     python main.py
 echo ^) else ^(
 echo     echo main.py nicht gefunden. Bitte Integrationsbericht pruefen.
 echo     pause
 echo ^)
) > "%TARGET%\START_KONTINUUM_22_8.bat"

(
 echo @echo off
 echo cd /d "%%~dp0"
 echo echo Starte GUI 22.8, falls vorhanden...
 echo if exist desktop_gui.py ^(
 echo     python desktop_gui.py
 echo ^) else ^(
 echo     echo desktop_gui.py nicht gefunden. Bitte aus Master-Version 18.x uebernehmen.
 echo     pause
 echo ^)
) > "%TARGET%\START_GUI_22_8.bat"

(
 echo @echo off
 echo cd /d "%%~dp0"
 echo echo Installiere Requirements, falls vorhanden...
 echo if exist requirements.txt python -m pip install -r requirements.txt
 echo if exist requirements_windows.txt python -m pip install -r requirements_windows.txt
 echo if exist requirements-web.txt python -m pip install -r requirements-web.txt
 echo pause
) > "%TARGET%\INSTALL_REQUIREMENTS_22_8.bat"

echo [6/7] Erzeuge 22.8 Integrationsmanifest...
(
 echo Projekt Kontinuum 22.8 - Vollintegration 1 bis 22
 echo ============================================================
 echo Erstellt: %date% %time%
 echo Quelle: %PROJECT_ROOT%
 echo Ziel: %TARGET%
 echo.
 echo Inhalt:
 echo - legacy_versions: Vollkopien aller vorhandenen Versionen 1 bis 22
 echo - legacy_data: gesammelte JSON-Daten, Memory, Wissen, Quellen, Einstellungen
 echo - legacy_security: gesammelte Login-/Security-/Auth-Kandidaten
 echo - START_KONTINUUM_22_8.bat
 echo - START_GUI_22_8.bat
 echo - INSTALL_REQUIREMENTS_22_8.bat
 echo.
 echo Wichtiger Hinweis:
 echo Dies ist eine sichere Arbeitsintegration, noch keine bereinigte finale Runtime.
 echo Die finale Runtime muss danach anhand der Master-Auswahl aufgebaut werden.
 echo Login/Auth muss gezielt migriert werden, nicht blind ersetzt.
 echo.
 echo Empfohlene Master:
 echo - Version 18.x fuer GUI/Web/Agenten/Internetstatus
 echo - Version 6.3 und 9 fuer Security/Login
 echo - Version 22.x fuer Connector-/Superadmin-/Projektprinzip-Erweiterungen
) > "%TARGET%\docs\INTEGRATIONSMANIFEST_22_8.txt"

echo [7/7] Erzeuge Dateilisten...
dir "%TARGET%" /s /b > "%OUT%\ziel_dateiliste_22_8.txt" 2>nul
tree "%TARGET%" /F /A > "%OUT%\ziel_ordnerbaum_22_8.txt" 2>nul

echo Fertig. >> "%REPORT%"
echo Zielordner: %TARGET% >> "%REPORT%"
echo Berichtordner: %OUT% >> "%REPORT%"

echo.
echo Fertig.
echo Zielordner: %TARGET%
echo Berichtordner: %OUT%
echo.
echo Bitte ZIPPE danach den Zielordner und sende ihn zur Pruefung.
pause
exit /b 0
