# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from urllib.parse import urlparse


class SourceQualityClassifier:
    CLASSES = ("peer_reviewed", "university", "government", "book", "news", "forum", "unknown")
    WEIGHTS = {
        "peer_reviewed": 1.0,
        "university": 0.9,
        "government": 0.88,
        "book": 0.78,
        "news": 0.58,
        "forum": 0.28,
        "unknown": 0.4,
    }
    TRUST_CLASSES = {
        "A": {
            "label": "Universitaeten, wissenschaftliche Publikationen, Behoerden, offizielle Dokumentationen",
            "source_classes": ("peer_reviewed", "university", "government"),
        },
        "B": {
            "label": "Fachbuecher, Fachorganisationen, technische Standards",
            "source_classes": ("book",),
        },
        "C": {
            "label": "Etablierte Fachportale, Wikipedia, serioese Nachrichtenquellen",
            "source_classes": ("news",),
        },
        "D": {
            "label": "Foren, Communitys, Reddit",
            "source_classes": ("forum",),
        },
        "E": {
            "label": "Social Media oder unbekannte Quellen",
            "source_classes": ("unknown",),
        },
    }
    CLASS_TO_TRUST = {
        "peer_reviewed": "A",
        "university": "A",
        "government": "A",
        "book": "B",
        "news": "C",
        "forum": "D",
        "unknown": "E",
    }

    def classify(self, url: str, title: str = "", text: str = "") -> dict:
        domain = urlparse(url or "").netloc.casefold().removeprefix("www.")
        combined = f"{title} {text[:6000]}".casefold()
        source_class, reason = self._class(domain, combined)
        trust_class = self.CLASS_TO_TRUST.get(source_class, "E")
        return {
            "class": source_class,
            "trust_class": trust_class,
            "trust_label": self.TRUST_CLASSES[trust_class]["label"],
            "weight": self.WEIGHTS[source_class],
            "domain": domain,
            "reason": reason,
        }

    @staticmethod
    def _class(domain: str, combined: str) -> tuple[str, str]:
        if any(marker in combined for marker in ("doi:", "peer reviewed", "peer-reviewed", "journal article", "abstract")):
            return "peer_reviewed", "Publikations- oder Peer-Review-Marker erkannt."
        if domain.endswith(".edu") or ".ac." in domain or "universit" in domain:
            return "university", "Universitätsdomain oder Hochschulmarker erkannt."
        if domain.endswith(".gov") or domain.endswith(".gov.uk") or domain.endswith(".bund.de") or domain.endswith(".europa.eu"):
            return "government", "Behördliche Domain erkannt."
        if any(marker in combined for marker in ("isbn", "ebook", "buch", "book edition", "publisher")):
            return "book", "Buch- oder Verlagsmarker erkannt."
        if any(marker in domain for marker in ("reuters.", "apnews.", "bbc.", "zeit.", "spiegel.", "tagesschau.")) or any(
            marker in combined for marker in ("nachrichten", "news report", "breaking news")
        ):
            return "news", "Nachrichtenquelle erkannt."
        if any(marker in domain for marker in ("reddit.", "quora.", "stackexchange.", "stackoverflow.", "forum.")) or "forum" in combined:
            return "forum", "Forum- oder Communityquelle erkannt."
        return "unknown", "Keine belastbare Quellenklasse erkannt."
