from __future__ import annotations

"""
Projekt Kontinuum 32.3 – Desktop-GUI

Ziele:
- großes Texteingabefeld
- getrenntes Antwortfenster
- Such-/Aktivitätsfenster: zeigt, wo Kontinuum gerade sucht
- Agentenstatus
- Systemstatus inklusive Backend-Version 32.3
- Meaning-Core-Schnellbefehle für Bedeutungsstatus und Bedeutungspfad
- Motivation-Core-Schnellbefehle für Bedeutungsgewichtung
- Motivation-Explanation-Schnellbefehle für erklärbare Scores
- Runtime-Hardening-Schnellbefehle für Sessionstatus und Foundation-Recovery
- kompatibel mit bestehendem KontinuumSystem, falls vorhanden
- Fallback-Demo, falls Backend noch nicht installiert ist
"""

import os
import sys
import threading
import time
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText


DEFAULT_ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
SYSTEM_PATH = str(DEFAULT_ROOT / "01_system")
if SYSTEM_PATH not in sys.path:
    sys.path.insert(0, SYSTEM_PATH)

from kontinuum.core.auth import AuthManager
from kontinuum.version import APP_VERSION


APP_TITLE = f"Projekt Kontinuum {APP_VERSION} – Neue GUI"


class FallbackKontinuumSystem:
    """Fallback, solange das echte Backend noch nicht geladen werden kann."""

    def __init__(self):
        self.version = APP_VERSION

    def status(self) -> dict:
        return {
            "name": "Projekt Kontinuum",
            "version": APP_VERSION,
            "backend": "Fallback-Demo",
            "note": "Echtes Backend noch nicht geladen."
        }

    def ask(self, prompt: str) -> str:
        lower = prompt.lower().strip()
        if not lower:
            return "Ich bin bereit, Raphael."
        if "name" in lower or "wer bist" in lower:
            return f"Mein Name ist Kontinuum. Ich bin die neue GUI-Vorlage für Version {APP_VERSION}."
        if "schöpfer" in lower or "schoepfer" in lower:
            return "Mein Schöpfer gemäß Kernarchitektur ist Raphael Schatz."
        if "mathematik" in lower:
            return f"Suchlogik {APP_VERSION}: zuerst 04_knowledge, dann 03_memory, 06_learning, 32_data, Chronicle, Legacy."
        return f"Eingabe empfangen. Das echte Kontinuum-Backend wird in Version {APP_VERSION} hier angebunden."


def load_backend():
    """Versucht, das echte KontinuumSystem zu laden."""
    try:
        system_path = str(DEFAULT_ROOT / "01_system")
        if system_path not in sys.path:
            sys.path.insert(0, system_path)
        from kontinuum.core.system import KontinuumSystem
        return KontinuumSystem(DEFAULT_ROOT)
    except Exception:
        return FallbackKontinuumSystem()


