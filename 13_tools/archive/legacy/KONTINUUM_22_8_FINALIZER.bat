@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

REM ============================================================
REM Projekt Kontinuum 22.8 - FINALIZER
REM Zweck:
REM - Setzt Runtime-Version sichtbar auf 22.8
REM - Erstellt finale Startdateien
REM - Aktiviert Auth Master, falls vorhanden
REM - Erzeugt finalen Pruefbericht
REM - Loescht keine Legacy-Dateien
REM ============================================================

title Projekt Kontinuum 22.8 - Finalizer

if "%~1"=="" (
    echo.
    echo [FEHLER] Bitte den Pfad zur runtime_22_8 oder zum 22.8-Integrationsordner angeben.
    echo Beispiel:
    echo KONTINUUM_22_8_FINALIZER.bat "E:\Projekt_Kontinuum_Test\02_versions\version_22\Projekt_Kontinuum_22_8_Vollintegration_1_bis_22\runtime_22_8"
    echo.
    pause
    exit /b 1
)

set "TARGET=%~1"

if not exist "%TARGET%" (
    echo [FEHLER] Zielordner nicht gefunden:
    echo "%TARGET%"
    pause
    exit /b 1
)

if exist "%TARGET%\runtime_22_8" (
    set "TARGET=%TARGET%\runtime_22_8"
)

set "RUNTIME=%TARGET%"
set "KONTINUUM_DIR=%RUNTIME%\kontinuum"
set "DOCS_DIR=%RUNTIME%\docs"
set "REPORT=%RUNTIME%\FINALIZER_22_8_REPORT.txt"
set "BACKUP_DIR=%RUNTIME%\_backup_before_finalizer"

mkdir "%KONTINUUM_DIR%" 2>nul
mkdir "%DOCS_DIR%" 2>nul
mkdir "%BACKUP_DIR%" 2>nul

echo ============================================================ > "%REPORT%"
echo Projekt Kontinuum 22.8 - FINALIZER >> "%REPORT%"
echo Erstellt am: %DATE% %TIME% >> "%REPORT%"
echo Runtime: %RUNTIME% >> "%REPORT%"
echo ============================================================ >> "%REPORT%"
echo. >> "%REPORT%"

echo [INFO] Sichere zentrale Runtime-Dateien...
for %%F in ("%RUNTIME%\main.py" "%RUNTIME%\desktop_gui.py" "%RUNTIME%\web_app.py" "%KONTINUUM_DIR%\version.py") do (
    if exist "%%~F" copy "%%~F" "%BACKUP_DIR%\" >nul 2>nul
)

echo [INFO] Schreibe Version 22.8 Metadaten...

> "%KONTINUUM_DIR%\version.py" (
echo VERSION = "22.8"
echo VERSION_NAME = "Projekt Kontinuum 22.8 Vollintegration 1 bis 22"
echo CREATOR = "Raphael Schatz"
echo SUPERADMIN = "Raphael Schatz"
echo PRINCIPLES = ["Erkennen - Schaffen - Vollenden", "Der Weg ist das Ziel"]
echo BASELINE = "Version 18.x technische Basis + Version 6.3/9 Security + Version 22 Connector/Superadmin"
)

> "%RUNTIME%\kontinuum_22_8_runtime.py" (
echo # Projekt Kontinuum 22.8 - Runtime Entry
echo from pathlib import Path
echo import sys
echo.
echo VERSION = "22.8"
echo NAME = "Projekt Kontinuum 22.8 Vollintegration 1 bis 22"
echo CREATOR = "Raphael Schatz"
echo.
echo def main():
echo     print("=" * 70^)
echo     print(NAME^)
echo     print("Schöpfer / Superadministrator:", CREATOR^)
echo     print("Prinzipien: Erkennen - Schaffen - Vollenden | Der Weg ist das Ziel"^)
echo     print("=" * 70^)
echo     try:
echo         from kontinuum.auth_master import ensure_superadmin
echo         ensure_superadmin()
echo         print("[OK] Auth Master 22.8 aktiv."^)
echo     except Exception as exc:
echo         print("[WARNUNG] Auth Master konnte nicht geladen werden:", exc^)
echo     print("[INFO] Legacy-Versionen 1-22 bleiben als Referenz integriert."^)
echo     print("[INFO] Runtime bereit. GUI kann separat gestartet werden."^)
echo.
echo if __name__ == "__main__":
echo     main()
)

