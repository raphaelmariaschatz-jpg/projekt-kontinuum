"""Compatibility path for integrations that still import Foundation 2.1.

Foundation 2.2 is the active implementation. This module intentionally
re-exports its public API so older callers keep working without maintaining
a second Foundation rule set.
"""

from .foundation_2_2 import (
    FOUNDATION_2_2_RULES,
    FoundationAPI,
    FoundationMigrationManager,
    FoundationRegistry,
    FoundationRule,
    FoundationRuleEngine,
    FoundationStatusCenter,
    ImprovementFoundation,
)

FOUNDATION_2_1_RULES = FOUNDATION_2_2_RULES

__all__ = [
    "FOUNDATION_2_1_RULES",
    "FoundationAPI",
    "FoundationMigrationManager",
    "FoundationRegistry",
    "FoundationRule",
    "FoundationRuleEngine",
    "FoundationStatusCenter",
    "ImprovementFoundation",
]
