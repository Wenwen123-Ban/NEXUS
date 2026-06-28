# ============================================================
# modules/nas/nas_web.py — Flask API bridge for the Vite NAS UI
# ============================================================
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.config import CONFIG  # noqa: E402
from core.logger import log  # noqa: E402

app = Flask(__name__)
CORS(app)

NAS_ROOT = Path(str(CONFIG.get("nas_root") or CONFIG.get("nas_path", "./nas_storage"))).expanduser().resolve()
UPLOAD_PATH = Path(str(CONFIG.get("nas_upload_path", str(NAS_ROOT / "uploads")))).expanduser().resolve()
DOWNLOAD_PATH = Path(str(CONFIG.get("nas_download_path", str(NAS_ROOT / "downloads")))).expanduser().resolve()
LOG_PATH = ROOT_DIR / "data" / "nexus.log"

for folder in (NAS_ROOT, UPLOAD_PATH, DOWNLOAD_PATH):
    folder.mkdir(parents=True, exist_ok=True)


def _safe_path(raw_path: str = "") -> Path:
    candidate = Path(raw_path).expanduser().resolve() if raw_path else NAS_ROOT
    if candidate != NAS_ROOT and NAS_ROOT not in candidate.parents:
        candidate = (NAS_ROOT / raw_path).resolve()
    if candidate != NAS_ROOT and NAS_ROOT not in candidate.parents:
        raise ValueError("Access denied.")
    return candidate


@app.route("/api/overview")
def api_overview():
    from modules.nas.nas_monitor import get_stats

    return jsonify(get_stats())


@app.route("/api/files")
def api_files():
    from modules.nas.nas_browser import list_dir

    data = list_dir(request.args.get("path"))
    return (jsonify(data), 403) if "error" in data else jsonify(data)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file in request."}), 400
    upload = request.files["file"]
    filename = secure_filename(upload.filename or f"upload-{uuid4().hex}")
    dest = UPLOAD_PATH / filename
    upload.save(dest)
    size = dest.stat().st_size
    log(f"Upload: {filename} ({size} bytes) -> {dest}")
    return jsonify({"message": f"{filename} uploaded successfully.", "path": str(dest), "size": size})


@app.route("/api/download")
def api_download():
    try:
        full = _safe_path(request.args.get("path", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 403
    if not full.is_file():
        return jsonify({"error": "File not found."}), 404
    log(f"Download: {full}")
    return send_file(full, as_attachment=True)


@app.route("/api/delete", methods=["DELETE"])
def api_delete():
    try:
        full = _safe_path(request.args.get("path", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 403
    if full == NAS_ROOT:
        return jsonify({"error": "Refusing to delete NAS root."}), 400
    if not full.exists():
        return jsonify({"error": "Not found."}), 404
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

    print("\n  [→] NEXUS PY NAS API running on http://localhost:5000")
    print("  [→] Start Vite frontend: cd app && npm run dev")
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:5173")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
