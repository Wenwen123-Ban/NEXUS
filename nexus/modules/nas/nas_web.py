# ============================================================
# modules/nas/nas_web.py — Flask NAS API + plain HTML dashboard
# ============================================================
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import shutil
import sys
from functools import wraps
from pathlib import Path
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, send_file, send_from_directory, session
from flask_cors import CORS
from werkzeug.utils import secure_filename

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.config import CONFIG  # noqa: E402
from core.logger import log  # noqa: E402

WEB_DIR_CANDIDATES = (ROOT_DIR / "app", ROOT_DIR)
WEB_DIR = next((path for path in WEB_DIR_CANDIDATES if (path / "index.html").is_file()), ROOT_DIR)
NAS_ROOT = Path(str(CONFIG.get("nas_root") or CONFIG.get("nas_path", "./nas_storage"))).expanduser().resolve()
UPLOAD_PATH = Path(str(CONFIG.get("nas_upload_path", str(NAS_ROOT / "uploads")))).expanduser().resolve()
DOWNLOAD_PATH = Path(str(CONFIG.get("nas_download_path", str(NAS_ROOT / "downloads")))).expanduser().resolve()
LOG_PATH = ROOT_DIR / "data" / "nexus.log"
DATA_DIR = ROOT_DIR / "data"
USERS_PATH = DATA_DIR / "nas_users.json"
TASKS_PATH = DATA_DIR / "nas_tasks.json"
SESSION_SECRET_PATH = DATA_DIR / ".nas_session_secret"

DATA_DIR.mkdir(parents=True, exist_ok=True)
if not SESSION_SECRET_PATH.exists():
    SESSION_SECRET_PATH.write_text(secrets.token_hex(32), encoding="utf-8")

app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=SESSION_SECRET_PATH.read_text(encoding="utf-8").strip(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=str(CONFIG.get("nas_cookie_secure", "false")).lower() == "true",
    MAX_CONTENT_LENGTH=int(CONFIG.get("nas_max_upload_mb", 256)) * 1024 * 1024,
)
CORS(app, supports_credentials=True)

for folder in (NAS_ROOT, UPLOAD_PATH, DOWNLOAD_PATH):
    folder.mkdir(parents=True, exist_ok=True)



def _load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def _save_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _users() -> dict:
    return _load_json(USERS_PATH, {})


def _tasks() -> dict:
    return _load_json(TASKS_PATH, {})


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 260_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt, digest = stored.split("$", 2)
    except ValueError:
        return False
    if algo != "pbkdf2_sha256":
        return False
    candidate = _hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(candidate, digest)


def _current_user() -> str | None:
    user = session.get("nas_user")
    return str(user) if user else None


def _user_root(username: str | None = None) -> Path:
    username = username or _current_user()
    if not username:
        return NAS_ROOT
    root = (NAS_ROOT / "users" / secure_filename(username)).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if _users() and not _current_user():
            return _json_error("Authentication required.", 401)
        return fn(*args, **kwargs)
    return wrapper

def _safe_path(raw_path: str | None = "") -> Path:
    """Resolve a user-supplied path while keeping access inside NAS_ROOT."""
    if not raw_path or raw_path == "root":
        return _user_root()

    root = _user_root()
    raw = Path(raw_path).expanduser()
    candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Access denied.")
    return candidate


def _public_path(path: Path) -> str:
    root = _user_root()
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return path.name
    return "root" if str(rel) == "." else str(rel)


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



@app.route("/api/auth/status")
def api_auth_status():
    users = _users()
    user = _current_user()
    return jsonify({"authenticated": bool(user), "user": user, "registration_open": not bool(users)})


@app.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    if _users():
        return _json_error("Registration is closed because a NAS account already exists.", 403)
    payload = request.get_json(silent=True) or {}
    username = secure_filename(str(payload.get("username") or "")).lower()
    password = str(payload.get("password") or "")
    if len(username) < 3:
        return _json_error("Username must be at least 3 characters.", 400)
    if len(password) < 8:
        return _json_error("Password must be at least 8 characters.", 400)
    users = {username: {"password": _hash_password(password), "created_at": int(time())}}
    _save_json(USERS_PATH, users)
    _user_root(username)
    session.clear()
    session["nas_user"] = username
    log(f"NAS user registered: {username}")
    return jsonify({"message": "Account created.", "user": username})


