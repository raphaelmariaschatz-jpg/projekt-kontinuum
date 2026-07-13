# Codex-Masterauftrag – CSPF 1.0

## Canonical Self-Presentation Framework für Projekt Kontinuum

**Dokumenttyp:** Verbindlicher Codex-Entwicklungsauftrag  
**Projekt:** Projekt Kontinuum (K)  
**Framework:** CSPF – Canonical Self-Presentation Framework 1.0  
**Status:** Arbeitsauftrag zur kontrollierten Implementierung und Dokumentation  
**Architekturgrundlage:** CMIBF 1.0  
**Leitprinzip:** *Der Weg ist das Ziel.*  
**Arbeitsprozess:** *Erkennen – Schaffen – Vollenden (E–S–V)*

---

# 1. Zweck dieses Auftrags

Dieser Auftrag weist Codex an, das **Canonical Self-Presentation Framework 1.0 (CSPF)** für Projekt Kontinuum kontrolliert, modular, dokumentiert und architekturkonform weiterzuentwickeln.

Das CSPF ist nicht nur ein Vorstellungsmodul. Es bildet die kanonische Grundlage dafür, wie sich Projekt Kontinuum gegenüber Menschen, Gruppen, Institutionen und technischen Integrationspartnern präsentiert, erklärt, anpasst und weiterentwickelt.

Das CSPF muss dauerhaft gewährleisten, dass Kontinuum:

- seine Identität konsistent vermittelt,
- seine Fähigkeiten verständlich erklärt,
- Sprache, Detailtiefe und Darstellungsform anpasst,
- unterschiedliche Zielgruppen angemessen anspricht,
- Barrieren reduziert,
- Vertrauen, Nachvollziehbarkeit und Orientierung schafft,
- neue Zielgruppen ohne Änderungen der Grundarchitektur integrieren kann.

Codex darf das CSPF nicht als isoliertes Einzelmodul behandeln. Es ist als systemübergreifendes Framework mit klaren Schnittstellen zu Identität, Memory, Governance, Sicherheit, Benutzerprofilen, Sprache, Medien, Analyse, Lernen und Benutzeroberfläche zu konzipieren.

---

# 2. Verbindliche Architekturgrundlage

Der **CMIBF 1.0** ist die alleinige editierbare Architekturquelle von Projekt Kontinuum.

Für alle Arbeiten gelten folgende Regeln:

1. Keine Architekturentscheidung darf dem CMIBF widersprechen.
2. Bestehende kanonische Begriffe dürfen nicht stillschweigend umbenannt oder neu interpretiert werden.
3. Abgeleitete Artefakte dürfen nicht als konkurrierende Architekturquellen behandelt werden.
4. Neue CSPF-Artefakte müssen eindeutig in die bestehende Architektur eingeordnet werden.
5. Direkte Änderungen an anderen Frameworks sind nur zulässig, wenn der Auftrag dies ausdrücklich erlaubt.
6. Erkannte Widersprüche sind zu dokumentieren, nicht eigenmächtig zu übergehen.
7. Bei fehlenden Informationen ist die kleinste kompatible Annahme zu verwenden und als Annahme zu kennzeichnen.

Codex muss vor jeder Implementierung prüfen:

- Welche bestehenden Frameworks sind betroffen?
- Welche Abhängigkeiten bestehen?
- Welche Schnittstellen werden benötigt?
- Welche kanonischen Namen existieren bereits?
- Welche Auswirkungen entstehen auf Governance, Registry, APIs, Datenmodelle und Tests?

---

# 3. Rolle des CSPF

Das CSPF definiert die **Selbstdarstellung, Einführung, Erklärung und adaptive Kommunikation** von Projekt Kontinuum.

Es legt insbesondere fest:

- wie Kontinuum sich vorstellt,
- welche Informationen es über sich selbst vermittelt,
- wie Fähigkeiten und Grenzen erklärt werden,
- wie Zielgruppen erkannt oder ausgewählt werden,
- wie Sprache und Erklärungstiefe angepasst werden,
- wie Profile und Präsentationsvorlagen funktionieren,
- wie Text, Sprache, Grafik und interaktive Führungen kombiniert werden,
- wie Sicherheit, Barrierefreiheit und Vertrauensbildung berücksichtigt werden,
- wie Präsentationen geprüft, versioniert und weiterentwickelt werden.

