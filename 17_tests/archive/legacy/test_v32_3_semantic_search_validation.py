from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.semantic_result_validator import SemanticResultValidator
from kontinuum.version import APP_VERSION


validator = SemanticResultValidator()
accepted = validator.validate(
    "Kontinuum Identität Kontinuität",
    {
        "title": "Kontinuum Identität und Kontinuität",
        "snippet": "Kontinuität, Identität und Chronik bilden die Projektgrundlage.",
        "provider": "brave_search",
    },
    threshold=0.65,
)
rejected = validator.validate(
    "Kontinuum Identität Kontinuität",
    {
        "title": "Arxiv paper about galaxy clusters",
        "snippet": "This article discusses astrophysical redshift measurements.",
        "provider": "arxiv",
    },
    threshold=0.65,
)
learning = validator.validate(
    "lerne Quantenmechanik Hamiltonoperator",
    {
        "title": "Quantenmechanik Hamiltonoperator Grundlagen",
        "snippet": "Hamiltonoperator, Zustände und Quantenmechanik.",
        "provider": "semantic_scholar",
    },
    threshold=0.75,
)

assert accepted["ok"] is True
assert rejected["ok"] is False
assert learning["ok"] is True

print(f"Kontinuum {APP_VERSION} semantic search validation tests passed")
