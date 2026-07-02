@echo off
setlocal
title Projekt Kontinuum 34.1 Release Integrity Gate
for %%I in ("%~dp0..") do set "KONTINUUM_ROOT=%%~fI"
set "PYTHONPATH=%KONTINUUM_ROOT%\01_system"
set "PYTHON_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Signierte Python-Laufzeit nicht gefunden. Release-Gate abgebrochen.
  exit /b 1
)
pushd "%KONTINUUM_ROOT%"
"%PYTHON_EXE%" "13_tools\release_integrity_34_1.py" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
endlocal & exit /b %EXIT_CODE%
