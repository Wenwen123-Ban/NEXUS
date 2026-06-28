from __future__ import annotations

from core.display import error, menu, pause, section, success, table, warn
from modules.link.chat_session import open_chat
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
    while True:
        section("NEXUS LINK")
        choice = menu("LAN CHAT", ["Open Chat", "Add Peer", "Discover Peers", "View Known Peers"])
        if choice == "1":
            open_chat(user)
        elif choice == "2":
            _add_peer()
        elif choice == "3":
            found = scan_for_peers(int((user or {}).get("port", 9876)))
            success(f"Discovered {len(found)} peer(s).")
            pause()
        elif choice == "4":
            _view_peers()
        elif choice == "0":
            break
        else:
            warn("Invalid selection. Choose a listed option.")
