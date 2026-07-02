@echo off
setlocal
title Projekt Kontinuum 34.1 Vollverifikation
call "%~dp0RELEASE_GATE_34_1.bat" %*
exit /b %ERRORLEVEL%
