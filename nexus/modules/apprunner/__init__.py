from __future__ import annotations

from core.config import DATA_DIR
from core.display import clear, error, menu, pause, section, success, table, warn
from modules.apprunner.port_checker import is_port_in_use, open_in_browser
from modules.apprunner.process_store import get_app, load_apps
from modules.apprunner.runner import launch_app, refresh_statuses, restart_app, stop_app


def _select_app(apps: list[dict]) -> dict | None:
    if not apps:
        return None

    identifier = input("  App ID or number: ").strip()
    if not identifier:
        return None

    if identifier.isdigit():
        index = int(identifier) - 1
        if 0 <= index < len(apps):
            return apps[index]
        return None

    for app in apps:
        if str(app.get("id", "")).lower() == identifier.lower():
            return app
    return None


def _show_apps(apps: list[dict]) -> None:
    if not apps:
        warn("No tracked apps yet.")
        return

    rows = [
        [
            app.get("id", "-"),
            app.get("name", "-"),
            app.get("port", "-"),
            app.get("status", "unknown"),
            app.get("pid") or "-",
        ]
        for app in apps
    ]
    table(["ID", "Name", "Port", "Status", "PID"], rows)


def _launch_new_app() -> None:
    section("LAUNCH NEW APP")
    name = input("  Display name: ").strip()
    file_path = input("  Python file path: ").strip()
    port_raw = input("  Port (5000): ").strip()

    if not name or not file_path:
        error("Name and file path are required.")
        pause()
        return

    try:
        port = int(port_raw or 5000)
    except ValueError:
        error("Port must be a number.")
        pause()
        return

    if is_port_in_use(port):
        warn(f"Port {port} is already in use. Continue anyway? [y/N]")
        answer = input("  ").strip().lower()
        if answer not in {"y", "yes"}:
            success("Launch cancelled.")
            pause()
            return

    result = launch_app(name, file_path, port)
    if result:
        success(f"{result['name']} launched on port {result['port']} (PID {result['pid']}).")
    else:
        error("Launch failed. Check the file path or process startup.")
    pause()


def _stop_app() -> None:
    apps = refresh_statuses()
    if not apps:
        warn("No tracked apps to stop.")
        pause()
        return

    section("STOP AN APP")
    _show_apps(apps)
    chosen = _select_app(apps)
    if not chosen:
        warn("No app selected.")
        pause()
        return

    if stop_app(chosen["id"]):
        success(f"{chosen['name']} stopped.")
    else:
        error(f"Could not stop {chosen['name']}.")
    pause()


def _restart_app() -> None:
    apps = refresh_statuses()
    if not apps:
        warn("No tracked apps to restart.")
        pause()
        return

    section("RESTART AN APP")
    _show_apps(apps)
    chosen = _select_app(apps)
    if not chosen:
        warn("No app selected.")
        pause()
        return

    result = restart_app(chosen["id"])
    if result:
        success(f"{result['name']} restarted on port {result['port']} (PID {result['pid']}).")
    else:
        error(f"Could not restart {chosen['name']}.")
    pause()


def _view_app_log() -> None:
    section("APP LOG")
    log_path = DATA_DIR / "nexus.log"
    if not log_path.exists():
        warn("No log file found.")
        pause()
        return

    app_name = input("  App name to filter: ").strip()
    if not app_name:
        app_name = ""

    with log_path.open("r", encoding="utf-8") as handle:
        lines = [line.rstrip() for line in handle if app_name.lower() in line.lower()]

    if not lines:
        warn("No matching log entries found.")
    else:
        for line in lines[-20:]:
            print(f"  {line}")
    pause()


def _toggle_auto_start() -> None:
    apps = refresh_statuses()
    if not apps:
        warn("No tracked apps to toggle.")
        pause()
        return

    section("TOGGLE AUTO-START")
    _show_apps(apps)
    chosen = _select_app(apps)
    if not chosen:
        warn("No app selected.")
        pause()
        return

    auto_start = bool(chosen.get("auto_start", False))
    current = "enabled" if auto_start else "disabled"
    new_value = not auto_start
    get_app(chosen["id"])
    from modules.apprunner.process_store import update_app

    update_app(chosen["id"], {"auto_start": new_value})
    success(f"Auto-start {new_value and 'enabled' or 'disabled'} for {chosen['name']}.")
    pause()


def apprunner_menu() -> None:
    while True:
        clear()
        refresh_statuses()
        apps = load_apps()
        section("NEXUS APP RUNNER")
        print(f"  Apps tracked: {len(apps)}")
        _show_apps(apps)
        choice = menu("APP RUNNER", ["Launch New App", "Stop an App", "Restart an App", "View App Log", "Open in Browser", "Toggle Auto-Start"])

        if choice == "1":
            _launch_new_app()
        elif choice == "2":
            _stop_app()
        elif choice == "3":
            _restart_app()
        elif choice == "4":
            _view_app_log()
        elif choice == "5":
            apps = refresh_statuses()
            if not apps:
                warn("No tracked apps to open.")
                pause()
                continue
            _show_apps(apps)
            chosen = _select_app(apps)
            if chosen:
                open_in_browser(int(chosen.get("port", 5000)))
                success(f"Opened http://localhost:{chosen.get('port', 5000)}")
            else:
                warn("No app selected.")
            pause()
        elif choice == "6":
            _toggle_auto_start()
        elif choice == "0":
            break
        else:
            warn("Invalid selection. Choose a listed option.")
            pause()
