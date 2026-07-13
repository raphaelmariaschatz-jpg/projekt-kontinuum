# Projektstatus aktuell - Kontinuum 33.0

Kontinuum 33.0 ist der aktive Projektstand. Der Autonomous Diagnostics Core
fuehrt beim Start acht interne Pruefbereiche aus, klassifiziert Befunde,
erstellt Loesungsvorschlaege und informiert den Benutzer im Chatfenster.

Am 20.06.2026 wurde Foundation Knowledge Protection 2.0 integriert. Der neue
Foundation Integrity Core trennt Fundamentwissen über eine eigene immutable
Schutzklasse dauerhaft von Fachwissen, Lerninhalten, Berichten, Diagnosen und
Wissenslücken. Sechs kanonische Schutzbereiche besitzen Herkunfts-, Versions-
und SHA-256-Integritätsnachweise. Unautorisierte Integrations- und
Änderungsversuche werden blockiert und auditiert; die autonome Diagnostik prüft
die Schutzschicht regelmäßig.

- Version: 33.0
- GUI: `16_installation/START_GUI_33_0.bat`
- CLI: `16_installation/START_KONTINUUM_33_0.bat`
- Tests: `16_installation/TEST_KONTINUUM_33_0.bat`
- Status: `13_tools/status_check_33_0.py`
- Auditberichte: `14_documents/interne_fehler_und_loesungen/`
- Foundation-Integrität: Befehl `fundamentintegritätsstatus`

Foundation Knowledge Protection 3.0 ergänzt Protection 2.0 um den Foundation
Memory Layer. Identität, Prinzipien, Moral, Schöpferwissen und langfristige
Ziele sind als getrennte `foundation.*`-Klassen gespeichert. Fach- und
Lernwissen trägt die Gegenklasse `learned.knowledge`; beide Layer besitzen
getrennte Tabellen und Schreibpfade. Neue Befehle: `foundationmemorystatus`
und `wissensklasse <Aussage>`.

Als direkte Nutzungsschicht ist außerdem Foundation Query Layer 1.0 aktiv.
Identitäts-, Schöpfer-, Prinzipien- und moralische Begründungsfragen werden
priorisiert aus `foundation_memory` und `foundation_knowledge` beantwortet.
Normales Fachwissen und Internetsuche werden hierfür nicht verwendet; jede
Abfrage wird mit Herkunft, Klasse und verwendeter Fundamentregel auditiert.

Foundation Reasoning Layer 4.0 führt Entscheidungen, Antworten und
Motivationserklärungen auf 31 stabile Regel-IDs einschließlich der zwölf
`foundation.guiding.*`-IDs zurück.
Einflussstärke, Alternativen, Unsicherheit und Foundation-Pfad werden bereits
beim Entscheidungsbeginn unveränderlich gespeichert. Der Befehl
`foundationreasoningstatus` zeigt Integrität und Nachweisbestand.

Am 21.06.2026 wurden zwölf vorläufige und bis zum ausdrücklichen Widerruf
geltende Leitprinzipien als geschützte Foundation-Policy aktiviert. Sie besitzen
die stabilen IDs `foundation.guiding.01` bis `foundation.guiding.12`, werden im
Foundation Memory mit Herkunft, Policy-Status und Integritätshash geführt und
vom Foundation Reasoning bei relevanten Entscheidungen verwendet. Eine spätere
Ablösung erfolgt ausschließlich als neue append-only Foundation-Migration.


> © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.
