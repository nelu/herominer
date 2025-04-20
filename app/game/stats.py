import time

import app
from app.driver import player
from app.settings import logger, APP_GAME_URL
from app.utils.data_model import DataModel
from app.utils.service import GracefulExit

log = logger(__name__)


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

    def get_stats(self, timeout=100, max_retries=5, close_browser=False):
        for attempt in range(max_retries):
            if app.STOP_SIGNALED:
                player.stop()
                raise GracefulExit()

            log.info(f"Attempting to get stats (attempt {attempt + 1}/{max_retries})")
            title = None
            try:
                browser = player.browser()  # start seleniumwire
                browser.get(APP_GAME_URL)
                title = browser.title
            except (KeyboardInterrupt, GracefulExit) as e:
                raise
            except Exception as e:
                title = None
                log.exception('get_game_stats: get game url failure')
                player.stop()

            if not title:
                continue

            start = time.time()
            while time.time() - start < timeout:
                if app.STOP_SIGNALED:
                    player.stop()
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
                    break

                matches = player.ajax_requests(url_pattern=r".*\/api\/$",
                                               body_pattern=r".*userGetInfo.*",
                                               content_type_filter=None)
                if matches.__len__():
                    item = matches.pop()
                    data = item.get('data') and item['data'].get('results')
                    if data:
                        self.api_response = data
                        return True
                    else:
                        log.error('get_game_stats: Failed to get game stats - result: ', item)

        log.error('get_game_stats: Failed to get game stats')
        close_browser and browser.quit()

        return False

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

        return not self.api_response and (self.get_stats(close_browser=False)
                                          and self.save_stats()
                                          or log.error("update_stats: Failed to get game stats"))
