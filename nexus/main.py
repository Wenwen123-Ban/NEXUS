# ============================================================
# NEXUS — Main Entry Point
# Run: python main.py
# ============================================================
from core.display import banner, menu, clear
from core.logger import log

def main():
    while True:
        clear()
        banner()
        choice = menu("MAIN MENU", [
            "NAS Manager",
            "Network Tools",
            "Security Center",
            "System Monitor",
            "Email Tools",
            "Task Scheduler",
        ])

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

if __name__ == "__main__":
    main()
