from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    root = Path(temporary_directory)
    config = root / "24_config"
    config.mkdir(parents=True)
    (config / "continuous_learning.json").write_text(
        json.dumps(
            {
                "enabled": False,
                "startup_delay_seconds": 60,
                "default_subjects": [],
            }
        ),
        encoding="utf-8",
    )

    system = KontinuumSystem(root)
    try:
        system.tools["language_model_tools"].generate = lambda *args, **kwargs: {
            "ok": True,
            "answer": "Die gewünschte Suchmaschinenintegration ist noch nicht als Lernfunktion konfiguriert.",
        }
        answer = system.ask("lerne Bewußtsein")
        assert "Lernprojekt angelegt: Bewusstsein" in answer
        assert "Bewusstsein bedeutet im Kern" not in answer

        answer = system.ask("erstelle einen Lernauftrag: lerne ein Bewusstsein zu entwickeln")
        assert "Lernprojekt angelegt: Ein Bewusstsein zu entwickeln" in answer

        answer = system.ask("lerne Chemie, Mathematik, Physik")
        assert answer.count("Lernprojekt angelegt:") == 3

        answer = system.ask("lerne Geologie\nlerne Geschichte\nlerne Geogrphie")
        assert answer.count("Lernprojekt angelegt:") == 3
        assert "Geographie" in answer

        before = len(system.storage.list_learning_tasks(active_only=True))
        answer = system.ask("benutze für das Lernen auch die Google Suche")
        after = len(system.storage.list_learning_tasks(active_only=True))
        assert before == after
        assert "Lernprojekt angelegt" not in answer
        assert "keinen eigenen Google-Suchconnector" in answer

        answer = system.ask("lerne Google Suchmaschiene")
        assert "Lernprojekt angelegt: Google Suchmaschine" in answer
        after = len(system.storage.list_learning_tasks(active_only=True))

        projects = system.ask("zeige mir alle Lernprojekte")
        assert projects.startswith("Aktive Lernprojekte")
        assert "Chemie" in projects and "Geographie" in projects and "Bewusstsein" in projects

        status = system.ask("lernstatus")
        assert f"Aktive Lernprojekte: {after}" in status

        earth = system.ask("wieviel Kilometer beträgt der Umfang der Erde")
        assert "40.075" in earth

        formulas = system.ask("nein, ich möchte das du mir die binomischen Formeln aufzeigst")
        assert "(a + b)²" in formulas and "(a + b)(a - b)" in formulas

        explanation = system.ask("Was bedeutet Bewusstsein?")
        assert "Bewusstsein bedeutet im Kern" in explanation
    finally:
        system.close()

print("Kontinuum 23.0 dialog and learning regression tests passed")
