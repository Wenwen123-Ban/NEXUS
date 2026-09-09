# ============================================================
# modules/link/listener.py — NEXUS LINK socket listener
# ============================================================
from __future__ import annotations

import socket
import threading
from datetime import datetime
from typing import Callable

from core.logger import log

_running = threading.Event()


def _handle_payload(payload: str, conn: socket.socket, local_username: str) -> None:
    parts = payload.split("|", 2)
    kind = parts[0] if parts else ""
    now = datetime.now().strftime("%H:%M")
    if kind == "MSG" and len(parts) == 3:
        username, message = parts[1], parts[2]
        print(f"\n  [{now}] {username}: {message}")
        log(f"NEXUS LINK received message from {username}.")
        conn.sendall(b"NEXUS_OK")
    elif kind == "NEXUS_DISCOVER" and len(parts) >= 2:
        # The probing peer already knows the address it used to reach us.  Do
        # not resolve the hostname here: on many VMs that resolves to 127.0.0.1
        # and causes the remote peer to save an unusable loopback address.
        conn.sendall(f"NEXUS_HELLO|{local_username}".encode("utf-8"))
        log(f"NEXUS LINK discovery handshake from {parts[1]}.")
    else:
        print(f"\n  [{now}] Unknown NEXUS LINK payload: {payload}")
        log(f"Unknown NEXUS LINK payload: {payload}", "WARNING")
        conn.sendall(b"NEXUS_ERROR|Invalid payload")


def start_listener(
    port: int = 9876,
    username: str = "NEXUS",
    on_ready: Callable[[OSError | None], None] | None = None,
) -> None:
    """Run a blocking socket server until stop_listener() is called."""
    global _running
    _running.set()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(("0.0.0.0", port))
        except OSError as exc:
            log(f"NEXUS LINK listener could not start on port {port}: {exc}", "ERROR")
            if on_ready:
                on_ready(exc)
            return
        server.listen(5)
        server.settimeout(1.0)
        if on_ready:
            on_ready(None)
        log(f"NEXUS LINK listener started on port {port}.")
        while _running.is_set():
            try:
                conn, _addr = server.accept()
            except socket.timeout:
                continue
            except OSError as exc:
                log(f"NEXUS LINK listener stopped by socket error: {exc}", "ERROR")
                break
            with conn:
                conn.settimeout(2.0)
                try:
                    data = conn.recv(1024)
                except OSError as exc:
                    log(f"NEXUS LINK receive failed: {exc}", "WARNING")
                    continue
                if data:
                    _handle_payload(data.decode("utf-8", errors="replace"), conn, username)
        log("NEXUS LINK listener stopped.")


def stop_listener() -> None:
    """Signal the listener loop to stop."""
    global _running
    _running.clear()
