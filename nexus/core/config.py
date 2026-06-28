# ============================================================
# core/config.py — Central configuration loader
# Edit data/config.json to change settings.
# ============================================================
import json, os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")

DEFAULTS = {
    "sender_email":    "your_email@gmail.com",
    "sender_password": "your_app_password",
    "smtp_server":     "smtp.gmail.com",
    "smtp_port":       587,
    "alert_email":     "your_email@gmail.com",
    "nas_path":        "/mnt/nas",
    "cpu_alert_threshold":  90,
    "ram_alert_threshold":  85,
    "disk_alert_threshold": 90,
    "ping_range":      "192.168.1.1-254",
}

def load():
    if not os.path.exists(CONFIG_PATH):
        save(DEFAULTS)
        return DEFAULTS
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save(cfg: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)

CONFIG = load()
