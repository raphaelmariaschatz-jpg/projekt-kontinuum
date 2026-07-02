@echo off
rem Kompatibilitaetseinstieg: der kanonische CLI-Start liegt ab 34.1 unter START_KONTINUUM_34_1.bat.
call "%~dp0START_KONTINUUM_34_1.bat" %*
exit /b %ERRORLEVEL%
