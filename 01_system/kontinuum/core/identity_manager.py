# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from kontinuum.foundation.canonical_identity_manager import CanonicalIdentityManager, IdentityValidationError


IdentityManager = CanonicalIdentityManager

__all__ = ["CanonicalIdentityManager", "IdentityManager", "IdentityValidationError"]
