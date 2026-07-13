# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

"""Core runtime for Projekt Kontinuum."""

__all__ = ["KontinuumSystem"]


def __getattr__(name: str):
    if name == "KontinuumSystem":
        from .system import KontinuumSystem

        return KontinuumSystem
    raise AttributeError(name)