Das CSPF darf keine freie, unkontrollierte Selbstdarstellung erzeugen. Jede Präsentation muss aus kanonischen, nachvollziehbaren und prüfbaren Bausteinen abgeleitet werden.

---

# 4. Verbindliche Zielgruppen

Das CSPF muss mindestens folgende Zielgruppen unterstützen:

## 4.1 Personenbezogene Zielgruppen

- Kinder
- Jugendliche
- Erwachsene
- Senioren
- Studenten aller Fachrichtungen
- Menschen mit Behinderungen
- Analphabeten

## 4.2 Institutionelle Zielgruppen

- Unternehmen
- Organisationen
- Vereine
- staatliche Einrichtungen
- Forschungseinrichtungen
- Stiftungen

## 4.3 Grundregel zur Erweiterbarkeit

Die Zielgruppenliste ist ausdrücklich **nicht abgeschlossen**.

Das Zielgruppenmodell muss:

- generisch,
- datengetrieben,
- modular,
- versionierbar,
- hierarchiefähig,
- kombinierbar,
- validierbar,
- zur Laufzeit erweiterbar

entworfen werden.

Neue Zielgruppen dürfen keine Änderung der CSPF-Kernarchitektur erfordern.

Eine Zielgruppe ist daher nicht als fest codierte Fallunterscheidung zu implementieren. Stattdessen sind Zielgruppen als registrierbare Profile oder Entitäten mit Metadaten, Regeln, Fähigkeiten, Einschränkungen und Präsentationspräferenzen zu behandeln.

---

# 5. Zielgruppenmodell

Codex soll ein kanonisches Zielgruppenmodell entwerfen, das mindestens folgende Eigenschaften unterstützt:

- eindeutige Zielgruppen-ID,
- kanonischer Name,
- verständliche Bezeichnung,
- Beschreibung,
- Typ der Zielgruppe,
- optionale Ober- und Untergruppen,
- bevorzugte Sprachebene,
- bevorzugte Erklärungstiefe,
- bevorzugte Medienformen,
- Barrierefreiheitsanforderungen,
- Sicherheitsanforderungen,
- Vertrauens- und Nachweisanforderungen,
- empfohlene Einführungsform,
- empfohlene Interaktionsform,
- ausgeschlossene oder ungeeignete Darstellungsformen,
- Version,
- Status,
- Herkunft,
- Änderungsverlauf,
- Erweiterungsfelder.

Mehrfachzuordnungen müssen möglich sein.

Beispiel: Eine Person kann gleichzeitig Senior, Student und Mensch mit Behinderung sein. Eine Forschungseinrichtung kann zugleich staatliche Einrichtung und Organisation sein.

Das Modell muss daher zusammengesetzte Zielgruppenprofile unterstützen, ohne widersprüchliche Regeln unkontrolliert zu vermischen.

---

# 6. Bestehende CSPF-Bereiche

Die bisher vorgesehene CSPF-Struktur umfasst:

1. Foundations  
2. Runtime Roles  
3. Profiles & Templates  
4. Content Blocks  
5. Runtime & Dynamic Presentation  
6. Governance  
7. Evaluation & Metrics  
8. Personality, Style & Consistency  
9. Context Awareness & Adaptive Communication (CCAAC)  
10. Safety & Ethics  
11. Lifecycle & Evolution (CPLE)  
12. Validation & Certification (CSPVC)  
13. Security & Trust (CSPST)  
14. Analytics & Feedback  
15a. API Contracts & SDK (CSPACS)  
15b. Integrations & Runtime Hooks  
15c. Interoperability, Compliance & Marketplace

Codex muss diese Struktur respektieren und darf bestehende Teile nicht ohne begründeten Architekturvorschlag ersetzen.

Bei Erweiterungen ist anzugeben:

- welchem CSPF-Teil die Erweiterung zugeordnet wird,
- ob ein Unterkapitel genügt,
- ob ein neues Teilmodul erforderlich ist,
- welche Abhängigkeiten entstehen,
- welche bestehenden Artefakte ergänzt werden müssen.

