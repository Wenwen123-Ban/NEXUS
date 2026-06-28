# ============================================================
# modules/nas/nas_browser.py — Browse files on the configured NAS path
# ============================================================
from __future__ import annotations

from pathlib import Path

from core.config import CONFIG
from core.display import error, menu, pause, section, table, warn
from core.logger import log

MAX_PREVIEW_BYTES = 4096


def _format_bytes(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def _safe_child(root: Path, current: Path, raw: str) -> Path:
    target = (current / raw).expanduser().resolve()
    root_resolved = root.resolve()
    if target != root_resolved and root_resolved not in target.parents:
        raise ValueError("Cannot browse outside the configured NAS path.")
    return target


def list_directory(path: Path) -> list[list[str]]:
    """Return sorted directory entries for display."""
    rows: list[list[str]] = []
    for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        try:
            stat = item.stat()
        except OSError:
            rows.append([item.name, "?", "unreadable"])
            continue
        rows.append([item.name + ("/" if item.is_dir() else ""), _format_bytes(stat.st_size), "dir" if item.is_dir() else "file"])
    return rows


def preview_file(path: Path) -> None:
    section(f"PREVIEW {path.name}")
    try:
        data = path.read_bytes()[:MAX_PREVIEW_BYTES]
    except OSError as exc:
        error(f"Unable to read file: {exc}")
        return
    print(data.decode("utf-8", errors="replace"))
    if path.stat().st_size > MAX_PREVIEW_BYTES:
        warn(f"Preview limited to first {MAX_PREVIEW_BYTES} bytes.")


def run() -> None:
    root = Path(str(CONFIG.get("nas_path", "/mnt/nas"))).expanduser()
    current = root

    if not root.exists() or not root.is_dir():
        section("NAS FILE BROWSER")
        error(f"NAS path is unavailable: {root}")
        warn("Update data/config.json with a mounted NAS directory.")
        log(f"NAS browser unavailable for path: {root}", "ERROR")
        pause()
        return

    while True:
        section(f"NAS FILE BROWSER — {current}")
        try:
            rows = list_directory(current)
        except OSError as exc:
            error(f"Unable to list directory: {exc}")
            log(f"NAS browser failed to list {current}: {exc}", "ERROR")
            pause()
            return

        if rows:
            table(["Name", "Size", "Type"], rows)
        else:
            warn("Directory is empty.")

        choice = menu("BROWSER OPTIONS", ["Open folder", "Go up", "Preview text file"])
        if choice == "1":
            name = input("  Folder name: ").strip()
            try:
                target = _safe_child(root, current, name)
            except ValueError as exc:
                error(str(exc))
                continue
            if target.is_dir():
                current = target
                log(f"NAS browser opened folder: {current}")
            else:
                error("That folder does not exist.")
        elif choice == "2":
            if current.resolve() == root.resolve():
                warn("Already at NAS root.")
            else:
                current = current.parent
        elif choice == "3":
            name = input("  File name: ").strip()
            try:
                target = _safe_child(root, current, name)
            except ValueError as exc:
                error(str(exc))
                continue
            if target.is_file():
                preview_file(target)
                log(f"NAS browser previewed file: {target}")
                pause("  Press Enter to continue browsing...")
            else:
                error("That file does not exist.")
        elif choice == "0":
            break
        else:
            warn("Invalid selection. Choose a listed option.")
