# modules/email_tools/alert_mailer.py
# Called by other modules to fire alert emails
from modules.email_tools.email_sender import build_email, send_email
from core.config import CONFIG
from core.display import section, warn

def send_alert(subject: str, body: str):
    """Send an alert to the configured alert_email address."""
    msg = build_email(
        to      = CONFIG["alert_email"],
        subject = f"[NEXUS ALERT] {subject}",
        body    = body
    )
    send_email(msg)

def run():
    section("SEND ALERT EMAIL")
    warn("This module is triggered automatically by other modules.")
    warn("You can also call send_alert(subject, body) directly in code.")
    input("  Press Enter to go back...")
