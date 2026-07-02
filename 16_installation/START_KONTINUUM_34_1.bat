@echo off
setlocal
title Projekt Kontinuum 34.1 CLI
for %%I in ("%~dp0..") do set "KONTINUUM_ROOT=%%~fI"
set "PYTHONPATH=%KONTINUUM_ROOT%\01_system"
set "PYTHON_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Signierte Python-Laufzeit nicht gefunden. Start abgebrochen.
  exit /b 1
)
pushd "%KONTINUUM_ROOT%"
"%PYTHON_EXE%" -m kontinuum %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
endlocal & exit /b %EXIT_CODE%
