@echo off
setlocal
title Projekt Kontinuum 33.0 Tests
for %%I in ("%~dp0..") do set "KONTINUUM_ROOT=%%~fI"
set "PYTHONPATH=%KONTINUUM_ROOT%\01_system"
set "PYTHON_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Signierte Python-Laufzeit nicht gefunden. Tests abgebrochen.
  exit /b 1
)

pushd "%KONTINUUM_ROOT%"
set "FAILED=0"
for %%F in ("17_tests\test_*.py") do (
  echo.
  echo === %%~nxF ===
  "%PYTHON_EXE%" "%%~fF"
  if errorlevel 1 set "FAILED=1"
)
popd

if "%FAILED%"=="1" (
  echo.
  echo Mindestens ein Test ist fehlgeschlagen.
  endlocal
  exit /b 1
)

echo.
echo Alle Kontinuum-Tests wurden erfolgreich ausgefuehrt.
endlocal
exit /b 0
