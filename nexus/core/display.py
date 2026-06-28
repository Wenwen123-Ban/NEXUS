# ============================================================
# core/display.py — Shared CLI display helpers
# Colors, banners, menus, tables
# ============================================================
import os

# ANSI color codes
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    DIM    = "\033[2m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(f"""{C.CYAN}{C.BOLD}
  ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
  ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
  ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
  ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
  ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{C.DIM}  Node EXecution & Unified System  |  v1.0{C.RESET}
""")

def menu(title: str, options: list) -> str:
    print(f"  {C.YELLOW}{C.BOLD}[ {title} ]{C.RESET}")
    print(f"  {C.DIM}{'─' * 34}{C.RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {C.GREEN}[{i}]{C.RESET} {opt}")
    print(f"  {C.RED}[0]{C.RESET} Exit / Back")
    print(f"  {C.DIM}{'─' * 34}{C.RESET}")
    return input(f"  {C.CYAN}>{C.RESET} ").strip()

def section(title: str):
    print(f"\n  {C.CYAN}{C.BOLD}── {title} ──{C.RESET}\n")

def success(msg: str):
    print(f"  {C.GREEN}[✓]{C.RESET} {msg}")

def warn(msg: str):
    print(f"  {C.YELLOW}[!]{C.RESET} {msg}")

def error(msg: str):
    print(f"  {C.RED}[✗]{C.RESET} {msg}")

def table(headers: list, rows: list):
    widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    row_fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    sep = "  " + "  ".join("─" * w for w in widths)
    print(f"{C.DIM}{sep}{C.RESET}")
    print(f"{C.BOLD}" + row_fmt.format(*headers) + f"{C.RESET}")
    print(f"{C.DIM}{sep}{C.RESET}")
    for row in rows:
        print(row_fmt.format(*[str(c) for c in row]))
    print(f"{C.DIM}{sep}{C.RESET}")
