from core.display import menu, clear, section

def system_menu():
    while True:
        clear()
        section("SYSTEM MONITOR")
        choice = menu("SYSTEM OPTIONS", [
            "Resource Monitor (CPU / RAM / Disk)",
            "Process Manager",
            "Service Checker",
        ])
        if choice == "1":
            from modules.system.resource_monitor import run
            run()
        elif choice == "2":
            from modules.system.process_manager import run
            run()
        elif choice == "3":
            from modules.system.service_checker import run
            run()
        elif choice == "0":
            break
