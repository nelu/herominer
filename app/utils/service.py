"""Utility functions for game automation"""

import time

import app
from app.utils.session import status


# set the app stop flag
class GracefulExit(Exception):
    pass


def check_shutdown():
    app.STOP_SIGNALED = status().exists("game:stop")

    if app.STOP_SIGNALED:
        raise GracefulExit(f"{__name__} received shutdown signal.")

    # self.close()
    # self.process.terminate()
    return app.STOP_SIGNALED

def clear_shutdown():
    app.STOP_SIGNALED = False
    status().remove("game:stop")

def wait(seconds):
    """Pauses execution for a specified time"""
    time.sleep(seconds)
