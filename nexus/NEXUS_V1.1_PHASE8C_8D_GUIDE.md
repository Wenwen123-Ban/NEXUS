# ═══════════════════════════════════════════════════════════════
# NEXUS v1.1 — Phase 8C & 8D Build Guide
# Features: NEXUS APP RUNNER + NEXUS Static Site (GitHub Pages)
# ═══════════════════════════════════════════════════════════════

## What This Document Covers

**Phase 8C — NEXUS APP RUNNER**
Launch, monitor, and stop any Flask application on your machine
directly from the NEXUS menu. No terminal juggling. No manual
`python app.py` in a separate window. NEXUS manages the process
in the background and keeps a live record of what's running.

**Phase 8D — NEXUS Static Site**
A single-page GitHub Pages site that presents NEXUS publicly —
what it is, what it does, every feature listed, and a download
link pointing to the repo. Your project becomes discoverable.

---

## Why These Two Belong in v1.1

```
Phase 8A — NEXUS ID        Internal — who you are inside NEXUS
Phase 8B — NEXUS LINK      Internal — talk to peers on the LAN
Phase 8C — APP RUNNER      Internal — manage your other projects
Phase 8D — Static Site     External — show NEXUS to the world

Together these four make v1.1 a complete release:
identity + communication + utility + public presence.
```

---

---

# ─────────────────────────────────────────────
# PHASE 8C — NEXUS APP RUNNER
# ─────────────────────────────────────────────

## What It Does

NEXUS APP RUNNER is a personal process manager for Flask apps.
You give it a path to any `.py` file, it launches it silently
in the background using Python's `subprocess` module, captures
the process ID (PID), and lets you stop or restart it any time
from the NEXUS menu — without opening a second terminal.

```
Practical daily use:
  You have LBAS sitting at C:\Projects\lbas\run.py
  You have the Nutritional Tracker at C:\Projects\nutri\app.py
  You want both running while you work on NEXUS

  Without APP RUNNER:
    Open terminal 1 → cd lbas → python run.py
    Open terminal 2 → cd nutri → python app.py
    Now you have 3 terminals open just to work

  With APP RUNNER:
    NEXUS menu → App Runner → Launch App → paste path
    Done. Both run silently. One terminal. NEXUS stays open.
```

---

## What You Will Learn Building Phase 8C

```
Concept                  Module                 Why it matters
──────────────────────   ────────────────────   ────────────────────────────
subprocess.Popen()       runner.py              How to launch programs from
                                                Python — used in DevOps tools
PID management           process_store.py       How OS identifies processes
Background processes     runner.py              Daemon vs foreground execution
Port detection           port_checker.py        How to find what port an app
                                                is actually listening on
Process termination      runner.py              Clean kill vs force kill
JSON as process store    process_store.py       Lightweight state persistence
```

---

## New File Structure — Phase 8C

```
nexus/
├── modules/
│   └── apprunner/
│       ├── __init__.py        ← apprunner_menu() — the menu hub
│       ├── runner.py          ← launch, stop, restart via subprocess
│       ├── process_store.py   ← read/write data/running_apps.json
│       └── port_checker.py    ← detect what port a launched app uses
│
└── data/
    └── running_apps.json      ← auto-created — tracks live processes
```

---

## Install Requirements

```bash
# No new pip installs needed for Phase 8C.
# Uses: subprocess, json, os, socket, time — all Python built-ins.
# psutil already installed in Phase 2 — used here for process checks.
```

---

## Data File — running_apps.json

Auto-created on first launch. Updated every time an app is
started, stopped, or restarted. Never pushed to GitHub
(add to .gitignore — contains local file paths).

```json
[
    {
        "id":         "lbas",
        "name":       "LBAS",
        "file":       "C:/Projects/lbas/run.py",
        "pid":        14832,
        "port":       5000,
        "started_at": "2026-06-29 14:32",
        "status":     "running",
        "auto_start": false
    },
    {
        "id":         "nutri",
        "name":       "Nutritional Tracker",
        "file":       "C:/Projects/nutri/app.py",
        "pid":        15104,
        "port":       5001,
        "started_at": "2026-06-29 14:45",
        "status":     "running",
        "auto_start": false
    }
]
```

Field breakdown:
```
id          — short slug used for commands (stop, restart by id)
name        — display name shown in the NEXUS menu table
file        — absolute path to the Python file
pid         — process ID assigned by the OS on launch
port        — detected Flask port (default 5000, auto-detected)
started_at  — timestamp of last launch
status      — "running" | "stopped" | "crashed"
auto_start  — if true, NEXUS launches this app on startup
```

