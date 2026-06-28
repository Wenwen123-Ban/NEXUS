# ============================================================
# NEXUS — Main Entry Point
# Run: python main.py
# ============================================================
from __future__ import annotations

from core.display import banner, clear, menu, warn
from core.logger import log
from modules.identity.auth import is_first_run, login
from modules.identity.user_setup import run_setup


def main() -> None:
    log("NEXUS session started.")
    clear()
    if is_first_run():
        run_setup()

    user = login()
    if user is None:
        print("\n  [✗] Access denied. Exiting NEXUS.")
        return

    while True:
        clear()
        banner(username=str(user.get("username", "")))
        choice = menu(
            "MAIN MENU",
            [
                "NAS Manager",
                "Network Tools",
                "Security Center",
                "System Monitor",
                "Email Tools",
                "Task Scheduler",
                "NEXUS LINK — LAN Chat",
                "My Identity",
            ],
        )

        if choice == "1":
            from modules.nas import nas_menu

            nas_menu()
        elif choice == "2":
            from modules.network import network_menu

            network_menu()
        elif choice == "3":
            from modules.security import security_menu

            security_menu()
        elif choice == "4":
            from modules.system import system_menu

            system_menu()
        elif choice == "5":
            from modules.email_tools import email_menu

            email_menu()
        elif choice == "6":
            from modules.scheduler import scheduler_menu

            scheduler_menu()
        elif choice == "7":
            from modules.link import link_menu

            link_menu(user)
        elif choice == "8":
            from modules.identity import identity_menu

            user = identity_menu(user)
        elif choice == "0":
            log("NEXUS session ended.")
            print("\n[✓] Goodbye.\n")
            break
        else:
            warn("Invalid selection. Choose a listed option.")
            input("  Press Enter to continue...")


if __name__ == "__main__":
    main()
