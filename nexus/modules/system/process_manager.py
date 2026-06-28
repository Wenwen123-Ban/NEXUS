# ============================================================
# modules/system/process_manager.py — List and terminate processes
# ============================================================
from __future__ import annotations

import psutil

from core.display import error, menu, pause, section, success, table, warn
from core.logger import log


def _process_rows(limit: int = 15) -> list[list[object]]:
    processes: list[dict[str, object]] = []
    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                {
                    "pid": info.get("pid", ""),
                    "name": info.get("name") or "<unknown>",
                    "user": info.get("username") or "<unknown>",
                    "cpu": float(info.get("cpu_percent") or 0.0),
                    "mem": float(info.get("memory_percent") or 0.0),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda p: (p["cpu"], p["mem"]), reverse=True)
    return [
        [p["pid"], p["name"], p["user"], f"{p['cpu']:.1f}%", f"{p['mem']:.1f}%"]
        for p in processes[:limit]
    ]


def list_processes() -> None:
    section("RUNNING PROCESSES")
    rows = _process_rows()
    if rows:
        table(["PID", "Name", "User", "CPU", "RAM"], rows)
    else:
        warn("No processes found or process information is unavailable.")
    log("Process list viewed.")
    pause()


def kill_process() -> None:
    section("TERMINATE PROCESS")
    pid_text = input("  PID to terminate: ").strip()
    if not pid_text.isdigit():
        error("PID must be a number.")
        pause()
        return

    pid = int(pid_text)
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        confirm = input(f"  Terminate PID {pid} ({name})? [y/N]: ").strip().lower()
        if confirm != "y":
            warn("Termination cancelled.")
            pause()
            return
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except psutil.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        success(f"Terminated PID {pid} ({name}).")
        log(f"Terminated process PID {pid} ({name}).", "WARNING")
    except psutil.NoSuchProcess:
        error(f"No process exists with PID {pid}.")
    except psutil.AccessDenied:
        error(f"Access denied while terminating PID {pid}.")
        log(f"Access denied terminating PID {pid}.", "ERROR")
    pause()


def run() -> None:
    while True:
        section("PROCESS MANAGER")
        choice = menu("PROCESS OPTIONS", ["List top processes", "Terminate a process by PID"])
        if choice == "1":
            list_processes()
        elif choice == "2":
            kill_process()
        elif choice == "0":
            break
        else:
            warn("Invalid selection. Choose a listed option.")