@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    payload = request.get_json(silent=True) or {}
    username = secure_filename(str(payload.get("username") or "")).lower()
    password = str(payload.get("password") or "")
    user = _users().get(username)
    if not user or not _verify_password(password, user.get("password", "")):
        return _json_error("Invalid username or password.", 401)
    session.clear()
    session["nas_user"] = username
    return jsonify({"message": "Signed in.", "user": username})


@app.route("/api/auth/logout", methods=["POST"])
def api_auth_logout():
    session.clear()
    return jsonify({"message": "Signed out."})

@app.route("/api/overview")
@_auth_required
def api_overview():
    from modules.nas.nas_monitor import get_stats

    return jsonify(get_stats())


@app.route("/api/files")
@_auth_required
def api_files():
    from modules.nas.nas_browser import list_dir

    try:
        target = _safe_path(request.args.get("path"))
    except ValueError as exc:
        return _json_error(str(exc), 403)
    data = list_dir(str(target))
    return (jsonify(data), 403) if "error" in data else jsonify(data)


@app.route("/api/folder", methods=["POST"])
@_auth_required
def api_folder():
    payload = request.get_json(silent=True) or {}
    folder_name = secure_filename(str(payload.get("name") or ""))
    if not folder_name:
        return _json_error("Folder name is required.", 400)
    try:
        parent = _safe_path(payload.get("path") or request.args.get("path"))
        target = (parent / folder_name).resolve()
        root = _user_root()
        if target != root and root not in target.parents:
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
@_auth_required
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
    root = _user_root()
    if dest != root and root not in dest.parents:
        return _json_error("Access denied.", 403)
    upload.save(dest)
    size = dest.stat().st_size
    log(f"Upload: {filename} ({size} bytes) -> {dest}")
    return jsonify({"message": f"{filename} uploaded successfully.", "path": str(dest), "size": size})


@app.route("/api/download")
@_auth_required
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
@_auth_required
def api_delete():
    try:
        full = _safe_path(request.args.get("path", ""))
    except ValueError as exc:
        return _json_error(str(exc), 403)
    if full == _user_root():
        return _json_error("Refusing to delete NAS root.", 400)
    if not full.exists():
        return _json_error("Not found.", 404)
    os.remove(full) if full.is_file() else shutil.rmtree(full)
    log(f"Deleted: {full}")
    return jsonify({"message": "Deleted."})



@app.route("/api/tasks", methods=["GET", "POST"])
@_auth_required
def api_tasks():
    user = _current_user() or "default"
    data = _tasks()
    if request.method == "GET":
        return jsonify({"tasks": data.get(user, [])})
    payload = request.get_json(silent=True) or {}
    task = {
        "id": secure_filename(str(payload.get("id") or f"task-{uuid4().hex}")),
        "name": str(payload.get("name") or "Recorded task")[:160],
        "type": str(payload.get("type") or "download"),
        "progress": float(payload.get("progress") or 0),
        "speed": payload.get("speed"),
        "eta": payload.get("eta"),
        "status": str(payload.get("status") or "queued"),
        "created_at": int(time()),
    }
    data[user] = [task, *data.get(user, [])]
    _save_json(TASKS_PATH, data)
    return jsonify({"message": "Task saved.", "task": task})


@app.route("/api/tasks/<task_id>", methods=["PATCH", "DELETE"])
@_auth_required
def api_task(task_id: str):
    user = _current_user() or "default"
    data = _tasks()
    tasks = data.get(user, [])
    idx = next((i for i, task in enumerate(tasks) if task.get("id") == task_id), None)
    if idx is None:
        return _json_error("Task not found.", 404)
    if request.method == "DELETE":
        removed = tasks.pop(idx)
        data[user] = tasks
        _save_json(TASKS_PATH, data)
        return jsonify({"message": "Task deleted.", "task": removed})
    patch = request.get_json(silent=True) or {}
    allowed = {"name", "type", "progress", "speed", "eta", "status"}
    tasks[idx].update({key: patch[key] for key in allowed if key in patch})
    data[user] = tasks
    _save_json(TASKS_PATH, data)
    return jsonify({"message": "Task updated.", "task": tasks[idx]})


@app.route("/api/logs")
@_auth_required
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
    print(f"  [→] Serving dashboard files from {WEB_DIR}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
