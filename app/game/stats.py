import time
from multiprocessing import Process, Queue, Event

import app
from app.driver import player
from app.settings import APP_GAME_URL
from app.utils.log import logger
from app.utils.data_model import DataModel
from app.utils.service import GracefulExit

log = logger(__name__)


def fetch_stats(timeout=100,  close_tab=False):
    browser = None
    try:
        browser = player.browser()  # start seleniumwire
        browser.get(APP_GAME_URL)

    except (KeyboardInterrupt, GracefulExit) as e:
        raise
    except Exception as e:
        log.exception(f'get_game_stats: Failed to start driver {e}')
        player.stop()
        return False

    start = time.time()
    while time.time() - start < timeout:
        if app.STOP_SIGNALED:
            raise GracefulExit()
        try:
            request = browser.wait_for_request(
                pat=r".*\/api\/$",
                timeout=timeout
            )
        except (KeyboardInterrupt, GracefulExit) as e:
            raise
        except Exception as e:
            log.exception('get_game_stats: wait_for_request failure')
            player.stop()
            continue

        matches = player.ajax_requests(url_pattern=r".*\/api\/$",
                                       body_pattern=r".*userGetInfo.*",
                                       content_type_filter=None)
        if matches.__len__():
            item = matches.pop()
            data = item.get('data') and item['data'].get('results')
            if data:
                return data
            else:
                log.error('get_game_stats: Failed to get game stats - result: ', item)
                # retry


    log.error('get_game_stats: Failed to get game stats')
    player.close_selenium()
    #close_tab and player.close_selenium()

    return False


def fetch_stats_wrap(queue: Queue, stop_event: Event, timeout=100, max_retries=5, close_tab=False):
    response = None
    for attempt in range(max_retries):
        if stop_event.is_set():
            log.info("fetch_stats_wrap: Stop event detected, shutting down gracefully...")
            break

        log.info(f"fetch_stats_wrap: Attempting to get stats (attempt {attempt + 1}/{max_retries})")
        response = fetch_stats(timeout=timeout, close_tab=close_tab)

        if response:
            break

    return response
    # if response:
    #     queue.put({"data": response})  # ✅ Send result to parent process
    #     # Wait for shutdown signal
    #     log.info("[fetch_stats_wrap] Waiting for stop_event...")
    #     stop_event.wait()  # ⏳ blocks here until parent sets it
    # else:
    #     queue.put({"error": "no-attempts", "success": False})

    #player.stop()


class GameStats:
    api_response: [dict] = None
    data: DataModel = None

    def __init__(self):
        self.data = DataModel("game_stats")

    def get_data(self, field=None):
        self.data.store.count() or self.update_stats()

        if not field:
            return self.data.all()
        return self.data.get_item(field)

    def get_stats(self, timeout=100, max_retries=5, close_tab=False):
        response = player.do_request(fetch_stats_wrap, timeout, max_retries, close_tab)

        if response:
            self.api_response = response['data']

        return self.api_response
        # return fetch_stats( timeout=100, max_retries=5, close_tab=False)

    def save_stats(self):
        """
        Saves all key-value pairs from api_response into the data store.
        """
        if not self.api_response:
            return False

        for item in self.api_response:
            self.data.store.set(item['ident'], item['result']['response'])

        return True

    def heroes_stats(self, hero_id=None):
        data = self.get_data("heroGetAll")
        return data and (hero_id is None and data or data.get(f"{hero_id}"))

    def reset_stats(self):
        self.api_response = None

    def update_stats(self):
        if self.api_response:
            return True

        return not self.api_response and (self.get_stats(close_tab=False)
                                          and self.save_stats()
                                          or log.error("update_stats: Failed to get game stats"))
