# ============================================================
# modules/link/sender.py — NEXUS LINK socket sender
# ============================================================
from __future__ import annotations

import socket

from core.logger import log


def send_message(target_ip: str, port: int, username: str, message: str) -> bool:
    """Send one UTF-8 NEXUS LINK message to a peer."""
    payload = f"MSG|{username}|{message}".encode("utf-8")
    try:
        with socket.create_connection((target_ip, port), timeout=5) as sock:
            sock.sendall(payload[:1024])
        log(f"NEXUS LINK sent message to {target_ip}:{port}.")
        return True
    except OSError as exc:
        log(f"NEXUS LINK send failed to {target_ip}:{port}: {exc}", "ERROR")
        return False
