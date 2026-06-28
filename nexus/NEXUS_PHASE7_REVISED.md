# ─────────────────────────────────────────────────────────────
# PHASE 7 — NEXUS PY NAS  (Vite Frontend ↔ Flask Backend)
# ─────────────────────────────────────────────────────────────

## What This Phase Does

Connects the existing Vite + TypeScript frontend in `app/` to the
Python NAS modules in `modules/nas/` through a Flask API layer.
The UI follows the design reference: a dark dashboard with a server
status card, CPU/RAM/Temp/Network stats, storage pool bar, and a
physical disk list — plus a File Station tab for browsing, uploading,
and downloading files.

**Fixes the headless problem:** right now `nas_browser.py` and
`nas_sync.py` ask for paths interactively. This phase anchors them
to fixed paths in `data/config.json` so the web frontend can call
them without user input.

---

## Current State vs Target State

```
BEFORE (headless, path questions)          AFTER (connected)
─────────────────────────────────          ──────────────────────────────────
python main.py                             python main.py
→ NAS Manager                              → NAS Manager → [4] Launch Web
→ File Browser                                 Flask starts on :5000
→ "Enter path: ____"   ← problem              Vite dev server on :5173
                                               Browser opens dashboard
                                               All paths come from config.json
```

---

## Full Architecture

```
                    Browser (http://localhost:5173)
                            │
                    ┌───────▼────────┐
                    │   Vite App     │  app/src/
                    │  (TypeScript)  │  Fetches /api/* via proxy
                    └───────┬────────┘
                            │ proxy → :5000
                    ┌───────▼────────┐
                    │  Flask Server  │  modules/nas/nas_web.py
                    │  (port 5000)   │  Serves JSON only
                    └───────┬────────┘
                            │ imports
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       nas_monitor.py  nas_browser.py  nas_sync.py
       (disk/cpu/ram)  (list/upload/   (mirror
                        download)       folders)
```

---

## Step 0 — Fix the Headless Problem First

**This is the root cause.** Open `data/config.json` and add these
three keys. Every module reads from here instead of asking the user.

```json
{
    "sender_email":         "your_email@gmail.com",
    "sender_password":      "your_app_password",
    "smtp_server":          "smtp.gmail.com",
    "smtp_port":            587,
    "alert_email":          "your_email@gmail.com",

    "nas_root":             "C:/NAS",
    "nas_upload_path":      "C:/NAS/uploads",
    "nas_download_path":    "C:/NAS/downloads",
    "nas_sync_source":      "C:/Users/YourName/Projects/nexus",

    "cpu_alert_threshold":  90,
    "ram_alert_threshold":  85,
    "disk_alert_threshold": 90,
    "ping_range":           "192.168.1.1-254"
}
```

> Replace `C:/NAS` with any real folder on your machine.
> On Linux/T3500 use `/mnt/nas` or `/srv/nas`.
> Create the folders first:
> ```bash
> mkdir -p C:/NAS/uploads C:/NAS/downloads
> # or on Linux:
> mkdir -p /mnt/nas/uploads /mnt/nas/downloads
> ```

Then update `core/config.py` to expose the new keys:

```python
DEFAULTS = {
    ...
    "nas_root":          "./nas_storage",
    "nas_upload_path":   "./nas_storage/uploads",
    "nas_download_path": "./nas_storage/downloads",
    "nas_sync_source":   "",
    ...
}
```

---

## Step 1 — Update nas_monitor.py (feeds the dashboard cards)

`nas_monitor.py` needs a `get_stats()` function that returns JSON-
serializable data. The Flask API will call this directly.

