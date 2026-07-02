@echo off
rem Kompatibilitaetseinstieg: der kanonische Teststart liegt ab 34.1 unter TEST_KONTINUUM_34_1.bat.
call "%~dp0TEST_KONTINUUM_34_1.bat" %*
exit /b %ERRORLEVEL%
