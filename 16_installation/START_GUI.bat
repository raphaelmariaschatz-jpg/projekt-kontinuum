@echo off
setlocal
title Projekt Kontinuum GUI
for %%I in ("%~dp0..") do set "KONTINUUM_ROOT=%%~fI"
set "PYTHONPATH=%KONTINUUM_ROOT%\01_system"
set "PYTHON_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Signierte Python-Laufzeit nicht gefunden. Start abgebrochen.
  pause
  exit /b 1
)
pushd "%KONTINUUM_ROOT%"
"%PYTHON_EXE%" "11_gui\desktop_gui.py"
set "EXIT_CODE=%ERRORLEVEL%"
popd
pause
endlocal & exit /b %EXIT_CODE%