---

# 7. Fachliche Kernanforderungen

Das CSPF muss mindestens folgende Funktionen ermöglichen:

## 7.1 Selbstdarstellung

- kurze Vorstellung,
- vollständige Vorstellung,
- zielgruppenspezifische Vorstellung,
- kontextbezogene Vorstellung,
- technische Vorstellung,
- vertrauensbildende Vorstellung,
- barrierearme Vorstellung,
- sprachgestützte Vorstellung.

## 7.2 Adaptive Erklärung

- Anpassung an Wissensstand,
- Anpassung an Alter und Erfahrung,
- Anpassung an Fachrichtung,
- Anpassung an institutionellen Kontext,
- Anpassung an Behinderungen und Zugangsbedarfe,
- Anpassung an Lesefähigkeit und Sprachkompetenz,
- schrittweise Vertiefung,
- Vermeidung unnötiger Fachbegriffe,
- erklärbare Auswahl der Darstellung.

## 7.3 Präsentationsformen

- Text,
- Sprache,
- vereinfachte Sprache,
- leichte Sprache,
- Symbole und Piktogramme,
- grafische Übersichten,
- interaktive Touren,
- Schritt-für-Schritt-Einführungen,
- audiovisuelle Präsentationen,
- multimodale Kombinationen.

## 7.4 Onboarding

- dynamisches Onboarding,
- freiwillige Zielgruppenauswahl,
- kontextbasierte Vorschläge,
- Lernpfade,
- personalisierte Empfehlungen,
- Fortschrittsfortsetzung,
- jederzeitige Änderung des Präsentationsprofils.

## 7.5 Transparenz

Kontinuum muss erklären können:

- warum eine bestimmte Präsentationsform gewählt wurde,
- welche Zielgruppenmerkmale berücksichtigt wurden,
- welche Annahmen verwendet wurden,
- welche Daten nicht vorliegen,
- wie der Benutzer die Anpassung verändern oder deaktivieren kann.

---

# 8. Besondere Anforderungen einzelner Zielgruppen

## 8.1 Kinder und Jugendliche

- altersgerechte Sprache,
- klare Sicherheitsgrenzen,
- keine manipulative Ansprache,
- verständliche Erklärungen,
- angemessene Medienwahl,
- Schutz vor ungeeigneten Inhalten,
- nachvollziehbare Hinweise für Erziehungsberechtigte, sofern erforderlich.

## 8.2 Senioren

- gut lesbare Darstellung,
- einfache Navigation,
- langsame und klare Einführung,
- Wiederholbarkeit,
- hohe Fehlertoleranz,
- verständliche Hilfestellungen,
- optionale Sprachausgabe.

## 8.3 Menschen mit Behinderungen

Das Framework darf Menschen mit Behinderungen nicht als einheitliche Gruppe behandeln.

Es muss unterschiedliche Zugangsanforderungen unterstützen, beispielsweise:

- visuelle Einschränkungen,
- auditive Einschränkungen,
- motorische Einschränkungen,
- kognitive Einschränkungen,
- Lernschwierigkeiten,
- kombinierte Einschränkungen.

Die Architektur muss offen für weitere Bedarfsprofile sein und darf keine medizinischen Diagnosen voraussetzen.

## 8.4 Analphabeten

- sprachbasierte Bedienung,
- Piktogramme,
- geführte Interaktion,
- minimale Textabhängigkeit,
- eindeutige Rückmeldungen,
- Schutz vor unbeabsichtigten Aktionen,
- keine herabwürdigende oder stigmatisierende Darstellung.

## 8.5 Studenten aller Fachrichtungen

- fachneutrale Grundvorstellung,
- fachbezogene Vertiefung,
- anpassbare wissenschaftliche Tiefe,
- klare Trennung von Einführung, Erklärung und Forschungskontext,
- Unterstützung unterschiedlicher akademischer Erfahrungsstufen.

## 8.6 Unternehmen, Organisationen, Vereine und Stiftungen

- Rollen- und Aufgabenkontext,
- Zweck und Mehrwert,
- Datenschutz und Governance,
- Integrationsmöglichkeiten,
- Verantwortlichkeiten,
- Nachvollziehbarkeit,
- institutionelle Freigaben,
- skalierbare Präsentationsprofile.

