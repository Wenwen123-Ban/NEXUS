# NEXUS — Build Guide
> Node EXecution & Unified System | Personal Homelab Control Panel

This document is your **phase-by-phase build reference**. Follow it top to bottom.
Each phase has its own goal, file targets, install requirements, and a checklist to
tick off before moving to the next phase.

---

## Before You Start — One-Time Setup

### Requirements
- Python 3.10 or higher
- Git installed
- A Gmail account with **2-Step Verification enabled**
- A Gmail **App Password** (16-character) — get one at:
  https://myaccount.google.com/apppasswords

### Run the scaffolder (if not done yet)
```bash
python nexus_scaffold.py
cd nexus
```

### Initialize the Git repository
```bash
git init
git add .
git commit -m "feat: initial NEXUS scaffold"
```

### Open in VS Code
```bash
code .
```

---

## Project Folder Reference

```
nexus/
├── main.py                        ← Entry point — run this always
├── core/
│   ├── config.py                  ← Reads data/config.json
│   ├── logger.py                  ← Writes to data/nexus.log
│   └── display.py                 ← Colors, banners, menus, tables
├── modules/
│   ├── nas/                       ← Phase 4
│   ├── network/                   ← Phase 3
│   ├── security/                  ← Phase 5
│   ├── system/                    ← Phase 2
│   ├── email_tools/               ← Phase 1 (already done)
│   └── scheduler/                 ← Phase 6
└── data/
    ├── config.json                ← Auto-generated on first run
    ├── nexus.log                  ← Auto-generated on first run
    └── tasks.json                 ← Created in Phase 6
```

---

---

# ─────────────────────────────────────────────
# PHASE 1 — The Shell & Email Tools
# ─────────────────────────────────────────────
**Goal:** Get NEXUS running with a working menu, shared core utilities,
and a fully functional email sender. This is your foundation — every
future module depends on what you build here.

## Files in This Phase
```
core/config.py          ← Already scaffolded. Edit data/config.json.
core/logger.py          ← Already scaffolded. No changes needed.
core/display.py         ← Already scaffolded. No changes needed.
modules/email_tools/
  ├── email_sender.py   ← Already scaffolded. Fully working.
  └── alert_mailer.py   ← Already scaffolded. Fully working.
main.py                 ← Already scaffolded. No changes needed.
```

## Install Requirements
```bash
# No pip installs needed for Phase 1.
# smtplib and email are Python built-ins.
```

## Configuration
On first run, `data/config.json` is auto-generated. Open it and fill in:
```json
{
    "sender_email":    "your_email@gmail.com",
    "sender_password": "your_16char_app_password",
    "smtp_server":     "smtp.gmail.com",
    "smtp_port":       587,
    "alert_email":     "your_email@gmail.com",
    "nas_path":        "/mnt/nas",
    "cpu_alert_threshold":  90,
    "ram_alert_threshold":  85,
    "disk_alert_threshold": 90,
    "ping_range":      "192.168.1.1-254"
}
```
> ⚠️  data/config.json is in .gitignore — your password will NOT be pushed to GitHub.

## How to Test Phase 1
```bash
python main.py
# → Select [5] Email Tools
# → Select [1] Send a Test Email
# → Enter your own email as recipient and send a test
# → Check your inbox — it should arrive within 30 seconds
```

## Phase 1 Checklist
- [ ] Scaffolder ran successfully (`python nexus_scaffold.py`)
- [ ] Git repository initialized and first commit made
- [ ] `data/config.json` filled with real Gmail App Password
- [ ] `python main.py` shows the NEXUS banner without errors
- [ ] All 6 menu options are reachable (they show "not yet implemented")
- [ ] Test email sent and received successfully
- [ ] `data/nexus.log` created and shows the sent email entry

## Git Commit for This Phase
```bash
git add .
git commit -m "feat(phase-1): shell, core utilities, email sender working"
```

---

---

# ─────────────────────────────────────────────
# PHASE 2 — System Monitor
# ─────────────────────────────────────────────
**Goal:** Build the System Monitor — a live view of CPU, RAM, disk usage,
running processes, and service health. Wire it to the alert mailer so
NEXUS emails you when something exceeds your thresholds.

