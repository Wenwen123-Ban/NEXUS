# ============================================================
# core/display.py — Shared CLI display helpers
# Colors, banners, menus, tables
# ============================================================
from __future__ import annotations

import os
from collections.abc import Sequence


# ANSI color codes
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    DIM = "\033[2m"


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner(username: str = "") -> None:
    user_line = f"  Logged in as: {username}" if username else ""
    print(f"""{C.CYAN}{C.BOLD}
  ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
  ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
  ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
  ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
  ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{C.DIM}  Node EXecution & Unified System  |  v1.1{C.RESET}
{C.DIM}{user_line}{C.RESET}
""")


def menu(title: str, options: Sequence[str]) -> str:
    print(f"  {C.YELLOW}{C.BOLD}[ {title} ]{C.RESET}")
    print(f"  {C.DIM}{'─' * 34}{C.RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {C.GREEN}[{i}]{C.RESET} {opt}")
    print(f"  {C.RED}[0]{C.RESET} Exit / Back")
    print(f"  {C.DIM}{'─' * 34}{C.RESET}")
    return input(f"  {C.CYAN}>{C.RESET} ").strip()


def section(title: str) -> None:
    print(f"\n  {C.CYAN}{C.BOLD}── {title} ──{C.RESET}\n")


def success(msg: str) -> None:
    print(f"  {C.GREEN}[✓]{C.RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {C.YELLOW}[!]{C.RESET} {msg}")


def error(msg: str) -> None:
    print(f"  {C.RED}[✗]{C.RESET} {msg}")


def pause(prompt: str = "  Press Enter to go back...") -> None:
    input(prompt)


def table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> None:
    if not headers:
        warn("No table headers provided.")
        return

    normalized_rows = [list(row) for row in rows]
    widths = [
        max(len(str(row[i])) for row in ([list(headers)] + normalized_rows))
        for i in range(len(headers))
    ]
    row_fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    sep = "  " + "  ".join("─" * w for w in widths)
    print(f"{C.DIM}{sep}{C.RESET}")
    print(f"{C.BOLD}" + row_fmt.format(*headers) + f"{C.RESET}")
    print(f"{C.DIM}{sep}{C.RESET}")
    for row in normalized_rows:
        print(row_fmt.format(*[str(c) for c in row]))
    print(f"{C.DIM}{sep}{C.RESET}")
