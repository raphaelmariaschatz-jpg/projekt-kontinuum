@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

title Projekt Kontinuum 22.8 - Runtime Builder

echo ============================================================
echo Projekt Kontinuum 22.8 - RUNTIME BUILDER
echo ============================================================
echo.

set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%CD%"

if not exist "%PROJECT_ROOT%" (
  echo [FEHLER] Projektordner nicht gefunden: "%PROJECT_ROOT%"
  echo Nutzung: RUNTIME_BUILDER_22_8.bat "E:\Projekt_Kontinuum_Test\02_versions\version_22\Projekt_Kontinuum_22_8_Vollintegration_1_bis_22"
  pause
  exit /b 1
)

set "STAMP=%DATE:~-4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "STAMP=%STAMP: =0%"
set "RUNTIME=%PROJECT_ROOT%\runtime_22_8"
set "APP=%RUNTIME%\app"
set "REPORT_DIR=%PROJECT_ROOT%\_berichte_22_8"
set "REPORT=%REPORT_DIR%\runtime_builder_%STAMP%.txt"

mkdir "%RUNTIME%" 2>nul
mkdir "%APP%" 2>nul
mkdir "%APP%\kontinuum" 2>nul
mkdir "%APP%\docs" 2>nul
mkdir "%APP%\data" 2>nul
mkdir "%APP%\logs" 2>nul
mkdir "%APP%\legacy_index" 2>nul
mkdir "%REPORT_DIR%" 2>nul

(
 echo Projekt Kontinuum 22.8 - Runtime Builder
 echo Erstellt am: %DATE% %TIME%
 echo Projektordner: %PROJECT_ROOT%
 echo Runtime: %RUNTIME%
 echo.
 echo Diese BAT baut eine Runtime-Struktur und loescht keine Legacy-Dateien.
 echo.
) > "%REPORT%"

echo [1/7] Pruefe Login-Konsolidierung...
if not exist "%RUNTIME%\security\auth_master_22_8.py" (
  echo [WARNUNG] auth_master_22_8.py fehlt. Bitte zuerst LOGIN_MIGRATION/KONSOLIDIERUNG ausfuehren.
  echo WARNUNG: auth_master_22_8.py fehlt>>"%REPORT%"
) else (
  mkdir "%APP%\kontinuum\security" 2>nul
  copy "%RUNTIME%\security\auth_master_22_8.py" "%APP%\kontinuum\security\auth_master_22_8.py" >nul
  copy "%RUNTIME%\security\PASSWORT_SETZEN_22_8.bat" "%APP%\PASSWORT_SETZEN_22_8.bat" >nul 2>nul
  echo Auth-Master uebernommen.>>"%REPORT%"
)

echo [2/7] Suche technische Basis Version 18...
set "BASE18="
for /d /r "%PROJECT_ROOT%" %%D in (*18*Vollaktiviert* *18_7* *version_18*) do (
  if exist "%%~fD\main.py" if not defined BASE18 set "BASE18=%%~fD"
)
if defined BASE18 (
  echo BASE18=!BASE18!>>"%REPORT%"
  xcopy "!BASE18!\kontinuum" "%APP%\kontinuum" /E /I /H /Y >nul 2>nul
  if exist "!BASE18!\main.py" copy "!BASE18!\main.py" "%APP%\main.py" >nul
  if exist "!BASE18!\desktop_gui.py" copy "!BASE18!\desktop_gui.py" "%APP%\desktop_gui.py" >nul
  if exist "!BASE18!\web_app.py" copy "!BASE18!\web_app.py" "%APP%\web_app.py" >nul
  if exist "!BASE18!\requirements.txt" copy "!BASE18!\requirements.txt" "%APP%\requirements.txt" >nul
  if exist "!BASE18!\requirements-web.txt" copy "!BASE18!\requirements-web.txt" "%APP%\requirements-web.txt" >nul
) else (
  echo [WARNUNG] Keine Version-18-Basis mit main.py gefunden.
  echo WARNUNG: Keine Version-18-Basis gefunden.>>"%REPORT%"
)

echo [3/7] Erzeuge Runtime-Konfiguration...
mkdir "%APP%\config" 2>nul
(
 echo {
 echo   "version": "22.8",
 echo   "name": "Projekt Kontinuum 22.8 Vollintegration 1 bis 22",
 echo   "creator": "Raphael Schatz",
 echo   "superadmin": "Raphael Schatz",
 echo   "principles": ["Erkennen - Schaffen - Vollenden", "Der Weg ist das Ziel"],
 echo   "base_runtime": "version_18_x",
 echo   "security_basis": "version_6_3_plus_version_9_plus_22_x",
 echo   "legacy_versions": "../legacy_versions",
 echo   "status": "runtime_candidate"
 echo }
) > "%APP%\config\runtime_22_8.json"

