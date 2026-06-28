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
- [ ] Phase 2 — System Monitor
- [ ] Phase 3 — Network Tools
- [ ] Phase 4 — NAS Manager
- [ ] Phase 5 — Security Center
- [ ] Phase 6 — Task Scheduler
