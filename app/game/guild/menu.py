from ..lobby import Menus, back_to_lobby
from .. import open_game
from app.driver import player as driver

from app.settings import logger

log = logger(__name__)

class GuildMenus(Menus):
    def __init__(self):
        super().__init__("guild")

    @staticmethod
    def config():
        return Menus.config()['guild']

    @staticmethod
    def back_to_menu():
        return driver.start("guild/back-to-menu")

    def open_menu(self, name="default"):

        log.debug(f"open_menu: {name}")
        r = (open_game() and self.set_menu_search(name).start("guild/menu-open"))

        return r

    def process_menu(self, menu_name):
        log.debug(f"process_menu: {menu_name}")
        o = self.open_menu(menu_name) and driver.start(f"guild/menu-{menu_name}")
        back_to_lobby()
        return o
