# ============================================================
# modules/network/ping_sweep.py — Discover alive hosts in a network range
# ============================================================
from __future__ import annotations

import ipaddress
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.config import CONFIG
from core.display import error, pause, section, success, table, warn
from core.logger import log

MAX_HOSTS = 1024
PING_TIMEOUT_SECONDS = 1


def expand_targets(raw: str) -> list[str]:
    """Expand CIDR, single IP, or final-octet range notation into IP strings."""
    value = raw.strip()
    if not value:
        raise ValueError("A target range is required.")

    if "/" in value:
        network = ipaddress.ip_network(value, strict=False)
        targets = [str(host) for host in network.hosts()]
    elif "-" in value:
        base, end_text = value.rsplit(".", 1)
        start_text, stop_text = end_text.split("-", 1)
        start, stop = int(start_text), int(stop_text)
        if start > stop or start < 0 or stop > 255:
            raise ValueError("IP ranges must use an ascending final octet between 0 and 255.")
        targets = [f"{base}.{octet}" for octet in range(start, stop + 1)]
        for target in targets:
            ipaddress.ip_address(target)
    else:
        ipaddress.ip_address(value)
        targets = [value]

    if len(targets) > MAX_HOSTS:
        raise ValueError(f"Refusing to ping more than {MAX_HOSTS} hosts at once.")
    return targets


def ping_host(host: str) -> bool:
    """Return True when a host responds to one ICMP ping."""
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(PING_TIMEOUT_SECONDS * 1000), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(PING_TIMEOUT_SECONDS), host]

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return result.returncode == 0


def run() -> None:
    section("PING SWEEP")
    default_range = str(CONFIG.get("ping_range", "192.168.1.1-254"))
    raw_range = input(f"  Target range (CIDR/IP/final-octet range) [{default_range}]: ").strip() or default_range
    try:
        targets = expand_targets(raw_range)
    except (ValueError, ipaddress.AddressValueError) as exc:
        error(str(exc))
        pause()
        return

    warn(f"Pinging {len(targets)} host(s)...")
    alive: list[str] = []
    with ThreadPoolExecutor(max_workers=min(128, len(targets) or 1)) as executor:
        futures = {executor.submit(ping_host, target): target for target in targets}
        for future in as_completed(futures):
            target = futures[future]
            if future.result():
                alive.append(target)

    if alive:
        table(["Alive Host"], [[host] for host in sorted(alive, key=ipaddress.ip_address)])
        success(f"Discovered {len(alive)} alive host(s).")
    else:
        warn("No hosts responded to ping.")

    log(f"Ping sweep completed for {raw_range}: {len(alive)} alive of {len(targets)} checked.")
    pause()
