from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "running_apps.json"


def _ensure_store_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_apps() -> list[dict[str, Any]]:
    _ensure_store_exists()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
            if isinstance(payload, list):
                return payload
    except (json.JSONDecodeError, OSError):
        return []
    return []


def save_apps(apps: list[dict[str, Any]]) -> None:
    _ensure_store_exists()
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(apps, handle, indent=4)
        handle.write("\n")


def add_app(entry: dict[str, Any]) -> None:
    apps = load_apps()
    apps.append(entry)
    save_apps(apps)


def update_app(app_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    apps = load_apps()
    for app in apps:
        if app.get("id") == app_id:
            app.update(updates)
            save_apps(apps)
            return app
    return None


def remove_app(app_id: str) -> None:
    apps = load_apps()
    apps = [app for app in apps if app.get("id") != app_id]
    save_apps(apps)


def get_app(app_id: str) -> dict[str, Any] | None:
    for app in load_apps():
        if app.get("id") == app_id:
            return app
    return None
