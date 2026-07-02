@echo off
setlocal
title Projekt Kontinuum 32.4 - Oracle Cloud Einrichtung
set "OCI_EXE=C:\Program Files (x86)\Oracle\oci_cli\oci.exe"

if not exist "%OCI_EXE%" (
  echo OCI CLI wurde nicht unter dem erwarteten Pfad gefunden.
  exit /b 1
)

echo Die offizielle OCI CLI richtet Zugangsdaten ausserhalb des Projekts ein.
echo Private Schluessel und Geheimnisse duerfen nicht unter C:\Projekt Kontinuum gespeichert werden.
echo.
"%OCI_EXE%" setup config
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo Oracle-Cloud-Einrichtung wurde nicht erfolgreich abgeschlossen.
  exit /b %EXIT_CODE%
)

echo.
echo OCI-Profil wurde eingerichtet.
echo Trage nun Region, Compartment-OCID und Tenancy-OCID in
echo 24_config\oracle_cloud.json ein und pruefe danach mit oraclestatus.
endlocal
exit /b 0