```python
# modules/nas/nas_monitor.py

import psutil
import platform
from core.config import CONFIG

def get_stats() -> dict:
    """Returns all stats needed by the dashboard Overview tab."""
    cpu     = psutil.cpu_percent(interval=0.5)
    ram     = psutil.virtual_memory()
    temps   = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
    net     = psutil.net_io_counters()
    nas_root = CONFIG.get("nas_root", "/")

    # System temp — first available sensor, fallback to None
    temp_c = None
    for sensor_list in temps.values():
        if sensor_list:
            temp_c = round(sensor_list[0].current, 1)
            break

    # Disk stats for the configured NAS root
    try:
        disk = psutil.disk_usage(nas_root)
        disk_pct   = disk.percent
        disk_used  = disk.used
        disk_total = disk.total
        disk_free  = disk.free
    except Exception:
        disk_pct = disk_used = disk_total = disk_free = 0

    # All mounted drives (Physical Disks panel)
    drives = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
            drives.append({
                "device":     p.device,
                "mountpoint": p.mountpoint,
                "fstype":     p.fstype,
                "percent":    u.percent,
                "used_gb":    round(u.used  / 1e9, 1),
                "total_gb":   round(u.total / 1e9, 1),
                "free_gb":    round(u.free  / 1e9, 1),
            })
        except PermissionError:
            continue

    return {
        "server_name":  platform.node() or "NAS-Server-01",
        "platform":     platform.system(),
        "cpu_percent":  cpu,
        "ram_percent":  ram.percent,
        "ram_used_gb":  round(ram.used  / 1e9, 1),
        "ram_total_gb": round(ram.total / 1e9, 1),
        "temp_c":       temp_c,
        "net_dl_kbs":   round(net.bytes_recv / 1024, 1),
        "net_ul_kbs":   round(net.bytes_sent / 1024, 1),
        "disk_percent": disk_pct,
        "disk_used_gb": round(disk_used  / 1e9, 1),
        "disk_total_gb":round(disk_total / 1e9, 1),
        "disk_free_gb": round(disk_free  / 1e9, 1),
        "nas_root":     nas_root,
        "drives":       drives,
    }

def run():
    """CLI fallback — called from nas_menu."""
    from core.display import section, table
    section("NAS MONITOR")
    s = get_stats()
    table(
        ["Metric", "Value"],
        [
            ["CPU",   f"{s['cpu_percent']}%"],
            ["RAM",   f"{s['ram_percent']}%"],
            ["Temp",  f"{s['temp_c']} °C" if s['temp_c'] else "N/A"],
            ["Disk",  f"{s['disk_percent']}%  ({s['disk_used_gb']} / {s['disk_total_gb']} GB)"],
        ]
    )
    input("\n  Press Enter to go back...")
```

---

## Step 2 — Update nas_browser.py (feeds File Station tab)

Replace the interactive path prompt with path from config:

```python
# modules/nas/nas_browser.py

import os
from core.config import CONFIG

NAS_ROOT = CONFIG.get("nas_root", "./nas_storage")

def list_dir(path: str = None) -> dict:
    """
    Returns directory listing. Path must stay inside NAS_ROOT.
    Called by Flask /api/files endpoint.
    """
    target = os.path.abspath(path or NAS_ROOT)

    # Security: block path traversal above NAS_ROOT
    if not target.startswith(os.path.abspath(NAS_ROOT)):
        return {"error": "Access denied — outside NAS root."}

    if not os.path.exists(target):
        os.makedirs(target, exist_ok=True)

    entries = []
    for name in sorted(os.listdir(target)):
        full   = os.path.join(target, name)
        is_dir = os.path.isdir(full)
        try:
            size  = os.path.getsize(full) if not is_dir else 0
            mtime = os.path.getmtime(full)
        except Exception:
            size, mtime = 0, 0
        entries.append({
            "name":    name,
            "path":    full,
            "is_dir":  is_dir,
            "size":    size,
            "mtime":   mtime,
        })

    return {
        "current": target,
        "root":    os.path.abspath(NAS_ROOT),
        "parent":  str(os.path.dirname(target)) if target != os.path.abspath(NAS_ROOT) else None,
        "entries": entries,
    }

def run():
    """CLI fallback."""
    from core.display import section, table
    section("NAS FILE BROWSER")
    data = list_dir()
    rows = [[e["name"], "DIR" if e["is_dir"] else "FILE"] for e in data["entries"]]
    table(["Name", "Type"], rows)
    input("\n  Press Enter to go back...")
```

---

## Step 3 — Write nas_web.py (the Flask API bridge)

This file is the only thing the Vite frontend talks to.
It imports from the updated `nas_monitor.py` and `nas_browser.py`
and exposes clean JSON endpoints.