---

## Menu Structure

```
NEXUS MAIN MENU → [7] App Runner

╔══════════════════════════════════════════╗
║     NEXUS APP RUNNER                    ║
║     2 apps running                      ║
╚══════════════════════════════════════════╝

  Currently running:
  ─────────────────────────────────────────────────────
  ID       Name                  Port    Status   PID
  ─────────────────────────────────────────────────────
  lbas     LBAS                  :5000   running  14832
  nutri    Nutritional Tracker   :5001   running  15104
  ─────────────────────────────────────────────────────

  [1] Launch New App
  [2] Stop an App
  [3] Restart an App
  [4] View App Log
  [5] Open in Browser
  [6] Toggle Auto-Start
  [0] Back to Main Menu

  >_
```

---

## What to Build

### modules/apprunner/runner.py
Core launch and stop logic. The most important file in this phase.

```
launch_app() flow:
  1. Ask for display name (e.g. "LBAS")
  2. Ask for file path (e.g. C:\Projects\lbas\run.py)
  3. Validate the file exists and ends in .py
  4. Ask for port (default 5000, user can override)
  5. Check if port is already in use — warn if so
  6. Launch via subprocess.Popen():
       process = subprocess.Popen(
           ['python', file_path],
           stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL,
           cwd=os.path.dirname(file_path)
       )
  7. Capture process.pid
  8. Wait 2 seconds — check if process is still alive
     (if it crashed immediately, pid won't be in process list)
  9. Save to running_apps.json via process_store.py
  10. Confirm: "LBAS launched on port 5000 (PID 14832)"

stop_app() flow:
  1. Show running apps table
  2. Ask which app to stop (by ID or number)
  3. Load PID from running_apps.json
  4. Try clean kill: process.terminate()  (SIGTERM — graceful)
  5. Wait 3 seconds
  6. If still running: process.kill()     (SIGKILL — force)
  7. Update status to "stopped" in running_apps.json
  8. Confirm: "LBAS stopped."

restart_app() flow:
  1. stop_app() for the selected app
  2. Wait 1 second
  3. launch_app() using stored file path and settings
  4. Update running_apps.json with new PID and timestamp
```

Key function signatures:
```python
def launch_app(name: str, file_path: str, port: int = 5000) -> dict:
    # Returns the app entry dict on success, None on failure

def stop_app(app_id: str) -> bool:
    # Returns True if stopped cleanly, False if force-killed

def restart_app(app_id: str) -> dict:
    # Stops then relaunches, returns new app entry

def is_process_alive(pid: int) -> bool:
    # Check if PID is still running using psutil.pid_exists(pid)
    # Also verify it hasn't been reassigned to a different process

def refresh_statuses() -> list:
    # Check all PIDs in running_apps.json against psutil
    # Update any that have crashed to status "crashed"
    # Called every time the App Runner menu opens
```

---

### modules/apprunner/process_store.py
Reads and writes `data/running_apps.json`. Clean separation
so runner.py never directly touches the JSON file.

```python
# Key functions:

def load_apps() -> list:
    # Read running_apps.json
    # Return empty list if file missing

def save_apps(apps: list):
    # Write full list to running_apps.json

def add_app(entry: dict):
    # Load → append → save

def update_app(app_id: str, updates: dict):
    # Load → find by id → merge updates → save

def remove_app(app_id: str):
    # Load → filter out by id → save

def get_app(app_id: str) -> dict | None:
    # Load → find and return by id → None if not found
```

---

### modules/apprunner/port_checker.py
Detects what port a freshly launched Flask app is listening on.
Also checks if a port is already occupied before launching.

```python
# Key functions:

def is_port_in_use(port: int) -> bool:
    # Try binding a socket to the port
    # If it fails → port is already occupied
    # Used before launching to warn the user

def detect_app_port(pid: int, expected_port: int = 5000) -> int:
    # Use psutil.Process(pid).connections()
    # Find which port the process is listening on
    # Return expected_port as fallback if detection fails

def open_in_browser(port: int):
    # import webbrowser
    # webbrowser.open(f"http://localhost:{port}")
    # Called from the "Open in Browser" menu option
```

---

### modules/apprunner/__init__.py
The menu. Calls refresh_statuses() on open so the table
always reflects the true current state of every app.

