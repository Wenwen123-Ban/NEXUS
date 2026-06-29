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


def _build_entry(name: str, file_path: str, port: int, pid: int, create_time: float | None = None) -> dict[str, Any]:
    return {
        "id": _slugify(name),
        "name": name,
        "file": os.path.abspath(file_path),
        "pid": pid,
        "port": port,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # store numeric create_time from psutil so we can detect PID reuse
        "create_time": create_time,
        "status": "running",
        "auto_start": False,
    }


def is_process_alive(pid: int, create_time: float | None = None) -> bool:
    """Return True only if PID exists and (optionally) matches create_time.

    Verifies the process has not been re-used for a different program by
    comparing psutil.Process.create_time() to the stored create_time.
    """
    try:
        process = psutil.Process(pid)
        if create_time is not None:
            try:
                return abs(process.create_time() - create_time) < 1 and process.is_running()
            except (OSError, psutil.Error):
                return False
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

    # capture psutil create_time to ensure PID hasn't been reused later
    create_time = None
    try:
        create_time = psutil.Process(process.pid).create_time()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        create_time = None

    detected_port = detect_app_port(process.pid, expected_port=port)
    entry = _build_entry(name.strip(), normalized_path, detected_port, process.pid, create_time=create_time)
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
    # verify the PID we have is still the same process (not reused)
    stored_create = app.get("create_time")
    try:
        process = psutil.Process(int(pid))
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        update_app(app_id, {"status": "crashed", "pid": None})
        return False

    if stored_create is not None:
        try:
            if abs(process.create_time() - float(stored_create)) > 1:
                # PID was reused for another process
                update_app(app_id, {"status": "crashed", "pid": None})
                return False
        except (OSError, psutil.Error):
            update_app(app_id, {"status": "crashed", "pid": None})
            return False

    # attempt a graceful termination, then force-kill if needed
    try:
        process.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        update_app(app_id, {"status": "stopped", "pid": None})
        return True

    gone, alive = psutil.wait_procs([process], timeout=3)
    if alive:
        for p in alive:
            try:
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        psutil.wait_procs(alive, timeout=2)

    # final verification
    if not is_process_alive(int(pid), create_time=stored_create):
        update_app(app_id, {"status": "stopped", "pid": None})
        log(f"Stopped app {app['name']} ({app_id})")
        return True

    # if still somehow running, mark as stopped but warn
    update_app(app_id, {"status": "stopped", "pid": None})
    log(f"Stop attempted for {app['name']} ({app_id}) but process still present")
    return False


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
