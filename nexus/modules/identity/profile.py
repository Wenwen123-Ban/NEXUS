# ============================================================
# modules/identity/profile.py — View and edit local NEXUS ID
# ============================================================
from __future__ import annotations

from core.display import error, menu, pause, section, success, table, warn
from core.logger import log
from modules.identity.auth import check_password, load_user
from modules.identity.user_setup import VALID_COLORS, get_local_ip, hash_password, save_user, validate_username


def view_profile(user: dict) -> None:
    section("MY PROFILE")
    table(["Field", "Value"], [["Username", user.get("username", "")], ["IP", user.get("ip", "")], ["Port", user.get("port", "")], ["Color", user.get("color", "")], ["Created", user.get("created_at", "")]])
    pause()


def change_username(user: dict) -> dict:
    section("CHANGE USERNAME")
    name = input("  New username: ").strip()
    if not validate_username(name):
        error("Username must be 3-20 characters and use only letters, numbers, or underscore.")
        pause()
        return user
    old = user.get("username", "unknown")
    user["username"] = name
    save_user(user)
    log(f"NEXUS ID username changed from {old} to {name}.")
    success("Username updated.")
    pause()
    return user


def change_password(user: dict) -> dict:
    section("CHANGE PASSWORD")
    old_password = input("  Current password: ").strip()
    if not check_password(old_password, str(user.get("password", ""))):
        error("Current password is incorrect.")
        pause()
        return user
    new_password = input("  New password (min 6 chars): ").strip()
    confirm = input("  Confirm new password: ").strip()
    if len(new_password) < 6 or new_password != confirm:
        error("New passwords must match and be at least 6 characters.")
        pause()
        return user
    user["password"] = hash_password(new_password)
    save_user(user)
    log(f"NEXUS ID password changed for {user.get('username', 'unknown')}.")
    success("Password updated.")
    pause()
    return user


def change_color(user: dict) -> dict:
    section("CHANGE CHAT COLOR")
    color = input("  New color [cyan/green/yellow]: ").strip().lower()
    if color not in VALID_COLORS:
        error("Choose one of: cyan, green, yellow.")
        pause()
        return user
    user["color"] = color
    save_user(user)
    success("Chat color updated.")
    pause()
    return user


def identity_menu(user: dict | None = None) -> dict:
    current = user or load_user() or {}
    while True:
        section("MY IDENTITY")
        choice = menu("PROFILE OPTIONS", ["View My Profile", "Change Username", "Change Password", "Change Chat Color", "Show My IP"])
        if choice == "1":
            view_profile(current)
        elif choice == "2":
            current = change_username(current)
        elif choice == "3":
            current = change_password(current)
        elif choice == "4":
            current = change_color(current)
        elif choice == "5":
            current["ip"] = get_local_ip()
            save_user(current)
            success(f"My IP: {current['ip']}")
            pause()
        elif choice == "0":
            return current
        else:
            warn("Invalid selection. Choose a listed option.")
