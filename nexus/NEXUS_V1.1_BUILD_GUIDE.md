# ═══════════════════════════════════════════════════════════════
# NEXUS v1.1 — Build Guide
# Features: NEXUS ID (Local Identity) + NEXUS LINK (LAN Chat)
# ═══════════════════════════════════════════════════════════════

## What v1.1 Adds

Two features that work together as one system:

**NEXUS ID** — Local identity layer. Before anything in NEXUS loads,
the user sets up a name and password stored only on their own machine
in `data/users.json`. No server. No cloud. No account registration.
Just you and your local file.

**NEXUS LINK** — LAN-only peer-to-peer chat. Once identified, NEXUS
users on the same network can send messages directly to each other
by IP address. No internet required. No middleman. Each machine is
both the sender and the receiver simultaneously.

---

## Why These Two Features Together

```
Without NEXUS ID:
  Anyone who opens NEXUS on your machine gets full access.
  LAN chat has no identity — messages arrive with no name.

Without NEXUS LINK:
  NEXUS ID is just a login screen with nothing behind it.

Together:
  You log in as Erwin @ 192.168.1.10
  You see Juan is online @ 192.168.1.15
  You open a chat lane directly to Juan's machine
  Juan sees "Erwin: hey" on his terminal
  Nothing left your LAN.
```

---

## What You Will Learn Building v1.1

```
Concept                Module               New skill level
─────────────────────  ───────────────────  ──────────────────────────────
Password hashing       auth.py              Security fundamentals
JSON as a local DB     user_setup.py        Lightweight data persistence
Socket programming     listener.py          How computers talk directly
Threading              chat_session.py      Two things running at once
Port binding           listener.py          How servers actually work
LAN device discovery   peer_discovery.py    How networks find each other
Login gate pattern     main.py update       Auth before access — industry std
```

---

## New File Structure for v1.1

```
nexus/
├── main.py                          ← Updated: login gate added
│
├── modules/
│   │
│   ├── identity/                    ← NEW — NEXUS ID
│   │   ├── __init__.py              ← identity_menu()
│   │   ├── user_setup.py            ← first-time setup wizard
│   │   ├── auth.py                  ← login, hashing, session
│   │   └── profile.py               ← view and edit your identity
│   │
│   └── link/                        ← NEW — NEXUS LINK
│       ├── __init__.py              ← link_menu()
│       ├── listener.py              ← receives messages (socket server)
│       ├── sender.py                ← sends messages (socket client)
│       ├── chat_session.py          ← live two-way chat via threads
│       └── peer_discovery.py        ← find NEXUS users on the LAN
│
└── data/
    ├── users.json                   ← NEW — your local identity
    ├── peers.json                   ← NEW — known peers on your LAN
    ├── config.json                  ← existing
    └── nexus.log                    ← existing
```

---

## Data File Specifications

### data/users.json
Stores your local identity. One user per machine. Never synced anywhere.

```json
{
    "username":   "Erwin",
    "password":   "5e884898da...",
    "ip":         "192.168.1.10",
    "port":       9876,
    "color":      "cyan",
    "created_at": "2026-06-28"
}
```

Field breakdown:
- `username`   — display name shown in chat and the NEXUS banner
- `password`   — SHA-256 hashed, never stored as plaintext
- `ip`         — auto-detected from your network interface on setup
- `port`       — the port NEXUS LINK listens on (default 9876)
- `color`      — your chat color (cyan/green/yellow — terminal ANSI)
- `created_at` — setup date for your own reference

---

### data/peers.json
Stores other NEXUS users you have discovered or added manually.
Each peer entry is added automatically on first contact.

```json
[
    {
        "username":  "Juan",
        "ip":        "192.168.1.15",
        "port":      9876,
        "last_seen": "2026-06-28 14:32",
        "status":    "online"
    },
    {
        "username":  "Maria",
        "ip":        "192.168.1.22",
        "port":      9876,
        "last_seen": "2026-06-27 09:10",
        "status":    "offline"
    }
]
```

