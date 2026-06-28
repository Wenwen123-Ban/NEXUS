from core.display import menu, clear, section

def network_menu():
    while True:
        clear()
        section("NETWORK TOOLS")
        choice = menu("NETWORK OPTIONS", [
            "Port Scanner",
            "Port Listener",
            "Ping Sweep / Device Discovery",
        ])
        if choice == "1":
            from modules.network.port_scanner import run
            run()
        elif choice == "2":
            from modules.network.port_listener import run
            run()
        elif choice == "3":
            from modules.network.ping_sweep import run
            run()
        elif choice == "0":
            break
