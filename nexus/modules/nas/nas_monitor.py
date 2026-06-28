# ============================================================
# modules/nas/nas_monitor.py — NAS disk usage and health checks
# ============================================================
from __future__ import annotations

import shutil
from pathlib import Path

from core.config import CONFIG
from core.display import error, pause, section, success, table, warn
from core.logger import log


def _format_bytes(num_bytes: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if num_bytes < 1024 or unit == "PB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def nas_usage(path: Path) -> list[str]:
    """Return a display row with disk usage for the configured NAS path."""
    usage = shutil.disk_usage(path)
    percent = usage.used / usage.total * 100 if usage.total else 0.0
    threshold = float(CONFIG.get("disk_alert_threshold", 90))
    status = "ALERT" if percent >= threshold else "OK"
    return [
        str(path),
        _format_bytes(usage.used),
        _format_bytes(usage.free),
        _format_bytes(usage.total),
        f"{percent:.1f}%",
        status,
    ]


def run() -> None:
    section("NAS MONITOR")
    nas_path = Path(str(CONFIG.get("nas_path", "/mnt/nas"))).expanduser()

    if not nas_path.exists():
        error(f"NAS path does not exist: {nas_path}")
        warn("Update data/config.json with the mounted NAS path before monitoring.")
        log(f"NAS monitor failed because path does not exist: {nas_path}", "ERROR")
        pause()
        return

    if not nas_path.is_dir():
        error(f"NAS path is not a directory: {nas_path}")
        log(f"NAS monitor failed because path is not a directory: {nas_path}", "ERROR")
        pause()
        return

    try:
        row = nas_usage(nas_path)
    except OSError as exc:
        error(f"Unable to read NAS disk usage: {exc}")
        log(f"NAS monitor disk usage failed for {nas_path}: {exc}", "ERROR")
        pause()
        return

    table(["Path", "Used", "Free", "Total", "Usage", "Status"], [row])
    if row[-1] == "ALERT":
        warn(f"NAS disk usage is above the configured threshold ({CONFIG.get('disk_alert_threshold', 90)}%).")
        log(f"NAS monitor detected high disk usage for {nas_path}: {row[4]}", "WARNING")
    else:
        success("NAS storage is within the configured disk threshold.")
        log(f"NAS monitor completed for {nas_path}: {row[4]} used.")

    pause()
