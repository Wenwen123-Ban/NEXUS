# modules/email_tools/email_sender.py
# Your email sender — migrated from standalone script
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from core.config import CONFIG
from core.display import section, success, error, warn
from core.logger import log

def build_email(to, subject, body, body_type="plain", attachment_path=None):
    msg = MIMEMultipart()
    msg["From"]    = CONFIG["sender_email"]
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, body_type))
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attachment_path)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)
    return msg

def send_email(msg):
    try:
        server = smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"])
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(CONFIG["sender_email"], CONFIG["sender_password"])
        server.sendmail(CONFIG["sender_email"], msg["To"], msg.as_string())
        log(f"Email sent to {msg['To']} | Subject: {msg['Subject']}")
        success(f"Email sent to {msg['To']}!")
    except smtplib.SMTPAuthenticationError:
        error("Auth failed. Check your App Password in data/config.json")
        log("Email auth failed.", "ERROR")
    except Exception as e:
        error(f"Failed: {e}")
        log(str(e), "ERROR")
    finally:
        try: server.quit()
        except: pass

def run():
    section("SEND TEST EMAIL")
    to      = input("  To      : ").strip()
    subject = input("  Subject : ").strip()
    body    = input("  Body    : ").strip()
    msg = build_email(to, subject, body)
    send_email(msg)
    input("\n  Press Enter to go back...")
