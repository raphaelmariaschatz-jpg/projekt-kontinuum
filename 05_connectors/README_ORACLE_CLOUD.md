# Oracle Cloud Connector

Kontinuum bindet Oracle Cloud Infrastructure über die offizielle OCI CLI an.

## Einrichtung

1. In OCI einen eigenen Benutzer oder eine eigene Gruppe mit minimalen
   Berechtigungen für Kontinuum anlegen.
2. OCI CLI konfigurieren. Zugangsdaten und private Schlüssel bleiben außerhalb
   des Projektordners, standardmäßig unter `%USERPROFILE%\.oci`.
3. In `24_config\oracle_cloud.json` ausschließlich Region, Compartment-OCID und
   Tenancy-OCID eintragen.
4. Mit `oraclestatus`, `oracle instanzen`, `oracle speicher` und
   `oracle limits` prüfen.

Schreibende Aktionen sind standardmäßig gesperrt. Kontinuum erstellt keine
Cloud-Ressourcen automatisch und garantiert nicht, dass eine Ressource vom
Oracle-Free-Tier abgedeckt ist.

Vor jeder potenziell kostenverursachenden Aktion verlangt Kontinuum eine
ausdrückliche Bestätigung und die erneute maskierte Eingabe des
Superadmin-Passworts. Die Freigabe gilt genau einmal. Das Passwort wird nur
lokal geprüft, nicht gespeichert und nicht an Oracle übertragen.
