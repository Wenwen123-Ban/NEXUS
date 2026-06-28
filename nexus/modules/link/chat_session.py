# ============================================================
# modules/link/chat_session.py — NEXUS LINK live chat session
# ============================================================
from __future__ import annotations

import threading
from datetime import datetime

from core.display import clear, error, pause, section, success, table, warn
from modules.identity.auth import load_user
from modules.link.listener import start_listener, stop_listener
from modules.link.peer_discovery import load_peers, save_peer
from modules.link.sender import send_message


def _choose_peer() -> tuple[str, int] | None:
    peers = load_peers()
    if peers:
        table(["#", "Name", "IP", "Port", "Status"], [[i, p.get("username", "?"), p.get("ip", ""), p.get("port", 9876), p.get("status", "?")] for i, p in enumerate(peers, 1)])
    raw = input("  Peer # or manual IP (blank to cancel): ").strip()
    if not raw:
        return None
    if raw.isdigit() and 1 <= int(raw) <= len(peers):
        peer = peers[int(raw) - 1]
        return str(peer.get("ip", "127.0.0.1")), int(peer.get("port", 9876))
    port_raw = input("  Port (9876): ").strip()
    return raw, int(port_raw or 9876)


def _help() -> None:
    print("  Commands: /exit, /peers, /clear, /myip, /help")


def open_chat(user: dict | None = None) -> None:
    current = user or load_user()
    if not current:
        error("No logged-in user available.")
        pause()
        return
    target = _choose_peer()
    if target is None:
        return
    peer_ip, peer_port = target
    save_peer("Manual Peer", peer_ip, peer_port, "unknown")
    listener = threading.Thread(target=start_listener, kwargs={"port": int(current.get("port", 9876)), "username": str(current.get("username", "NEXUS"))}, daemon=True)
    listener.start()
    section(f"NEXUS LINK CHAT → {peer_ip}:{peer_port}")
    _help()
    try:
        while True:
            text = input(f"  {current.get('username', 'You')} > ").strip()
            if not text:
                continue
            if text == "/exit":
                break
            if text == "/peers":
                peers = load_peers()
                table(["Name", "IP", "Port", "Status", "Last Seen"], [[p.get("username", "?"), p.get("ip", ""), p.get("port", 9876), p.get("status", "?"), p.get("last_seen", "")] for p in peers])
                continue
            if text == "/clear":
                clear()
                continue
            if text == "/myip":
                success(f"My IP: {current.get('ip', '')}:{current.get('port', 9876)}")
                continue
            if text == "/help":
                _help()
                continue
            sent = send_message(peer_ip, peer_port, str(current.get("username", "NEXUS")), text)
            now = datetime.now().strftime("%H:%M")
            if sent:
                print(f"  [{now}] You: {text}")
            else:
                warn("Message could not be delivered. Peer may be offline.")
    finally:
        stop_listener()
        listener.join(timeout=1.5)
