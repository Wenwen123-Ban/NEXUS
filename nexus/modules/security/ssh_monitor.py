# ============================================================
# modules/security/ssh_monitor.py — Inspect recent SSH authentication failures
# ============================================================
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from core.config import CONFIG
from core.display import error, pause, section, success, table, warn
from core.logger import log

DEFAULT_AUTH_LOGS = [Path("/var/log/auth.log"), Path("/var/log/secure")]
FAILED_SSH_RE = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>[\w:.\-]+)")
MAX_LINES = 5000


def auth_log_path() -> Path | None:
    """Return the configured or first common readable authentication log path."""
    configured = CONFIG.get("auth_log_path")
    if configured:
        return Path(str(configured)).expanduser()

    for path in DEFAULT_AUTH_LOGS:
        if path.exists():
            return path
    return None


def failed_ssh_attempts(path: Path, max_lines: int = MAX_LINES) -> list[list[str]]:
    """Parse failed SSH attempts and return rows grouped by source IP and user."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    attempts: Counter[tuple[str, str]] = Counter()
    for line in lines:
        match = FAILED_SSH_RE.search(line)
        if match:
            attempts[(match.group("ip"), match.group("user"))] += 1

    return [[ip, user, str(count)] for (ip, user), count in attempts.most_common()]


def run() -> None:
    section("SSH LOGIN MONITOR")
    path = auth_log_path()
    if path is None:
        error("No authentication log found. Set auth_log_path in data/config.json.")
        log("SSH monitor could not find an authentication log.", "ERROR")
        pause()
        return

    if not path.exists() or not path.is_file():
        error(f"Authentication log is unavailable: {path}")
        log(f"SSH monitor authentication log unavailable: {path}", "ERROR")
        pause()
        return

    try:
        rows = failed_ssh_attempts(path)
    except OSError as exc:
        error(f"Unable to read authentication log: {exc}")
        log(f"SSH monitor failed reading {path}: {exc}", "ERROR")
        pause()
        return

    if rows:
        table(["Source IP", "Username", "Failures"], rows[:25])
        warn(f"Detected {sum(int(row[2]) for row in rows)} failed SSH login attempt(s).")
        log(f"SSH monitor found {len(rows)} source/user failure group(s) in {path}.", "WARNING")
    else:
        success(f"No failed SSH password attempts found in the last {MAX_LINES} log line(s).")
        log(f"SSH monitor completed with no failures in {path}.")
    pause()
