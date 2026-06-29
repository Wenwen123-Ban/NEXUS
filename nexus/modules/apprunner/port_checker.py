from __future__ import annotations

import socket
import webbrowser

import psutil


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
            return False
        except OSError:
            return True


def detect_app_port(pid: int, expected_port: int = 5000) -> int:
    try:
        process = psutil.Process(pid)
        for connection in process.connections(kind="inet"):
            if getattr(connection, "status", None) == psutil.CONN_LISTEN and connection.laddr:
                return connection.laddr.port or expected_port
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return expected_port
    return expected_port


def open_in_browser(port: int) -> None:
    webbrowser.open(f"http://localhost:{port}")
