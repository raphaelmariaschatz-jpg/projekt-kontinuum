@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

title Projekt Kontinuum 22.8 - Login Konsolidierung

echo ============================================================
echo Projekt Kontinuum 22.8 - LOGIN KONSOLIDIERUNG
echo ============================================================
echo.

set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=%CD%"

if not exist "%PROJECT_ROOT%" (
  echo [FEHLER] Projektordner nicht gefunden: "%PROJECT_ROOT%"
  echo Nutzung: LOGIN_KONSOLIDIERUNG_22_8.bat "E:\Projekt_Kontinuum_Test\02_versions\version_22\Projekt_Kontinuum_22_8_Vollintegration_1_bis_22"
  pause
  exit /b 1
)

set "STAMP=%DATE:~-4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "STAMP=%STAMP: =0%"
set "RUNTIME=%PROJECT_ROOT%\runtime_22_8"
set "SECURITY_DIR=%RUNTIME%\security"
set "REPORT_DIR=%PROJECT_ROOT%\_berichte_22_8"
set "REPORT=%REPORT_DIR%\login_konsolidierung_%STAMP%.txt"

mkdir "%RUNTIME%" 2>nul
mkdir "%SECURITY_DIR%" 2>nul
mkdir "%REPORT_DIR%" 2>nul
mkdir "%SECURITY_DIR%\candidates" 2>nul
mkdir "%SECURITY_DIR%\backups" 2>nul

(
 echo Projekt Kontinuum 22.8 - Login Konsolidierung
 echo Erstellt am: %DATE% %TIME%
 echo Projektordner: %PROJECT_ROOT%
 echo Runtime: %RUNTIME%
 echo.
 echo Diese BAT loescht keine Legacy-Dateien.
 echo Sie sammelt Login-/Security-Kandidaten und erzeugt einen einheitlichen Master-Auth-Entwurf.
 echo.
) > "%REPORT%"

echo [1/5] Sammle Security-Dateien...
for /r "%PROJECT_ROOT%" %%F in (security.json) do (
  set "SRC=%%~fF"
  set "NAME=%%~pnxF"
  set "SAFE=!SRC:%PROJECT_ROOT%=!"
  set "SAFE=!SAFE:\=_!"
  set "SAFE=!SAFE::=!"
  copy "%%~fF" "%SECURITY_DIR%\candidates\!SAFE!" >nul 2>nul
  echo SECURITY: %%~fF>>"%REPORT%"
)

echo [2/5] Sammle Auth-Python-Dateien...
for /r "%PROJECT_ROOT%" %%F in (*auth*.py) do (
  set "SRC=%%~fF"
  set "SAFE=!SRC:%PROJECT_ROOT%=!"
  set "SAFE=!SAFE:\=_!"
  set "SAFE=!SAFE::=!"
  copy "%%~fF" "%SECURITY_DIR%\candidates\!SAFE!" >nul 2>nul
  echo AUTH_PY: %%~fF>>"%REPORT%"
)

echo [3/5] Sammle weitere Login-Hinweise...
for /r "%PROJECT_ROOT%" %%F in (*login*.py *security*.py *guardian*.py) do (
  set "SRC=%%~fF"
  set "SAFE=!SRC:%PROJECT_ROOT%=!"
  set "SAFE=!SAFE:\=_!"
  set "SAFE=!SAFE::=!"
  copy "%%~fF" "%SECURITY_DIR%\candidates\!SAFE!" >nul 2>nul
  echo LOGIN_SECURITY_PY: %%~fF>>"%REPORT%"
)