---

---

# ─────────────────────────────────────────────
# PHASE 8A — NEXUS ID (Identity System)
# ─────────────────────────────────────────────

**Goal:** Every user sets up a local identity once. On every subsequent
launch of NEXUS, a login prompt appears before the main menu. If no
identity exists yet, the setup wizard runs automatically.

**Build order within this phase:**
```
user_setup.py  →  auth.py  →  profile.py  →  main.py update
```

---

## Install Requirements

```bash
# No new pip installs needed for Phase 8A.
# Uses: hashlib, json, os, socket — all Python built-ins.
```

---

## What to Build

### modules/identity/user_setup.py
First-time setup wizard. Runs once. Writes `data/users.json`.

```
Wizard flow:
  1. Welcome message
  2. Ask for username (3–20 chars, letters/numbers/underscore only)
  3. Ask for password (min 6 chars)
  4. Confirm password
  5. Auto-detect local IP using socket
  6. Ask for preferred chat color (cyan/green/yellow)
  7. Hash the password with SHA-256
  8. Write to data/users.json
  9. Confirm setup complete
```

Key function signatures to implement:
```python
def get_local_ip() -> str:
    # Use socket to detect the machine's LAN IP
    # socket.gethostbyname(socket.gethostname()) as fallback
    # Return "127.0.0.1" if detection fails

def hash_password(password: str) -> str:
    # SHA-256 hash using hashlib
    # hashlib.sha256(password.encode()).hexdigest()
    # Return the hex string

def validate_username(name: str) -> bool:
    # 3-20 chars, alphanumeric + underscore only
    # Use re.match(r'^[a-zA-Z0-9_]{3,20}$', name)

def run_setup() -> dict:
    # Full wizard, returns the user dict after saving
    # Called automatically if users.json does not exist
```

---

### modules/identity/auth.py
Login check. Called every time NEXUS starts.
Returns the logged-in user dict if successful, None if failed.

```
Login flow:
  1. Load data/users.json
  2. Display "NEXUS — Login" prompt
  3. Ask for password (3 attempts max)
  4. Hash the input and compare to stored hash
  5. On success → return user dict, log the login
  6. On 3 failures → lock for 30 seconds, then exit
```

Key function signatures to implement:
```python
def load_user() -> dict | None:
    # Read data/users.json
    # Return dict if exists, None if not

def check_password(input_password: str, stored_hash: str) -> bool:
    # Hash the input and compare to stored hash
    # Return True if match

def login() -> dict | None:
    # Full login flow with 3-attempt limit
    # Returns user dict on success, None on failure

def is_first_run() -> bool:
    # Check if data/users.json exists
    # Return True if missing (triggers setup wizard)
```

---

### modules/identity/profile.py
View and edit your identity after login. Accessible from the menu.

```
Profile menu options:
  [1] View My Profile    — show username, IP, port, created date
  [2] Change Username    — validate and update
  [3] Change Password    — confirm old password first
  [4] Change Chat Color  — cyan / green / yellow
  [5] Show My IP         — useful for sharing with peers
  [0] Back
```

---

### Update main.py — Login Gate

Add the identity check at the very top of `main()` before the menu
loop. This is the gate — nothing in NEXUS is accessible without it.

```python
# main.py — updated main() function

from modules.identity.auth import login, is_first_run
from modules.identity.user_setup import run_setup

def main():
    clear()

    # ── Identity gate ──────────────────────────────────────
    if is_first_run():
        run_setup()            # first time: run wizard

    user = login()             # every time: require login
    if user is None:
        print("\n  [✗] Access denied. Exiting NEXUS.")
        return

    # ── Logged in — show banner with username ──────────────
    while True:
        clear()
        banner(username=user["username"])    # pass name to banner
        choice = menu("MAIN MENU", [
            "NAS Manager",
            "Network Tools",
            "Security Center",
            "System Monitor",
            "Email Tools",
            "Task Scheduler",
            "NEXUS LINK — LAN Chat",         # ← new in v1.1
            "My Identity",                   # ← new in v1.1
        ])
        # ... rest of routing
```

