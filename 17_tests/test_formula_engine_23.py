from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.tools.formula_engine import FormulaEngine
from kontinuum.core.system import KontinuumSystem


engine = FormulaEngine()
assert engine.calculate("2 + 3 * 4") == 14
assert engine.calculate("sqrt(81)") == 9
assert engine.format_math("a^2 + b^2") == "a² + b²"
assert engine.format_chemical("H2SO4") == "H₂SO₄"
assert engine.format_chemical("Ca(OH)2") == "Ca(OH)₂"
assert engine.format_chemical("SO4^2-") == "SO₄²⁻"
assert engine.format_reaction("2 H2 + O2 -> 2 H2O") == "2 H₂ + O₂ → 2 H₂O"
assert engine.parse_chemical_formula("Ca(OH)2") == {"Ca": 1, "O": 2, "H": 2}
try:
    engine.calculate("__import__('os').system('echo unsicher')")
    raise AssertionError("Unsichere Mathematikauswertung wurde nicht blockiert.")
except ValueError:
    pass

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config"
    config.mkdir()
    (config / "continuous_learning.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    (config / "search_engine.json").write_text(json.dumps({"enabled": False}), encoding="utf-8")
    system = KontinuumSystem(root)
    try:
        assert "Formel-Engine aktiv" in system.ask("formelstatus")
        assert "14" in system.ask("berechne 2 + 3 * 4")
        assert "9" in system.ask("berechne sqrt(81)")
        assert "Natriumchlorid" in system.ask("lies die Formel NaCl")
        assert "C₆H₅OH" in system.ask("Phenol")
        assert "C₆H₆" in system.ask("Benzol")
        assert "C₂H₅OH" in system.ask("Ethanol")
        assert "CH₃OH" in system.ask("Methanol")
        assert "C₃H₆O" in system.ask("Aceton")
        assert "CH₃COOH" in system.ask("Essigsäure")
        assert "NaCl" in system.ask("Natriumchlorid")
        assert "H₂SO₄" in system.ask("Schwefelsäure")
        assert "H₂O" in system.ask("Wasser")
        assert "O₂" in system.ask("Sauerstoff")
        assert "Masse-Energie-Äquivalenz" in system.ask("Einstein")
        assert "Ethanol" in system.ask("welcher Stoff ist C2H5OH?")
        assert "Ethanol" in system.ask("lies die organische Halbstrukturformel CH3-CH2-OH")
        assert "Ca(OH)₂" in system.ask("lies die Formel Ca(OH)2")
        assert "2 H₂ + O₂ → 2 H₂O" in system.ask("formatiere die Reaktionsgleichung 2 H2 + O2 -> 2 H2O")
        assert "Ohmsches Gesetz" in system.ask("zeige die Formel des Ohmschen Gesetzes")
        assert "Masse-Energie-Äquivalenz" in system.ask("Was bedeutet E=mc²?")
        assert "a² + b² = c²" in system.ask("Wie lautet der Satz des Pythagoras?")
        assert "drei binomischen Formeln" in system.ask("Wie lauten die binomischen Formeln?")
    finally:
        system.close()

print("Kontinuum formula engine tests passed")
