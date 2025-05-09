import importlib
from datetime import datetime, timedelta
from pytimeparse import parse
import schedule

from app.utils.events import publish_event
from app.utils.service import run_package, parse_call_function
from app.utils.session import status
from app.utils.log import logger

log = logger(__name__)

CONFIG = {}


def get_configured_tasks():
    return CONFIG


def has_ran(task_name, outside_timeframe):
    interval = int(outside_timeframe) if isinstance(outside_timeframe, int) else parse(outside_timeframe)
    lr = get_last_run(task_name)
    return lr and (datetime.now() - lr).total_seconds() <= interval - 10 # 10 seconds offset


def schedule_task(task_name, config):
    """
    Schedules a specific task based on its configuration.

    :param config:
    :param task_name: Name of the task.
    """

    job = None
    if config.get("after"):
        # hourly after a specific hour
        job = schedule.every(parse(config["interval"])).days.at(config["after"])
        job.unit = 'seconds'
        job = job.do(execute_task, task_name, job)
    elif config.get("interval"):
        job = schedule.every(parse(config["interval"]))  # Parse interval dynamically
        job.unit = 'seconds'
        job = job.do(execute_task, task_name, job)
    elif config.get("at"):
        # daily at a specific hour
        job = schedule.every().day.at(config["at"])
        job = job.do(execute_task, task_name, job)

    if task_name not in CONFIG:
        config['job'] = job
        set_task_config(task_name, config)

    return job


def schedule_from_config(tasks_config):
    tasks = {}
    for task_name, conf in tasks_config.items():
        conf['function'] = conf.get('function', f"{task_name}")
        tasks[f"{task_name}"] = conf

    return schedule_tasks(tasks)


def schedule_tasks(configuration):
    """Schedules all tasks dynamically based on defined intervals."""
    for task_name in configuration:
        schedule_task(task_name, configuration[task_name])


def execute_task(task_name, job):
    now = datetime.now()  # 10 seconds offset
    interval = parse(CONFIG[task_name]["interval"])
    remaining = (job.next_run
                 and interval - abs(job.next_run - datetime.now()).total_seconds()
                 or interval)

    if not has_ran(task_name, interval):
        log.info(f"Task executing {task_name}")
        call_function = CONFIG[task_name]["function"]
        args = CONFIG[task_name].get("args", [])

        update_run_stats(task_name, now, job)

        if isinstance(call_function, str):
            args_dict = {
                'args': args,
            }
            # Import the function dynamically from a string
            args_dict.update(parse_call_function(f"app.{call_function}"))
            r = run_package(args_dict, log)

        elif callable(call_function):
            # Directly call it if it's already a function or method
            r = call_function(*args)
        else:
            raise TypeError(f"Invalid function type for task '{task_name}': {type(call_function)}")

        update_run_stats(task_name, now, job, task_result=r)

        remaining = interval - abs((job.next_run - datetime.now()).total_seconds())
        log.debug(f"Task {task_name} result {r}. Next run in {remaining / 60} minutes.")

    else:
        log.debug(f"Task skipping {task_name}. Next run in {remaining / 60} minutes.")

    if CONFIG[task_name].get("once"):
        log.info(f"One-time task '{task_name}' completed. Unscheduling.")
        schedule.cancel_job(job)


def set_task_config(task_name, config):
    """
    Sets or updates the configuration for a task.

    :param task_name: Name of the task.
    :param config:
        - function: The function to execute.
        - interval: Interval at which the task should run (e.g., "1 hour").

    """
    CONFIG[task_name] = config
    log.debug(
        f"Task created: {task_name} → interval: {config.get('interval')} - at: {config.get('at')} - after: {config.get('after')}")


def get_last_run(task_name):
    """Retrieve last run time from Redis"""
    last_run = status('tasks').get(task_name)
    return last_run and datetime.strptime(last_run['task_start'], "%Y-%m-%d %H:%M:%S")


def update_run_stats(task_name, task_start, job, task_result=None):
    value = {
        "once": CONFIG[task_name].get("once"),
        "function": str(CONFIG[task_name].get("function", task_name)),
        "interval_seconds": parse(CONFIG[task_name]["interval"]),
        "task_start": task_start.strftime('%Y-%m-%d %H:%M:%S'),
        "task_nextrun": job.next_run.strftime('%Y-%m-%d %H:%M:%S'),
        "task_finish": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "task_result": task_result,
    }

    if task_result:
        publish_event('task_result', value)

    return status('tasks').set(task_name, value=value)


def get_last_run_status(task_name):
    """Retrieve last run time from Redis"""
    last_run = status('tasks').get(task_name)
    return last_run and last_run['task_result']