Also update `core/display.py` banner to accept and show the username:
```python
def banner(username: str = ""):
    user_line = f"  Logged in as: {username}" if username else ""
    print(f"""
  {C.CYAN}NEXUS v1.1{C.RESET}
  {C.DIM}{user_line}{C.RESET}
""")
```

---

## How to Test Phase 8A

```bash
python main.py

# First run:
# → Setup wizard appears automatically
# → Enter username: Erwin
# → Enter password: ******
# → Confirm password: ******
# → Detect IP: 192.168.1.10
# → Choose color: cyan
# → "Setup complete. Welcome, Erwin."
# → Login prompt appears immediately after

# Second run:
# → Login prompt only (no wizard)
# → Enter password: ******
# → Main menu appears with "Logged in as: Erwin"

# Wrong password 3 times:
# → "Too many failed attempts. Locked for 30 seconds."
# → NEXUS exits
```

## Phase 8A Checklist
- [ ] `data/users.json` created after setup wizard completes
- [ ] Password stored as SHA-256 hash, never plaintext
- [ ] IP auto-detected correctly (check with `ipconfig` on Windows)
- [ ] Login appears on every subsequent run
- [ ] 3 failed attempts locks and exits
- [ ] Banner shows username after login
- [ ] Profile menu shows correct stored info
- [ ] Password change requires confirming old password first

## Git Commit
```bash
git add .
git commit -m "feat(v1.1): NEXUS ID — local identity, login gate, profile"
```

---

---

# ─────────────────────────────────────────────
# PHASE 8B — NEXUS LINK (LAN Chat)
# ─────────────────────────────────────────────

**Goal:** Two machines on the same LAN, both running NEXUS, can open
a direct chat session with each other. No internet. No server.
Messages travel IP-to-IP over port 9876.

**Build order within this phase:**
```
listener.py → sender.py → chat_session.py → peer_discovery.py
```

> ⚠️  You can build and test Phase 8B solo using 127.0.0.1 (localhost).
> Send a message from one terminal window to another on the same machine.
> Full two-machine testing waits until the T3500 arrives or a second PC
> is available.

---

## Install Requirements

```bash
# No new pip installs needed for Phase 8B.
# Uses: socket, threading, json, datetime — all Python built-ins.
```

---

## How the Socket System Works

```
LISTENER (your machine, always running while NEXUS LINK is open)
──────────────────────────────────────────────────────────────────
  socket.socket()                 create a socket
  socket.bind(('0.0.0.0', 9876)) bind to all interfaces on port 9876
  socket.listen(5)                wait for up to 5 connections
  socket.accept()                 block until someone connects
  conn.recv(1024)                 receive their message (up to 1024 bytes)
  print the message               show it in the terminal
  loop back to accept()           wait for the next one


SENDER (connects to peer's IP when you type a message)
──────────────────────────────────────────────────────────────────
  socket.socket()                 create a socket
  socket.connect((peer_ip, 9876)) connect to their listener
  socket.send(message.encode())   send the message as bytes
  socket.close()                  close after each message
```

Each machine runs BOTH simultaneously using threads:
- **Thread 1** — the listener (always waiting)
- **Thread 2** — the input loop (you type, it sends)

Neither thread blocks the other. This is why threading is needed.

---

## What to Build

### modules/link/listener.py
The server side. Runs in a background thread.
Receives messages and prints them to the terminal.

```python
# Key behavior:
# - Binds to 0.0.0.0:9876 (accepts from any IP on the LAN)
# - Loops forever accepting connections
# - Each message arrives as bytes — decode to string
# - Message format received: "USERNAME|MESSAGE_TEXT"
# - Parse and print: "[14:32] Juan: hey are you there"
# - Log each received message to nexus.log

# Key functions:
def start_listener(port: int = 9876):
    # Runs in a thread — loop forever
    # Print incoming messages as they arrive

def stop_listener():
    # Sets a flag to stop the loop cleanly on exit
```

