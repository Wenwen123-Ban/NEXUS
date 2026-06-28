# ============================================================
# modules/nas/nas_monitor.py — NAS disk usage and health checks
# ============================================================
from __future__ import annotations

import platform
from pathlib import Path

import psutil

from core.config import CONFIG
from core.display import error, pause, section, success, table, warn
from core.logger import log


def _format_bytes(num_bytes: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if num_bytes < 1024 or unit == "PB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def _nas_root() -> Path:
    return Path(str(CONFIG.get("nas_root") or CONFIG.get("nas_path", "./nas_storage"))).expanduser()


def get_stats() -> dict:
    """Return JSON-serializable NAS/system stats for the web dashboard."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
    net = psutil.net_io_counters()
    nas_root = _nas_root()

    temp_c = None
    for sensor_list in temps.values():
        if sensor_list:
            temp_c = round(sensor_list[0].current, 1)
            break

    try:
        nas_root.mkdir(parents=True, exist_ok=True)
        disk = psutil.disk_usage(str(nas_root))
        disk_pct = disk.percent
        disk_used = disk.used
        disk_total = disk.total
        disk_free = disk.free
    except Exception as exc:  # Web endpoint must stay JSON-safe even when storage is unavailable.
        log(f"NAS dashboard disk stats failed for {nas_root}: {exc}", "ERROR")
        disk_pct = disk_used = disk_total = disk_free = 0

    drives = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
        except (OSError, PermissionError):
            continue
        drives.append({"device": p.device, "mountpoint": p.mountpoint, "fstype": p.fstype, "percent": u.percent, "used_gb": round(u.used / 1e9, 1), "total_gb": round(u.total / 1e9, 1), "free_gb": round(u.free / 1e9, 1)})

    return {"server_name": platform.node() or "NAS-Server-01", "platform": platform.system(), "cpu_percent": cpu, "ram_percent": ram.percent, "ram_used_gb": round(ram.used / 1e9, 1), "ram_total_gb": round(ram.total / 1e9, 1), "temp_c": temp_c, "net_dl_kbs": round(net.bytes_recv / 1024, 1), "net_ul_kbs": round(net.bytes_sent / 1024, 1), "disk_percent": disk_pct, "disk_used_gb": round(disk_used / 1e9, 1), "disk_total_gb": round(disk_total / 1e9, 1), "disk_free_gb": round(disk_free / 1e9, 1), "nas_root": str(nas_root), "drives": drives}


def nas_usage(path: Path) -> list[str]:
    """Return a display row with disk usage for the configured NAS path."""
    usage = psutil.disk_usage(str(path))
    percent = usage.percent
    threshold = float(CONFIG.get("disk_alert_threshold", 90))
    status = "ALERT" if percent >= threshold else "OK"
    return [str(path), _format_bytes(usage.used), _format_bytes(usage.free), _format_bytes(usage.total), f"{percent:.1f}%", status]


def run() -> None:
    section("NAS MONITOR")
    nas_path = _nas_root()
    nas_path.mkdir(parents=True, exist_ok=True)

    try:
        row = nas_usage(nas_path)
    except OSError as exc:
        error(f"Unable to read NAS disk usage: {exc}")
        log(f"NAS monitor disk usage failed for {nas_path}: {exc}", "ERROR")
        pause()
        return

    stats = get_stats()
    table(["Metric", "Value"], [["Server", f"{stats['server_name']} ({stats['platform']})"], ["CPU", f"{stats['cpu_percent']}%"], ["RAM", f"{stats['ram_percent']}% ({stats['ram_used_gb']} / {stats['ram_total_gb']} GB)"], ["Temp", f"{stats['temp_c']} °C" if stats["temp_c"] is not None else "N/A"], ["Disk", f"{stats['disk_percent']}% ({stats['disk_used_gb']} / {stats['disk_total_gb']} GB)"]])
    table(["Path", "Used", "Free", "Total", "Usage", "Status"], [row])
    if row[-1] == "ALERT":
        warn(f"NAS disk usage is above the configured threshold ({CONFIG.get('disk_alert_threshold', 90)}%).")
        log(f"NAS monitor detected high disk usage for {nas_path}: {row[4]}", "WARNING")
    else:
        success("NAS storage is within the configured disk threshold.")
        log(f"NAS monitor completed for {nas_path}: {row[4]} used.")
    pause()
