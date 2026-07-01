# Codex-Integration in Kontinuum 23.0

Stand: 2026-06-10

Kontinuum besitzt einen eigenen `CodexAgent` und ein kontrolliertes
`CodexTools`-Gateway.

## Befehle

```text
codexstatus
codex: Prüfe die Python-Dateien auf Syntaxfehler
```

## Sicherheit

- Standardmodus: `read-only`
- Prompts und Codex-Antworten werden nicht dauerhaft gespeichert.
- Codex läuft als separater Prozess im Projektwurzelverzeichnis.
- Eine Schreibfreigabe muss bewusst über `KONTINUUM_CODEX_SANDBOX` gesetzt werden.

## Aktive CLI

```text
C:\Projekt Kontinuum\13_tools\codex_cli\codex.exe
```

Die integrierte CLI wird automatisch erkannt. Für eine andere CLI-Version kann
optional `KONTINUUM_CODEX_COMMAND` gesetzt werden.

Statusprüfung:

```text
16_installation\START_KONTINUUM_23.bat codexstatus
```