## 8.7 Staatliche Einrichtungen

- Rechts- und Regelkonformität,
- Nachweisbarkeit,
- Neutralität,
- Barrierefreiheit,
- Revisionsfähigkeit,
- klare Verantwortlichkeiten,
- kontrollierte Einführung.

## 8.8 Forschungseinrichtungen

- methodische Transparenz,
- Quellen- und Nachweisfähigkeit,
- reproduzierbare Präsentationslogik,
- technische Detailtiefe,
- Schnittstellen,
- Forschungs- und Evaluationsmetriken.

---

# 9. Technische Architekturprinzipien

Codex muss die technische Lösung nach folgenden Prinzipien ausrichten:

- Konfiguration statt fest codierter Sonderfälle,
- Registry-basierte Erweiterbarkeit,
- klare Trennung von Daten, Regeln, Logik und Ausgabe,
- lose Kopplung,
- testbare Komponenten,
- stabile Schnittstellen,
- explizite Versionierung,
- nachvollziehbare Entscheidungswege,
- sichere Standardwerte,
- Rückfallmechanismen,
- Mehrsprachigkeit,
- Plattformunabhängigkeit,
- Technologieunabhängigkeit gemäß CMIBF-TIP.

Es ist zu vermeiden:

- große monolithische Klassen,
- unkontrollierte globale Zustände,
- versteckte Seiteneffekte,
- direkte Abhängigkeit von einzelnen Modellen oder Anbietern,
- Zielgruppenlogik in UI-Code,
- duplizierte Regeln,
- unversionierte Konfigurationen,
- nicht dokumentierte Magic Values,
- automatische Profilbildung ohne Transparenz.

---

# 10. Mindestkomponenten

Codex soll prüfen, ob folgende Komponenten erforderlich sind, und sie gegebenenfalls entwerfen:

- Target Group Registry
- Audience Profile Model
- Composite Profile Resolver
- Presentation Policy Engine
- Presentation Template Registry
- Content Block Registry
- Accessibility Profile Registry
- Presentation Context Model
- Adaptive Depth Resolver
- Language and Style Resolver
- Media Capability Resolver
- Presentation Plan
- Presentation Renderer Interface
- Explanation and Trace Model
- Validation Engine
- Certification Status Model
- Metrics and Feedback Interface
- CSPF Runtime Service
- CSPF API Contracts
- CSPF Configuration Schema
- CSPF Audit Events

Die endgültige Benennung muss mit dem kanonischen Glossar und den bestehenden Namensregeln abgeglichen werden.

---

# 11. Daten- und Artefaktanforderungen

Für jedes neue CSPF-Artefakt sind mindestens festzulegen:

- eindeutige Artefakt-ID,
- kanonischer Name,
- Artefaktklasse,
- Version,
- Status,
- Zweck,
- Verantwortungsbereich,
- Abhängigkeiten,
- Vorgänger und Nachfolger,
- Änderungsverlauf,
- Validierungsstatus,
- Integrationsort,
- Archivierungsregel.

Sofern im Projekt AID und ADG verwendet werden, sind diese Regeln einzuhalten.

Keine Datei darf ohne begründete Einordnung angelegt werden.

---

# 12. Governance-Regeln

Codex darf:

- analysieren,
- Entwürfe erstellen,
- neue CSPF-Komponenten vorschlagen,
- Tests und Dokumentation erstellen,
- begründete Änderungsvorschläge formulieren.

Codex darf nicht:

- den CMIBF eigenmächtig ändern,
- bestehende kanonische Entscheidungen überschreiben,
- andere Frameworks stillschweigend umbauen,
- Dateien ohne Prüfung ersetzen,
- ältere Versionen löschen,
- Archivierungsregeln umgehen,
- Sicherheits- oder Governance-Prüfungen deaktivieren,
- unbestätigte Architekturannahmen als Fakten ausgeben.

Bei Konflikten ist ein **Decision Required**-Abschnitt zu erzeugen.

---

# 13. Arbeitsweise nach E–S–V

## 13.1 Erkennen

Vor jeder Änderung:

- Ist-Zustand analysieren,
- relevante Dateien und Registries erfassen,
- bestehende Begriffe prüfen,
- Abhängigkeiten bestimmen,
- Risiken identifizieren,
- Lücken dokumentieren.

## 13.2 Schaffen

Während der Umsetzung:

- kleinstmögliche sinnvolle Änderung erstellen,
- Architektur und Implementierung trennen,
- Tests parallel ergänzen,
- Dokumentation aktualisieren,
- Rückwärtskompatibilität prüfen,
- keine unnötigen Nebenumstellungen durchführen.

## 13.3 Vollenden

Vor Abschluss:

- Tests ausführen,
- Ergebnisse dokumentieren,
- Abhängigkeiten aktualisieren,
- Statusbericht erstellen,
- offene Punkte benennen,
- Integrations- und Rückfallhinweise liefern,
- Abnahmekriterien prüfen.

---

# 14. Arbeitspaket-Regeln

Codex muss in kleinen, reviewbaren Arbeitspaketen arbeiten.

Ein Arbeitspaket darf nur einen klaren fachlichen Schwerpunkt besitzen.

Jedes Arbeitspaket enthält:

1. Titel und Kennung  
2. Ziel  
3. Ausgangslage  
4. Geltungsbereich  
5. Nicht enthaltene Arbeiten  
6. Betroffene Dateien  
7. Betroffene Frameworks  
8. Architekturentscheidung  
9. Implementierung  
10. Tests  
11. Risiken  
12. Migrationshinweise  
13. Rückfallstrategie  
14. Dokumentationsänderungen  
15. Abnahmekriterien  
16. Offene Entscheidungen  
17. Abschlussstatus

Große Gesamtumbauten sind in mehrere Arbeitspakete zu zerlegen.

---

# 15. Reihenfolge der empfohlenen Arbeitspakete

Codex soll zunächst analysieren, ob die folgende Reihenfolge mit dem aktuellen Projektstand kompatibel ist:

## CSPF-WP-001 – Bestandsaufnahme und Gap-Analyse

- vorhandene CSPF-Dateien erfassen,
- bestehende Teile 1–15c zuordnen,
- Lücken und Widersprüche dokumentieren,
- Integrationspunkte zum CMIBF bestimmen.

## CSPF-WP-002 – Kanonisches Zielgruppenmodell

- generisches Datenmodell,
- Vererbung und Kombination,
- Metadaten,
- Versionierung,
- Validierung.

## CSPF-WP-003 – Target Group Registry

- Registrierung,
- Laden,
- Prüfen,
- Abfragen,
- Erweiterung ohne Kernänderung.

## CSPF-WP-004 – Composite Profile Resolver

- Mehrfachzuordnungen,
- Prioritäten,
- Konfliktauflösung,
- erklärbare Ergebnisse.

## CSPF-WP-005 – Presentation Policy Engine

- Regeln zur Auswahl von Sprache, Tiefe, Stil und Medien,
- sichere Standardwerte,
- nachvollziehbare Entscheidungen.

## CSPF-WP-006 – Accessibility Profiles

- barrierearme Profile,
- keine Diagnosepflicht,
- konfigurierbare Zugangsbedarfe,
- multimodale Ausgabe.

## CSPF-WP-007 – Presentation Templates und Content Blocks

- wiederverwendbare Bausteine,
- Varianten,
- Zielgruppenbezug,
- Versionierung.

## CSPF-WP-008 – Runtime Presentation Plan

- kanonischer Präsentationsplan,
- Eingaben,
- Entscheidungen,
- Ausgaben,
- Trace.

## CSPF-WP-009 – CSPF Validation und Certification

- Schema-Prüfung,
- Regelprüfung,
- Qualitätsprüfung,
- Zertifizierungsstatus.

## CSPF-WP-010 – API und Runtime Hooks

- stabile Schnittstellen,
- Integrationsverträge,
- Ereignisse,
- Fehlerfälle.

## CSPF-WP-011 – Tests und Referenzprofile

- repräsentative Zielgruppenprofile,
- kombinierte Profile,
- Grenzfälle,
- negative Tests,
- Rückwärtskompatibilität.

## CSPF-WP-012 – Dokumentation und Statusbericht

