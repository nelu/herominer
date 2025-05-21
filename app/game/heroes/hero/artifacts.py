from datetime import datetime

from app.driver import player as driver
from app.game.player import player_stats
from app.game.heroes.stats import StatusData
from app.utils.log import logger

log = logger(__name__)


class Artifacts(StatusData):
    def __init__(self, hero):
        super().__init__(default_data={f"{i}":
            {
                'cost': None,
                'has_lvl_upgrade': False,
                'has_evolution': False,
                'lvl': 1,
                'stars': 0,
                'name': ''
            }
            for i in range(1, 4)
        })

        self._hero = hero
        self.update(hero._data.get('artifacts', {}))

    def awake_artifact(self, skin_name):
        self.available[skin_name] = {'cost': None, 'lvl': 1, 'name': skin_name}

    def has_max_evolve(self, artifact):
        return self.available[f"{artifact}"]['stars'] >= 6

    def has_max_level(self, artifact):
        return self.available[f"{artifact}"]['lvl'] >= 130

    @staticmethod
    def set_open_settings(update_stats, artifact_id=None, upgrade_lvl=None, evolution=None):
        entries = {
            'artifact_update.txt': update_stats and "update" or "",
            'artifact_upgrade_evolution.txt': evolution and 1 or "",
            'artifact_upgrade_level.txt': upgrade_lvl and "1" or "",
            'artifact_upgrade_id.txt': artifact_id or ""
        }
        return driver.set_run_inputs(entries)

    def open(self, update_stats=True, evolution=False):
        o = self._hero.open_side_tab('artifacts')
        if not update_stats:
            update_stats = self.is_old()

        if o:
            # driver.to_clipboard(update_stats and "update" or "")
            r = (self.set_open_settings(update_stats=True)
                 .play_action("heroes/artifacts-open"))

            r and update_stats and self.check_stats()

            return r

        return o

    @staticmethod
    def is_upgradable(item, bellow=None, fresh=False):
        awaken = item["stars"] > 0
        return awaken and StatusData.is_upgradable(item, bellow)

    def check_stats(self):
        if self.update_from_screen():
            return self._hero.save()

        return False

    def get_random_artifact(self):
        cheapest = self.get_upgradable_items('lvl', bellow=130, fresh=False)
        return cheapest and list(cheapest).pop(0)
        # return random.choice(sorted_by_cost)

    def update_from_screen(self):

        player_stats.set_artifact_coins(self._screen_data.get(f"player-artifact-coins"))
        i = 0
        for key, item in self.available.items():
            i += 1
            item.update({
                'name': self.clean_string(self._screen_data.get(f"artifact_{key}_name")) or "",
                'has_evolution': self._screen_data.get(f"artifact_{key}_has_evolution"),
                'has_lvl_upgrade': self._screen_data.get(f"artifact_{key}_has_lvl_upgrade"),
            })
        if i:
            self.last_update = int(datetime.now().timestamp())
        return i

    def upgrade_any(self, evolution=False):
        item = self.get_random_artifact()

        if not item:
            log.warning(
                f"upgrade_any: {self._hero.short_name} no artifacts available for upgrade: -> {self.available}")
            return item

        return self.open() and self.upgrade_artifact(item, evolution=evolution)

    def upgrade_artifact(self, artifact_id, levels=1, evolution=False):

        self.set_open_settings(update_stats=True, artifact_id=artifact_id, evolution=evolution, upgrade_lvl=1)

        o = 0
        for _ in range(levels):
            r = driver.play_action("heroes/artifacts-open")
            if r:
                o += 1
                self.increase_stats("artifact-upgrades")
                if self.available[artifact_id].get('lvl') is None:
                    self.available[artifact_id]['lvl'] = 0

                self.available[artifact_id]['lvl'] += 1
                self._hero.save()
            else:
                break

        return o

    def update_from_api(self, game_stats):
        stats = game_stats['artifacts']

        for _id, entry in enumerate(stats, start=1):
            self.available[f"{_id}"].update({
                'lvl': entry['level'],
                'stars': entry['star'],
            })
