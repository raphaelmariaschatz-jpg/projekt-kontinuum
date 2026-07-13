# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import argparse
import getpass

from kontinuum.core.auth import AuthManager
from kontinuum.core.system import KontinuumSystem
from kontinuum.version import APP_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Projekt Kontinuum {APP_VERSION}")
    parser.add_argument("prompt", nargs="*")
    args = parser.parse_args()
    auth = AuthManager()
    identity = None
    for _ in range(5):
        username = input("Benutzername: ").strip()
        password = getpass.getpass("Passwort: ")
        identity = auth.verify_login(username, password)
        if identity:
            break
        print("Zugang verweigert.")
    if not identity:
        print("Zu viele fehlgeschlagene Anmeldeversuche.")
        return 1
    system = KontinuumSystem()
    system.set_user_context(identity)

    def confirm_cost(action: str, resource: str) -> bool:
        print(f"Kostenrelevante Oracle-Aktion: {action}")
        print(f"Ressource: {resource}")
        if input("Aktion ausdrücklich bestätigen? [ja/NEIN]: ").strip().casefold() != "ja":
            return False
        password = getpass.getpass("Superadmin-Passwort erneut eingeben: ")
        return AuthManager().verify_superadmin_confirmation(identity, password, f"{action} | {resource}")

    system.set_cost_confirmation_handler(confirm_cost)
    try:
        if args.prompt:
            print(system.ask(" ".join(args.prompt)))
            return 0
        print(system.status())
        return 0
    finally:
        system.close()


if __name__ == "__main__":
    raise SystemExit(main())
