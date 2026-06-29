from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import datetime
from typing import Any

import psutil

from core.logger import log
from modules.apprunner.port_checker import detect_app_port, is_port_in_use
from modules.apprunner.process_store import add_app, get_app, load_apps, update_app


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or "app"


def _build_entry(name: str, file_path: str, port: int, pid: int) -> dict[str, Any]:
    return {
        "id": _slugify(name),
        "name": name,
        "file": os.path.abspath(file_path),
        "pid": pid,
        "port": port,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "running",
        "auto_start": False,
    }


def is_process_alive(pid: int) -> bool:
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def launch_app(name: str, file_path: str, port: int = 5000) -> dict[str, Any] | None:
    if not name.strip():
        return None

    normalized_path = os.path.abspath(file_path)
    if not os.path.exists(normalized_path) or not normalized_path.endswith(".py"):
        return None

    if is_port_in_use(port):
        return None

    try:
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        process = subprocess.Popen(
            [sys.executable, normalized_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(normalized_path) or ".",
            creationflags=creationflags,
        )
    except OSError:
        return None

    time.sleep(2)
    if not is_process_alive(process.pid):
        return None

    detected_port = detect_app_port(process.pid, expected_port=port)
    entry = _build_entry(name.strip(), normalized_path, detected_port, process.pid)
    add_app(entry)
    log(f"Started app {entry['name']} from {entry['file']} on port {entry['port']} (PID {entry['pid']})")
    return entry


def stop_app(app_id: str) -> bool:
    app = get_app(app_id)
    if not app:
        return False

    pid = app.get("pid")
    if not pid:
        update_app(app_id, {"status": "stopped"})
        return True

    try:
        process = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        update_app(app_id, {"status": "crashed"})
        return False

    if process.is_running():
        process.terminate()
        time.sleep(3)
        if process.is_running():
            process.kill()
            time.sleep(1)

    update_app(app_id, {"status": "stopped", "pid": None})
    log(f"Stopped app {app['name']} ({app_id})")
    return True


def restart_app(app_id: str) -> dict[str, Any] | None:
    app = get_app(app_id)
    if not app:
        return None

    stop_app(app_id)
    time.sleep(1)
    return launch_app(app["name"], app["file"], app.get("port", 5000))


def refresh_statuses() -> list[dict[str, Any]]:
    apps = load_apps()
    updated: list[dict[str, Any]] = []
    for app in apps:
        if app.get("status") == "running" and app.get("pid"):
            if not is_process_alive(int(app["pid"])):
                app["status"] = "crashed"
        updated.append(app)
    if updated != apps:
        from modules.apprunner.process_store import save_apps

        save_apps(updated)
    return updated
