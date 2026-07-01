from __future__ import annotations

import ast
import math
import operator
import re
from collections import Counter


class FormulaEngine:
    SUBSCRIPT = str.maketrans("0123456789+-()", "₀₁₂₃₄₅₆₇₈₉₊₋₍₎")
    SUPERSCRIPT = str.maketrans("0123456789+-()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾")
    ELEMENTS = {
        "H": "Wasserstoff", "He": "Helium", "Li": "Lithium", "Be": "Beryllium", "B": "Bor",
        "C": "Kohlenstoff", "N": "Stickstoff", "O": "Sauerstoff", "F": "Fluor", "Ne": "Neon",
        "Na": "Natrium", "Mg": "Magnesium", "Al": "Aluminium", "Si": "Silicium", "P": "Phosphor",
        "S": "Schwefel", "Cl": "Chlor", "Ar": "Argon", "K": "Kalium", "Ca": "Calcium",
        "Fe": "Eisen", "Cu": "Kupfer", "Zn": "Zink", "Ag": "Silber", "Au": "Gold", "Hg": "Quecksilber",
        "Pb": "Blei", "Sn": "Zinn", "Br": "Brom", "I": "Iod", "Mn": "Mangan", "Cr": "Chrom",
        "Co": "Cobalt", "Ni": "Nickel", "Pt": "Platin", "U": "Uran", "Ba": "Barium",
        "Sc": "Scandium", "Ti": "Titan", "V": "Vanadium", "Ga": "Gallium", "Ge": "Germanium",
        "As": "Arsen", "Se": "Selen", "Kr": "Krypton", "Rb": "Rubidium", "Sr": "Strontium",
        "Y": "Yttrium", "Zr": "Zirconium", "Nb": "Niob", "Mo": "Molybdän", "Tc": "Technetium",
        "Ru": "Ruthenium", "Rh": "Rhodium", "Pd": "Palladium", "Cd": "Cadmium", "In": "Indium",
        "Sb": "Antimon", "Te": "Tellur", "Xe": "Xenon", "Cs": "Cäsium", "La": "Lanthan",
        "Ce": "Cer", "Pr": "Praseodym", "Nd": "Neodym", "Pm": "Promethium", "Sm": "Samarium",
        "Eu": "Europium", "Gd": "Gadolinium", "Tb": "Terbium", "Dy": "Dysprosium", "Ho": "Holmium",
        "Er": "Erbium", "Tm": "Thulium", "Yb": "Ytterbium", "Lu": "Lutetium", "Hf": "Hafnium",
        "Ta": "Tantal", "W": "Wolfram", "Re": "Rhenium", "Os": "Osmium", "Ir": "Iridium",
        "Tl": "Thallium", "Bi": "Bismut", "Po": "Polonium", "At": "Astat", "Rn": "Radon",
        "Fr": "Francium", "Ra": "Radium", "Ac": "Actinium", "Th": "Thorium", "Pa": "Protactinium",
        "Np": "Neptunium", "Pu": "Plutonium", "Am": "Americium", "Cm": "Curium", "Bk": "Berkelium",
        "Cf": "Californium", "Es": "Einsteinium", "Fm": "Fermium", "Md": "Mendelevium", "No": "Nobelium",
        "Lr": "Lawrencium", "Rf": "Rutherfordium", "Db": "Dubnium", "Sg": "Seaborgium", "Bh": "Bohrium",
        "Hs": "Hassium", "Mt": "Meitnerium", "Ds": "Darmstadtium", "Rg": "Röntgenium", "Cn": "Copernicium",
        "Nh": "Nihonium", "Fl": "Flerovium", "Mc": "Moscovium", "Lv": "Livermorium",
        "Ts": "Tenness", "Og": "Oganesson",
    }
    CHEMICALS = {
        "H2O": ("Wasser", "anorganisch"),
        "CO2": ("Kohlenstoffdioxid", "anorganisch"),
        "CO": ("Kohlenstoffmonoxid", "anorganisch"),
        "O2": ("Sauerstoff", "anorganisch"),
        "N2": ("Stickstoff", "anorganisch"),
        "NH3": ("Ammoniak", "anorganisch"),
        "HCl": ("Chlorwasserstoff", "anorganisch"),
        "H2SO4": ("Schwefelsäure", "anorganisch"),
        "HNO3": ("Salpetersäure", "anorganisch"),
        "NaCl": ("Natriumchlorid", "anorganisch"),
        "NaOH": ("Natriumhydroxid", "anorganisch"),
        "CaCO3": ("Calciumcarbonat", "anorganisch"),
        "CH4": ("Methan", "organisch"),
        "C2H6": ("Ethan", "organisch"),
        "C2H4": ("Ethen", "organisch"),
        "C2H2": ("Ethin", "organisch"),
        "C2H5OH": ("Ethanol", "organisch"),
        "CH3CH2OH": ("Ethanol, Halbstrukturformel", "organisch"),
        "CH3OH": ("Methanol", "organisch"),
        "CH3COOH": ("Ethansäure (Essigsäure)", "organisch"),
        "CH3COCH3": ("Propanon (Aceton)", "organisch"),
        "C3H6O": ("Propanon (Aceton)", "organisch"),
        "C6H6": ("Benzol", "organisch"),
        "C6H5OH": ("Phenol", "organisch"),
        "C6H12O6": ("Glucose", "organisch"),
        "C12H22O11": ("Saccharose", "organisch"),
    }
    PHYSICS = {
        "f=m*a": ("Newtons zweites Gesetz", "F = m · a", "Kraft = Masse · Beschleunigung", "N = kg · m/s²"),
        "e=m*c^2": ("Masse-Energie-Äquivalenz", "E = m · c²", "Energie = Masse · Lichtgeschwindigkeit²", "J"),
        "u=r*i": ("Ohmsches Gesetz", "U = R · I", "Spannung = Widerstand · Stromstärke", "V = Ω · A"),
        "p=u*i": ("Elektrische Leistung", "P = U · I", "Leistung = Spannung · Stromstärke", "W = V · A"),
        "p=w/t": ("Leistung", "P = W / t", "Leistung = Arbeit / Zeit", "W = J/s"),
        "v=s/t": ("Geschwindigkeit", "v = s / t", "Geschwindigkeit = Weg / Zeit", "m/s"),
        "a=dv/dt": ("Beschleunigung", "a = Δv / Δt", "Beschleunigung = Geschwindigkeitsänderung / Zeitänderung", "m/s²"),
        "f=-k*x": ("Hookesches Gesetz", "F = -k · x", "Rückstellkraft = -Federkonstante · Auslenkung", "N"),
        "e=h*f": ("Photonenenergie", "E = h · f", "Energie = Planck-Konstante · Frequenz", "J"),
        "p=rho*g*h": ("Hydrostatischer Druck", "p = ρ · g · h", "Druck = Dichte · Fallbeschleunigung · Höhe", "Pa"),
    }
    MATH_FORMULAS = {
        "binom": (
            "Die drei binomischen Formeln:\n"
            "1. (a + b)² = a² + 2ab + b²\n"
            "2. (a - b)² = a² - 2ab + b²\n"
            "3. (a + b)(a - b) = a² - b²"
        ),
        "quadratisch": "Mitternachtsformel: x₁,₂ = (-b ± √(b² - 4ac)) / (2a).",
        "pythagoras": "Satz des Pythagoras: a² + b² = c².",
        "kreis": "Kreis: Umfang U = 2πr; Fläche A = πr².",
    }

    BINARY = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    }
    UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    FUNCTIONS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log10, "ln": math.log}
    CONSTANTS = {"pi": math.pi, "e": math.e}

    def status(self) -> str:
        return (
            "Formel-Engine aktiv: sichere Mathematikberechnung, physikalische Formeln und Einheiten, "
            "anorganische und organische Summen-/Halbstrukturformeln mit Unicode-Indizes."
        )

    def answer(self, prompt: str) -> str | None:
        text = (prompt or "").strip()
        lower = text.casefold()
        if lower in {"formelstatus", "formelnstatus"}:
            return self.status()
        if "binom" in lower:
            return self.MATH_FORMULAS["binom"]
        if "pythagoras" in lower:
            return self.MATH_FORMULAS["pythagoras"]
        if "mitternachtsformel" in lower or "quadratische formel" in lower:
            return self.MATH_FORMULAS["quadratisch"]
        if "kreisformel" in lower or ("formel" in lower and "kreis" in lower):
            return self.MATH_FORMULAS["kreis"]
        if "->" in text or "→" in text or "reaktionsgleichung" in lower:
            reaction = self.format_reaction(text)
            if reaction:
                return f"Chemische Reaktionsgleichung:\n{reaction}"

        expression = self._extract_math_expression(text)
        if expression:
            try:
                value = self.calculate(expression)
                return f"{self.format_math(expression)} = {self._format_number(value)}"
            except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
                pass

        physics = self._physics_answer(text)
        if physics:
            return physics
        chemical = self._chemical_answer(text)
        if chemical:
            return chemical
        return None

    def calculate(self, expression: str) -> float:
        normalized = (
            expression.strip().rstrip("?.!").replace("×", "*").replace("·", "*").replace("÷", "/")
            .replace("^", "**").replace("²", "**2").replace("³", "**3").replace(",", ".").replace("√", "sqrt")
        )
        normalized = re.sub(r"(?i)\bwurzel\s*\(", "sqrt(", normalized)
        normalized = re.sub(r"(?i)\bwurzel\s+(\d+(?:\.\d+)?)", r"sqrt(\1)", normalized)
        normalized = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", normalized)
        normalized = re.sub(r"(?<=\d)\s*[xX]\s*(?=\d)", "*", normalized)
        node = ast.parse(normalized, mode="eval")
        return float(self._eval_node(node.body))

    def _eval_node(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in self.BINARY:
            return self.BINARY[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in self.UNARY:
            return self.UNARY[type(node.op)](self._eval_node(node.operand))
        if isinstance(node, ast.Name) and node.id in self.CONSTANTS:
            return self.CONSTANTS[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in self.FUNCTIONS and len(node.args) == 1:
            return self.FUNCTIONS[node.func.id](self._eval_node(node.args[0]))
        raise ValueError("Nicht erlaubter mathematischer Ausdruck.")

    def _physics_answer(self, text: str) -> str | None:
        lower = text.casefold()
        aliases = {
            "newton": "f=m*a", "kraft": "f=m*a", "masse-energie": "e=m*c^2",
            "einstein": "e=m*c^2", "ohm": "u=r*i", "elektrische leistung": "p=u*i",
            "geschwindigkeit": "v=s/t", "beschleunigung": "a=dv/dt", "hook": "f=-k*x",
            "photonenenergie": "e=h*f", "hydrostatisch": "p=rho*g*h",
        }
        key = next((value for alias, value in aliases.items() if alias in lower), None)
        compact = re.sub(r"\s+", "", lower.replace("·", "*").replace("×", "*").replace("²", "^2"))
        compact = compact.strip(".,;:!?")
        equation = re.search(r"[a-z]=[a-z0-9*^/+\-]+", compact)
        compact = equation.group(0) if equation else compact
        compact_aliases = {"e=mc^2": "e=m*c^2", "f=ma": "f=m*a", "ui=ri": "u=r*i"}
        key = key or compact_aliases.get(compact)
        key = key or next((candidate for candidate in self.PHYSICS if candidate in compact), None)
        if not key:
            return None
        name, formula, reading, unit = self.PHYSICS[key]
        return f"{name}:\nFormel: {formula}\nGelesen: {reading}\nEinheit/Zusammenhang: {unit}"

    def _chemical_answer(self, text: str) -> str | None:
        lower = text.casefold()
        name_aliases = {
            "wasser": "H2O", "sauerstoff": "O2", "phenol": "C6H5OH", "benzol": "C6H6",
            "ethanol": "C2H5OH", "methanol": "CH3OH", "aceton": "C3H6O",
            "essigsäure": "CH3COOH", "essigsaure": "CH3COOH",
            "natriumchlorid": "NaCl", "schwefelsäure": "H2SO4", "schwefelsaure": "H2SO4",
        }
        candidates = re.findall(r"\b(?:[A-Z][a-z]?\d*|\([A-Za-z0-9]+\)\d*)(?:-?(?:[A-Z][a-z]?\d*|\([A-Za-z0-9]+\)\d*))*\^?\d*[+-]?\b", text)
        candidates = [item for item in candidates if any(character.isdigit() for character in item) or item in self.CHEMICALS]
        named_formula = next(
            (
                formula for name, formula in sorted(name_aliases.items(), key=lambda item: len(item[0]), reverse=True)
                if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", lower)
            ),
            None,
        )
        if named_formula:
            candidates.append(named_formula)
        if not candidates:
            return None
        original = candidates[-1]
        formula = re.sub(r"\^\d*[+-]$", "", original).replace("-", "")
        try:
            counts = self.parse_chemical_formula(formula)
        except ValueError:
            return f"Die chemische Formel `{formula}` konnte nicht sicher validiert werden."
        display = self.format_chemical(original)
        known = self.CHEMICALS.get(formula)
        composition = ", ".join(
            f"{count} × {self.ELEMENTS[element]} ({element})" for element, count in counts.items()
        )
        if known:
            return f"{known[0]} ({known[1]}): {display}\nGelesen: {composition}"
        return f"Chemische Formel: {display}\nGelesen: {composition}\nDer Stoffname ist in der geprüften lokalen Formelsammlung noch nicht hinterlegt."

    def parse_chemical_formula(self, formula: str) -> Counter:
        tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)
        if "".join(tokens) != formula:
            raise ValueError("Ungültige Zeichen.")
        stack = [Counter()]
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "(":
                stack.append(Counter())
            elif token == ")":
                if len(stack) == 1:
                    raise ValueError("Unpassende Klammer.")
                group = stack.pop()
                multiplier = int(tokens[index + 1]) if index + 1 < len(tokens) and tokens[index + 1].isdigit() else 1
                if multiplier != 1:
                    index += 1
                for element, count in group.items():
                    stack[-1][element] += count * multiplier
            elif token.isdigit():
                raise ValueError("Zahl ohne Element.")
            else:
                if token not in self.ELEMENTS:
                    raise ValueError(f"Unbekanntes Elementsymbol: {token}")
                multiplier = int(tokens[index + 1]) if index + 1 < len(tokens) and tokens[index + 1].isdigit() else 1
                if multiplier != 1:
                    index += 1
                stack[-1][token] += multiplier
            index += 1
        if len(stack) != 1:
            raise ValueError("Offene Klammer.")
        return stack[0]

    @classmethod
    def format_chemical(cls, formula: str) -> str:
        charge = ""
        match = re.search(r"\^(\d*)([+-])$", formula)
        if match:
            charge = ((match.group(1) or "1") + match.group(2)).translate(cls.SUPERSCRIPT)
            formula = formula[: match.start()]
        formatted = re.sub(
            r"(?<=[A-Za-z)])(\d+)|(?<=\))(\d+)",
            lambda item: item.group(0).translate(cls.SUBSCRIPT),
            formula,
        )
        return formatted + charge

    @classmethod
    def format_reaction(cls, text: str) -> str:
        text = re.sub(
            r"^.*?(?:reaktionsgleichung|reaktion)\s*:?\s*",
            "",
            text,
            flags=re.I,
        )
        match = re.search(r"((?:\d*\s*[A-Z][A-Za-z0-9()^+\-\s]*)(?:->|→|=>)(?:[A-Za-z0-9()^+\-\s]+))", text)
        if not match:
            return ""
        reaction = match.group(1).strip().replace("=>", "→").replace("->", "→")
        pieces = re.split(r"(\s+\+\s+|\s*→\s*)", reaction)
        formatted = []
        for piece in pieces:
            if "→" in piece:
                formatted.append(" → ")
                continue
            if re.fullmatch(r"\s+\+\s+", piece):
                formatted.append(" + ")
                continue
            compound = piece.strip()
            coefficient = re.match(r"^(\d+)\s*(.*)$", compound)
            if coefficient:
                formatted.append(f"{coefficient.group(1)} {cls.format_chemical(coefficient.group(2))}")
            else:
                formatted.append(cls.format_chemical(compound))
        return "".join(formatted)

    @classmethod
    def format_math(cls, expression: str) -> str:
        value = expression.replace("**", "^").replace("*", " · ")
        return re.sub(r"\^([0-9()+-]+)", lambda match: match.group(1).translate(cls.SUPERSCRIPT), value)

    @staticmethod
    def _extract_math_expression(text: str) -> str:
        match = re.search(r"(?:berechne|rechne|wieviel ist|wie viel ist)\s*:?\s*(.+)$", text, re.I)
        if match:
            return match.group(1).strip()
        candidate = (text or "").strip().rstrip("=?!.")
        candidate = re.sub(r"(?i)^(was ergibt|ergibt|wie viel sind|wieviel sind)\s+", "", candidate).strip()
        allowed = re.fullmatch(r"[0-9\s,.+\-*/×xX·÷^%()√²³]+", candidate)
        return candidate if allowed and re.search(r"[+\-*/×xX·÷^%√²³]", candidate) else ""

    @staticmethod
    def _format_number(value: float) -> str:
        if value.is_integer():
            return f"{int(value):,}".replace(",", " ")
        rounded = round(value, 10)
        if rounded.is_integer():
            return f"{int(rounded):,}".replace(",", " ")
        raw = f"{rounded:,.10f}".rstrip("0").rstrip(".")
        return raw.replace(",", " ").replace(".", ",")
