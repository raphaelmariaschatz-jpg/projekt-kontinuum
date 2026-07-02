# Isolierte Legacy-Tests

`legacy_kontinuum_23.py` ist ein historischer Live-Root-Integrationstest. Er
startet `KontinuumSystem` gegen die reale Projektwurzel und kann dadurch den
vollständigen historischen Meaning-Graphen neu aufbauen sowie Laufzeitdaten
verändern. Bei der Analyse am 21.06.2026 lag die lange Laufzeit bereits während
der Initialisierung in `MeaningCore.rebuild()` / `_ensure_edge()`.

Der Test ist deshalb bewusst vom aktiven Muster `17_tests/test_*.py` getrennt
und gehört nicht zur Release-Verifikation von Version 34.0. Er bleibt als
historischer Nachweis erhalten und darf nur manuell gegen eine vorbereitete
Kopie der damaligen Laufzeit und Daten ausgeführt werden.

`legacy_sourced_research_23.py` ist ein historischer lokaler HTTP-End-to-End-
Harness. Sein Seitenabruf kann abhängig vom Thread-Scheduling das alte
Zeitbudget überschreiten. Der aktuelle Suchmaschinen-Connector bleibt durch
`test_search_engine_connector_23.py` deterministisch abgedeckt. Auch dieser
Harness wird nur manuell als Kompatibilitätsprüfung ausgeführt.
