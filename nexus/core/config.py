# ============================================================
# core/config.py — Central configuration loader
# Edit data/config.json to change settings.
# ============================================================
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULTS: dict[str, Any] = {
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "alert_email": "your_email@gmail.com",
    "nas_path": "/mnt/nas",
    "cpu_alert_threshold": 90,
    "ram_alert_threshold": 85,
    "disk_alert_threshold": 90,
    "ping_range": "192.168.1.1-254",
}


def save(cfg: dict[str, Any]) -> None:
    """Persist configuration as pretty-printed JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
        f.write("\n")


def load() -> dict[str, Any]:
    """Load configuration, creating or backfilling data/config.json as needed."""
    if not CONFIG_PATH.exists():
        cfg = deepcopy(DEFAULTS)
        save(cfg)
        return cfg

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    changed = False
    for key, value in DEFAULTS.items():
        if key not in cfg:
            cfg[key] = value
            changed = True

    if changed:
        save(cfg)

    return cfg


CONFIG = load()
