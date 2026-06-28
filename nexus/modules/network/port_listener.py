# ============================================================
# modules/network/port_listener.py — Listen on a local port and log connections
# ============================================================
from __future__ import annotations

import socket
import threading
from datetime import datetime

from core.display import error, pause, section, success, table, warn
from core.logger import log

BUFFER_SIZE = 1024


def _handle_client(conn: socket.socket, addr: tuple[str, int], connections: list[list[str]]) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        conn.settimeout(2)
        try:
            data = conn.recv(BUFFER_SIZE)
        except OSError:
            data = b""
        preview = data.decode("utf-8", errors="replace").strip().replace("\n", " ")[:60]
        connections.append([timestamp, addr[0], str(addr[1]), preview or "<no data>"])
        log(f"Port listener connection from {addr[0]}:{addr[1]} payload={preview or '<no data>'}")


def run() -> None:
    section("PORT LISTENER")
    port_text = input("  Local port to listen on: ").strip()
    if not port_text.isdigit():
        error("Port must be a number.")
        pause()
        return

    port = int(port_text)
    if port < 1 or port > 65535:
        error("Port must be between 1 and 65535.")
        pause()
        return

    host = input("  Bind address [0.0.0.0]: ").strip() or "0.0.0.0"
    connections: list[list[str]] = []
    stop_event = threading.Event()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen()
            server.settimeout(0.5)
            success(f"Listening on {host}:{port}. Press Enter to stop.")
            log(f"Port listener started on {host}:{port}.")

            stopper = threading.Thread(target=lambda: (input(), stop_event.set()), daemon=True)
            stopper.start()
            while not stop_event.is_set():
                try:
                    conn, addr = server.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=_handle_client, args=(conn, addr, connections), daemon=True).start()
    except OSError as exc:
        error(f"Could not start listener: {exc}")
        log(f"Port listener failed on {host}:{port}: {exc}", "ERROR")
        pause()
        return

    section("LISTENER SUMMARY")
    if connections:
        table(["Time", "Host", "Port", "Payload Preview"], connections)
    else:
        warn("No connections received.")
    log(f"Port listener stopped on {host}:{port} after {len(connections)} connection(s).")
    pause()
