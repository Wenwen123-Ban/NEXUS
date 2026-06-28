# ============================================================
# modules/nas/nas_sync.py — Sync a local folder to the configured NAS path
# ============================================================
from __future__ import annotations

import shutil
from pathlib import Path

from core.config import CONFIG
from core.display import error, pause, section, success, table, warn
from core.logger import log


def collect_files(source: Path) -> list[Path]:
    """Collect regular files below source in deterministic order."""
    return sorted((path for path in source.rglob("*") if path.is_file()), key=lambda p: str(p.relative_to(source)))


def sync_folder(source: Path, destination: Path) -> tuple[int, int]:
    """Copy new or newer files from source into destination, preserving metadata."""
    copied = 0
    skipped = 0
    destination.mkdir(parents=True, exist_ok=True)

    for src_file in collect_files(source):
        rel_path = src_file.relative_to(source)
        dest_file = destination / rel_path
        if dest_file.exists() and dest_file.stat().st_mtime >= src_file.stat().st_mtime and dest_file.stat().st_size == src_file.stat().st_size:
            skipped += 1
            continue
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        copied += 1

    return copied, skipped


def run() -> None:
    section("NAS FOLDER SYNC")
    nas_root = Path(str(CONFIG.get("nas_path", "/mnt/nas"))).expanduser()
    if not nas_root.exists() or not nas_root.is_dir():
        error(f"NAS path is unavailable: {nas_root}")
        warn("Update data/config.json with a mounted NAS directory before syncing.")
        log(f"NAS sync unavailable for path: {nas_root}", "ERROR")
        pause()
        return

    source = Path(input("  Local folder to sync: ").strip()).expanduser()
    if not source.exists() or not source.is_dir():
        error("Source folder does not exist or is not a directory.")
        pause()
        return

    dest_name = input(f"  Destination folder under NAS [{source.name}]: ").strip() or source.name
    destination = (nas_root / dest_name).resolve()
    nas_resolved = nas_root.resolve()
    if destination != nas_resolved and nas_resolved not in destination.parents:
        error("Destination must stay inside the configured NAS path.")
        pause()
        return

    files = collect_files(source)
    table(["Source", "Destination", "Files"], [[str(source), str(destination), len(files)]])
    if not files:
        warn("No files found to sync.")
        pause()
        return

    confirm = input("  Copy new/updated files now? [y/N]: ").strip().lower()
    if confirm != "y":
        warn("Sync cancelled.")
        pause()
        return

    try:
        copied, skipped = sync_folder(source, destination)
    except OSError as exc:
        error(f"Sync failed: {exc}")
        log(f"NAS sync failed from {source} to {destination}: {exc}", "ERROR")
        pause()
        return

    success(f"Sync complete: {copied} copied/updated, {skipped} already current.")
    log(f"NAS sync completed from {source} to {destination}: {copied} copied, {skipped} skipped.")
    pause()
