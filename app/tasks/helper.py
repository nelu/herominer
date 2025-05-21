from datetime import datetime
from pytimeparse import parse
import schedule

from app.utils.events import publish_event
from app.utils.service import run_package, parse_call_function, GracefulExit
from app.utils.session import status
from app.utils.log import logger

log = logger(__name__)

CONFIG = {}


def get_configured_tasks():
    return CONFIG


def has_ran(task_name, outside_timeframe):
    interval = int(outside_timeframe) if isinstance(outside_timeframe, int) else parse(outside_timeframe)
    lr = get_last_run(task_name)
    offset = 10  # trigger 10 seconds earlier; 1s should be sufficient for the task last run to get updated
    return lr and (datetime.now() - lr).total_seconds() + offset <= interval


def schedule_task(task_name, config):
    """
    Schedules a specific task based on its configuration.

    :param config:
    :param task_name: Name of the task.
    """
    job = None

    # Only scheduling logic without 'after'
    if config.get("interval"):
        job = schedule.every(parse(config["interval"]))
        job.unit = 'seconds'
    elif config.get("at"):
        job = schedule.every().day.at(config["at"])

    job = job.do(execute_task, task_name, job)

    tags = config.get("tags")
    if tags:
        job.tag(*tags)

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
    task_config = CONFIG[task_name]
    r = None

    task_before = task_config.get("before")
    task_after = task_config.get("after")

    current_time = now.time()

    # Skip if the current time is beyond the 'before' limit
    if task_before:
        before_limit = datetime.strptime(task_before, "%H:%M:%S").time()
        if current_time >= before_limit:
            log.debug(
                f"execute_task: {task_name} - Skipped (current time {current_time} is after 'before' limit {task_before})")
            return False

    # Skip if the current time hasn't reached the 'after' limit yet
    if task_after:
        after_limit = datetime.strptime(task_after, "%H:%M:%S").time()
        if current_time < after_limit:
            log.debug(
                f"execute_task: {task_name} - Skipped (current time {current_time} is before 'after' limit {task_after})")
            return False

    interval = parse(task_config["interval"])
    remaining = (job.next_run
                 and interval - abs(job.next_run - datetime.now()).total_seconds()
                 or interval)

    if not has_ran(task_name, interval):
        log.info(f"execute_task: {task_name}")
        args = task_config.get("args", [])

        update_run_stats(task_name, now, job)
        tag_checks = parse_tag_actions(task_config.get("tags", []))

        r = (tag_checks is not False
             and run_package({
                    'function': task_config["function"],
                    'args': args
                }, log))

        update_run_stats(task_name, now, job, task_result=r)

        remaining = interval - abs((job.next_run - datetime.now()).total_seconds())
        duration = datetime.now() - now
        log.debug(
            f"execute_task: {task_name} - result: {r}. Duration: {duration.total_seconds()}s. Next run in {remaining / 60} minutes.")

    else:
        log.debug(f"execute_task: {task_name} - skipping. Next run in {remaining / 60} minutes.")

    if task_config.get("once"):
        log.info(f"execute_task: {task_name}: unscheduling one-time task.")
        schedule.cancel_job(job)
        # return schedule.CancelJob

    return r


def parse_tag_actions(tags):
    r = None
    for tag in tags:
        if ':' not in tag:
            continue

        tag_action, method_name = tag.split(':', 1)

        match tag_action:
            case 'if':
                r = bool(run_package({'function': method_name}, log, False))
            case 'do':
                pass
            case _:
                pass

        if r is False:
            break

    return r


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
