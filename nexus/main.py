# ============================================================
# NEXUS — Main Entry Point
# Run: python main.py
# ============================================================
from __future__ import annotations

from core.display import banner, clear, menu, warn
from core.logger import log


def main() -> None:
    log("NEXUS session started.")
    while True:
        clear()
        banner()
        choice = menu(
            "MAIN MENU",
            [
                "NAS Manager",
                "Network Tools",
                "Security Center",
                "System Monitor",
                "Email Tools",
                "Task Scheduler",
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
        elif choice == "0":
            log("NEXUS session ended.")
            print("\n[✓] Goodbye.\n")
            break
        else:
            warn("Invalid selection. Choose a listed option.")
            input("  Press Enter to continue...")


if __name__ == "__main__":
    main()