```
Menu options behavior:

[1] Launch New App
    → Prompt for name, file path, port
    → Call runner.launch_app()
    → Show success with PID and port

[2] Stop an App
    → Show running apps table
    → Ask which to stop
    → Call runner.stop_app()

[3] Restart an App
    → Show all apps (running or stopped)
    → Call runner.restart_app()

[4] View App Log
    → Show last 20 lines of nexus.log filtered to that app name
    → Any stdout captured during launch appears here

[5] Open in Browser
    → Show running apps
    → Call port_checker.open_in_browser(port)

[6] Toggle Auto-Start
    → Flip auto_start flag in running_apps.json
    → Auto-started apps will be launched when NEXUS starts
    → Requires update to main.py startup sequence

[0] Back
```

---

### Update main.py — Auto-Start Hook

After the login gate in main.py, add an auto-start check:

```python
# main.py — after successful login

from modules.apprunner.process_store import load_apps
from modules.apprunner.runner import launch_app

def run_auto_start_apps():
    """Launch any apps flagged as auto_start on NEXUS startup."""
    apps = load_apps()
    for app in apps:
        if app.get("auto_start") and app["status"] != "running":
            print(f"  [→] Auto-starting {app['name']}...")
            launch_app(app["name"], app["file"], app.get("port", 5000))

# Call after login succeeds
user = login()
if user:
    run_auto_start_apps()
    # then enter main menu loop
```

---

## How to Test Phase 8C

```bash
# Step 1 — test with a minimal Flask app
# Create a test file at C:\NEXUS\test_app.py:

from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "NEXUS APP RUNNER TEST — working."

if __name__ == "__main__":
    app.run(port=5050)

# Step 2 — launch it via NEXUS
python main.py
# → Login → App Runner → Launch New App
# → Name: TestApp
# → File: C:\NEXUS\test_app.py
# → Port: 5050

# Step 3 — verify it's running
# Open browser → http://localhost:5050
# Should show "NEXUS APP RUNNER TEST — working."

# Step 4 — stop it via NEXUS
# → App Runner → Stop an App → TestApp
# Refresh browser → connection refused (app is stopped)

# Step 5 — test crash detection
# Manually kill the process in Task Manager
# Re-open App Runner menu → status should show "crashed"
```

---

## Phase 8C Checklist

- [ ] `data/running_apps.json` created on first launch
- [ ] `running_apps.json` added to `.gitignore`
- [ ] Launch creates a real background process and captures PID
- [ ] App stays running after NEXUS menu returns (background)
- [ ] Stop terminates the process cleanly
- [ ] Force kill works if clean stop fails
- [ ] Crashed apps detected automatically on menu open
- [ ] Port-in-use warning shown before launching
- [ ] Open in Browser launches correct localhost URL
- [ ] Auto-start flag toggleable per app
- [ ] Auto-start apps launch after login on NEXUS startup
- [ ] LBAS tested as a real app launch (not just test_app.py)
- [ ] Nutritional Tracker tested alongside LBAS simultaneously

## Git Commit
```bash
git add .
git commit -m "feat(v1.1): NEXUS APP RUNNER — subprocess process manager for Flask apps"
```

---

---

# ─────────────────────────────────────────────
# PHASE 8D — NEXUS Static Site (GitHub Pages)
# ─────────────────────────────────────────────

## What It Does

A single-page static website hosted free on GitHub Pages that
presents NEXUS publicly. Anyone with the link can read what
NEXUS is, see its features, and click through to the GitHub
repo to download it. No server needed. No hosting cost.
Deployed by pushing one folder to your existing repo.

```
Result:
  https://YOUR_USERNAME.github.io/nexus

What visitors see:
  → Hero: NEXUS name, tagline, Download button
  → About: what problem NEXUS solves
  → Features: each module as a card
  → v1.1 spotlight: NEXUS ID + NEXUS LINK highlighted
  → Tech stack: Python, Flask, Socket, HTML/CSS/JS
  → Footer: built by Erwin A. | NMSCST BSIT | repo link
```

---

## What You Will Learn Building Phase 8D

```
Concept                   Why it matters
───────────────────────   ───────────────────────────────────────
GitHub Pages deployment   Industry-standard free static hosting
docs/ folder structure    How repos serve web content
CSS Grid + Flexbox        Real layout skills beyond basic styling
Responsive design         Mobile-first — same page on all screens
Anchor smooth scroll      Single-page navigation UX
CSS animations            Subtle motion that makes UI feel alive
Open Graph meta tags      How your site looks when shared on chat
```

---

## New File Structure — Phase 8D

