# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

from .error_classification import DiagnosticFinding


class SolutionProposalEngine:
    """Creates stable, reviewable proposals; it never modifies runtime data."""

    PROPOSALS = {
        "routing": "Routing-Prioritaeten und Intent-Grenzen pruefen; den erwarteten Kontext vor dem Router injizieren.",
        "knowledge_graph": "Betroffene Knoten/Kanten validieren und inkonsistente Metadaten kontrolliert neu aufbauen.",
        "database": "Datenbank sichern, Integritaetspruefung wiederholen und beschaedigte Datensaetze aus einer geprueften Sicherung wiederherstellen.",
        "chronicle": "Chronik schreibgeschuetzt lassen, Hash-Kette gegen Sicherung vergleichen und fehlende Signaturen kontrolliert rekonstruieren.",
        "memory": "Fehlerhafte Memory-Metadaten isolieren und aus der letzten konsistenten Quelle neu erzeugen.",
        "foundation": "Offene Foundation-Zyklen pruefen und erst nach Audit mit FoundationCycleRecovery abschliessen.",
        "agent_communication": "Agentenregister, gemeinsame Config und Tool-/Storage-Bindings synchronisieren.",
        "version": "APP_VERSION und alle aktiven Start-, GUI-, Status- und Dokumentationspfade auf dieselbe Version migrieren.",
        "identity": "Session Context vor Identity Router binden und geschuetzten Identitaetskern unveraendert priorisieren.",
    }

    def propose(self, finding: DiagnosticFinding) -> str:
        return self.PROPOSALS.get(
            finding.area,
            "Fundstelle reproduzieren, Ursache eingrenzen und die kleinste gepruefte Korrektur mit Regressionstest umsetzen.",
        )

    def apply(self, finding: DiagnosticFinding) -> DiagnosticFinding:
        if finding.solution:
            return finding
        data = dict(finding.__dict__)
        data["solution"] = self.propose(finding)
        return DiagnosticFinding(**data)
