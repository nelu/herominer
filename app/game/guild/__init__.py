from app.game.lobby import Menus, back_to_lobby
from app import game
from app.driver import JSONConfig, player as driver

from app.utils.log import logger
from app.utils.session import daily

log = logger(__name__)


def config():
    return JSONConfig('guild.json')


class GuildMenus(Menus):
    def __init__(self):
        super().__init__("guild")

    @staticmethod
    def config():
        return config()

    @staticmethod
    def back_to_menu():
        return driver.start("guild/back-to-menu")

    def open_menu(self, name="default"):
        log.debug(f"open_menu: {name}")
        r = (game.open_game() and self.set_menu_search(name).start("guild/menu-open"))

        return r

    def process_menu(self, menu_name):
        log.debug(f"process_menu: {menu_name}")
        o = self.open_menu(menu_name) and driver.start(f"guild/menu-{menu_name}")
        back_to_lobby()
        return o

    @staticmethod
    def is_disabled():
        return daily().exists("guild-disabled")


guild_menus = GuildMenus()


def play(file, go_back=False):
    return not guild_menus.is_disabled() and game.play_action(file, go_back)


def check_complete(item, complete_macro, auto=True, day=True):
    return not guild_menus.is_disabled() and game.check_complete(item, complete_macro, auto, day)


def if_daily_count(status_flag, action, count=1):
    return not guild_menus.is_disabled() and game.if_daily_count(status_flag, action, count)