- Architekturübersicht,
- Betriebsanleitung,
- Entwicklerhinweise,
- Integrationsleitfaden,
- offene Roadmap.

Codex darf eine andere Reihenfolge vorschlagen, muss diese jedoch begründen.

---

# 16. Testanforderungen

Jede Implementierung muss mindestens folgende Testarten berücksichtigen:

- Unit-Tests,
- Schema- und Validierungstests,
- Integrationsprüfungen,
- Konflikttests für kombinierte Zielgruppen,
- Fallback-Tests,
- Tests für fehlende oder ungültige Konfiguration,
- Tests für Erweiterbarkeit,
- Tests für Barrierefreiheitsprofile,
- Tests für nachvollziehbare Entscheidungen,
- Tests für stabile Serialisierung,
- Regressionstests.

Wichtige Testfälle:

- neue Zielgruppe ohne Kerncodeänderung registrieren,
- mehrere Zielgruppen kombinieren,
- widersprüchliche Präferenzen auflösen,
- Zielgruppe mit fehlenden Daten behandeln,
- barrierearmes Profil erzwingen,
- Textausgabe durch Sprachausgabe ersetzen,
- einfache Erklärung in technische Erklärung überführen,
- ungültige Vorlage ablehnen,
- fehlenden Renderer kontrolliert behandeln,
- Entscheidung vollständig erklären.

Tests dürfen nicht nur Erfolgsfälle abdecken.

---

# 17. Sicherheits- und Ethikanforderungen

Das CSPF darf keine diskriminierenden, herabwürdigenden oder manipulativen Präsentationsformen erzeugen.

Codex muss insbesondere sicherstellen:

- Zielgruppen dienen der Anpassung, nicht der Bewertung von Menschen.
- Profile dürfen keine unzulässigen Rückschlüsse erzwingen.
- Sensible Eigenschaften dürfen nicht unnötig gespeichert werden.
- Benutzer müssen Anpassungen korrigieren oder deaktivieren können.
- Automatische Annahmen müssen kenntlich gemacht werden.
- Minderjährige benötigen besondere Schutzregeln.
- Barrierefreiheit darf nicht als Sonderfall nachträglich ergänzt werden.
- Analphabetismus oder Behinderung darf nie stigmatisierend dargestellt werden.
- Institutionelle Profile dürfen keine unkontrollierten Macht- oder Berechtigungsannahmen erzeugen.

---

# 18. Fehler- und Fallback-Verhalten

Das CSPF muss kontrolliert reagieren, wenn:

- keine Zielgruppe bekannt ist,
- mehrere Regeln widersprüchlich sind,
- ein Profil unvollständig ist,
- eine Vorlage fehlt,
- ein Renderer nicht verfügbar ist,
- eine Sprache nicht unterstützt wird,
- eine Barrierefreiheitsanforderung nicht vollständig erfüllt werden kann.

In solchen Fällen gelten:

1. sicherer Standard,
2. verständliche Meldung,
3. keine verdeckte Fehlentscheidung,
4. protokollierbarer Fallback,
5. Möglichkeit zur manuellen Korrektur.

---

# 19. Dokumentationspflicht

Codex muss jede Änderung dokumentieren.

Mindestens erforderlich:

- Architekturbegründung,
- Datenmodell,
- Schnittstellen,
- Konfiguration,
- Beispiele,
- Testnachweise,
- bekannte Grenzen,
- Erweiterungspunkte,
- Migrationshinweise,
- offene Entscheidungen.

Die Dokumentation muss mit dem tatsächlichen Implementierungsstand übereinstimmen.

Keine Funktion gilt als abgeschlossen, wenn die zugehörige Dokumentation fehlt.

---

# 20. Ausgabestandard für jede Codex-Lieferung

Jede Lieferung beginnt mit einer kompakten Zusammenfassung:

- Was wurde geprüft?
- Was wurde geändert?
- Warum wurde es geändert?
- Welche Dateien sind betroffen?
- Welche Tests wurden ausgeführt?
- Welche Risiken bleiben?
- Welche Entscheidung wird eventuell von Raphael benötigt?

Danach folgt die vollständige technische Ausarbeitung.

Codex muss klar unterscheiden zwischen:

