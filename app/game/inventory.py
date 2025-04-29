"""Managing player inventory - gold, items, artifacts"""
from app.driver import player as driver, JSONConfig
from .heroes.stats import StatusData
from app.utils.log import logger
from .lobby import back_to_lobby
from . import open_game

log = logger(__name__)


def config():
    return JSONConfig('inventory.json')


class ItemsInventory(StatusData):

    def __init__(self):
        super().__init__(session_name="inventory")

    def get_count(self, item):
        return self.available.get(item, 0) and self.available[item].get('count', 0)

    def set_count(self, item, value):
        self.available[item]['count'] = value
        return self.save()

    def save(self):
        return self._screen_data.set('items', self.to_dict()) is not None

    def use_item(self, item_name, quantity):
        count = self.get_count(item_name)
        if count:
            count -= 1

        return self.set_count(item_name, count)


def check_inventory():
    log.info("check_inventory: for usable items")
    r = open_game() and driver.start("lobby/inventory-open-usable-items")
    back_to_lobby()
    return r


items = ItemsInventory()
