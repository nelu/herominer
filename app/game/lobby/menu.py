from app.driver import player as driver
from app.utils.log import logger
from app.utils.session import daily as daily_session, status
from .. import open_game, play_action

log = logger(__name__)


def daily():
    return daily_session("menu")


class Menus:
    def __init__(self, set_name="menu"):
        self.screen_data = status(set_name)

    def has_menu_notification(self, name):
        value = self.screen_data.get(name)
        return bool(value)

    @staticmethod
    def back_to_lobby():
        from app.game.lobby import back_to_lobby
        return back_to_lobby()

    @staticmethod
    def config():
        from . import config
        return config()

    def open_menu_notification(self, name):
        """Returns True if lobby menu checks are needed."""
        log.info(f"open_menu_notification: {name} - checking notification")

        return self.has_menu_notification(name) and self.open_menu(name)

    def process_menu(self, menu_name):
        """Checks and processes a menu if it has a notification."""
        # coords = self.has_menu_notification(menu_name)
        # if coords:
        #     o = self.open_menu(menu_name, coords) and driver.start(f"lobby/menu-{menu_name}")
        #     back_to_lobby()
        #     return o
        log.debug(f"process_menu: {menu_name}")
        r = False

        o = self.open_menu(menu_name) and play_action(f"lobby/menu-{menu_name}", True)
        return o

        # if session.persist('menu-check.txt', f"{menu_name}"):
        #     if open_game():
        #         r = driver.start(f"lobby/menu-notification-run")
        #         back_to_lobby()
        #         r or log.info(f"process_menu: {menu_name} menu has no notification")

    def open_menu(self, name):
        log.debug(f"open_menu: {name}")
        r = (open_game() and self.set_menu_search(name).start("lobby/menu-open"))

        return r

    @staticmethod
    def set_menu_search(name="default"):
        return driver.set_run_inputs({'menu-check.txt': f"{name}"})

    def open_menu_click(self, name, coords=None):
        from app.game import set_view
        if not coords:
            coords = self.config()['coords'].get(name, None)

        log.debug(f"open_menu_click: {name} @ {coords}")

        if open_game():
            r = driver.click(coords)

            r and set_view(f"open_menu-{name}")
            r or self.back_to_lobby()  # something is wrong
            return r

        return False
