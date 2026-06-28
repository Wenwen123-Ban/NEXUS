# ============================================================
# modules/nas/nas_web.py — Flask NAS API + plain HTML dashboard
# ============================================================
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.config import CONFIG  # noqa: E402
from core.logger import log  # noqa: E402

WEB_DIR = ROOT_DIR / "app"
NAS_ROOT = Path(str(CONFIG.get("nas_root") or CONFIG.get("nas_path", "./nas_storage"))).expanduser().resolve()
UPLOAD_PATH = Path(str(CONFIG.get("nas_upload_path", str(NAS_ROOT / "uploads")))).expanduser().resolve()
DOWNLOAD_PATH = Path(str(CONFIG.get("nas_download_path", str(NAS_ROOT / "downloads")))).expanduser().resolve()
LOG_PATH = ROOT_DIR / "data" / "nexus.log"

app = Flask(__name__, static_folder=None)
CORS(app)

for folder in (NAS_ROOT, UPLOAD_PATH, DOWNLOAD_PATH):
    folder.mkdir(parents=True, exist_ok=True)


def _safe_path(raw_path: str | None = "") -> Path:
    """Resolve a user-supplied path while keeping access inside NAS_ROOT."""
    if not raw_path or raw_path == "root":
        return NAS_ROOT

    raw = Path(raw_path).expanduser()
    candidate = raw.resolve() if raw.is_absolute() else (NAS_ROOT / raw).resolve()
    if candidate != NAS_ROOT and NAS_ROOT not in candidate.parents:
        raise ValueError("Access denied.")
    return candidate


def _json_error(message: str, status: int):
    return jsonify({"error": message}), status


@app.route("/")
def web_index():
    """Serve the plain HTML/CSS/JS dashboard directly from NEXUS."""
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/<path:filename>")
def web_asset(filename: str):
    """Serve dashboard assets without requiring any React/Vite dev server."""
    target = (WEB_DIR / filename).resolve()
    if WEB_DIR not in target.parents and target != WEB_DIR:
        return _json_error("Access denied.", 403)
    if target.is_file():
        return send_from_directory(WEB_DIR, filename)
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/api/overview")
def api_overview():
    from modules.nas.nas_monitor import get_stats

    return jsonify(get_stats())


@app.route("/api/files")
def api_files():
    from modules.nas.nas_browser import list_dir

    try:
        target = _safe_path(request.args.get("path"))
    except ValueError as exc:
        return _json_error(str(exc), 403)
    data = list_dir(str(target))
    return (jsonify(data), 403) if "error" in data else jsonify(data)


@app.route("/api/folder", methods=["POST"])
def api_folder():
    payload = request.get_json(silent=True) or {}
    folder_name = secure_filename(str(payload.get("name") or ""))
    if not folder_name:
        return _json_error("Folder name is required.", 400)
    try:
        parent = _safe_path(payload.get("path") or request.args.get("path"))
        target = (parent / folder_name).resolve()
        if target != NAS_ROOT and NAS_ROOT not in target.parents:
            raise ValueError("Access denied.")
    except ValueError as exc:
        return _json_error(str(exc), 403)
    try:
        target.mkdir(parents=False, exist_ok=False)
    except FileExistsError:
        return _json_error("Folder already exists.", 409)
    except OSError as exc:
        return _json_error(f"Unable to create folder: {exc}", 500)
    log(f"Created folder: {target}")
    return jsonify({"message": "Folder created.", "path": str(target)})


@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return _json_error("No file in request.", 400)
    try:
        upload_dir = _safe_path(request.args.get("path"))
    except ValueError as exc:
        return _json_error(str(exc), 403)
    if not upload_dir.is_dir():
        return _json_error("Upload target is not a folder.", 400)

    upload = request.files["file"]
    filename = secure_filename(upload.filename or f"upload-{uuid4().hex}")
    dest = (upload_dir / filename).resolve()
    if dest != NAS_ROOT and NAS_ROOT not in dest.parents:
        return _json_error("Access denied.", 403)
    upload.save(dest)
    size = dest.stat().st_size
    log(f"Upload: {filename} ({size} bytes) -> {dest}")
    return jsonify({"message": f"{filename} uploaded successfully.", "path": str(dest), "size": size})


@app.route("/api/download")
def api_download():
    try:
        full = _safe_path(request.args.get("path", ""))
    except ValueError as exc:
        return _json_error(str(exc), 403)
    if not full.is_file():
        return _json_error("File not found.", 404)
    log(f"Download: {full}")
    return send_file(full, as_attachment=True)


@app.route("/api/delete", methods=["DELETE"])
def api_delete():
    try:
        full = _safe_path(request.args.get("path", ""))
    except ValueError as exc:
        return _json_error(str(exc), 403)
    if full == NAS_ROOT:
        return _json_error("Refusing to delete NAS root.", 400)
    if not full.exists():
        return _json_error("Not found.", 404)
    os.remove(full) if full.is_file() else shutil.rmtree(full)
    log(f"Deleted: {full}")
    return jsonify({"message": "Deleted."})


@app.route("/api/logs")
def api_logs():
    if not LOG_PATH.exists():
        return jsonify({"lines": []})
    with LOG_PATH.open(encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return jsonify({"lines": [line.rstrip() for line in lines[-50:]][::-1]})


def run() -> None:
    import threading
    import webbrowser

    url = "http://localhost:5000"
    print(f"\n  [→] NEXUS NAS web dashboard running on {url}")
    print("  [→] Serving nexus/app directly; no React or Vite server is required.")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
