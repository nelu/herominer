from datetime import datetime

from parse import search

from app.driver import player as driver
from app.game.heroes.stats import StatusData
from app.game.player import player_stats, PlayerStats
from app.utils.log import logger

log = logger(__name__)


class Skins(StatusData):
    def __init__(self, hero):
        super().__init__(default_data={'1': {'cost': None, 'lvl': 1, 'name': 'Default Skin'}})
        self._hero = hero
        self.skin_color = None
        self.update(hero._data.get('skins', {}))

    def unlock_skin(self, skin_name):
        self.available[skin_name] = {'cost': None, 'lvl': 1, 'name': skin_name}

    def open(self):
        return (  # self._hero.open_side_tab('skins') and
            self.check_stats())

    def check_stats(self):
        o = driver.play_action("heroes/skins/check-stats")

        if o and self.update_from_screen():
            self._hero.save()

        return o

    def has_coins(self):
        return player_stats.has_skin_coins(self.skin_color)

    def get_random_skin(self):
        cheapest = self.get_upgradable_items('lvl')
        # return random.choice(sorted_by_cost)
        return cheapest and list(cheapest).pop(0)

    def upgrade_any(self, levels=1):
        item = self.get_random_skin()
        if not item:
            log.warning(f"upgrade_any: no skins available for upgrade: {self._hero._slug} -> {self.available}")
            return False

        return self.has_coins() and self.upgrade_skin(item, levels)

    def upgrade_skin(self, skin_id, levels=1):
        # o = self.open() and player_stats.has_skin_coins()
        #
        # if not o:
        #     return o

        o = 0
        for _ in range(levels):

            # regex_name = driver.get_regex_pattern(self.available[skin_id]['name'].split(" ")[0])
            regex_name = self.available[skin_id]['name'].split(" ")[0]

            log.debug("find_skin: looking for skin regex: {}".format(regex_name))

            if not driver.to_clipboard(regex_name).play_action("heroes/hero-skin-upgrade"):
                break

            self.update_from_screen()
            self.increase_stats("skin-upgrades")

            if self.available[skin_id].get('lvl') is None:
                self.available[skin_id]['lvl'] = 0
            self.available[skin_id]['lvl'] += 1
            o += 1

        o and self._hero.save()

        return o

    def update_from_screen(self, value=None):

        if not self.skin_color:
            for color in player_stats.skin_colors:
                if self.parse_data(f'skins_coins_{color}', "{xpos:d}"):
                    self.skin_color = color
                    break

        value = value or self._screen_data.get('skins')

        if not value:
            return value

        parts = value.split('name ')

        i = 0
        for part in parts:
            if part == "":
                continue

            result = (search("{name}\n{_}Level:{lvl:d}{}Upgrad{}{cost:d}", part) or
                      search("{name}\n{_}Level:{lvl:d}", part) or
                      search("{name}\n{_}obtained", part) or
                      search("{name}\n{_}from{locked:d}", part)
                      )

            if result:
                i += 1
                data = {
                    'name': self.clean_string(result.named.get('name')),
                    'lvl': result.named.get('lvl'),
                    'cost': result.named.get('cost'),
                    'locked': not result.named.get('lvl') or (result.named.get('locked', False) and True),
                }

                if self.available.get(f"{i}"):
                    self.available[f"{i}"].update(data)
                else:
                    self.available[f"{i}"] = data

        if i:
            self.last_update = int(datetime.now().timestamp())

        return i
