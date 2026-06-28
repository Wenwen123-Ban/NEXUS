# ============================================================
# modules/security/intrusion_log.py — Parse system logs for suspicious IPs
# ============================================================
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from core.config import CONFIG
from core.display import error, pause, section, success, table, warn
from core.logger import log

IP_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
SUSPICIOUS_TERMS = ("failed", "failure", "invalid", "denied", "refused", "authentication failure", "disconnect")
DEFAULT_LOGS = [Path("/var/log/auth.log"), Path("/var/log/secure"), Path("/var/log/syslog")]
MAX_LINES = 10000


def candidate_logs() -> list[Path]:
    """Return configured security logs, or common system logs that exist."""
    configured = CONFIG.get("security_log_paths")
    if isinstance(configured, list) and configured:
        return [Path(str(item)).expanduser() for item in configured]
    return [path for path in DEFAULT_LOGS if path.exists()]


def suspicious_ip_rows(paths: list[Path], max_lines: int = MAX_LINES) -> list[list[str]]:
    """Return suspicious IP counts across readable log files."""
    counts: Counter[str] = Counter()
    sources: dict[str, set[str]] = {}
    for path in paths:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
        for line in lines:
            lowered = line.lower()
            if not any(term in lowered for term in SUSPICIOUS_TERMS):
                continue
            for ip in IP_RE.findall(line):
                counts[ip] += 1
                sources.setdefault(ip, set()).add(path.name)

    return [[ip, str(count), ", ".join(sorted(sources[ip]))] for ip, count in counts.most_common()]


def run() -> None:
    section("INTRUSION LOG PARSER")
    paths = candidate_logs()
    if not paths:
        error("No security logs found. Set security_log_paths in data/config.json.")
        log("Intrusion log parser could not find security logs.", "ERROR")
        pause()
        return

    readable = [path for path in paths if path.exists() and path.is_file()]
    missing = [str(path) for path in paths if path not in readable]
    if missing:
        warn(f"Skipping unavailable log(s): {', '.join(missing)}")

    try:
        rows = suspicious_ip_rows(readable)
    except OSError as exc:
        error(f"Unable to read security logs: {exc}")
        log(f"Intrusion log parser failed: {exc}", "ERROR")
        pause()
        return

    if rows:
        table(["IP Address", "Events", "Log Files"], rows[:25])
        warn(f"Found suspicious activity from {len(rows)} IP address(es).")
        log(f"Intrusion log parser found {len(rows)} suspicious IP address(es).", "WARNING")
    else:
        success("No suspicious IP activity found in the selected logs.")
        log("Intrusion log parser completed with no suspicious IPs.")
    pause()