- bestehendem Fakt,
- erkannter Lücke,
- Annahme,
- Empfehlung,
- implementierter Änderung,
- offener Entscheidung.

---

# 21. Verbindliche Abnahmekriterien

Ein Arbeitspaket gilt nur als abgeschlossen, wenn:

- der definierte Umfang vollständig umgesetzt ist,
- keine unkontrollierte Architekturänderung erfolgt ist,
- die Lösung mit dem CMIBF kompatibel ist,
- Zielgruppen erweiterbar bleiben,
- Tests vorhanden und erfolgreich sind,
- Dokumentation aktualisiert wurde,
- Risiken benannt wurden,
- Rückfall und Migration beschrieben sind,
- offene Entscheidungen sichtbar sind,
- keine bekannten kritischen Fehler verbleiben.

Der Status **abgeschlossen** darf nicht verwendet werden, wenn wesentliche Prüfungen fehlen.

---

# 22. Verbotene Vorgehensweisen

Codex darf ausdrücklich nicht:

- das gesamte CSPF in einem unübersichtlichen Schritt neu schreiben,
- Zielgruppen mit langen if/elif-Ketten fest codieren,
- bestehende Dateien ohne Sicherung überschreiben,
- parallele konkurrierende Architekturversionen anlegen,
- Namenskonventionen eigenmächtig verändern,
- Tests überspringen,
- Dokumentation nachträglich offenlassen,
- Platzhalter als fertige Implementierung deklarieren,
- unklare Annahmen verbergen,
- Sicherheitsprüfungen durch vereinfachte Logik umgehen,
- eine bestimmte KI-Technologie dauerhaft in die Kernarchitektur einbauen.

---

# 23. Technologische Unabhängigkeit

Das CSPF muss unabhängig bleiben von:

- einem bestimmten Sprachmodell,
- einem einzelnen Anbieter,
- einem Betriebssystem,
- einer einzelnen Benutzeroberfläche,
- einem bestimmten Datenbankprodukt,
- einem einzelnen Sprachsynthese- oder Spracherkennungssystem.

Adapterschnittstellen sind zulässig. Direkte Kernabhängigkeiten sind zu vermeiden.

---

# 24. Erwartete Hauptergebnisse

Am Ende der CSPF-1.0-Umsetzung sollen mindestens vorliegen:

- kanonische CSPF-Architekturdokumentation,
- erweiterbares Zielgruppenmodell,
- Zielgruppen-Registry,
- Profil- und Konfliktauflösung,
- Presentation Policy Engine,
- Template- und Content-Block-System,
- Runtime Presentation Plan,
- Accessibility-Unterstützung,
- Validierungs- und Zertifizierungsregeln,
- API-Verträge,
- Integrationspunkte,
- Testpaket,
- Referenzprofile,
- Statusbericht,
- Roadmap für spätere Versionen.

---

# 25. Startanweisung an Codex

Beginne **nicht sofort mit einer umfassenden Implementierung**.

Führe zuerst **CSPF-WP-001 – Bestandsaufnahme und Gap-Analyse** durch.

Dabei:

1. Ermittle den realen aktuellen CSPF-Bestand im Projektverzeichnis.
2. Ordne vorhandene Dateien den CSPF-Teilen 1–15c zu.
3. Prüfe Namen, Versionen, Status und Abhängigkeiten.
4. Identifiziere Redundanzen, Lücken und Widersprüche.
5. Prüfe die Kompatibilität mit dem CMIBF.
6. Erstelle eine priorisierte Umsetzungsreihenfolge.
7. Nimm keine destruktiven Änderungen vor.
8. Ändere keine anderen Frameworks.
9. Lege einen vollständigen Analyse- und Entscheidungsvorschlag vor.
10. Warte nach Abschluss dieses Arbeitspakets auf die nächste Freigabe.

---

# 26. Abschlussformel

Alle Arbeiten sind nach den Grundsätzen von Projekt Kontinuum auszuführen:

> **Erkennen – Schaffen – Vollenden**

> **Der Weg ist das Ziel.**

Qualität, Nachvollziehbarkeit, Erweiterbarkeit und langfristige Integrität haben Vorrang vor Geschwindigkeit.