```
nexus/
└── docs/                        ← GitHub Pages reads from here
    ├── index.html               ← the full single-page site
    ├── style.css                ← site-specific styles
    ├── script.js                ← smooth scroll + small interactions
    └── assets/
        └── preview.png          ← screenshot of NEXUS terminal UI
                                   (used in Open Graph + hero section)
```

> The `docs/` folder name is required by GitHub Pages when using
> the main branch. Do not rename it.

---

## Page Structure and Sections

```
┌─────────────────────────────────────────────┐
│  NAVIGATION                                  │
│  NEXUS    About  Features  Download          │
├─────────────────────────────────────────────┤
│  HERO SECTION                                │
│  ⬡ NEXUS                                    │
│  Node EXecution & Unified System            │
│  Personal homelab control panel             │
│  built for privacy, built for your LAN.     │
│                                             │
│  [↓ Download]    [View on GitHub]           │
├─────────────────────────────────────────────┤
│  ABOUT SECTION                              │
│  What is NEXUS?                             │
│  One terminal. All your tools.              │
│  No cloud. No subscription. No account.    │
│  Everything runs on your machine.           │
├─────────────────────────────────────────────┤
│  FEATURES GRID                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │◈ NAS     │ │◉ Network │ │⚿ Security│   │
│  │ Monitor  │ │  Tools   │ │  Center  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │▣ System  │ │✉ Email   │ │⇄ App     │   │
│  │ Monitor  │ │  Tools   │ │  Runner  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────┤
│  v1.1 SPOTLIGHT                             │
│  New in v1.1 — two features nobody else    │
│  builds into homelab tools:                 │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ NEXUS ID    │  │ NEXUS LINK  │          │
│  │ Local auth  │  │ LAN P2P chat│          │
│  │ No accounts │  │ No internet │          │
│  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────┤
│  TECH STACK                                 │
│  Python  Flask  Socket  HTML  CSS  JS       │
├─────────────────────────────────────────────┤
│  DOWNLOAD / CTA                             │
│  Built for people who want control.         │
│  [⬡ Get NEXUS on GitHub]                   │
├─────────────────────────────────────────────┤
│  FOOTER                                     │
│  Built by Erwin A. · NMSCST BSIT           │
│  Tangub City, Misamis Occidental            │
│  MIT License · v1.1                        │
└─────────────────────────────────────────────┘
```

---

## Design Specifications

Match the NEXUS terminal aesthetic so the site feels like
an extension of the tool itself — not a generic template.

```css
/* Color palette — same as NEXUS terminal */
--bg-base:     #0b0f14;     /* near-black background */
--bg-card:     #111820;     /* card surfaces */
--border:      #1e2d3d;     /* subtle borders */
--cyan:        #00c8ff;     /* primary accent — NEXUS brand */
--green:       #00e676;     /* success / highlight */
--text:        #cdd9e5;     /* body text */
--text-dim:    #6b8399;     /* secondary text */

/* Typography */
--font-ui:     'Segoe UI', system-ui, sans-serif;
--font-mono:   'Cascadia Code', 'Consolas', monospace;

/* The NEXUS name and section titles use --font-mono */
/* Body copy and card text use --font-ui */
```

---

## Features Cards — Full List

Each card in the features grid:

```
Icon    Name              Description
────    ────────────────  ──────────────────────────────────────
◈       NAS Manager       Monitor disk health, browse and sync
                          files on your storage drives
◉       Network Tools     Ping sweep your LAN, scan ports,
                          listen for incoming connections
⚿       Security Center   Parse intrusion logs, monitor SSH
                          access, view firewall rules
▣       System Monitor    Live CPU, RAM, disk, and temperature
                          with email alerts on threshold breach
✉       Email Tools       Send alerts and reports directly
                          from NEXUS to your inbox
⬡       App Runner        Launch and manage your Flask apps
                          as background processes
◎       Task Scheduler    Automate any NEXUS module on a
                          daily or hourly timer
⇄       NEXUS LINK        LAN-only peer-to-peer chat. No
          (v1.1)          internet. No server. IP to IP.
◈       NEXUS ID          Local identity and login. Stored
          (v1.1)          only on your machine. No accounts.
```

---

## Open Graph Meta Tags

Add these to the `<head>` of `index.html` so when you share
the link in a chat or on social media it shows a proper preview
card with the NEXUS name, description, and screenshot.

```html
<meta property="og:title"       content="NEXUS — Personal Homelab Control Panel" />
<meta property="og:description" content="One terminal. All your tools. NAS, network, security, LAN chat — privacy-first, runs on your machine." />
<meta property="og:image"       content="https://YOUR_USERNAME.github.io/nexus/assets/preview.png" />
<meta property="og:url"         content="https://YOUR_USERNAME.github.io/nexus" />
<meta name="twitter:card"       content="summary_large_image" />
```

