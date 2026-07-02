# Installation und Start 34.1

## Kanonischer CLI-Start

Der kanonische CLI-Start liegt im Projektstamm:

```text
START_KONTINUUM.bat <Befehl>
```

Die Startdatei setzt `PYTHONPATH` automatisch auf
`C:\Projekt Kontinuum\01_system` und startet Kontinuum ueber:

```text
python -m kontinuum
```

Starts ueber `main.py` oder `python -m 01_system.kontinuum` sind veraltet.

## GUI und Gates

```text
16_installation\START_GUI.bat
16_installation\START_GUI_34_1.bat
16_installation\RELEASE_GATE_34_1.bat
16_installation\TEST_KONTINUUM_34_1.bat
```

Das Release-Gate prueft den Root-Starter als Pflichtpfad und validiert, dass er
den kanonischen Paketstart verwendet.

## Internet-Learning

Internet-Learning ist kanonisch standardmaessig aktiviert:

```text
24_config\internet_learning_policy_34_1.json
enabled=true
continuous_internet_learning_enabled=true
```

Der Dienst startet beim Systemstart automatisch. Deaktivierung ist ueber GUI
oder Konfiguration moeglich. Queue, Review, Provenienzpflicht, IKG 1.0 und das
10-Prozent-Bandbreitenlimit bleiben unveraendert verbindlich.