---

### modules/link/sender.py
The client side. Called each time the user presses Enter.

```python
# Key behavior:
# - Takes target IP, port, sender username, and message text
# - Opens a socket connection to target
# - Sends "USERNAME|MESSAGE_TEXT" encoded as bytes
# - Closes connection immediately after
# - Returns True on success, False on failure (peer offline)

# Key function:
def send_message(target_ip: str, port: int, username: str, message: str) -> bool:
    # Try to connect and send
    # Handle ConnectionRefusedError gracefully
    # Return bool so chat_session knows if it worked
```

---

### modules/link/chat_session.py
Combines listener and sender into one live chat experience.
This is the main function the menu calls.

```python
# Full chat session flow:
# 1. Load logged-in user from data/users.json
# 2. Show peer selection (from data/peers.json or manual IP entry)
# 3. Start listener thread (background)
# 4. Enter input loop:
#    - Print prompt with user's name
#    - Wait for user to type
#    - On Enter: call sender.send_message()
#    - On /exit: stop listener thread, return to menu
#    - On /peers: show known peers list
#    - On /clear: clear the chat display

# Chat display format:
# ──────────────────────────────────────
#   [14:32] You    : hey are you there
#   [14:32] Juan   : yeah whats up
#   [14:33] You    : check the NAS later
# ──────────────────────────────────────
#   Erwin > _
```

Special commands to implement inside the chat:
```
/exit       — leave chat, back to NEXUS LINK menu
/peers      — list known peers and their status
/clear      — clear the terminal chat display
/myip       — show your own IP (useful for sharing)
/help       — show available commands
```

---

### modules/link/peer_discovery.py
Scans the LAN for other machines running NEXUS on port 9876.
Saves discovered peers to `data/peers.json`.

```python
# Discovery strategy:
# 1. Get your own IP (e.g. 192.168.1.10)
# 2. Derive the base range (192.168.1.1 to 192.168.1.254)
# 3. For each IP in range, try socket.connect((ip, 9876))
# 4. If connection succeeds → NEXUS is running there
# 5. Send a special discovery handshake: "NEXUS_DISCOVER|your_username"
# 6. Peer responds with: "NEXUS_HELLO|their_username"
# 7. Save peer to data/peers.json with username and IP
# 8. Use ThreadPoolExecutor for speed (scan all IPs concurrently)

# Key functions:
def scan_for_peers(port: int = 9876) -> list:
    # Returns list of discovered peer dicts

def save_peer(username: str, ip: str, port: int):
    # Add to peers.json if not already there
    # Update last_seen if already exists

def load_peers() -> list:
    # Read peers.json
    # Return list, empty list if file missing
```

---

### modules/link/__init__.py
The menu that ties everything together.

```
NEXUS LINK menu:
  [1] Open Chat        — select a peer and start chatting
  [2] Add Peer         — manually add a peer by IP
  [3] Discover Peers   — scan LAN for NEXUS users
  [4] View Known Peers — list everyone in peers.json
  [0] Back to Main Menu
```

---

## Message Protocol Specification

All messages between NEXUS instances follow this format:

```
STANDARD MESSAGE:
  "MSG|username|message_text"
  Example: "MSG|Erwin|hey are you there"

DISCOVERY HANDSHAKE:
  Sent:     "NEXUS_DISCOVER|username|ip"
  Response: "NEXUS_HELLO|username|ip"

All strings encoded as UTF-8 bytes.
Max message size: 1024 bytes per transmission.
```

Both machines must follow this protocol so listener.py can
correctly parse every incoming transmission type.

---

## Solo Testing Method (No Second PC Needed)

