from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core import foundation_2_1, foundation_2_2


assert foundation_2_1.FoundationRegistry is foundation_2_2.FoundationRegistry
assert foundation_2_1.FoundationAPI is foundation_2_2.FoundationAPI
assert foundation_2_1.FoundationStatusCenter is foundation_2_2.FoundationStatusCenter
assert foundation_2_1.FoundationMigrationManager is foundation_2_2.FoundationMigrationManager
assert foundation_2_1.FOUNDATION_2_1_RULES is foundation_2_2.FOUNDATION_2_2_RULES
assert foundation_2_1.FoundationRegistry.VERSION == "2.2"
assert foundation_2_1.FoundationMigrationManager.COMPATIBILITY_MIGRATION_ID == "foundation-2.1-fnd-id-048"

print("Kontinuum Foundation 2.1 compatibility path tests passed")
