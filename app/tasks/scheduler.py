"""Scheduler for automating tasks execution"""

import time

import schedule

from app import settings
from .helper import schedule_tasks
from ..game import tasks, close_game, game_is_open
from ..utils.events import run_handle_events
from ..utils.service import check_shutdown
from app.utils.log import logger
log = logger(__name__)


def check_idle():

    next_job_time = schedule.next_run()

    if 0 < settings.ACTION_DRIVER_IDLE_CLOSE < next_job_time.timestamp() - time.time():
        # proc = driver.is_running()
        is_open = game_is_open()
        log.info(
            f"check_idle: Entering idle {settings.ACTION_DRIVER_IDLE_CLOSE}s. isopen: {is_open} Next job: {next_job_time}")

        if is_open:
            # proc:
            close_game()
            return True

    return False

def keep_running():
    if check_shutdown():
        log.warning("Shutdown received")
        return False

    check_idle()

    return True


def run_scheduled_tasks():
    from .daily import run_all_tasks as DailyTasks
    from .hourly import run_all_tasks as HourlyTasks

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