```python
# modules/nas/nas_web.py

import os, json, shutil
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from core.config import CONFIG
from core.logger import log

app = Flask(__name__)
CORS(app)   # Allow Vite dev server (different port) to call the API

NAS_ROOT     = CONFIG.get("nas_root",          "./nas_storage")
UPLOAD_PATH  = CONFIG.get("nas_upload_path",   "./nas_storage/uploads")
DOWNLOAD_PATH= CONFIG.get("nas_download_path", "./nas_storage/downloads")
LOG_PATH     = os.path.join("data", "nexus.log")

os.makedirs(UPLOAD_PATH,   exist_ok=True)
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# ── Overview tab endpoints ─────────────────────────────────────
@app.route("/api/overview")
def api_overview():
    from modules.nas.nas_monitor import get_stats
    return jsonify(get_stats())

# ── File Station tab endpoints ────────────────────────────────
@app.route("/api/files")
def api_files():
    from modules.nas.nas_browser import list_dir
    path = request.args.get("path", None)
    data = list_dir(path)
    if "error" in data:
        return jsonify(data), 403
    return jsonify(data)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Receives a file from the browser and saves to nas_upload_path."""
    if "file" not in request.files:
        return jsonify({"error": "No file in request."}), 400
    f    = request.files["file"]
    dest = os.path.join(UPLOAD_PATH, f.filename)
    f.save(dest)
    size = os.path.getsize(dest)
    log(f"Upload: {f.filename} ({size} bytes) → {dest}")
    return jsonify({"message": f"{f.filename} uploaded successfully.", "path": dest})

@app.route("/api/download")
def api_download():
    """Sends a file from the NAS root to the browser."""
    rel  = request.args.get("path", "")
    full = os.path.abspath(os.path.join(NAS_ROOT, rel))
    # Security check
    if not full.startswith(os.path.abspath(NAS_ROOT)):
        return jsonify({"error": "Access denied."}), 403
    if not os.path.isfile(full):
        return jsonify({"error": "File not found."}), 404
    log(f"Download: {full}")
    return send_file(full, as_attachment=True)

@app.route("/api/delete", methods=["DELETE"])
def api_delete():
    """Deletes a file inside NAS root."""
    rel  = request.args.get("path", "")
    full = os.path.abspath(os.path.join(NAS_ROOT, rel))
    if not full.startswith(os.path.abspath(NAS_ROOT)):
        return jsonify({"error": "Access denied."}), 403
    if not os.path.exists(full):
        return jsonify({"error": "Not found."}), 404
    os.remove(full) if os.path.isfile(full) else shutil.rmtree(full)
    log(f"Deleted: {full}")
    return jsonify({"message": "Deleted."})

# ── Log feed ──────────────────────────────────────────────────
@app.route("/api/logs")
def api_logs():
    if not os.path.exists(LOG_PATH):
        return jsonify({"lines": []})
    with open(LOG_PATH) as f:
        lines = f.readlines()
    return jsonify({"lines": [l.rstrip() for l in lines[-50:]][::-1]})

# ── Launcher ──────────────────────────────────────────────────
def run():
    import threading, webbrowser
    print("\n  [→] NEXUS PY NAS API running on http://localhost:5000")
    print("  [→] Start Vite frontend: cd app && npm run dev")
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:5173")).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    run()
```

---

## Step 4 — Configure the Vite Proxy (app/vite.config.ts)

Vite runs on port 5173. Any call to `/api/*` gets forwarded to Flask
on port 5000. You do NOT need to type the full URL in your TypeScript.

Open `app/vite.config.ts` and add the `server.proxy` block:

```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
```

After this, inside your TypeScript you simply call:
```typescript
const res  = await fetch('/api/overview');   // goes to Flask :5000
const data = await res.json();
```

---

## Step 5 — Map the Design to API Endpoints

Use this table to know which API call populates each UI section:

