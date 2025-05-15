from app.driver import player as driver
from app.game import play_action

from app.game.heroes.stats import StatusData
from app.utils.log import logger

log = logger(__name__)


class Items(StatusData):
    has_items_equip = None
    has_items_buy = None
    has_items_promote = None
    has_items_create = None

    def __init__(self, hero):
        super().__init__(default_data={f"{i}": {'equipped': False} for i in range(1, 7)})

        self.color_lvl = 0

        self._hero = hero
        self.update(hero._data.get('slots', {}))

    def acquire_items(self):
        self._hero.set_search()
        o = play_action("heroes/items/acquire")
        o or log.warning(f"acquire_items: {self._hero._slug}")
        return o

    def equip_item(self, item_name, item_stats):
        self.available[item_name] = item_stats

    def promote_items(self):
        self._hero.set_search()
        o = play_action("heroes/items/promote-items")
        o or log.warning(f"promote_items: {self._hero._slug}")
        return o

    def update_from_screen(self):
        return self.upgrade_target_flags([
            "has_items_create", "has_items_buy", "has_items_equip", "has_items_promote"
        ])

    def update_from_api(self, game_stats):
        self.color_lvl = game_stats.get('color', 0)
        slot_stats = game_stats['slots']

        for slot_id, value in self.available.items():
            game_id = int(slot_id) - 1
            value['equipped'] = not f"{game_id}" in slot_stats

    def upgrade_all(self, count=1):
        from app.game.player import player_stats
        slot_items = player_stats.has_energy() and self.acquire_items()
        promote = player_stats.has_gold() and self.promote_items()

        return slot_items and promote
