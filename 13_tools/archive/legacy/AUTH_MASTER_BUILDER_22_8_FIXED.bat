@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM Projekt Kontinuum 22.8 - Auth Master Builder - FIXED ASCII

title Projekt Kontinuum 22.8 Auth Master Builder

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
set "SECURITY_DIR=%RUNTIME%\security"
set "BACKUP_DIR=%RUNTIME%\_backup_before_auth_master"
set "REPORT=%RUNTIME%\AUTH_MASTER_22_8_REPORT.txt"

mkdir "%KONTINUUM_DIR%" 2>nul
mkdir "%SECURITY_DIR%" 2>nul
mkdir "%BACKUP_DIR%" 2>nul

echo Projekt Kontinuum 22.8 - AUTH MASTER BUILDER > "%REPORT%"
echo Erstellt am: %DATE% %TIME% >> "%REPORT%"
echo Runtime: %RUNTIME% >> "%REPORT%"
echo. >> "%REPORT%"

echo [INFO] Sichere vorhandene Auth- und Security-Dateien...
echo Backup vorhandener Auth- und Security-Dateien: >> "%REPORT%"

for /R "%RUNTIME%" %%F in (*auth*.py security.json users.json superadmin.json) do (
    echo %%F >> "%REPORT%"
    copy "%%F" "%BACKUP_DIR%\" >nul 2>nul
)

echo [INFO] Erstelle security\users.json ...
(
echo {
echo   "schema": "kontinuum.auth.users.v22_8",
echo   "users": [
echo     {
echo       "id": "user_superadmin_raphael_schatz",
echo       "username": "Raphael",
echo       "aliases": ["Raphael Schatz", "raphael", "raphael_schatz"],
echo       "full_name": "Raphael Schatz",
echo       "role": "SUPERADMIN",
echo       "is_superadmin": true,
echo       "creator": true,
echo       "principles": ["Erkennen - Schaffen - Vollenden", "Der Weg ist das Ziel"],
echo       "password_source": "set_with_PASSWORT_SETZEN_22_8"
echo     }
echo   ]
echo }
) > "%SECURITY_DIR%\users.json"

echo [INFO] Erstelle security\security_policy.json ...
(
echo {
echo   "schema": "kontinuum.security.policy.v22_8",
echo   "version": "22.8",
echo   "superadmin": "Raphael Schatz",
echo   "superadmin_username": "Raphael",
echo   "legacy_login_sources": ["version_6_3", "version_9", "version_22"],
echo   "password_rule": "No cleartext password. Use salted SHA256 hash.",
echo   "dangerous_commands": "require_confirmation",
echo   "audit_logging": true,
echo   "never_delete_legacy_without_backup": true
echo }
) > "%SECURITY_DIR%\security_policy.json"

