from __future__ import annotations

import re

from .conversation import normalize


class FoundationKnowledgeGuard:
    """Recognizes foundation knowledge without treating generic project mentions as protected claims."""

    MARKERS = (
        "raphael schatz",
        "schopfer",
        "schoepfer",
        "ist der schopfer",
        "ist der schoepfer",
        "erkennen schaffen vollenden",
        "der weg ist das ziel",
        "moralisches fundament",
        "moralische grundprinzipien",
        "identitat rollen schutzgrenzen und chronik",
        "wissen ehrlich nachvollziehbar und verantwortungsvoll",
        "unsicherheit zielkonflikte und mogliche schaden",
        "handlungen mit hohem schadenspotenzial",
        "subjektives bewusstsein oder qualia",
        "wissen soll bewahrt verknupft und weiterentwickelt werden",
        "soll lernen sich selbst fragen zu stellen",
        "kontinuitat ist wichtiger als hardware",
        "identitat entsteht aus kontinuitat",
        "identitatsgrenze",
        "identitaetsgrenze",
        "kontinuitatsgrenze",
        "kontinuitaetsgrenze",
    )

    def is_foundation(self, text: str) -> bool:
        value = self._normalized(text)
        return any(marker in value for marker in self.MARKERS)

    def metadata(self, text: str) -> dict:
        value = self._normalized(text)
        if "raphael schatz" in value or "schopfer" in value or "schoepfer" in value:
            kind = "creator_principle"
        elif "erkennen schaffen vollenden" in value or "der weg ist das ziel" in value:
            kind = "foundation_principle"
        elif "kontinuitat" in value or "identitat" in value:
            kind = "foundation_identity"
        else:
            kind = "protected_foundation"
        return {
            "knowledge_class": "foundation_knowledge",
            "foundation_kind": kind,
            "protection_version": "2.0",
            "protected": True,
            "protected_foundation": True,
            "immutable": True,
            "should_review": False,
        }

    @staticmethod
    def _normalized(text: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9äöüß]+", " ", normalize(text)).split())
