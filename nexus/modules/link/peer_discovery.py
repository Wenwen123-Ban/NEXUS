# ============================================================
# modules/link/peer_discovery.py — NEXUS LINK peer storage/scanning
# ============================================================
from __future__ import annotations

import json
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from core.config import DATA_DIR
from core.logger import log
from modules.identity.auth import load_user
from modules.identity.user_setup import get_local_ip

PEERS_PATH = DATA_DIR / "peers.json"


def load_peers() -> list:
    if not PEERS_PATH.exists():
        return []
    try:
        with PEERS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _write_peers(peers: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with PEERS_PATH.open("w", encoding="utf-8") as f:
        json.dump(peers, f, indent=4)
        f.write("\n")


def save_peer(username: str, ip: str, port: int, status: str = "online") -> None:
    peers = load_peers()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for peer in peers:
        if peer.get("ip") == ip and int(peer.get("port", port)) == port:
            peer.update({"username": username, "last_seen": now, "status": status})
            _write_peers(peers)
            return
    peers.append({"username": username, "ip": ip, "port": port, "last_seen": now, "status": status})
    _write_peers(peers)


def _probe(ip: str, port: int, username: str, my_ip: str) -> dict | None:
    try:
        with socket.create_connection((ip, port), timeout=0.35) as sock:
            sock.sendall(f"NEXUS_DISCOVER|{username}|{my_ip}".encode("utf-8"))
            sock.settimeout(0.75)
            response = sock.recv(1024).decode("utf-8", errors="replace")
        parts = response.split("|", 2)
        if len(parts) >= 2 and parts[0] == "NEXUS_HELLO":
            peer = {"username": parts[1], "ip": ip, "port": port, "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "online"}
            save_peer(peer["username"], ip, port)
            return peer
    except OSError:
        return None
    return None


def scan_for_peers(port: int = 9876) -> list:
    user = load_user() or {"username": "NEXUS"}
    my_ip = get_local_ip()
    octets = my_ip.split(".")
    targets = ["127.0.0.1"]
    if len(octets) == 4:
        base = ".".join(octets[:3])
        targets.extend(f"{base}.{i}" for i in range(1, 255) if f"{base}.{i}" != my_ip)
    found: list[dict] = []
    with ThreadPoolExecutor(max_workers=64) as executor:
        futures = {executor.submit(_probe, ip, port, str(user.get("username", "NEXUS")), my_ip): ip for ip in targets}
        for future in as_completed(futures):
            peer = future.result()
            if peer:
                found.append(peer)
    log(f"NEXUS LINK peer scan found {len(found)} peer(s).")
    return found
