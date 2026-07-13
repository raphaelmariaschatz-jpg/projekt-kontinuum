# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from .conversation import normalize


class IdentityRouter:
    """Routes identity questions away from internet and research."""

    PHRASES = (
        "wer bin ich",
        "weisst du wer ich bin",
        "weißt du wer ich bin",
        "kennst du mich",
        "wer ist angemeldet",
        "welcher benutzer ist aktiv",
        "bin ich raphael",
        "wer ist dein schopfer",
        "wer ist dein schoepfer",
        "wer hat dich erschaffen",
    )

    def __init__(self, session_context, identity: dict):
        self.session_context = session_context
        self.identity = identity

    def answer(self, text: str) -> str | None:
        value = normalize(text)
        if not any(phrase in value for phrase in self.PHRASES):
            return None
        user = self.session_context.current()
        if any(phrase in value for phrase in ("wer ist dein schopfer", "wer ist dein schoepfer", "wer hat dich erschaffen")):
            return f"Mein Schöpfer gemäß geschütztem Identitätskern ist {self.identity.get('creator', 'Raphael Schatz')}."
        name = user.get("display_name") or "Raphael Schatz"
        role = user.get("role") or "SUPERADMIN"
        creator = "Du bist der Schöpfer von Projekt Kontinuum." if user.get("is_creator") else "Du bist als Benutzer dieser Sitzung angemeldet."
        return (
            f"Du bist {name}.\n"
            f"{creator}\n"
            f"Rolle: {role}.\n"
            "Diese lokale Information stammt aus Session Context, geschütztem Identitätskern, Creator Memory und Foundation Layer. "
            "Dafür wurde keine Internet-, arXiv-, Brave- oder DuckDuckGo-Suche gestartet."
        )