## Files in This Phase
```
modules/system/
  ├── resource_monitor.py   ← CPU %, RAM %, disk %, temps
  ├── process_manager.py    ← List and kill processes by name
  └── service_checker.py    ← Check if services (nginx, mysql) are up
```

## Install Requirements
```bash
pip install psutil rich
```
- `psutil`  — reads CPU, RAM, disk, processes, temps
- `rich`    — optional but makes live dashboards look great in terminal

## What to Build

### resource_monitor.py
```python
import psutil
from core.display import section, table, warn
from core.config import CONFIG
from modules.email_tools.alert_mailer import send_alert

def run():
    section("RESOURCE MONITOR")
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    table(
        headers=["Metric", "Usage", "Status"],
        rows=[
            ["CPU",  f"{cpu}%",  "OK" if cpu  < CONFIG["cpu_alert_threshold"]  else "HIGH"],
            ["RAM",  f"{ram}%",  "OK" if ram  < CONFIG["ram_alert_threshold"]  else "HIGH"],
            ["Disk", f"{disk}%", "OK" if disk < CONFIG["disk_alert_threshold"] else "HIGH"],
        ]
    )
    # Auto-alert if over threshold
    if cpu > CONFIG["cpu_alert_threshold"]:
        send_alert("High CPU Usage", f"CPU is at {cpu}%")
    if ram > CONFIG["ram_alert_threshold"]:
        send_alert("High RAM Usage", f"RAM is at {ram}%")
    if disk > CONFIG["disk_alert_threshold"]:
        send_alert("High Disk Usage", f"Disk is at {disk}%")

    input("\n  Press Enter to go back...")
```

### process_manager.py
Use `psutil.process_iter()` to list processes with PID, name, CPU%, and
memory. Let the user enter a PID to kill a process using `psutil.Process(pid).kill()`.

### service_checker.py
Define a list of service names in `config.json` (e.g., `["nginx", "mysql"]`).
Use `psutil.process_iter()` and check if any running process name matches.
Show a green OK or red STOPPED status for each.

## How to Test Phase 2
```bash
python main.py
# → Select [4] System Monitor
# → Select [1] Resource Monitor
# → Confirm CPU, RAM, disk stats appear in a table
# → Temporarily lower cpu_alert_threshold to 1 in config.json
# → Run again — you should receive an alert email
```

## Phase 2 Checklist
- [ ] `psutil` installed successfully
- [ ] Resource Monitor shows real CPU, RAM, disk values
- [ ] Alert email fires when a threshold is exceeded
- [ ] Process Manager lists running processes
- [ ] Process Manager can kill a process by PID
- [ ] Service Checker shows correct UP/DOWN status

## Git Commit for This Phase
```bash
git add .
git commit -m "feat(phase-2): system monitor, process manager, service checker"
```

---

---

# ─────────────────────────────────────────────
# PHASE 3 — Network Tools
# ─────────────────────────────────────────────
**Goal:** Build the network toolkit — discover devices on your LAN, scan
ports on any IP, and open a local port listener that logs incoming connections.
These are the tools you will use daily on your homelab.

## Files in This Phase
```
modules/network/
  ├── port_scanner.py    ← Scan a target IP for open ports
  ├── port_listener.py   ← Open a local port, log who connects
  └── ping_sweep.py      ← Discover all alive devices on your LAN
```

## Install Requirements
```bash
# No new pip installs needed.
# Uses: socket, threading, subprocess, ipaddress — all built-in.
```

## What to Build

### ping_sweep.py
```python
import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from core.display import section, success, warn

def ping(ip):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "300", str(ip)],  # Windows
        # ["ping", "-c", "1", "-W", "1", str(ip)],  # Linux/Mac
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return str(ip) if result.returncode == 0 else None

def run():
    section("PING SWEEP")
    base = input("  Enter network base (e.g. 192.168.1): ").strip()
    ips  = [ipaddress.IPv4Address(f"{base}.{i}") for i in range(1, 255)]
    print(f"\n  Scanning {len(ips)} addresses...\n")
    alive = []
    with ThreadPoolExecutor(max_workers=50) as ex:
        results = ex.map(ping, ips)
    for ip in results:
        if ip:
            alive.append(ip)
            success(f"  ALIVE → {ip}")
    print(f"\n  Found {len(alive)} device(s).")
    input("  Press Enter to go back...")
```