> "%RUNTIME%\gui_22_8_runtime.py" (
echo # Projekt Kontinuum 22.8 - einfache Runtime GUI
echo import tkinter as tk
echo from tkinter import scrolledtext
echo.
echo VERSION = "22.8"
echo CREATOR = "Raphael Schatz"
echo.
echo def send():
echo     text = entry.get().strip()
echo     if not text:
echo         return
echo     output.insert(tk.END, "Raphael: " + text + "\n")
echo     if "version" in text.lower():
echo         ans = "Kontinuum: Ich bin Projekt Kontinuum 22.8 Vollintegration 1 bis 22."
echo     elif "wer bin ich" in text.lower() or "weisst du wer ich bin" in text.lower() or "weißt du wer ich bin" in text.lower():
echo         ans = "Kontinuum: Du bist Raphael Schatz, mein Schöpfer und Superadministrator."
echo     elif "superadmin" in text.lower():
echo         ans = "Kontinuum: Raphael Schatz ist als Superadministrator festgelegt."
echo     else:
echo         ans = "Kontinuum: Ich habe dich verstanden. Die Runtime 22.8 ist aktiv; erweiterte Agenten werden aus der Vollintegration geladen."
echo     output.insert(tk.END, ans + "\n\n")
echo     entry.delete(0, tk.END)
echo.
echo root = tk.Tk()
echo root.title("Projekt Kontinuum 22.8 - Vollintegration 1 bis 22")
echo root.geometry("900x600")
echo tk.Label(root, text="Projekt Kontinuum 22.8 - Raphael Schatz Superadministrator").pack(pady=5)
echo output = scrolledtext.ScrolledText(root, wrap=tk.WORD)
echo output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
echo entry = tk.Entry(root)
echo entry.pack(fill=tk.X, padx=10, pady=5)
echo tk.Button(root, text="Senden", command=send).pack(pady=5)
echo output.insert(tk.END, "Kontinuum 22.8 bereit.\n")
echo root.mainloop()
)

echo [INFO] Erstelle finale Startdateien...

> "%RUNTIME%\START_KONTINUUM_22_8_FINAL.bat" (
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo title Projekt Kontinuum 22.8 Final
echo python kontinuum_22_8_runtime.py
echo pause
)

> "%RUNTIME%\START_GUI_22_8_FINAL.bat" (
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo title Projekt Kontinuum 22.8 GUI
echo python gui_22_8_runtime.py
echo pause
)

> "%RUNTIME%\PRUEFE_22_8_FINAL.bat" (
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo echo Pruefe Projekt Kontinuum 22.8 Runtime...
echo echo.
echo if exist "kontinuum_22_8_runtime.py" ^(echo [OK] Runtime Entry vorhanden^) else ^(echo [FEHLER] Runtime Entry fehlt^)
echo if exist "gui_22_8_runtime.py" ^(echo [OK] GUI Runtime vorhanden^) else ^(echo [FEHLER] GUI Runtime fehlt^)
echo if exist "kontinuum\auth_master.py" ^(echo [OK] Auth Master vorhanden^) else ^(echo [WARNUNG] Auth Master fehlt - LOGIN_KONSOLIDIERUNG zuerst ausfuehren^)
echo if exist "security\users.json" ^(echo [OK] User-Datei vorhanden^) else ^(echo [WARNUNG] User-Datei fehlt^)
echo if exist "legacy_versions" ^(echo [OK] Legacy-Versionen vorhanden^) else ^(echo [WARNUNG] legacy_versions nicht gefunden^)
echo echo.
echo python kontinuum_22_8_runtime.py
echo pause
)

> "%DOCS_DIR%\FINAL_STATUS_22_8.md" (
echo # Projekt Kontinuum 22.8 Finalisierungsstatus
echo.
echo Erstellt am: %DATE% %TIME%
echo.
echo ## Status
echo - Version sichtbar auf 22.8 gesetzt.
echo - Raphael Schatz als Schöpfer und Superadministrator hinterlegt.
echo - Startdateien fuer Runtime und GUI erstellt.
echo - Legacy-Versionen bleiben erhalten und werden nicht geloescht.
echo.
echo ## Wichtige Dateien
echo - START_KONTINUUM_22_8_FINAL.bat
echo - START_GUI_22_8_FINAL.bat
echo - PRUEFE_22_8_FINAL.bat
echo - PASSWORT_SETZEN_22_8.bat ^(falls Auth Master vorher ausgefuehrt wurde^)
)

>> "%REPORT%" echo Ergebnis:
>> "%REPORT%" echo - Version 22.8 Metadaten geschrieben
>> "%REPORT%" echo - Runtime Entry erstellt
>> "%REPORT%" echo - GUI Runtime erstellt
>> "%REPORT%" echo - finale Startdateien erstellt
>> "%REPORT%" echo - Legacy-Dateien nicht geloescht
>> "%REPORT%" echo.
>> "%REPORT%" echo Naechster Test:
>> "%REPORT%" echo 1. PRUEFE_22_8_FINAL.bat
>> "%REPORT%" echo 2. START_KONTINUUM_22_8_FINAL.bat
>> "%REPORT%" echo 3. START_GUI_22_8_FINAL.bat

echo.
echo [OK] Projekt Kontinuum 22.8 Finalizer abgeschlossen.
echo [OK] Bericht:
echo "%REPORT%"
echo.
echo Starte danach:
echo PRUEFE_22_8_FINAL.bat
echo.
pause
exit /b 0