```
Dashboard Panel              API Endpoint         Key fields
────────────────────────     ─────────────────    ──────────────────────────────
Header "Nexus NAS"           /api/overview        server_name, platform
Server status card           /api/overview        server_name (Healthy = online)
CPU Load card                /api/overview        cpu_percent
RAM Usage card               /api/overview        ram_percent, ram_used_gb
System Temp card             /api/overview        temp_c
Network Rates card           /api/overview        net_dl_kbs, net_ul_kbs
Storage Pools bar            /api/overview        disk_percent, disk_used_gb,
                                                  disk_total_gb
Physical Disks list          /api/overview        drives[] array
File Station → folder list   /api/files?path=     entries[], current, parent
File Station → upload btn    /api/upload  POST    multipart form-data
File Station → download btn  /api/download?path=  sends file blob
File Station → delete btn    /api/delete?path=    DELETE method
Activity log                 /api/logs            lines[]
```

---

## Step 6 — Install Requirements

```bash
# Backend
pip install flask flask-cors psutil

# Frontend (if not done yet)
cd app
npm install
```

---

## Step 7 — How to Run the Full Stack

You need **two terminals open at the same time:**

**Terminal 1 — Flask API**
```bash
# From the nexus/ root
python modules/nas/nas_web.py
# Or via: python main.py → NAS Manager → Launch Web Dashboard
```

**Terminal 2 — Vite Frontend**
```bash
cd app
npm run dev
# Vite starts on http://localhost:5173
```

Then open `http://localhost:5173` — the frontend fetches data from
Flask automatically through the proxy.

---

## Step 8 — TypeScript API helper (app/src/api.ts)

Create this file once and import it everywhere in your components.
It gives you typed, consistent access to every backend endpoint.

```typescript
// app/src/api.ts

const BASE = '/api';

export async function getOverview() {
  const res = await fetch(`${BASE}/overview`);
  return res.json();
}

export async function getFiles(path?: string) {
  const url = path
    ? `${BASE}/files?path=${encodeURIComponent(path)}`
    : `${BASE}/files`;
  const res = await fetch(url);
  return res.json();
}

export async function uploadFile(file: File): Promise<{ message: string }> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
  return res.json();
}

export async function downloadFile(path: string) {
  window.location.href = `${BASE}/download?path=${encodeURIComponent(path)}`;
}

export async function deleteFile(path: string): Promise<{ message: string }> {
  const res = await fetch(
    `${BASE}/delete?path=${encodeURIComponent(path)}`,
    { method: 'DELETE' }
  );
  return res.json();
}

export async function getLogs(): Promise<{ lines: string[] }> {
  const res = await fetch(`${BASE}/logs`);
  return res.json();
}
```

Usage in any component:
```typescript
import { getOverview, getFiles, uploadFile } from '../api';

const stats = await getOverview();
console.log(stats.cpu_percent);   // 19
console.log(stats.drives);        // [{ device, mountpoint, percent ... }]
```

---

## Phase 7 Checklist

**Backend:**
- [ ] `data/config.json` has `nas_root`, `nas_upload_path`, `nas_download_path`
- [ ] Target folders physically exist on disk
- [ ] `nas_monitor.py` has `get_stats()` function (no CLI prompts)
- [ ] `nas_browser.py` has `list_dir()` function (uses config path, no prompts)
- [ ] `nas_web.py` written with all 6 endpoints
- [ ] `flask` and `flask-cors` installed
- [ ] `python modules/nas/nas_web.py` starts without error
- [ ] `http://localhost:5000/api/overview` returns JSON in browser

**Frontend:**
- [ ] `app/vite.config.ts` has proxy block pointing to `:5000`
- [ ] `app/src/api.ts` created
- [ ] `npm run dev` starts without error on `:5173`
- [ ] `fetch('/api/overview')` returns data in browser console

**Integration:**
- [ ] Overview dashboard shows real CPU/RAM/Temp/Network numbers
- [ ] Storage pool bar reflects actual disk usage
- [ ] Physical disks list shows all drives
- [ ] File Station lists folders from `nas_root`
- [ ] Upload sends a file and it appears in `nas_upload_path`
- [ ] Download retrieves a file to your browser's Downloads folder
- [ ] Delete removes the file and the list refreshes

---

## Git Commit for This Phase

```bash
git add .
git commit -m "feat(phase-7): connect Vite frontend to Flask NAS API, fix headless paths"
```