### port_scanner.py
Ask user for a target IP and a port range (e.g. 1–1024). Use `socket.connect_ex()`
inside a `ThreadPoolExecutor` to scan all ports concurrently. Print open ones
in a table. Log the scan to `nexus.log`.

### port_listener.py
Use `socket.socket()` to bind to a port the user specifies. Accept connections
in a loop, log the connecting IP and timestamp to `nexus.log`, and print it live.
Allow `Ctrl+C` to stop gracefully.

## How to Test Phase 3
```bash
python main.py
# → Select [2] Network Tools
# → Select [3] Ping Sweep — enter your LAN base (e.g. 192.168.1)
#   Confirm your router and other devices show as ALIVE

# → Select [1] Port Scanner — scan localhost (127.0.0.1), ports 1-1024
#   You should see any open ports on your own machine

# → Select [2] Port Listener — listen on port 9999
#   Open another terminal and run: nc 127.0.0.1 9999 (or telnet)
#   Confirm the connection is logged
```

## Phase 3 Checklist
- [ ] Ping Sweep discovers devices on your LAN (including your router)
- [ ] Port Scanner correctly identifies open ports on localhost
- [ ] Port Listener accepts a connection and logs the remote IP
- [ ] All activity written to `data/nexus.log`
- [ ] No crashes on `Ctrl+C` during listener

## Git Commit for This Phase
```bash
git add .
git commit -m "feat(phase-3): port scanner, port listener, ping sweep"
```

---

---

# ─────────────────────────────────────────────
# PHASE 4 — NAS Manager
# ─────────────────────────────────────────────
**Goal:** Build the NAS management layer — monitor disk health, browse
files on your NAS or a local share, and sync folders so your important
files are always backed up. This phase makes NEXUS directly useful with
your T3500 once it's set up.

## Files in This Phase
```
modules/nas/
  ├── nas_monitor.py   ← Disk usage per drive, free space, warnings
  ├── nas_browser.py   ← List, navigate, and delete files on NAS path
  └── nas_sync.py      ← Mirror a source folder to the NAS path
```

## Install Requirements
```bash
pip install paramiko   # Only needed if connecting to NAS over SSH
# psutil already installed in Phase 2 — covers local disk stats
```

## What to Build

### nas_monitor.py
Use `psutil.disk_partitions()` to list all mounted drives. For each, use
`psutil.disk_usage(partition.mountpoint)` to get total, used, and free space.
Display as a table. Highlight any drive above `disk_alert_threshold` in red
and call `send_alert()` automatically.

### nas_browser.py
```python
import os
from core.display import section, table, error
from core.config import CONFIG

def run():
    section("NAS FILE BROWSER")
    path = CONFIG["nas_path"]
    while True:
        if not os.path.exists(path):
            error(f"Path not found: {path}")
            break
        entries = os.listdir(path)
        rows = []
        for i, name in enumerate(entries, 1):
            full = os.path.join(path, name)
            kind = "DIR" if os.path.isdir(full) else "FILE"
            size = os.path.getsize(full) if kind == "FILE" else "-"
            rows.append([i, kind, name, size])
        table(["#", "Type", "Name", "Size (bytes)"], rows)
        choice = input("\n  Enter # to open dir / [D]#  to delete / [B] back: ").strip()
        if choice.upper() == "B":
            break
        elif choice.upper().startswith("D"):
            # Delete file by number
            ...
        elif choice.isdigit():
            # Navigate into directory
            ...
```

### nas_sync.py
Ask the user for a source folder. Walk the source with `os.walk()`.
For each file, check if it exists in the destination (`nas_path`) and
compare modification times using `os.path.getmtime()`. Copy newer or
missing files using `shutil.copy2()`. Print a summary: X files copied,
Y files skipped, Z errors. Log to `nexus.log`.

## How to Test Phase 4
```bash
# First, set "nas_path" in data/config.json to a real local folder.
# (Use a USB drive, a second folder, or your T3500 share when ready.)

python main.py
# → Select [1] NAS Manager
# → Select [1] Disk Usage Monitor — confirm all drives listed
# → Select [2] File Browser — navigate your NAS path
# → Select [3] Folder Sync — point it at your nexus/ project folder
#   Confirm files are copied to the NAS destination
```