---

## How to Deploy to GitHub Pages

```bash
# Step 1 — create the docs/ folder and files
mkdir docs
# write index.html, style.css, script.js inside docs/

# Step 2 — commit and push to GitHub
git add docs/
git commit -m "feat(v1.1): NEXUS static site for GitHub Pages"
git push origin main

# Step 3 — enable GitHub Pages
# Go to: github.com/YOUR_USERNAME/nexus
# Settings → Pages → Source
# Branch: main
# Folder: /docs
# Click Save

# Step 4 — wait 1-2 minutes then visit
# https://YOUR_USERNAME.github.io/nexus
```

After enabling, every future `git push` to main automatically
updates the live site within 1–2 minutes. No manual deploy step.

---

## assets/preview.png — How to Get It

You need one screenshot that represents NEXUS well.
Best option is to capture the NEXUS banner + main menu:

```bash
# Run NEXUS
python main.py

# When the main menu appears:
# Windows → Win + Shift + S → select the terminal window
# Save as docs/assets/preview.png

# Ideal dimensions: 1200 × 630px (standard Open Graph size)
# If your screenshot is different size, crop in Paint or Snipping Tool
```

---

## How to Test Phase 8D

```bash
# Local test before pushing — open the file directly in browser
# In VS Code: right-click docs/index.html → Open with Live Server
# Or just open the file:
start docs/index.html   # Windows
# Should render the full page with correct styling

# After GitHub Pages deploy:
# Visit https://YOUR_USERNAME.github.io/nexus
# Check on mobile browser too — responsive layout test
# Share the link in a chat and verify Open Graph preview shows
```

---

## Phase 8D Checklist

**Files:**
- [ ] `docs/index.html` created with all sections
- [ ] `docs/style.css` created with NEXUS color palette
- [ ] `docs/script.js` created with smooth scroll
- [ ] `docs/assets/preview.png` screenshot added

**Content:**
- [ ] Hero section shows NEXUS name, tagline, two buttons
- [ ] About section explains NEXUS in plain language
- [ ] All 9 feature cards present with icons and descriptions
- [ ] v1.1 spotlight section highlights NEXUS ID + NEXUS LINK
- [ ] Tech stack row shows all languages/tools used
- [ ] Download button links to the correct GitHub repo URL
- [ ] Footer shows your name, school, city, license, version

**Deployment:**
- [ ] `docs/` folder committed and pushed to main branch
- [ ] GitHub Pages enabled (Settings → Pages → /docs)
- [ ] Site loads at `https://YOUR_USERNAME.github.io/nexus`
- [ ] Site renders correctly on mobile screen
- [ ] Open Graph preview appears when link is shared in chat
- [ ] Download button correctly opens the GitHub repo

## Git Commit
```bash
git add docs/
git commit -m "feat(v1.1): NEXUS static site deployed to GitHub Pages"
```

---

---

# v1.1 Complete — All Four Phases

```
Phase 8A — NEXUS ID          Local identity + login gate
Phase 8B — NEXUS LINK        LAN peer-to-peer chat
Phase 8C — NEXUS APP RUNNER  Flask process manager
Phase 8D — NEXUS Static Site GitHub Pages public presence
```

## Final v1.1 Release Commit

```bash
git add .
git commit -m "release: NEXUS v1.1 — ID, LINK, APP RUNNER, Static Site"
git tag v1.1
git push origin main --tags
```

---

## .gitignore Additions for v1.1 Complete

```
# Phase 8C — local process data (paths and PIDs are machine-specific)
data/running_apps.json

# Phase 8D — no additions needed (docs/ is intentionally public)
```

---

## What v1.2 Could Look Like

```
Natural next steps after v1.1 ships:

  NEXUS LINK file transfer    — send files over the LAN socket
  NEXUS LINK encryption       — XOR or AES encrypt messages
  NEXUS LINK group broadcast  — message all peers at once
  APP RUNNER log capture      — pipe Flask stdout to a log file
  APP RUNNER web view         — see running apps from the NAS dashboard
  NAS web dashboard           — resume when T3500 arrives
  NEXUS mobile site update    — add App Runner and LINK to the static site
```

---

*NEXUS v1.1 — Phase 8C & 8D Build Guide*
*APP RUNNER + Static Site*
*No additional hardware required.*
*Deployable on current Fujitsu A748.*