echo [4/7] Erzeuge Legacy-Index...
dir "%PROJECT_ROOT%\legacy_versions" /S /B > "%APP%\legacy_index\legacy_versions_files.txt" 2>nul
dir "%PROJECT_ROOT%\legacy_security" /S /B > "%APP%\legacy_index\legacy_security_files.txt" 2>nul
dir "%PROJECT_ROOT%\legacy_data" /S /B > "%APP%\legacy_index\legacy_data_files.txt" 2>nul

echo [5/7] Erzeuge Startdateien...
(
 echo @echo off
 echo chcp 65001 ^>nul
 echo cd /d "%%~dp0app"
 echo echo Starte Projekt Kontinuum 22.8 Runtime...
 echo if exist main.py ^(
 echo   python main.py
 echo ^) else ^(
 echo   echo main.py nicht gefunden. Bitte Runtime-Bericht pruefen.
 echo   pause
 echo ^)
) > "%RUNTIME%\START_KONTINUUM_22_8_RUNTIME.bat"

(
 echo @echo off
 echo chcp 65001 ^>nul
 echo cd /d "%%~dp0app"
 echo echo Starte Projekt Kontinuum 22.8 GUI...
 echo if exist desktop_gui.py ^(
 echo   python desktop_gui.py
 echo ^) else ^(
 echo   echo desktop_gui.py nicht gefunden. Bitte Runtime-Bericht pruefen.
 echo   pause
 echo ^)
) > "%RUNTIME%\START_GUI_22_8_RUNTIME.bat"

(
 echo @echo off
 echo chcp 65001 ^>nul
 echo cd /d "%%~dp0app"
 echo if exist requirements.txt python -m pip install -r requirements.txt
 echo if exist requirements-web.txt python -m pip install -r requirements-web.txt
 echo pause
) > "%RUNTIME%\INSTALL_REQUIREMENTS_22_8_RUNTIME.bat"

echo [6/7] Erzeuge Runtime-Pruefung...
(
 echo @echo off
 echo chcp 65001 ^>nul
 echo cd /d "%%~dp0app"
 echo echo Pruefe Runtime 22.8...
 echo echo.
 echo if exist main.py ^(echo [OK] main.py vorhanden^) else ^(echo [FEHLT] main.py^)
 echo if exist desktop_gui.py ^(echo [OK] desktop_gui.py vorhanden^) else ^(echo [FEHLT] desktop_gui.py^)
 echo if exist kontinuum\security\auth_master_22_8.py ^(echo [OK] Auth-Master vorhanden^) else ^(echo [FEHLT] Auth-Master^)
 echo if exist config\runtime_22_8.json ^(echo [OK] Runtime-Konfiguration vorhanden^) else ^(echo [FEHLT] Runtime-Konfiguration^)
 echo pause
) > "%RUNTIME%\PRUEFE_RUNTIME_22_8.bat"

echo [7/7] Dokumentation...
(
 echo # Projekt Kontinuum 22.8 Runtime
 echo.
 echo Diese Runtime wurde aus der Vollintegration 1 bis 22 vorbereitet.
 echo.
 echo ## Start
 echo - START_KONTINUUM_22_8_RUNTIME.bat
 echo - START_GUI_22_8_RUNTIME.bat
 echo - INSTALL_REQUIREMENTS_22_8_RUNTIME.bat
 echo - PRUEFE_RUNTIME_22_8.bat
 echo.
 echo ## Sicherheit
 echo Raphael Schatz ist als Superadmin vorgesehen.
 echo Die Login-Konsolidierung liegt unter app/kontinuum/security/auth_master_22_8.py.
 echo.
 echo ## Hinweis
 echo Dies ist ein Runtime-Kandidat. Bitte testen und danach zur Pruefung senden.
) > "%APP%\docs\README_RUNTIME_22_8.md"

echo STATUS=RUNTIME_BUILDER_ABGESCHLOSSEN>>"%REPORT%"
echo RUNTIME=%RUNTIME%>>"%REPORT%"
echo APP=%APP%>>"%REPORT%"

echo.
echo [OK] Runtime Builder abgeschlossen.
echo Runtime: "%RUNTIME%"
echo Bericht: "%REPORT%"
echo.
echo Naechster Schritt: PRUEFE_RUNTIME_22_8.bat ausfuehren, dann Runtime-Ordner als ZIP senden.
echo.
pause
endlocal
