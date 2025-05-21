"""Core game mechanics and logic with Redis storage"""
import signal

import app
from app.utils.service import clear_shutdown, GracefulExit
from app.utils.session import status
from app.web import WebServer
from app.web.websocket_server import SocketIOWebServer
from utils.log import logger

#from app.web.webserver import DjangoServer

log = logger(__name__)

#httpserver = DjangoServer(port=80)
# httpserver = WebServer()
httpserver = SocketIOWebServer()



def start():
    from app.tasks import scheduler

    #signal.signal(signal.SIGINT, signal_shutdown)  # Handle Ctrl+C (SIGINT)
    signal.signal(signal.SIGTERM, signal_shutdown)  # Handle termination (SIGTERM)

    # Start server in background
    httpserver.start()
    #start_http_server(port=80, static_path=os.path.join(settings.APP_DATA_DIR, 'web'))

    """Starts the game mechanics"""
    log.info("Hero Wars automation started.")
    clear_shutdown()  # better be safe
    status().set("started_at")

    try:
        scheduler.run_scheduled_tasks()
    except (KeyboardInterrupt, GracefulExit) as err:
        log.exception(f"start: KeyboardInterrupt/GracefulExit {err}")
        stop_workers()
        raise
    except Exception:
        stop_workers()
        raise

    return True

def stop_workers():
    httpserver.stop()
    #stop_http_server()
    from app.driver import player as driver
    driver.stop()

def stop():
    """Starts the game mechanics"""
    log.info("Signaling shutdown of Hero Wars automation.")
    signal_shutdown()

    return True


def signal_shutdown(*args):
    stop_workers()
    log.info("signal_shutdown: {}".format(args))
    app.STOP_SIGNALED = status().set("game:stop")


if __name__ == "__main__":

    r = 0
    try:
        r = start()
    except Exception as e:
        log.error(f"Error: {e}")
        raise

    exit(int(r))
