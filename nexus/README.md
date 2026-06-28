# NEXUS
> Node EXecution & Unified System — Personal Homelab Control Panel

## Structure
- `main.py` — Entry point and main menu
- `core/` — Shared utilities (display, logging, config)
- `modules/` — Feature modules (NAS, Network, Security, System, Email, Scheduler)
- `data/` — Logs, config, task definitions

## Setup
```bash
pip install psutil rich schedule paramiko
python main.py
```

## Build Phases
- [x] Phase 1 — Shell & Core Utilities
- [x] Phase 2 — System Monitor
- [x] Phase 3 — Network Tools
- [x] Phase 4 — NAS Manager
- [x] Phase 5 — Security Center
- [x] Phase 6 — Task Scheduler


## Phase 4 Checklist — NAS Manager
- [x] Disk usage monitor validates the configured NAS path and reports used, free, total, percentage, and threshold status.
- [x] File browser lists NAS folders/files, supports safe navigation, and previews text files without leaving the NAS root.
- [x] Folder sync copies new or updated local files into the NAS path while preserving metadata.

## Phase 5 Checklist — Security Center
- [x] SSH login monitor reads the configured authentication log and summarizes failed password attempts by source IP and username.
- [x] Firewall rules viewer detects common local firewall backends (`ufw`, `iptables`, or `nft`) and displays available rules.
- [x] Intrusion log parser scans configured security logs for suspicious terms and groups matching events by IP address.

## Phase 6 Checklist — Task Scheduler
- [x] Scheduled task definitions are stored in `data/tasks.json` and are created automatically when missing.
- [x] Task viewer lists enabled state, command, interval, last run time, and next registered run time.
- [x] Task creation validates task name, command, positive interval, and supported time units.
- [x] Scheduler registers enabled tasks with the `schedule` library, executes commands, logs results, and persists run metadata.
