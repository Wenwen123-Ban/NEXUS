# ============================================================
# modules/nas/nas_browser.py — Browse files on the configured NAS path
# ============================================================
from __future__ import annotations

from pathlib import Path

from core.config import CONFIG
from core.display import error, pause, section, table, warn
from core.logger import log

MAX_PREVIEW_BYTES = 4096


def _nas_root() -> Path:
    return Path(str(CONFIG.get("nas_root") or CONFIG.get("nas_path", "./nas_storage"))).expanduser().resolve()


def _safe_target(path: str | None = None) -> Path:
    root = _nas_root()
    target = Path(path).expanduser().resolve() if path else root
    if target != root and root not in target.parents:
        raise ValueError("Access denied — outside NAS root.")
    return target


def _format_bytes(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def list_dir(path: str | None = None) -> dict:
    """Return a JSON-safe directory listing rooted inside configured NAS storage."""
    try:
        target = _safe_target(path)
    except ValueError as exc:
        return {"error": str(exc)}

    target.mkdir(parents=True, exist_ok=True)
    try:
        items = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError as exc:
        return {"error": f"Unable to list directory: {exc}"}

    entries = []
    for item in items:
        try:
            stat = item.stat()
            size = stat.st_size if item.is_file() else 0
            mtime = stat.st_mtime
        except OSError:
            size = 0
            mtime = 0
        entries.append({"name": item.name, "path": str(item), "is_dir": item.is_dir(), "size": size, "mtime": mtime})

    root = _nas_root()
    return {"current": str(target), "root": str(root), "parent": str(target.parent) if target != root else None, "entries": entries}


def list_directory(path: Path) -> list[list[str]]:
    """Return sorted directory entries for CLI display."""
    data = list_dir(str(path))
    if "error" in data:
        raise OSError(data["error"])
    return [[e["name"] + ("/" if e["is_dir"] else ""), _format_bytes(e["size"]), "dir" if e["is_dir"] else "file"] for e in data["entries"]]


def preview_file(path: Path) -> None:
    section(f"PREVIEW {path.name}")
    try:
        target = _safe_target(str(path))
        data = target.read_bytes()[:MAX_PREVIEW_BYTES]
    except (OSError, ValueError) as exc:
        error(f"Unable to read file: {exc}")
        return
    print(data.decode("utf-8", errors="replace"))
    if target.stat().st_size > MAX_PREVIEW_BYTES:
        warn(f"Preview limited to first {MAX_PREVIEW_BYTES} bytes.")


def run() -> None:
    section("NAS FILE BROWSER")
    data = list_dir()
    if "error" in data:
        error(data["error"])
        pause()
        return
    rows = [[e["name"], "DIR" if e["is_dir"] else "FILE", _format_bytes(e["size"])] for e in data["entries"]]
    if rows:
        table(["Name", "Type", "Size"], rows)
    else:
        warn("Directory is empty.")
    log(f"NAS browser listed {data['current']}")
    pause()