```bash
# Terminal 1 — start NEXUS as normal user
python main.py
# → Login → NEXUS LINK → Open Chat → type 127.0.0.1 as peer IP

# Terminal 2 — simulate a peer on the same machine
python -c "
import socket
s = socket.socket()
s.connect(('127.0.0.1', 9876))
s.send('MSG|Juan|hey this is a test message'.encode())
s.close()
print('Message sent.')
"

# Terminal 1 should display:
# [14:32] Juan: hey this is a test message
```

This lets you test the full receive path before any second machine
is available. Send path is tested the same way in reverse.

---

## How to Test Phase 8B (When Second Machine Available)

```
Machine A (yours):                Machine B (T3500 / second PC):
──────────────────────────────    ──────────────────────────────
python main.py                    python main.py
Login as Erwin                    Login as Juan
NEXUS LINK → Discover Peers       NEXUS LINK → (listener running)
→ finds Juan @ 192.168.1.15       → sees "Erwin wants to connect"
Open Chat → select Juan           → chat session opens on their end
Type: "hey Juan"                  → displays "[Erwin] hey Juan"
→ Juan types back                 Type: "hey Erwin whats up"
→ displays on your screen         → displays on your screen
```

---

## Phase 8B Checklist

- [ ] `listener.py` receives a message sent via raw socket test
- [ ] `sender.py` sends a message to 127.0.0.1 successfully
- [ ] `chat_session.py` runs listener thread in background without blocking input
- [ ] Typing a message in the input loop sends it via sender
- [ ] `/exit` closes the chat cleanly without crashing
- [ ] `/clear` clears terminal display
- [ ] `peer_discovery.py` scans LAN and finds at least localhost (127.0.0.1)
- [ ] Discovered peers saved to `data/peers.json`
- [ ] Known peers shown in the NEXUS LINK menu
- [ ] Messages logged to `data/nexus.log`

## Git Commit
```bash
git add .
git commit -m "feat(v1.1): NEXUS LINK — LAN p2p chat, peer discovery, solo tested"
```

---

---

# v1.1 Release Checklist (Both Phases Done)

```
NEXUS ID
  - [ ] Setup wizard runs on first launch
  - [ ] Login gate blocks access without correct password
  - [ ] Password stored as SHA-256 hash
  - [ ] Profile menu works (view, change name, change password)
  - [ ] Banner shows username after login
  - [ ] data/users.json in .gitignore (personal data not pushed)

NEXUS LINK
  - [ ] Listener receives messages from another socket
  - [ ] Sender delivers messages to a target IP
  - [ ] Chat session runs both simultaneously via threads
  - [ ] Solo test passes (127.0.0.1 loopback)
  - [ ] Peer discovery scans and saves peers
  - [ ] data/peers.json persists between sessions
  - [ ] All chat activity logged to nexus.log
  - [ ] data/peers.json in .gitignore (LAN topology stays private)
```

---

# .gitignore Updates for v1.1

Add these lines to your root `.gitignore`:

```
# v1.1 — identity and peer data (private, machine-specific)
data/users.json
data/peers.json
```

These files contain your local IP, hashed password, and LAN peer
list. They should never be pushed to GitHub — each machine generates
its own.

---

# Final v1.1 Git Tag

Once both phases pass their checklists:

```bash
git add .
git commit -m "release: NEXUS v1.1 — NEXUS ID + NEXUS LINK"
git tag v1.1
git push origin main --tags
```

---

# What v1.2 Could Look Like (Future Planning)

```
Possible next features after v1.1:
  → NEXUS LINK file transfer   — send a file over the LAN socket
  → Group broadcast            — send to all peers at once
  → Chat history               — persist messages to a local log file
  → NEXUS LINK encryption      — XOR or AES encrypt messages in transit
  → Web UI for NEXUS LINK      — chat in browser via Flask + WebSocket
  → NAS web dashboard          — resume when T3500 arrives
```

---

*NEXUS v1.1 Build Guide*
*Features: NEXUS ID + NEXUS LINK*
*All data stored locally. No server. No internet required.*
