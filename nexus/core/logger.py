# ============================================================
# core/logger.py — Shared logging utility
# All modules write here via log()
# ============================================================
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "nexus.log")

def log(message: str, level: str = "INFO"):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    with open(LOG_PATH, "a") as f:
        f.write(entry + "\n")
    if level in ("WARNING", "ERROR"):
        print(f"  {entry}")
