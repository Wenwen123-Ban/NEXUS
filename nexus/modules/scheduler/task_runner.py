# ============================================================
# modules/scheduler/task_runner.py — Cron-like task runner
# ============================================================
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import schedule

from core.config import DATA_DIR
from core.display import error, pause, section, success, table, warn
from core.logger import log

TASKS_PATH = DATA_DIR / "tasks.json"
SUPPORTED_UNITS = ("seconds", "minutes", "hours", "days")


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _default_tasks() -> list[dict[str, Any]]:
    return []


def load_tasks() -> list[dict[str, Any]]:
    """Load scheduled task definitions from data/tasks.json."""
    if not TASKS_PATH.exists():
        save_tasks(_default_tasks())
        return _default_tasks()

    with TASKS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{TASKS_PATH} must contain a JSON list of tasks.")

    return data


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    """Persist scheduled task definitions."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with TASKS_PATH.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)
        f.write("\n")


def validate_task(task: dict[str, Any]) -> dict[str, Any]:
    """Normalize and validate a task definition."""
    name = str(task.get("name", "")).strip()
    command = str(task.get("command", "")).strip()
    unit = str(task.get("unit", "minutes")).lower().strip()

    if not name:
        raise ValueError("Task name is required.")
    if not command:
        raise ValueError("Task command is required.")
    if unit not in SUPPORTED_UNITS:
        raise ValueError(f"Unit must be one of: {', '.join(SUPPORTED_UNITS)}.")

    try:
        every = int(task.get("every", 1))
    except (TypeError, ValueError) as exc:
        raise ValueError("Interval must be a positive integer.") from exc
    if every < 1:
        raise ValueError("Interval must be a positive integer.")

    return {
        "name": name,
        "command": command,
        "every": every,
        "unit": unit,
        "enabled": bool(task.get("enabled", True)),
        "last_run": task.get("last_run"),
        "next_run": task.get("next_run"),
    }


def run_task(task: dict[str, Any]) -> None:
    """Execute one task command and update its last-run timestamp."""
    name = task["name"]
    command = task["command"]
    started = _now()
    log(f"Scheduled task started: {name} ({command})")

    result = subprocess.run(command, shell=True, text=True, capture_output=True, check=False)
    task["last_run"] = started

    if result.returncode == 0:
        success(f"Task completed: {name}")
        log(f"Scheduled task completed: {name}")
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        error(f"Task failed: {name} (exit {result.returncode})")
        log(f"Scheduled task failed: {name} (exit {result.returncode})", "ERROR")
        if result.stderr.strip():
            print(result.stderr.strip())


def _register_task(task: dict[str, Any]) -> schedule.Job:
    job = schedule.every(task["every"])
    scheduler_unit = getattr(job, task["unit"])
    return scheduler_unit.do(run_task, task=task).tag(task["name"])


def build_schedule(tasks: list[dict[str, Any]]) -> list[schedule.Job]:
    """Register enabled tasks with the schedule library and return jobs."""
    schedule.clear()
    jobs: list[schedule.Job] = []
    for raw_task in tasks:
        task = validate_task(raw_task)
        raw_task.update(task)
        if task["enabled"]:
            job = _register_task(raw_task)
            raw_task["next_run"] = job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else None
            jobs.append(job)
    save_tasks(tasks)
    return jobs


def view_tasks() -> None:
    section("SCHEDULED TASKS")
    try:
        tasks = [validate_task(task) for task in load_tasks()]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        error(f"Unable to load tasks: {exc}")
        pause()
        return

    if not tasks:
        warn("No scheduled tasks configured yet.")
        pause()
        return

    rows = [
        [
            "yes" if task["enabled"] else "no",
            task["name"],
            f"every {task['every']} {task['unit']}",
            task.get("last_run") or "never",
            task.get("next_run") or "not registered",
            task["command"],
        ]
        for task in tasks
    ]
    table(["Enabled", "Name", "Schedule", "Last Run", "Next Run", "Command"], rows)
    pause()


def add_task() -> None:
    section("ADD TASK")
    name = input("  Task name: ").strip()
    command = input("  Command to run: ").strip()
    every = input("  Run every N units [1]: ").strip() or "1"
    unit = input("  Unit (seconds/minutes/hours/days) [minutes]: ").strip() or "minutes"

    try:
        task = validate_task({"name": name, "command": command, "every": every, "unit": unit})
        tasks = load_tasks()
        tasks.append(task)
        save_tasks(tasks)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        error(f"Unable to add task: {exc}")
    else:
        success(f"Added scheduled task: {task['name']}")
        log(f"Scheduled task added: {task['name']} ({task['command']})")
    pause()


def run_scheduler() -> None:
    section("RUN SCHEDULER")
    try:
        tasks = load_tasks()
        jobs = build_schedule(tasks)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        error(f"Unable to start scheduler: {exc}")
        pause()
        return

    if not jobs:
        warn("No enabled scheduled tasks to run.")
        pause()
        return

    success(f"Scheduler started with {len(jobs)} enabled task(s). Press Ctrl+C to stop.")
    log(f"Scheduler started with {len(jobs)} enabled task(s).")
    try:
        while True:
            schedule.run_pending()
            save_tasks(tasks)
            time.sleep(1)
    except KeyboardInterrupt:
        schedule.clear()
        save_tasks(tasks)
        log("Scheduler stopped by user.")
        success("Scheduler stopped.")
        pause()