## Phase 4 Checklist
- [ ] NAS Monitor lists all mounted drives with usage %
- [ ] Alert email fires if any drive is above threshold
- [ ] File Browser lists files and folders at the configured NAS path
- [ ] File Browser can navigate into subdirectories
- [ ] Folder Sync copies new/changed files from source to NAS
- [ ] Sync summary shows files copied vs skipped

## Git Commit for This Phase
```bash
git add .
git commit -m "feat(phase-4): NAS monitor, file browser, folder sync"
```

---

---

# ─────────────────────────────────────────────
# PHASE 5 — Security Center
# ─────────────────────────────────────────────
**Goal:** Build the security toolkit — parse system logs for failed login
attempts, monitor SSH access in real time, and view or manage firewall
rules. Wire any suspicious activity to an instant alert email.

## Files in This Phase
```
modules/security/
  ├── intrusion_log.py    ← Parse auth.log for failed logins, flag IPs
  ├── ssh_monitor.py      ← Live-tail auth.log, alert on new failures
  └── firewall_rules.py   ← View iptables rules (Linux) or netsh (Windows)
```

## Install Requirements
```bash
pip install watchdog    # For live file monitoring in ssh_monitor.py
```
> ⚠️  `firewall_rules.py` and `intrusion_log.py` read Linux system log
> files (`/var/log/auth.log`). On Windows, adapt to parse Windows Event
> Logs using the `pywin32` library or use the Task Scheduler logs instead.
> On your T3500 running Linux this will work natively.

## What to Build

### intrusion_log.py
```python
import re
from collections import Counter
from core.display import section, table, warn
from core.logger import log

LOG_FILE = "/var/log/auth.log"   # Linux path
PATTERN  = re.compile(r"Failed password.*from (\d+\.\d+\.\d+\.\d+)")

def run():
    section("INTRUSION LOG PARSER")
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        warn(f"Log file not found: {LOG_FILE}")
        input("  Press Enter to go back...")
        return

    ips = [PATTERN.search(l).group(1) for l in lines if PATTERN.search(l)]
    counts = Counter(ips).most_common(10)
    table(["IP Address", "Failed Attempts"], counts)
    log(f"Intrusion log parsed. Top offender: {counts[0] if counts else 'None'}")
    input("\n  Press Enter to go back...")
```

### ssh_monitor.py
Use `watchdog` to tail `/var/log/auth.log` in real time. On every new line
that contains "Failed password", extract the source IP and print a live
alert to the terminal. Call `send_alert()` after 3+ failures from the
same IP within a session. Allow `Ctrl+C` to stop cleanly.

### firewall_rules.py
On Linux: run `subprocess.run(["iptables", "-L", "-n", "-v"])` and parse
the output into a table. Offer options to add (`iptables -A INPUT -s IP -j DROP`)
or remove rules. On Windows: use `netsh advfirewall firewall show rule name=all`.

## How to Test Phase 5
```bash
# Requires Linux or WSL for full functionality.
# On Windows, adapt paths or use WSL terminal.

python main.py
# → Select [3] Security Center
# → Select [3] Intrusion Log — confirm failed login IPs are listed
# → Select [1] SSH Monitor — leave running, attempt an SSH login
#   from another terminal to trigger a live alert
# → Select [2] Firewall Rules — confirm current iptables rules display
```

## Phase 5 Checklist
- [ ] Intrusion Log parses `/var/log/auth.log` and lists top offender IPs
- [ ] SSH Monitor runs live and detects new failed logins in real time
- [ ] Alert email fires after repeated failures from the same IP
- [ ] Firewall Rules displays current rules in a readable table
- [ ] All security events written to `data/nexus.log`

## Git Commit for This Phase
```bash
git add .
git commit -m "feat(phase-5): intrusion log, SSH monitor, firewall viewer"
```

---

---

# ─────────────────────────────────────────────
# PHASE 6 — Task Scheduler
# ─────────────────────────────────────────────
**Goal:** Wire everything together with a scheduler. Define tasks that
run automatically — daily system report emailed to you, nightly NAS sync,
periodic ping sweeps, and so on. NEXUS becomes a background service.

## Files in This Phase
```
modules/scheduler/
  └── task_runner.py   ← Define, store, and run scheduled tasks
data/
  └── tasks.json       ← Persists your scheduled task definitions
```