class KontinuumGUI(tk.Tk):
    def __init__(self, identity: dict):
        super().__init__()
        self.identity = identity
        self.system = load_backend()
        self.active_requests = 0
        if hasattr(self.system, "set_user_context"):
            self.system.set_user_context(identity)
        if hasattr(self.system, "set_cost_confirmation_handler"):
            self.system.set_cost_confirmation_handler(self._confirm_cost_from_worker)
        if hasattr(self.system, "set_search_progress_handler"):
            self.system.set_search_progress_handler(self._search_progress_from_worker)
        self.title(APP_TITLE)
        self.geometry("1200x800")
        self.minsize(1000, 680)

        self._build_layout()
        self._write_system_message()
        self._refresh_status()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_layout(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(10, 8))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text=APP_TITLE, font=("Segoe UI", 15, "bold"))
        title.grid(row=0, column=0, sticky="w")

        self.status_label = ttk.Label(header, text="Status wird geladen …")
        self.status_label.grid(row=0, column=1, sticky="e")

        main = ttk.Frame(self, padding=(10, 4))
        main.grid(row=1, column=0, sticky="nsew")
        main.rowconfigure(0, weight=3)
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        self.output = ScrolledText(main, wrap="word", font=("Segoe UI", 11))
        self.output.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.output.configure(state="normal")

        input_frame = ttk.LabelFrame(main, text="Eingabe an Kontinuum", padding=8)
        input_frame.grid(row=1, column=0, sticky="nsew")
        input_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)

        self.input_box = ScrolledText(input_frame, wrap="word", height=5, font=("Segoe UI", 11))
        self.input_box.grid(row=0, column=0, sticky="nsew")
        self.input_box.bind("<Control-Return>", self.ask)

        button_row = ttk.Frame(input_frame)
        button_row.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        button_row.columnconfigure(0, weight=1)

        hint = ttk.Label(button_row, text="Senden: Strg + Enter oder Button")
        hint.grid(row=0, column=0, sticky="w")

        self.ask_button = ttk.Button(button_row, text="Frage senden", command=self.ask)
        self.ask_button.grid(row=0, column=1, padx=(8, 0))
        ttk.Button(button_row, text="Eingabe löschen", command=self.clear_input).grid(row=0, column=2, padx=(8, 0))

        side = ttk.Frame(self, padding=(4, 4, 10, 10))
        side.grid(row=1, column=1, sticky="nsew")
        side.rowconfigure(1, weight=2)
        side.rowconfigure(3, weight=1)
        side.columnconfigure(0, weight=1)

        ttk.Label(side, text="Such- und Aktivitätsfenster", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.activity = ScrolledText(side, wrap="word", height=16, font=("Consolas", 10))
        self.activity.grid(row=1, column=0, sticky="nsew", pady=(4, 10))

        ttk.Label(side, text="Agenten / Module", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w")
        self.agents = ScrolledText(side, wrap="word", height=10, font=("Consolas", 10))
        self.agents.grid(row=3, column=0, sticky="nsew", pady=(4, 10))

        controls = ttk.LabelFrame(side, text="Schnellbefehle", padding=8)
        controls.grid(row=4, column=0, sticky="ew")
        controls.columnconfigure(0, weight=1)
        ttk.Button(controls, text="Status", command=lambda: self.quick("status")).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Agentenstatus", command=lambda: self.quick("agenten")).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Internetstatus", command=lambda: self.quick("internetstatus")).grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Lernstatus", command=lambda: self.quick("lernstatus")).grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Modellstatus", command=lambda: self.quick("modellstatus")).grid(row=4, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Pythonstatus", command=lambda: self.quick("pythonstatus")).grid(row=5, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Wingetstatus", command=lambda: self.quick("wingetstatus")).grid(row=6, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Suche Mathematik", command=lambda: self.quick("suche Mathematik")).grid(row=7, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Formelstatus", command=lambda: self.quick("formelstatus")).grid(row=8, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Notizbuchstatus", command=lambda: self.quick("notizbuchstatus")).grid(row=9, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Bedeutungsstatus", command=lambda: self.quick("bedeutungsstatus")).grid(row=10, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Bedeutungspfad", command=lambda: self.quick("bedeutungspfad identität")).grid(row=11, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Fundamentschicht", command=lambda: self.quick("fundamentschichtstatus")).grid(row=12, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Motivationsstatus", command=lambda: self.quick("motivationsstatus")).grid(row=13, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Motivationsprioritäten", command=lambda: self.quick("motivationsprioritäten")).grid(row=14, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Motivationserklärung", command=lambda: self.quick("motivationserklärung identität")).grid(row=15, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Wichtige Einflüsse", command=lambda: self.quick("wichtige einflüsse identität")).grid(row=16, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Relevanzstatus", command=lambda: self.quick("relevanzstatus")).grid(row=17, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Bedeutungsinflation", command=lambda: self.quick("bedeutungsinflation")).grid(row=18, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Sessionstatus", command=lambda: self.quick("sessionstatus")).grid(row=19, column=0, sticky="ew", pady=2)
        ttk.Button(controls, text="Fundamentzyklen", command=lambda: self.quick("fundamentzyklenstatus")).grid(row=20, column=0, sticky="ew", pady=2)

        footer = ttk.Frame(self, padding=(10, 2, 10, 8))
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.footer_label = ttk.Label(footer, text="Bereit.")
        self.footer_label.grid(row=0, column=0, sticky="w")

    def _write_system_message(self):
        self.write_output(
            "Kontinuum",
            f"Neue GUI {APP_VERSION} bereit.\n"
            "Großes Eingabefeld, Aktivitätsfenster, Agentenanzeige, Meaning-, Motivation- und Explanation-Schnellbefehle sind aktiv.\n",
        )
        self.log_activity("Start", "GUI geladen.")
        self.log_activity(f"Suchreihenfolge {APP_VERSION}", "04_knowledge → 03_memory → 06_learning → 32_data → 22_project_chronicle → 02_versions → Internet")
        self.log_activity("Meaning Core", "Prinzip → Ziel → Handlung → Erinnerung → Chronik → Identität")
        self.log_activity("Motivation Core", "bewertet zentrale Bedeutungen, Ziele, Erinnerungen, Wissenslücken und Selbstfragen")
        self.log_activity("Motivation Explanation Core", "erklärt Scores über Meaning-Kanten, Evidenz und Pfade")
        self.log_activity("Temporal Relevance Core", "bewertet Bedeutung, Chronik und Wissenslücken über Zeit")
        self.refresh_agents()

    def _refresh_status(self):
        try:
            st = self.system.status() if hasattr(self.system, "status") else {}
            version = st.get("version", APP_VERSION) if isinstance(st, dict) else APP_VERSION
            backend = st.get("backend", "KontinuumSystem") if isinstance(st, dict) else "KontinuumSystem"
            self.status_label.configure(text=f"{self.identity.get('username')} | {self.identity.get('role')} | Version {version} | {backend}")
            self.footer_label.configure(text="Bereit.")
        except Exception as exc:
            self.status_label.configure(text="Statusfehler")
            self.log_activity("Fehler", str(exc))

    def refresh_agents(self):
        self.agents.delete("1.0", "end")
        fallback = [
            "dialogue",
            "research",
            "learning",
            "autonomous_learning",
            "internet_status",
            "system_monitor",
            "memory",
            "knowledge",
            "planner",
            "reflection",
            "foundation",
        ]
        try:
            if hasattr(self.system, "modules"):
                mods = self.system.modules.list_active()
            else:
                mods = fallback
        except Exception:
            mods = fallback
        for m in mods:
            self.agents.insert("end", f"✓ {m}\n")

    def write_output(self, speaker: str, text: str):
        self.output.insert("end", f"{speaker}:\n{text}\n\n")
        self.output.see("end")

    def log_activity(self, area: str, message: str):
        self.activity.insert("end", f"[{area}] {message}\n")
        self.activity.see("end")

    def predicted_search_path(self, prompt: str) -> list[str]:
        lower = prompt.lower()
        paths = []
        if lower.startswith("suche "):
            paths += ["04_knowledge", "03_memory", "06_learning", "32_data/kontinuum.db", "22_project_chronicle", "02_versions/legacy_index"]
        elif "internet" in lower or "web" in lower or "online" in lower:
            paths += [
                "01_system/kontinuum/tools/search_engine_tools.py",
                "24_config/search_engine.json",
                "21_internet_sources",
                "05_connectors",
                "27_logs",
            ]
        elif "lerne" in lower or "lern" in lower:
            paths += ["06_learning", "18_autonomous_learning", "04_knowledge", "03_memory"]
        elif lower.startswith("python") or "pythonstatus" in lower:
            paths += ["01_system/kontinuum/tools/python_tools.py", "13_tools/python_workspace"]
        elif lower.startswith("winget"):
            paths += ["01_system/kontinuum/tools/winget_tools.py", "24_config/winget.json"]
        elif "formel" in lower or lower.startswith(("berechne", "rechne")):
            paths += ["01_system/kontinuum/tools/formula_engine.py", "01_system/kontinuum/agents/formula_agent.py"]
        elif "bedeutung" in lower or "meaning" in lower:
            paths += [
                "01_system/kontinuum/core/meaning_core.py",
                "32_data/kontinuum.db/meaning_nodes",
                "32_data/kontinuum.db/meaning_edges",
                "32_data/kontinuum.db/meaning_paths",
            ]
        elif "motivation" in lower or "motivations" in lower or "priorität" in lower or "prioritaet" in lower or "score" in lower or "einfluss" in lower or "einflüsse" in lower or "einfluesse" in lower:
            paths += [
                "01_system/kontinuum/core/motivation_core.py",
                "01_system/kontinuum/core/motivation_explanation.py",
                "32_data/kontinuum.db/motivation_scores",
                "32_data/kontinuum.db/motivation_reports",
                "32_data/kontinuum.db/motivation_explanations",
                "32_data/kontinuum.db/motivation_evidence",
                "32_data/kontinuum.db/motivation_paths",
                "32_data/kontinuum.db/meaning_edges",
            ]
        elif "relevanz" in lower or "bedeutungsinflation" in lower or "chronikprägung" in lower or "chronikpraegung" in lower:
            paths += [
                "01_system/kontinuum/core/temporal_relevance.py",
                "32_data/kontinuum.db/relevance_assessments",
                "32_data/kontinuum.db/relevance_reports",
                "32_data/kontinuum.db/meaning_edges",
                "32_data/kontinuum.db/chronicle_entries",
            ]
        elif "session" in lower or "benutzer" in lower or "angemeldet" in lower or "rolle" in lower:
            paths += [
                "01_system/kontinuum/core/session_context.py",
                "01_system/kontinuum/core/identity_router.py",
                "03_memory/core_identity.json",
            ]
        elif "fundamentzyklus" in lower or "fundamentzyklen" in lower:
            paths += [
                "01_system/kontinuum/core/foundation_cycle_recovery.py",
                "32_data/kontinuum.db/foundation_decisions",
            ]
        elif "fundament" in lower or "moral" in lower or "kontinuit" in lower:
            paths += [
                "01_system/kontinuum/core/foundation_decision.py",
                "01_system/kontinuum/core/continuity.py",
                "01_system/kontinuum/core/moral_core.py",
                "32_data/kontinuum.db/foundation_decisions",
            ]
        elif "wer bist" in lower or "name" in lower or "schöpfer" in lower or "schoepfer" in lower:
            paths += ["03_memory/core_identity.json", "32_data/kontinuum.db"]
        else:
            paths += ["03_memory", "04_knowledge", "32_data/kontinuum.db"]
        return paths

    def ask(self, event=None):
        prompt = self.input_box.get("1.0", "end").strip()
        if not prompt:
            return "break"

        self.clear_input()
        self.write_output("Raphael", prompt)

        self.log_activity("Eingabe", prompt[:120])
        for path in self.predicted_search_path(prompt):
            self.log_activity("Suche", f"prüfe {path}")

        self.active_requests += 1
        self.footer_label.configure(text=f"Kontinuum arbeitet ... ({self.active_requests} Auftrag/Aufträge)")
        if hasattr(self.system, "ask_async"):
            self.system.ask_async(prompt, self._async_answer_ready)
        else:
            threading.Thread(target=self._ask_in_background, args=(prompt,), daemon=True).start()
        return "break"

    def _async_answer_ready(self, answer: str, error):
        if error:
            answer = "FEHLER:\n" + str(error)
        self.after(0, self._finish_answer, answer, str(error) if error else None)

    def _ask_in_background(self, prompt: str):
        try:
            answer = self.system.ask(prompt)
            error = None
        except Exception as exc:
            answer = "FEHLER:\n" + str(exc) + "\n\n" + traceback.format_exc()
            error = str(exc)
        self.after(0, self._finish_answer, answer, error)

    def _search_progress_from_worker(self, progress: dict):
        self.after(0, self._show_search_progress, dict(progress))

    def _show_search_progress(self, progress: dict):
        if progress.get("timed_out"):
            self.log_activity("Timeout", "Archivsuche abgebrochen: Zeitlimit erreicht.")
            return
        self.log_activity(
            "Archivsuche läuft...",
            f"Bereich: {progress.get('area', '')} | Treffer: {progress.get('hits', 0)} | "
            f"Zeit: {progress.get('elapsed', 0)} Sekunden",
        )

    def _confirm_cost_from_worker(self, action: str, resource: str) -> bool:
        completed = threading.Event()
        result = {"approved": False}

        def ask_on_ui_thread():
            try:
                approved = messagebox.askyesno(
                    "Systemänderung bestätigen",
                    f"Diese Aktion kann Kosten verursachen:\n\n{action}\n{resource}\n\nFortfahren?",
                    parent=self,
                )
                if approved:
                    password = simpledialog.askstring(
                        "Superadmin bestätigen",
                        "Superadmin-Passwort erneut eingeben:",
                        show="*",
                        parent=self,
                    )
                    if password is not None:
                        result["approved"] = AuthManager(DEFAULT_ROOT).verify_superadmin_confirmation(
                            self.identity,
                            password,
                            f"{action} | {resource}",
                        )
                        password = None
                    if not result["approved"]:
                        messagebox.showerror("Systemänderung", "Superadminbestätigung fehlgeschlagen.", parent=self)
            finally:
                completed.set()

        self.after(0, ask_on_ui_thread)
        completed.wait()
        return bool(result["approved"])

    def _finish_answer(self, answer: str, error: str | None):
        if error:
            self.log_activity("Fehler", error)
        self.write_output("Kontinuum", answer)
        self.active_requests = max(0, self.active_requests - 1)
        if self.active_requests:
            self.footer_label.configure(text=f"Kontinuum arbeitet ... ({self.active_requests} Auftrag/Aufträge)")
        else:
            self._refresh_status()

    def quick(self, command: str):
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", command)
        self.ask()

    def clear_input(self):
        self.input_box.delete("1.0", "end")

    def _close(self):
        if hasattr(self.system, "close"):
            self.system.close()
        self.destroy()


def main():
    identity = require_login()
    if not identity:
        return
    app = KontinuumGUI(identity)
    app.mainloop()


def require_login() -> dict | None:
    auth = AuthManager(DEFAULT_ROOT)
    result: dict[str, dict | None] = {"identity": None}
    root = tk.Tk()
    root.title(f"Projekt Kontinuum {APP_VERSION} - Login")
    root.geometry("430x270")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = ttk.Frame(root, padding=24)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Projekt Kontinuum", font=("Segoe UI", 17, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
    ttk.Label(frame, text="Anmeldung erforderlich").grid(row=1, column=0, columnspan=2, pady=(0, 18))
    ttk.Label(frame, text="Benutzername").grid(row=2, column=0, sticky="w", pady=5)
    username = ttk.Entry(frame)
    username.insert(0, "Raphael Schatz")
    username.grid(row=2, column=1, sticky="ew", pady=5)
    ttk.Label(frame, text="Passwort").grid(row=3, column=0, sticky="w", pady=5)
    password = ttk.Entry(frame, show="*")
    password.grid(row=3, column=1, sticky="ew", pady=5)
    message = ttk.Label(frame, text="")
    message.grid(row=4, column=0, columnspan=2, pady=(8, 4))
    attempts = {"count": 0}

    def cancel():
        result["identity"] = None
        root.destroy()

    def login(event=None):
        status = auth.status()
        if not status.get("configured") or not status.get("consistent"):
            messagebox.showerror("Login", status.get("message", "Authentifizierung ist nicht sicher konfiguriert."), parent=root)
            cancel()
            return "break"
        identity = auth.verify_login(username.get(), password.get())
        password.delete(0, "end")
        if identity:
            result["identity"] = identity
            root.destroy()
            return "break"
        attempts["count"] += 1
        remaining = max(0, 5 - attempts["count"])
        message.configure(text=f"Zugang verweigert. Verbleibende Versuche: {remaining}")
        if remaining == 0:
            messagebox.showerror("Login", "Zu viele fehlgeschlagene Anmeldeversuche. Kontinuum wird beendet.", parent=root)
            cancel()
        else:
            root.update_idletasks()
            time.sleep(min(attempts["count"], 3))
            password.focus_set()
        return "break"

    ttk.Button(frame, text="Anmelden", command=login).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 4))
    ttk.Button(frame, text="Beenden", command=cancel).grid(row=6, column=0, columnspan=2, sticky="ew")
    root.protocol("WM_DELETE_WINDOW", cancel)
    root.bind("<Return>", login)
    password.focus_set()
    root.mainloop()
    return result["identity"]


if __name__ == "__main__":
    main()