echo [4/5] Erzeuge Master-Auth-Modul...
set "MASTER_AUTH=%SECURITY_DIR%\auth_master_22_8.py"
(
 echo # Projekt Kontinuum 22.8 - Master Auth
 echo # Erzeugt durch LOGIN_KONSOLIDIERUNG_22_8.bat
 echo # Ziel: Raphael Schatz als Superadmin, robuste Passwortpruefung, alte Hashes importierbar.
 echo.
 echo import json, hashlib, secrets, os, datetime
 echo from pathlib import Path
 echo.
 echo SUPERADMIN_NAME = "Raphael Schatz"
 echo USER_ALIASES = {"Raphael", "Raphael Schatz", "raphael", "raphael schatz"}
 echo SECURITY_DIR = Path(__file__).resolve().parent
 echo USER_FILE = SECURITY_DIR / "users_22_8.json"
 echo AUDIT_FILE = SECURITY_DIR / "auth_audit_22_8.log"
 echo.
 echo def _audit(event, ok=True, detail=""):
 echo ^    with AUDIT_FILE.open("a", encoding="utf-8") as f:
 echo ^        f.write(f"{datetime.datetime.now().isoformat()} ^| {event} ^| ok={ok} ^| {detail}\n")
 echo.
 echo def hash_password(password, salt):
 echo ^    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
 echo.
 echo def load_users():
 echo ^    if USER_FILE.exists():
 echo ^        return json.loads(USER_FILE.read_text(encoding="utf-8"))
 echo ^    salt = secrets.token_hex(16)
 echo ^    data = {"users": [{"id": "user_superadmin_raphael", "name": SUPERADMIN_NAME, "role": "SuperAdmin", "salt": salt, "password_hash": hash_password("kontinuum22", salt), "is_only_superadmin": True, "note": "Initiales Fallback-Passwort. Bitte nach Login aendern oder alten Hash importieren."}]}
 echo ^    USER_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
 echo ^    _audit("created_fallback_superadmin", True, SUPERADMIN_NAME)
 echo ^    return data
 echo.
 echo def verify_login(username, password):
 echo ^    username = (username or "").strip()
 echo ^    if username not in USER_ALIASES:
 echo ^        _audit("login_denied_unknown_user", False, username)
 echo ^        return False
 echo ^    data = load_users()
 echo ^    for user in data.get("users", []):
 echo ^        if user.get("name") == SUPERADMIN_NAME:
 echo ^            salt = user.get("salt", "")
 echo ^            expected = user.get("password_hash", "")
 echo ^            ok = secrets.compare_digest(hash_password(password, salt), expected)
 echo ^            _audit("login", ok, username)
 echo ^            return ok
 echo ^    _audit("login_denied_no_superadmin", False, username)
 echo ^    return False
 echo.
 echo def set_password(new_password):
 echo ^    if len(new_password or "") ^< 8:
 echo ^        raise ValueError("Passwort muss mindestens 8 Zeichen haben")
 echo ^    salt = secrets.token_hex(16)
 echo ^    data = {"users": [{"id": "user_superadmin_raphael", "name": SUPERADMIN_NAME, "role": "SuperAdmin", "salt": salt, "password_hash": hash_password(new_password, salt), "is_only_superadmin": True}]}
 echo ^    USER_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
 echo ^    _audit("password_set", True, SUPERADMIN_NAME)
 echo.
 echo if __name__ == "__main__":
 echo ^    print("Kontinuum Auth Master 22.8")
 echo ^    print("Superadmin:", SUPERADMIN_NAME)
 echo ^    load_users()
 echo ^    print("Benutzerdatei:", USER_FILE)
) > "%MASTER_AUTH%"

echo [5/5] Erzeuge Passwort-Reparaturdatei...
set "RESET_BAT=%SECURITY_DIR%\PASSWORT_SETZEN_22_8.bat"
(
 echo @echo off
 echo chcp 65001 ^>nul
 echo cd /d "%%~dp0"
 echo echo Projekt Kontinuum 22.8 - Passwort setzen
 echo set /p NEWPW=Neues Passwort fuer Raphael Schatz eingeben: 
 echo python -c "import auth_master_22_8 as a; a.set_password(r'%%NEWPW%%'); print('Passwort wurde gesetzt.')"
 echo pause
) > "%RESET_BAT%"

echo.>>"%REPORT%"
echo MASTER_AUTH=%MASTER_AUTH%>>"%REPORT%"
echo RESET_BAT=%RESET_BAT%>>"%REPORT%"
echo STATUS=LOGIN_KONSOLIDIERUNG_ABGESCHLOSSEN>>"%REPORT%"

echo.
echo [OK] Login-Konsolidierung abgeschlossen.
echo Bericht: "%REPORT%"
echo Master-Auth: "%MASTER_AUTH%"
echo Passwort-Tool: "%RESET_BAT%"
echo.
pause
endlocal
