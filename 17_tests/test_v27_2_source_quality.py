from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.source_quality import SourceQualityClassifier


classifier = SourceQualityClassifier()
cases = [
    ("https://journal.example/paper", "Article", "Peer-reviewed journal article. DOI: 10.1/test", "peer_reviewed"),
    ("https://mit.edu/research", "MIT Research", "University research", "university"),
    ("https://agency.gov/report", "Report", "Official report", "government"),
    ("https://publisher.example/book", "Book", "ISBN 123 publisher edition", "book"),
    ("https://reuters.com/story", "News", "News report", "news"),
    ("https://reddit.com/r/test", "Forum", "Community discussion", "forum"),
    ("https://example.org/page", "Page", "General information", "unknown"),
]

for url, title, text, expected in cases:
    result = classifier.classify(url, title, text)
    assert result["class"] == expected
    assert 0 < result["weight"] <= 1

assert classifier.WEIGHTS["peer_reviewed"] > classifier.WEIGHTS["news"] > classifier.WEIGHTS["forum"]

print("Kontinuum 29.0 source quality classification tests passed")
