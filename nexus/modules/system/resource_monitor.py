# ============================================================
# modules/system/resource_monitor.py — CPU, RAM, and disk usage
# ============================================================
from __future__ import annotations

import shutil

import psutil

from core.config import CONFIG
from core.display import pause, section, success, table, warn
from core.logger import log


def _percent_status(value: float, threshold: float) -> str:
    return "ALERT" if value >= threshold else "OK"


def _format_bytes(num_bytes: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if num_bytes < 1024 or unit == "PB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def collect_resource_usage() -> list[list[str]]:
    """Return current CPU, memory, and disk usage rows for display."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    disk_percent = disk.used / disk.total * 100 if disk.total else 0.0

    thresholds = {
        "CPU": float(CONFIG.get("cpu_alert_threshold", 90)),
        "RAM": float(CONFIG.get("ram_alert_threshold", 85)),
        "Disk": float(CONFIG.get("disk_alert_threshold", 90)),
    }

    return [
        ["CPU", f"{cpu_percent:.1f}%", f"{thresholds['CPU']:.0f}%", _percent_status(cpu_percent, thresholds["CPU"])],
        [
            "RAM",
            f"{memory.percent:.1f}% ({_format_bytes(memory.used)} / {_format_bytes(memory.total)})",
            f"{thresholds['RAM']:.0f}%",
            _percent_status(memory.percent, thresholds["RAM"]),
        ],
        [
            "Disk /",
            f"{disk_percent:.1f}% ({_format_bytes(disk.used)} / {_format_bytes(disk.total)})",
            f"{thresholds['Disk']:.0f}%",
            _percent_status(disk_percent, thresholds["Disk"]),
        ],
    ]


def run() -> None:
    section("RESOURCE MONITOR")
    rows = collect_resource_usage()
    table(["Resource", "Usage", "Threshold", "Status"], rows)

    alerts = [row for row in rows if row[-1] == "ALERT"]
    if alerts:
        for resource, usage, threshold, _ in alerts:
            warn(f"{resource} usage is {usage}, exceeding threshold {threshold}.")
        log("Resource monitor detected threshold alert(s).", "WARNING")
    else:
        success("All monitored resources are within configured thresholds.")
        log("Resource monitor completed with all resources OK.")

    pause()
