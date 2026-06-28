from core.display import menu, clear, section

def email_menu():
    while True:
        clear()
        section("EMAIL TOOLS")
        choice = menu("EMAIL OPTIONS", [
            "Send a Test Email",
            "Send Alert Email",
        ])
        if choice == "1":
            from modules.email_tools.email_sender import run
            run()
        elif choice == "2":
            from modules.email_tools.alert_mailer import run
            run()
        elif choice == "0":
            break
