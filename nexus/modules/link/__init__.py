from __future__ import annotations

import threading

from core.display import error, menu, pause, section, success, table, warn
from modules.link.chat_session import open_chat
from modules.link.listener import start_listener, stop_listener
from modules.link.peer_discovery import load_peers, save_peer, scan_for_peers


def _view_peers() -> None:
    peers = load_peers()
    section("KNOWN NEXUS LINK PEERS")
    if peers:
        table(["Name", "IP", "Port", "Status", "Last Seen"], [[p.get("username", "?"), p.get("ip", ""), p.get("port", 9876), p.get("status", "?"), p.get("last_seen", "")] for p in peers])
    else:
        warn("No peers saved yet.")
    pause()


def _add_peer() -> None:
    section("ADD PEER")
    username = input("  Display name: ").strip() or "Manual Peer"
    ip = input("  IP address: ").strip()
    port_raw = input("  Port (9876): ").strip()
    if not ip:
        error("IP address is required.")
        pause()
        return
    save_peer(username, ip, int(port_raw or 9876), "unknown")
    success("Peer saved.")
    pause()


def link_menu(user: dict | None = None) -> None:
    current = user or {}
    port = int(current.get("port", 9876))
    ready = threading.Event()
    startup_error: list[OSError] = []

    def _listener_ready(exc: OSError | None) -> None:
        if exc:
            startup_error.append(exc)
        ready.set()

    listener = threading.Thread(
        target=start_listener,
        kwargs={"port": port, "username": str(current.get("username", "NEXUS")), "on_ready": _listener_ready},
        daemon=True,
    )
    listener.start()
    if not ready.wait(timeout=2):
        error(f"NEXUS LINK listener did not start on port {port}.")
        stop_listener()
        listener.join(timeout=1.5)
        pause()
        return
    if startup_error:
        error(f"Cannot receive NEXUS LINK messages on port {port}: {startup_error[0]}")
        pause()
        return
    success(f"Ready to receive LAN messages on port {port}.")

    try:
        while True:
            section("NEXUS LINK")
            choice = menu("LAN CHAT", ["Open Chat", "Add Peer", "Discover Peers", "View Known Peers"])
            if choice == "1":
                open_chat(user)
            elif choice == "2":
                _add_peer()
            elif choice == "3":
                found = scan_for_peers(port)
                success(f"Discovered {len(found)} peer(s).")
                pause()
            elif choice == "4":
                _view_peers()
            elif choice == "0":
                break
            else:
                warn("Invalid selection. Choose a listed option.")
    finally:
        stop_listener()
        listener.join(timeout=1.5)
