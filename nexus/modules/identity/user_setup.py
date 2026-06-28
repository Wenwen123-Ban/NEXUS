# ============================================================
# modules/identity/user_setup.py — NEXUS ID first-time setup
# ============================================================
from __future__ import annotations

import hashlib
import json
import re
import socket
from datetime import date

from core.config import DATA_DIR
from core.display import error, section, success, warn
from core.logger import log

USER_PATH = DATA_DIR / "users.json"
VALID_COLORS = {"cyan", "green", "yellow"}
DEFAULT_PORT = 9876


def get_local_ip() -> str:
    """Detect the machine's LAN IP, falling back safely to localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"


def hash_password(password: str) -> str:
    """Return a SHA-256 hex digest for the provided password."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_username(name: str) -> bool:
    """Validate 3-20 characters using letters, numbers, and underscores."""
    return re.match(r"^[a-zA-Z0-9_]{3,20}$", name) is not None


def _prompt_username() -> str:
    while True:
        username = input("  Choose username (3-20 letters/numbers/_): ").strip()
        if validate_username(username):
            return username
        error("Username must be 3-20 characters and use only letters, numbers, or underscore.")


def _prompt_password() -> str:
    while True:
        password = input("  Choose password (min 6 chars): ").strip()
        confirm = input("  Confirm password: ").strip()
        if len(password) < 6:
            error("Password must be at least 6 characters.")
        elif password != confirm:
            error("Passwords do not match.")
        else:
            return password


def _prompt_color() -> str:
    while True:
        color = input("  Chat color [cyan/green/yellow] (cyan): ").strip().lower() or "cyan"
        if color in VALID_COLORS:
            return color
        error("Choose one of: cyan, green, yellow.")


def save_user(user: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with USER_PATH.open("w", encoding="utf-8") as f:
        json.dump(user, f, indent=4)
        f.write("\n")


def run_setup() -> dict:
    """Run the first-time local identity wizard and save data/users.json."""
    section("NEXUS ID SETUP")
    print("  Create your local NEXUS identity. This stays on this machine only.\n")
    username = _prompt_username()
    password = _prompt_password()
    ip = get_local_ip()
    print(f"  Detected IP: {ip}")
    color = _prompt_color()
    user = {
        "username": username,
        "password": hash_password(password),
        "ip": ip,
        "port": DEFAULT_PORT,
        "color": color,
        "created_at": date.today().isoformat(),
    }
    save_user(user)
    log(f"NEXUS ID setup completed for {username} @ {ip}.")
    success(f"Setup complete. Welcome, {username}.")
    return user
