# ============================================================
# modules/system/service_checker.py — Check system service status
# ============================================================
from __future__ import annotations

import shutil
import subprocess

from core.display import pause, section, success, table, warn
from core.logger import log

DEFAULT_SERVICES = ["ssh", "cron", "docker", "nginx", "smbd"]


def check_service(name: str) -> str:
    """Return a concise status for a service using systemctl or service."""
    if shutil.which("systemctl"):
        result = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True,
            text=True,
            check=False,
        )
        status = result.stdout.strip() or result.stderr.strip() or "unknown"
        return status

    if shutil.which("service"):
        result = subprocess.run(
            ["service", name, "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        return "active" if result.returncode == 0 else "inactive/unknown"

    return "service manager unavailable"


def run() -> None:
    section("SERVICE CHECKER")
    raw = input(
        "  Services to check (comma-separated, blank for defaults): "
    ).strip()
    services = [item.strip() for item in raw.split(",") if item.strip()] or DEFAULT_SERVICES

    rows = [[service, check_service(service)] for service in services]
    table(["Service", "Status"], rows)

    inactive = [service for service, status in rows if status != "active"]
    if inactive:
        warn(f"Non-active services: {', '.join(inactive)}")
        log(f"Service checker found non-active services: {', '.join(inactive)}", "WARNING")
    else:
        success("All checked services are active.")
        log("Service checker completed with all services active.")

    pause()
