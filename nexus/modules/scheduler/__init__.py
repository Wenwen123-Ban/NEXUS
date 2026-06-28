from core.display import menu, clear, section

def scheduler_menu():
    while True:
        clear()
        section("TASK SCHEDULER")
        choice = menu("SCHEDULER OPTIONS", [
            "View Scheduled Tasks",
            "Add a Task",
            "Run Scheduler Now",
        ])
        if choice == "1":
            from modules.scheduler.task_runner import view_tasks
            view_tasks()
        elif choice == "2":
            from modules.scheduler.task_runner import add_task
            add_task()
        elif choice == "3":
            from modules.scheduler.task_runner import run_scheduler
            run_scheduler()
        elif choice == "0":
            break