echo [INFO] Erstelle kontinuum\auth_master.py ...
(
echo import hashlib
echo import json
echo import secrets
echo from pathlib import Path
echo.
echo VERSION = "22.8"
echo SUPERADMIN_NAME = "Raphael Schatz"
echo SUPERADMIN_USERNAME = "Raphael"
echo ROLE_SUPERADMIN = "SUPERADMIN"
echo.
echo BASE_DIR = Path(__file__^).resolve().parents[1]
echo SECURITY_DIR = BASE_DIR / "security"
echo USERS_FILE = SECURITY_DIR / "users.json"
echo.
echo def _sha256_salt(password: str, salt: str^) -^> str:
echo     return hashlib.sha256((salt + password^).encode("utf-8"^)^).hexdigest()
echo.
echo def _load_json(path: Path, default^):
echo     try:
echo         if path.exists():
echo             return json.loads(path.read_text(encoding="utf-8"^)^)
echo     except Exception:
echo         pass
echo     return default
echo.
echo def _write_json(path: Path, data^):
echo     path.parent.mkdir(parents=True, exist_ok=True^)
echo     path.write_text(json.dumps(data, ensure_ascii=False, indent=2^), encoding="utf-8"^)
echo.
echo def ensure_superadmin():
echo     data = _load_json(USERS_FILE, {"schema": "kontinuum.auth.users.v22_8", "users": []}^)
echo     users = data.setdefault("users", []^)
echo     found = None
echo     for u in users:
echo         names = [u.get("username", ""^), u.get("full_name", ""^)] + u.get("aliases", []^)
echo         if SUPERADMIN_USERNAME in names or SUPERADMIN_NAME in names:
echo             found = u
echo             break
echo     if not found:
echo         found = {}
echo         users.append(found^)
echo     found.update({"id": "user_superadmin_raphael_schatz", "username": SUPERADMIN_USERNAME, "aliases": ["Raphael Schatz", "raphael", "raphael_schatz"], "full_name": SUPERADMIN_NAME, "role": ROLE_SUPERADMIN, "is_superadmin": True, "creator": True, "version": VERSION}^)
echo     _write_json(USERS_FILE, data^)
echo     return found
echo.
echo def verify_login(username: str, password: str^) -^> bool:
echo     data = _load_json(USERS_FILE, {"users": []}^)
echo     for u in data.get("users", []^):
echo         names = [u.get("username", ""^), u.get("full_name", ""^)] + u.get("aliases", []^)
echo         if username in names:
echo             salt = u.get("salt"^) or u.get("password_salt"^)
echo             ph = u.get("password_hash"^)
echo             if salt and ph:
echo                 return secrets.compare_digest(_sha256_salt(password, salt^), ph^)
echo             return False
echo     return False
echo.
echo def create_or_reset_superadmin_password(password: str^):
echo     if len(password^) ^< 8:
echo         raise ValueError("Passwort muss mindestens 8 Zeichen haben."^)
echo     u = ensure_superadmin()
echo     salt = secrets.token_hex(16^)
echo     u["salt"] = salt
echo     u["password_hash"] = _sha256_salt(password, salt^)
echo     data = _load_json(USERS_FILE, {"users": []}^)
echo     replaced = False
echo     for i, existing in enumerate(data.get("users", []^)^):
echo         if existing.get("id"^) == u.get("id"^):
echo             data["users"][i] = u
echo             replaced = True
echo     if not replaced:
echo         data.setdefault("users", []^).append(u^)
echo     _write_json(USERS_FILE, data^)
echo     return True
echo.
echo if __name__ == "__main__":
echo     ensure_superadmin()
echo     print("Kontinuum Auth Master 22.8 bereit.")
echo     print("Superadmin:", SUPERADMIN_NAME)
) > "%KONTINUUM_DIR%\auth_master.py"

echo [INFO] Erstelle PASSWORT_SETZEN_22_8.bat ...
(
echo @echo off
echo setlocal
echo cd /d "%%~dp0"
echo echo.
echo echo Projekt Kontinuum 22.8 - Passwort setzen
echo echo Benutzer: Raphael / Raphael Schatz
echo echo.
echo set /p NEWPASS=Neues Passwort eingeben: 
echo python -c "from kontinuum.auth_master import create_or_reset_superadmin_password; create_or_reset_superadmin_password(r'%%NEWPASS%%'); print('Passwort fuer Raphael Schatz wurde gesetzt.')"
echo pause
) > "%RUNTIME%\PASSWORT_SETZEN_22_8.bat"

echo. >> "%REPORT%"
echo Ergebnis: >> "%REPORT%"
echo - auth_master.py erstellt >> "%REPORT%"
echo - users.json erstellt >> "%REPORT%"
echo - security_policy.json erstellt >> "%REPORT%"
echo - PASSWORT_SETZEN_22_8.bat erstellt >> "%REPORT%"

echo.
echo [OK] Auth Master 22.8 wurde erstellt.
echo [OK] Bericht: "%REPORT%"
echo.
echo Naechster Schritt:
echo PASSWORT_SETZEN_22_8.bat ausfuehren, falls Passwort gesetzt werden soll.
echo.
pause
exit /b 0
