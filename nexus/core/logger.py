# ============================================================
# core/logger.py — Shared logging utility
# All modules write here via log()
# ============================================================
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from core.config import DATA_DIR

LOG_PATH = DATA_DIR / "nexus.log"


def log(message: str, level: str = "INFO") -> None:
    """Append a timestamped message to the NEXUS log file."""
    normalized_level = level.upper()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{normalized_level}] {message}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")
    if normalized_level in {"WARNING", "ERROR"}:
        print(f"  {entry}")
