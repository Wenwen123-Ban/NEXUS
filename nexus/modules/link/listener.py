# ============================================================
# modules/link/listener.py — NEXUS LINK socket listener
# ============================================================
from __future__ import annotations

import socket
from datetime import datetime

from core.logger import log

_running = False


def _handle_payload(payload: str, conn: socket.socket, local_username: str) -> None:
    parts = payload.split("|", 2)
    kind = parts[0] if parts else ""
    now = datetime.now().strftime("%H:%M")
    if kind == "MSG" and len(parts) == 3:
        username, message = parts[1], parts[2]
        print(f"\n  [{now}] {username}: {message}")
        log(f"NEXUS LINK received message from {username}.")
    elif kind == "NEXUS_DISCOVER" and len(parts) >= 2:
        ip = socket.gethostbyname(socket.gethostname())
        conn.sendall(f"NEXUS_HELLO|{local_username}|{ip}".encode("utf-8"))
        log(f"NEXUS LINK discovery handshake from {parts[1]}.")
    else:
        print(f"\n  [{now}] Unknown NEXUS LINK payload: {payload}")
        log(f"Unknown NEXUS LINK payload: {payload}", "WARNING")


def start_listener(port: int = 9876, username: str = "NEXUS") -> None:
    """Run a blocking socket server until stop_listener() is called."""
    global _running
    _running = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        server.settimeout(1.0)
        log(f"NEXUS LINK listener started on port {port}.")
        while _running:
            try:
                conn, _addr = server.accept()
            except socket.timeout:
                continue
            except OSError as exc:
                log(f"NEXUS LINK listener stopped by socket error: {exc}", "ERROR")
                break
            with conn:
                data = conn.recv(1024)
                if data:
                    _handle_payload(data.decode("utf-8", errors="replace"), conn, username)
        log("NEXUS LINK listener stopped.")


def stop_listener() -> None:
    """Signal the listener loop to stop."""
    global _running
    _running = False
