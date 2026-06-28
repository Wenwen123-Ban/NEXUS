# ============================================================
# modules/network/port_scanner.py — Scan open ports on a target host
# ============================================================
from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.display import error, pause, section, success, table, warn
from core.logger import log

DEFAULT_PORTS = "22,80,443,8080"
TIMEOUT_SECONDS = 0.5
MAX_WORKERS = 100


def parse_ports(raw: str) -> list[int]:
    """Parse comma-separated ports and ranges into sorted unique port numbers."""
    ports: set[int] = set()
    for part in raw.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            if not start_text.isdigit() or not end_text.isdigit():
                raise ValueError(f"Invalid port range: {part}")
            start, end = int(start_text), int(end_text)
            if start > end:
                raise ValueError(f"Invalid descending port range: {part}")
            ports.update(range(start, end + 1))
        else:
            if not part.isdigit():
                raise ValueError(f"Invalid port: {part}")
            ports.add(int(part))

    invalid = [port for port in ports if port < 1 or port > 65535]
    if invalid:
        raise ValueError("Ports must be between 1 and 65535.")
    return sorted(ports)


def scan_port(host: str, port: int) -> tuple[int, str] | None:
    """Return an open port with its service name, or None when closed/filtered."""
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS):
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "unknown"
            return port, service
    except OSError:
        return None


def run() -> None:
    section("PORT SCANNER")
    host = input("  Target host/IP: ").strip()
    if not host:
        error("Target host is required.")
        pause()
        return

    raw_ports = input(f"  Ports (e.g. 22,80,443,8000-8100) [{DEFAULT_PORTS}]: ").strip() or DEFAULT_PORTS
    try:
        ports = parse_ports(raw_ports)
    except ValueError as exc:
        error(str(exc))
        pause()
        return

    warn(f"Scanning {host} across {len(ports)} port(s)...")
    open_ports: list[tuple[int, str]] = []
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(ports) or 1)) as executor:
        futures = [executor.submit(scan_port, host, port) for port in ports]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                open_ports.append(result)

    if open_ports:
        rows = [[port, service] for port, service in sorted(open_ports)]
        table(["Port", "Service"], rows)
        success(f"Found {len(open_ports)} open port(s) on {host}.")
    else:
        warn(f"No open ports found on {host} for the selected range.")

    log(f"Port scan completed for {host}: {len(open_ports)} open of {len(ports)} checked.")
    pause()
