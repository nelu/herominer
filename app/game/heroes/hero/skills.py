from datetime import datetime

from parse import search
from py_linq import Enumerable

from app.game.player import player_stats as player_stats
from app.utils.log import logger
from app.driver import player as driver
from app.game.heroes.stats import StatusData
from app.utils.session import status, daily

log = logger(__name__)


def get_skills_upgrade(today=True):
    data = today and daily() or status()
    return data.get_count("skill-upgrades")


class Skills(StatusData):
    has_skill_increase = None

    def __init__(self, hero):
        super().__init__(default_data={f"{i}": {'cost': None, 'lvl': None, 'name': ''} for i in range(1, 5)})
        self._hero = hero
        self.update(hero._data.get('skills', {}))

    @staticmethod
    def is_upgradable(item, bellow=None, fresh=False):
        is_fresh = fresh and (item["cost"] is None and item["lvl"] is None)
        valid_cost = item["cost"] is not None and 0 < item["cost"]

        return (bellow
                and (valid_cost and 0 < item["lvl"] < bellow or is_fresh)
                or (valid_cost or is_fresh)
                )

    def get_random_skill(self):
        cheapest = self.get_upgradable_items('cost', bellow=None, fresh=False)
        return cheapest and list(cheapest).pop(0)
        # return random.choice(sorted_by_cost)

    def open(self):
        return self._hero.open_side_tab('skills')

    def update_from_screen(self):
        self.upgrade_target_flags(['has_skill_increase'])
        player_stats.parse_skill_points(self._screen_data.get("player_skill_points"))
        return self.parse_skills_stats()

    def parse_skills_stats(self):
        value = self._screen_data.get('skills')

        if not value:
            return False

        skills = (Enumerable(value.split('|'))
                  .select(lambda s: self.clean_string(s))
                  .select(lambda s: (
                search("{name} Level{junk}{lvl:d}@{cost:d}", s) or
                search("{name} Level{junk}{lvl:d}{morejunk}@{cost:d}", s) or
               search("{name} Level{junk}{lvl:d}@", s) or
               search("{}@{cost:d}", s) or
                search("{name}@", s)
        ))
                  .where(lambda s: s is not None)
                  .select(lambda m: {
            'name': m.named.get('name'),
            'lvl': m.named.get('lvl') or 0,
            'cost': m.named.get('cost') or 0
        }))

        i = 0
        for skill_info in skills:
            i += 1
            if not self.available.get(f"{i}"):
                self.available[f"{i}"] = {}
            self.available[f"{i}"].update(skill_info)

        if i:
            self.last_update = int(datetime.now().timestamp())

        return i

    def reset_skills_cost(self):
        for skill in self.available.values():
            skill["cost"] = None

        self._hero.save()

    def upgrade_any(self, levels=1):
        item = self.get_random_skill()

        if not item:
            log.warning(
                f"upgrade_any: {self._hero.short_name} no skills available for upgrade: -> {self.available}")
            return item

        return player_stats.has_gold() and self.upgrade_skill(item)

    def upgrade_skill(self, skill_no, levels=1):
        # o = self.open()
        # if not o:
        #     return o

        # self._hero.set_side_tab('skills')

        o = 0
        for _ in range(levels):
            r = driver.to_clipboard(skill_no).play_action("heroes/skills-increase")

            if r:
                o += 1
                self.increase_stats("skill-upgrades")
                if self.available[skill_no].get('lvl') is None:
                    self.available[skill_no]['lvl'] = 0

                self.available[skill_no]['lvl'] += 1
                self._hero.save()
            else:
                break

        return o

    # def update_from_game_stats(self, game_stats):
    #     skills_stats = game_stats['skills']
    #
    #     for slot_id, value in enumerate(skills_stats.values(), start=1):
    #         self.available[f"{slot_id}"]['lvl'] = value
