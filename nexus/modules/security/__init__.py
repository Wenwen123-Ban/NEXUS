from core.display import menu, clear, section

def security_menu():
    while True:
        clear()
        section("SECURITY CENTER")
        choice = menu("SECURITY OPTIONS", [
            "SSH Login Monitor",
            "Firewall Rules Viewer",
            "Intrusion Log Parser",
        ])
        if choice == "1":
            from modules.security.ssh_monitor import run
            run()
        elif choice == "2":
            from modules.security.firewall_rules import run
            run()
        elif choice == "3":
            from modules.security.intrusion_log import run
            run()
        elif choice == "0":
            break
