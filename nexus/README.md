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
- [ ] Phase 5 — Security Center
- [ ] Phase 6 — Task Scheduler


## Phase 4 Checklist — NAS Manager
- [x] Disk usage monitor validates the configured NAS path and reports used, free, total, percentage, and threshold status.
- [x] File browser lists NAS folders/files, supports safe navigation, and previews text files without leaving the NAS root.
- [x] Folder sync copies new or updated local files into the NAS path while preserving metadata.
