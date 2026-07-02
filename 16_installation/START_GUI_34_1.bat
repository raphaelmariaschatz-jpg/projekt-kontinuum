@echo off
rem Kompatibilitaetseinstieg 34.1: kanonischer Start ist START_GUI.bat.
call "%~dp0START_GUI.bat" %*
exit /b %ERRORLEVEL%
