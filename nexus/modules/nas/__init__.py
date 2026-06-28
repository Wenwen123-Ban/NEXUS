from core.display import menu, clear, section
from core.logger import log

def nas_menu():
    while True:
        clear()
        section("NAS MANAGER")
        choice = menu("NAS OPTIONS", [
            "Disk Usage Monitor",
            "File Browser",
            "Folder Sync",
            "Launch Web Dashboard",
        ])
        if choice == "1":
            from modules.nas.nas_monitor import run
            run()
        elif choice == "2":
            from modules.nas.nas_browser import run
            run()
        elif choice == "3":
            from modules.nas.nas_sync import run
            run()
        elif choice == "4":
            from modules.nas.nas_web import run
            run()
        elif choice == "0":
            break