## Install Requirements
```bash
pip install schedule   # Lightweight cron-like scheduler for Python
```

## tasks.json Structure
```json
[
    {
        "id": 1,
        "name": "Daily System Report",
        "module": "modules.system.resource_monitor",
        "function": "run",
        "frequency": "daily",
        "time": "08:00",
        "enabled": true
    },
    {
        "id": 2,
        "name": "Nightly NAS Sync",
        "module": "modules.nas.nas_sync",
        "function": "run",
        "frequency": "daily",
        "time": "23:00",
        "enabled": true
    }
]
```

## What to Build

### task_runner.py
```python
import json, schedule, time, importlib, os
from core.display import section, table, success, warn
from core.logger import log

TASKS_PATH = os.path.join("data", "tasks.json")

def load_tasks():
    if not os.path.exists(TASKS_PATH):
        return []
    with open(TASKS_PATH) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_PATH, "w") as f:
        json.dump(tasks, f, indent=4)

def view_tasks():
    section("SCHEDULED TASKS")
    tasks = load_tasks()
    if not tasks:
        warn("No tasks defined yet.")
    else:
        table(
            ["ID", "Name", "Frequency", "Time", "Enabled"],
            [[t["id"], t["name"], t["frequency"], t["time"], t["enabled"]] for t in tasks]
        )
    input("\n  Press Enter to go back...")

def add_task():
    section("ADD TASK")
    tasks = load_tasks()
    task = {
        "id":        len(tasks) + 1,
        "name":      input("  Task name      : ").strip(),
        "module":    input("  Module path    : ").strip(),
        "function":  input("  Function name  : ").strip(),
        "frequency": input("  Frequency (daily/hourly): ").strip(),
        "time":      input("  Time (HH:MM, daily only): ").strip(),
        "enabled":   True
    }
    tasks.append(task)
    save_tasks(tasks)
    success(f"Task '{task['name']}' saved.")
    input("  Press Enter to go back...")

def run_scheduler():
    section("SCHEDULER RUNNING")
    tasks = [t for t in load_tasks() if t["enabled"]]
    for t in tasks:
        mod  = importlib.import_module(t["module"])
        func = getattr(mod, t["function"])
        if t["frequency"] == "daily":
            schedule.every().day.at(t["time"]).do(func)
        elif t["frequency"] == "hourly":
            schedule.every().hour.do(func)
        log(f"Scheduled: {t['name']} ({t['frequency']} at {t['time']})")
    print("  Scheduler running. Press Ctrl+C to stop.\n")
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n  [✓] Scheduler stopped.")
```

## How to Test Phase 6
```bash
python main.py
# → Select [6] Task Scheduler
# → Select [2] Add a Task
#   name:     "Test Report"
#   module:   modules.system.resource_monitor
#   function: run
#   freq:     daily
#   time:     (set 2 minutes from now, e.g. 14:35)

# → Select [1] View Tasks — confirm it appears
# → Select [3] Run Scheduler Now
#   Wait for the scheduled time — confirm the task fires
```

## Phase 6 Checklist
- [ ] `tasks.json` created and persists tasks between runs
- [ ] View Tasks displays all defined tasks in a table
- [ ] Add Task saves a new task correctly to `tasks.json`
- [ ] Scheduler runs and fires tasks at the correct time
- [ ] Daily system report email received at scheduled time
- [ ] NAS sync runs automatically at configured time
- [ ] `Ctrl+C` stops the scheduler cleanly without crashing

## Git Commit for This Phase
```bash
git add .
git commit -m "feat(phase-6): task scheduler, tasks.json, full automation"
```

---

---

# Final Steps After All Phases

## Full dependency install (all at once)
```bash
pip install psutil rich paramiko watchdog schedule
```

## Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/nexus.git
git branch -M main
git push -u origin main
```

## Run NEXUS
```bash
python main.py
```

## Future Ideas (Post-Phase 6)
- Web dashboard using Flask — view NEXUS stats from your browser
- Discord bot integration — send alerts to a Discord channel
- Docker container support — run NEXUS as a background service
- Multi-machine support — manage multiple IPs from one config
- SMS alerts via Twilio — text yourself when CPU spikes

---

*NEXUS — Built phase by phase. Erwin A., NMSCST BSIT.*
