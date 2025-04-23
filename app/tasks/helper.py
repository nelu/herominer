import importlib
from datetime import datetime
from pytimeparse import parse
import schedule
from app.utils.session import status
from app.utils.log import logger
log = logger(__name__)

CONFIG = {}


def has_ran(task_name, outside_timeframe):
    interval = int(outside_timeframe) if isinstance(outside_timeframe, int) else parse(outside_timeframe)
    lr = get_last_run(task_name)
    return lr is None or (datetime.now() - lr).total_seconds() >= interval


def schedule_task(task_name, config):
    """
    Schedules a specific task based on its configuration.

    :param config:
    :param task_name: Name of the task.
    """
    if task_name not in CONFIG:
        set_task_config(task_name, config)

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
    now = datetime.now()
    last_run_time = get_last_run(task_name)

    interval = (CONFIG[task_name].get("interval")
                and parse(CONFIG[task_name]["interval"])
                or int((job.next_run - datetime.now()).total_seconds()))
    remaining = interval - (now - last_run_time).total_seconds()

    if has_ran(task_name, interval):
        log.info(f"Task executing {task_name}")
        status().set("task_current", mapping={
            "task_current": task_name,
            "task_start": now.strftime('%Y-%m-%d %H:%M:%S'),
            "task_nextrun": job.next_run.strftime('%Y-%m-%d %H:%M:%S'),
        })

        call_function = CONFIG[task_name]["function"]
        args = CONFIG[task_name].get("args", [])

        if isinstance(call_function, str):
            # Import the function dynamically from a string
            module_name, func_name = call_function.rsplit(".", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
            r = func(*args)
        elif callable(call_function):
            # Directly call it if it's already a function or method
            r = call_function(*args)
        else:
            raise TypeError(f"Invalid function type for task '{task_name}': {type(call_function)}")
        log.debug(f"Task {task_name} result {r}. Next run in {remaining // 60} minutes.")
        set_last_run(task_name, run_status=r, timestamp=now)  # Update last run time in Redis
    else:
        log.debug(f"Task skipping {task_name}. Next run in {remaining // 60} minutes.")


def set_task_config(task_name, config):
    """
    Sets or updates the configuration for a task.

    :param task_name: Name of the task.
    :param config:
        - function: The function to execute.
        - interval: Interval at which the task should run (e.g., "1 hour").

    """
    CONFIG[task_name] = config
    log.debug(f"Task created: {task_name} → interval: {config.get('interval')} - at: {config.get('at')} - after: {config.get('after')}")


def get_last_run(task_name):
    """Retrieve last run time from Redis"""
    last_run = status('last_run').get(task_name)
    return last_run and datetime.strptime(last_run, "%Y-%m-%d %H:%M:%S")

def get_last_run_status(task_name):
    """Retrieve last run time from Redis"""
    return status('last_run_status').get(task_name)

def set_last_run(task_name, run_status = None, timestamp=datetime.now()):

    """Store last run time in Redis"""
    status('last_run_status').set(task_name, run_status)
    status().set('task_lastrun_result', run_status)
    return status('last_run').set(task_name, timestamp.strftime("%Y-%m-%d %H:%M:%S")) and timestamp
