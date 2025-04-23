import logging
import os
from logging.handlers import TimedRotatingFileHandler
from rlh import RedisStreamLogHandler

from app.settings import APP_LOG_FILE
from app.utils.redis_helpers import redis_client

# Create a log formatter
log_formatter = logging.Formatter("%(asctime)s - [%(process)d] - %(levelname)s - [%(name)s] - %(message)s")

# ** Console Handler** (Logs to terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logfile_handler = None
APP_LOG_VERBOSITY = 1


def setLogging(log_file=None):
    """Set up logging with a timed rotating file handler.

    Args:
        log_file (str): Full path of the log file (e.g., "/var/logs/app.log").
    """
    global logfile_handler

    if log_file is not None:
        # Extract directory from log file path
        logs_dir = os.path.dirname(log_file)

        # Ensure the log directory exists
        if logs_dir and not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)

        if os.path.exists(logs_dir) and not os.path.isdir(log_file):
            # ** Timed Rotating File Handler** (Logs to file)
            logfile_handler = TimedRotatingFileHandler(
                filename=log_file,
                when="midnight",  # Rotate daily at midnight
                interval=1,  # Rotate every 1 day
                backupCount=7,  # Keep last 7 days of logs
                encoding="utf-8",
                utc=True  # Use UTC time for log rotation
            )

            logfile_handler.setFormatter(log_formatter)
            logfile_handler.suffix = "%Y-%m-%d"  # Log file name format: app.log.YYYY-MM-DD


def logger(name=None):
    global logfile_handler

    l = logging.getLogger(name)

    l.setLevel(level=APP_LOG_VERBOSITY * 10)
    # ** Add handlers (console + file)**
    l.addHandler(console_handler)

    l.addHandler(RedisStreamLogHandler(
        fields=['process', "levelname", 'name', "msg", "asctime"],
        redis_client=redis_client,
        channel_name="logs",
        maxlen=30000))

    logfile_handler and l.addHandler(logfile_handler)

    # ** Prevent log duplication**
    l.propagate = False

    return l


setLogging(APP_LOG_FILE)
# root_logger = logger()
