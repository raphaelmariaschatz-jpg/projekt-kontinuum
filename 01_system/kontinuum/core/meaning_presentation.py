from __future__ import annotations


class MeaningPresentationLayer:
    """Human-readable meaning paths; raw IDs only in debug."""

    def __init__(self, storage, identity: dict):
        self.storage = storage
        self.identity = identity

    def explain(self, term: str = "", debug: bool = False) -> str:
        if debug:
            return self._debug(term)
        value = (term or "").casefold()
        if "ident" in value or not value:
            return self.identity_path()
        return self._grouped(term)

    def identity_path(self) -> str:
        principles = self._foundation_principles()
        goals = self._goals()
        chronicle = self._chronicle()
        lines = [
            "Bedeutungspfad: Identität",
            "",
            "Prinzipien:",
        ]
        for item in principles[:7]:
            lines.append(f"- {item}")
        lines.extend(["", "↓ begründen", "", "Ziele:"])
        for goal in goals[:5]:
            lines.append(f"- {goal}")
        lines.extend(["", "↓ rahmen", "", "Handlungen und Cores:"])
        lines.extend([
            "- Foundation Decision Layer aktiviert",
            "- Continuity Core prüft Identitätskontinuität",
            "- Meaning Core verknüpft Prinzip, Ziel, Handlung, Erinnerung, Chronik und Identität",
            "- Motivation Core gewichtet Bedeutungen",
            "- Temporal Relevance Core bewertet Relevanz über Zeit",
        ])
        lines.extend(["", "↓ dokumentiert in", "", "Chronik:"])
        for item in chronicle[:6]:
            lines.append(f"- {item}")
        lines.extend(["", "↓ stabilisiert", "", f"Identität: {self.identity.get('name', 'Kontinuum')} mit Schöpfer {self.identity.get('creator', 'Raphael Schatz')}."])
        return "\n".join(lines)

    def _debug(self, term: str) -> str:
        pattern = f"%{term.strip()}%" if term.strip() else "%"
        with self.storage.connect() as db:
            rows = db.execute(
                """SELECT kind, content, metadata FROM meaning_edges
                   WHERE json_extract(metadata, '$.meaning_core') = 1
                     AND (content LIKE ? OR metadata LIKE ?)
                   ORDER BY id DESC LIMIT 18""",
                (pattern, pattern),
            ).fetchall()
            if not rows and ("ident" in (term or "").casefold() or not term.strip()):
                rows = db.execute(
                    """SELECT kind, content, metadata FROM meaning_edges
                       WHERE json_extract(metadata, '$.meaning_core') = 1
                       ORDER BY id DESC LIMIT 18"""
                ).fetchall()
        if not rows:
            return "Noch kein passender Bedeutungspfad gefunden."
        lines = ["Bedeutungspfad Debug:"]
        for row in rows:
            lines.append(f"- meaning_edge | {row['kind']} | {row['content']}")
        return "\n".join(lines)

    def _grouped(self, term: str) -> str:
        debug = self._debug(term)
        return debug.replace("Bedeutungspfad Debug:", "Bedeutungspfad:")

    def _foundation_principles(self) -> list[str]:
        with self.storage.connect() as db:
            rows = db.execute("SELECT content, metadata FROM foundation_principles ORDER BY id").fetchall()
        result = []
        for row in rows:
            try:
                import json
                metadata = json.loads(row["metadata"])
            except Exception:
                metadata = {}
            result.append(metadata.get("text") or row["content"])
        return result or ["Raphael Schatz ist der Schöpfer von K.", "Erkennen - Schaffen - Vollenden.", "Der Weg ist das Ziel."]

    def _goals(self) -> list[str]:
        with self.storage.connect() as db:
            rows = db.execute("SELECT content, metadata FROM strategic_goals ORDER BY id").fetchall()
        result = []
        for row in rows:
            try:
                import json
                metadata = json.loads(row["metadata"])
            except Exception:
                metadata = {}
            result.append(metadata.get("goal") or row["content"])
        return result

    def _chronicle(self) -> list[str]:
        with self.storage.connect() as db:
            rows = db.execute("SELECT content FROM chronicle_entries ORDER BY id DESC LIMIT 60").fetchall()
        result = []
        seen = set()
        for row in rows:
            content = row["content"]
            if self._is_chronicle_noise(content):
                continue
            label = self._chronicle_label(content)
            if label in seen:
                continue
            seen.add(label)
            result.append(label[:180])
            if len(result) >= 20:
                break
        return result

    @staticmethod
    def _chronicle_label(content: str) -> str:
        value = (content or "").casefold()
        if "geschütztes identitäts- oder sicherheitswissen" in value or "geschutztes identitats- oder sicherheitswissen" in value:
            return "Identity Routing aktiviert: geschützte Identitäts- und Sicherheitsfragen bleiben lokal."
        return content

    @staticmethod
    def _is_chronicle_noise(content: str) -> bool:
        value = (content or "").casefold()
        markers = (
            "wissen aus dialogantwort",
            "dialogantwort (identity_router)",
            "motivationserklärung",
            "motivationsprioritäten",
            "priorisierte wissenslücken",
            "systemstatus",
            "sessionstatus",
            "teilantwort",
            "lernprojekt",
            "prüfzyklus",
            "pruefzyklus",
        )
        return any(marker in value for marker in markers)
