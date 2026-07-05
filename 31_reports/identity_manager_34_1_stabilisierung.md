# IdentityManager 34.1 Stabilisierung

Datum: 2026-07-02

## Ergebnis

- `24_config/canonical_identity_34_1.json` wird beim Systemstart über `IdentityManager.to_legacy_identity()` geladen.
- Seit CIM 1.0 ist `24_config/canonical_identity.json` die kanonische Datei; `canonical_identity_34_1.json` bleibt als Legacy-Kompatibilitätsansicht erhalten.
- `preferred_address` wird in normalen Antworten verwendet; der Leerprompt antwortet mit `Ich bin bereit, <preferred_address>.`
- Bestehende Identitätsdaten werden vor Änderungen in `24_config/history/canonical_identity_history/` gesichert.
- Der Statusbefehl `identity status` ist aktiv.

## Statusausgabe

`identity status` zeigt:

- Creator
- bevorzugte Anrede
- Assistant-Name
- Short Name
- Speicherpfad
- letzter Änderungszeitpunkt

## Test

Regressionstest: `17_tests/test_identity_config_routing_34_1.py`

Geprüft:

- Laden einer bestehenden `canonical_identity_34_1.json`
- Verwendung einer abweichenden bevorzugten Anrede
- Statusbefehl `identity status`
- Backup vor Überschreiben
- Aktualisierung der kanonischen Identity-Datei
- Quellenfuß mit lokaler Datei und Memory
