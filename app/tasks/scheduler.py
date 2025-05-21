"""Scheduler for automating tasks execution"""

import time

import schedule

from app import settings
from .helper import schedule_tasks, schedule_task
from ..game import tasks, close_game, game_is_open
from ..utils.events import run_handle_events, register_event
from ..utils.service import check_shutdown
from app.utils.log import logger
log = logger(__name__)
from pytimeparse import parse


def check_idle():

    next_job_time = schedule.next_run()

    if 0 < settings.ACTION_DRIVER_IDLE_CLOSE < next_job_time.timestamp() - time.time():
        # proc = driver.is_running()
        is_open = game_is_open()

        if is_open:
            log.info(
                f"check_idle: Entering idle {settings.ACTION_DRIVER_IDLE_CLOSE}s. is_open: {is_open} Next job: {next_job_time}")
            # proc:
            close_game()
            return True

    return False


def handle_schedule_task(data):
    try:
        task_name = data.get("name")
        function = data.get("function")
        interval = data.get("interval")
        args = data.get("args", [])
        once = data.get("once", False)

        log.info(f"[schedule_task] Scheduled task '{task_name}' -> {function} (once={once})")

        if not all([task_name, function, interval]):
            log.warning(f"[schedule_task] Missing required fields: {data}")
            return

        # Compose the config dict
        config = {
            "function": function,
            "interval": interval,
            "args": args,
            "once": once
        }

        # Use existing schedule_task function
        schedule_task(task_name, config)

    except Exception as e:
        log.exception(f"[schedule_task] Failed to schedule task: {e}")

def keep_running():
    if check_shutdown():
        log.warning("Shutdown received")
        return False

    # settings.ACTION_DRIVER_IDLE_CLOSE
    int(time.time()) % parse("2 minutes") == 0 and check_idle()

    return True


def run_scheduled_tasks():
    from .daily import run_all_tasks as DailyTasks
    from .hourly import run_all_tasks as HourlyTasks

    register_event("schedule_task", handle_schedule_task)

    tasks.schedule_game_tasks()

    # some generic internal tasks
    schedule_tasks({
        "hourly": {
            "function": HourlyTasks,
            "interval": "1 hour",  # Run every 1 hour,
        },
        "daily": {
            "function": DailyTasks,
            "interval": "1 day",
        }
    })
    log.info("Multi-task scheduler started...")

    schedule.run_all()

    while keep_running():
        schedule.run_pending()
        run_handle_events()  # ⬅️ now also checks for shutdown

        time.sleep(1)
