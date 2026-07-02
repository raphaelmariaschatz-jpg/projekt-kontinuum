from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.meta_learning import MetaLearningEngine


engine = MetaLearningEngine()
task = {
    "subject": "Chemie",
    "topics": ["Atombau", "Bindungen"],
    "metadata": {"cycles": 0, "successful_applications": 0},
}
assessment = engine.assess(task, [])
assert assessment.phase_name == "Bewusste Inkompetenz"
assert "Atombau" in assessment.open_gaps

references = [
    {"metadata": {"area": "04_knowledge", "topics": ["Atombau", "Bindungen"]}},
    {"metadata": {"area": "06_learning", "topics": ["Atombau", "Bindungen"]}},
    {"metadata": {"area": "03_memory", "topics": ["Atombau", "Bindungen"]}},
]
task["metadata"]["cycles"] = 2
assessment = engine.assess(task, references)
assert assessment.phase_name == "Bewusste Kompetenz"

task["metadata"]["successful_applications"] = 3
assessment = engine.assess(task, references)
assert assessment.phase_name == "Unbewusste Kompetenz"

task["metadata"]["last_application_successful"] = False
assessment = engine.assess(task, references)
assert assessment.phase_name == "Bewusste Inkompetenz"

assert not engine.is_valid_subject("Https://www")
assert engine.is_valid_subject("Chemie")
print("Kontinuum 23.0 meta learning tests passed")
