# ============================================================
# modules/identity/auth.py — NEXUS ID login gate
# ============================================================
from __future__ import annotations

import json
import time

from core.config import DATA_DIR
from core.display import error, section, success, warn
from core.logger import log
from modules.identity.user_setup import hash_password

USER_PATH = DATA_DIR / "users.json"


def load_user() -> dict | None:
    """Load the local identity file, returning None when missing or invalid."""
    if not USER_PATH.exists():
        return None
    try:
        with USER_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError) as exc:
        log(f"Unable to load NEXUS ID: {exc}", "ERROR")
        return None


def check_password(input_password: str, stored_hash: str) -> bool:
    """Hash user input and compare it to the stored SHA-256 digest."""
    return hash_password(input_password) == stored_hash


def is_first_run() -> bool:
    """Return True when no local identity exists yet."""
    return not USER_PATH.exists()


def login() -> dict | None:
    """Require password login with a three-attempt limit."""
    user = load_user()
    if user is None:
        error("No NEXUS ID found. Run setup first.")
        return None

    section("NEXUS — LOGIN")
    print(f"  User: {user.get('username', 'unknown')}\n")
    stored_hash = str(user.get("password", ""))
    for attempt in range(1, 4):
        password = input("  Password: ").strip()
        if check_password(password, stored_hash):
            success("Login accepted.")
            log(f"NEXUS ID login successful for {user.get('username', 'unknown')}.")
            return user
        remaining = 3 - attempt
        warn(f"Incorrect password. {remaining} attempt(s) remaining.")
        log(f"Failed NEXUS ID login attempt for {user.get('username', 'unknown')}.", "WARNING")

    error("Too many failed attempts. Locked for 30 seconds.")
    time.sleep(30)
    return None
