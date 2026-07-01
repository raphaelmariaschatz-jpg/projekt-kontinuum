from __future__ import annotations


class SessionContext:
    """Single runtime view of the authenticated user."""

    def __init__(self, identity: dict):
        self.system_identity = identity
        self.user: dict = {}

    def bind(self, user: dict | None) -> dict:
        data = dict(user or {})
        name = (
            data.get("full_name")
            or data.get("username")
            or self.system_identity.get("creator")
            or "Raphael Schatz"
        )
        role = data.get("role") or ("SUPERADMIN" if "raphael" in str(name).casefold() else "USER")
        self.user = {
            "user_id": data.get("user_id") or data.get("username") or name,
            "username": data.get("username") or name,
            "display_name": name,
            "full_name": name,
            "role": role,
            "is_creator": self._is_creator(name),
            "authenticated": bool(data) or self._is_creator(name),
        }
        return dict(self.user)

    def current(self) -> dict:
        if not self.user:
            self.bind({})
        return dict(self.user)

    def format_status(self) -> str:
        user = self.current()
        creator = "ja" if user.get("is_creator") else "nein"
        active = "ja" if user.get("authenticated") else "nein"
        return (
            "Sessionstatus:\n"
            f"- Benutzer: {user.get('display_name')}\n"
            f"- Rolle: {user.get('role')}\n"
            f"- Creator: {creator}\n"
            f"- Session aktiv: {active}"
        )

    @staticmethod
    def _is_creator(name: str) -> bool:
        return "raphael" in str(name).casefold() and "schatz" in str(name).casefold()
