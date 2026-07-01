# Projekt Kontinuum 23.0 – Agents & Tools Core

Dieses Paket füllt die bisher leeren Ordner:

```text
12_agents
13_tools
```

Zusätzlich enthält es eine Python-kompatible Runtime-Spiegelung:

```text
01_system\kontinuum\agents
01_system\kontinuum\tools
```

Grund: Python-Pakete dürfen nicht mit Zahlen beginnen. Die Architekturordner bleiben erhalten, aber der ausführbare Code liegt zusätzlich sauber unter `01_system\kontinuum`.

## Enthaltene Agenten

- DialogueAgent
- ResearchAgent
- LearningAgent
- AutonomousLearningAgent
- InternetStatusAgent
- SystemMonitorAgent
- MemoryAgent
- KnowledgeAgent
- PlannerAgent
- ReflectionAgent

## Enthaltene Tools

- PathTools
- JsonTools
- FileTools
- SearchTools
- WebTools
- BackupTools
- ImportTools
- ExportTools

## Test

```text
python 17_tests\test_runtime_agents_tools_23.py
```

## Wichtig für Vollversion 23.0

Dieses Paket ist ein Grundkern. Beim finalen Build wird es mit `storage.py`, `system.py`, `search_router.py`, `auth_master_23.py` und der neuen GUI verbunden.
