@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM Projekt Kontinuum 22.8 - Finalizer - FIXED ASCII

title Projekt Kontinuum 22.8 Finalizer

REM Wenn kein Parameter uebergeben wurde, aktuellen Ordner verwenden
if "%~1"=="" (
    set "TARGET=%CD%"
) else (
    set "TARGET=%~1"
)

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

echo Projekt Kontinuum 22.8 - FINALIZER > "%REPORT%"
echo Erstellt am: %DATE% %TIME% >> "%REPORT%"
echo Runtime: %RUNTIME% >> "%REPORT%"
echo. >> "%REPORT%"

echo [INFO] Sichere zentrale Runtime-Dateien...
if exist "%RUNTIME%\main.py" copy "%RUNTIME%\main.py" "%BACKUP_DIR%\" >nul 2>nul
if exist "%RUNTIME%\desktop_gui.py" copy "%RUNTIME%\desktop_gui.py" "%BACKUP_DIR%\" >nul 2>nul
if exist "%RUNTIME%\web_app.py" copy "%RUNTIME%\web_app.py" "%BACKUP_DIR%\" >nul 2>nul
if exist "%KONTINUUM_DIR%\version.py" copy "%KONTINUUM_DIR%\version.py" "%BACKUP_DIR%\" >nul 2>nul

echo [INFO] Schreibe Version 22.8 Metadaten...
(
echo VERSION = "22.8"
echo VERSION_NAME = "Projekt Kontinuum 22.8 Vollintegration 1 bis 22"
echo CREATOR = "Raphael Schatz"
echo SUPERADMIN = "Raphael Schatz"
echo PRINCIPLES = ["Erkennen - Schaffen - Vollenden", "Der Weg ist das Ziel"]
echo BASELINE = "Version 18.x technische Basis plus Version 6.3/9 Security plus Version 22 Connector/Superadmin"
) > "%KONTINUUM_DIR%\version.py"

echo [INFO] Erstelle kontinuum_22_8_runtime.py ...
(
echo from pathlib import Path
echo.
echo VERSION = "22.8"
echo NAME = "Projekt Kontinuum 22.8 Vollintegration 1 bis 22"
echo CREATOR = "Raphael Schatz"
echo.
echo def main():
echo     print("=" * 70^)
echo     print(NAME^)
echo     print("Schoepfer / Superadministrator:", CREATOR^)
echo     print("Prinzipien: Erkennen - Schaffen - Vollenden ^| Der Weg ist das Ziel"^)
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
) > "%RUNTIME%\kontinuum_22_8_runtime.py"

echo [INFO] Erstelle gui_22_8_runtime.py ...
(
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
echo     output.insert(tk.END, "Raphael: " + text + "\n"^)
echo     low = text.lower()
echo     if "version" in low:
echo         ans = "Kontinuum: Ich bin Projekt Kontinuum 22.8 Vollintegration 1 bis 22."
echo     elif "wer bin ich" in low or "weisst du wer ich bin" in low:
echo         ans = "Kontinuum: Du bist Raphael Schatz, mein Schoepfer und Superadministrator."
echo     elif "superadmin" in low:
echo         ans = "Kontinuum: Raphael Schatz ist als Superadministrator festgelegt."
echo     else:
echo         ans = "Kontinuum: Ich habe dich verstanden. Die Runtime 22.8 ist aktiv."
echo     output.insert(tk.END, ans + "\n\n"^)
echo     entry.delete(0, tk.END^)
echo.
echo root = tk.Tk()
echo root.title("Projekt Kontinuum 22.8 - Vollintegration 1 bis 22"^)
echo root.geometry("900x600"^)
echo tk.Label(root, text="Projekt Kontinuum 22.8 - Raphael Schatz Superadministrator"^).pack(pady=5^)
echo output = scrolledtext.ScrolledText(root, wrap=tk.WORD^)
echo output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10^)
echo entry = tk.Entry(root^)
echo entry.pack(fill=tk.X, padx=10, pady=5^)
echo tk.Button(root, text="Senden", command=send^).pack(pady=5^)
echo output.insert(tk.END, "Kontinuum 22.8 bereit.\n"^)
echo root.mainloop()
) > "%RUNTIME%\gui_22_8_runtime.py"

echo [INFO] Erstelle finale Startdateien...
(
echo @echo off
echo cd /d "%%~dp0"
echo title Projekt Kontinuum 22.8 Final
echo python kontinuum_22_8_runtime.py
echo pause
) > "%RUNTIME%\START_KONTINUUM_22_8_FINAL.bat"

(
echo @echo off
echo cd /d "%%~dp0"
echo title Projekt Kontinuum 22.8 GUI
echo python gui_22_8_runtime.py
echo pause
) > "%RUNTIME%\START_GUI_22_8_FINAL.bat"

(
echo @echo off
echo cd /d "%%~dp0"
echo echo Pruefe Projekt Kontinuum 22.8 Runtime...
echo if exist "kontinuum_22_8_runtime.py" ^(echo [OK] Runtime Entry vorhanden^) else ^(echo [FEHLER] Runtime Entry fehlt^)
echo if exist "gui_22_8_runtime.py" ^(echo [OK] GUI Runtime vorhanden^) else ^(echo [FEHLER] GUI Runtime fehlt^)
echo if exist "kontinuum\auth_master.py" ^(echo [OK] Auth Master vorhanden^) else ^(echo [WARNUNG] Auth Master fehlt - AUTH_MASTER_BUILDER zuerst ausfuehren^)
echo if exist "security\users.json" ^(echo [OK] User-Datei vorhanden^) else ^(echo [WARNUNG] User-Datei fehlt^)
echo if exist "legacy_versions" ^(echo [OK] Legacy-Versionen vorhanden^) else ^(echo [WARNUNG] legacy_versions nicht gefunden^)
echo echo.
echo python kontinuum_22_8_runtime.py
echo pause
) > "%RUNTIME%\PRUEFE_22_8_FINAL.bat"

(
echo # Projekt Kontinuum 22.8 Finalisierungsstatus
echo.
echo Erstellt am: %DATE% %TIME%
echo.
echo - Version sichtbar auf 22.8 gesetzt.
echo - Raphael Schatz als Schoepfer und Superadministrator hinterlegt.
echo - Startdateien fuer Runtime und GUI erstellt.
echo - Legacy-Versionen bleiben erhalten und werden nicht geloescht.
) > "%DOCS_DIR%\FINAL_STATUS_22_8.md"

echo Ergebnis: >> "%REPORT%"
echo - Version 22.8 Metadaten geschrieben >> "%REPORT%"
echo - Runtime Entry erstellt >> "%REPORT%"
echo - GUI Runtime erstellt >> "%REPORT%"
echo - finale Startdateien erstellt >> "%REPORT%"

echo.
echo [OK] Projekt Kontinuum 22.8 Finalizer abgeschlossen.
echo [OK] Bericht: "%REPORT%"
echo.
echo Starte danach:
echo PRUEFE_22_8_FINAL.bat
echo.
pause
exit /b 0
