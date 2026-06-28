# ============================================================
# modules/security/firewall_rules.py — View local firewall rules
# ============================================================
from __future__ import annotations

import shutil
import subprocess

from core.display import error, pause, section, success, table, warn
from core.logger import log


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def firewall_rows() -> tuple[str, list[list[str]]]:
    """Return firewall backend name and a display-friendly list of rules."""
    if shutil.which("ufw"):
        result = _run_command(["ufw", "status", "numbered"])
        output = result.stdout.strip() or result.stderr.strip()
        rows = [[line] for line in output.splitlines() if line.strip()]
        return "ufw", rows

    if shutil.which("iptables"):
        result = _run_command(["iptables", "-S"])
        output = result.stdout.strip() or result.stderr.strip()
        rows = [[line] for line in output.splitlines() if line.strip()]
        return "iptables", rows

    if shutil.which("nft"):
        result = _run_command(["nft", "list", "ruleset"])
        output = result.stdout.strip() or result.stderr.strip()
        rows = [[line] for line in output.splitlines() if line.strip()]
        return "nftables", rows

    return "none", []


def run() -> None:
    section("FIREWALL RULES VIEWER")
    backend, rows = firewall_rows()
    if backend == "none":
        error("No supported firewall command found (ufw, iptables, or nft).")
        log("Firewall rules viewer found no supported firewall backend.", "ERROR")
        pause()
        return

    if rows:
        table([f"{backend} rules"], rows[:80])
        success(f"Displayed {len(rows)} firewall rule line(s) from {backend}.")
        log(f"Firewall rules viewed with backend {backend}: {len(rows)} line(s).")
    else:
        warn(f"{backend} returned no firewall rules or access was denied.")
        log(f"Firewall rules viewer received no output from {backend}.", "WARNING")
    pause()
