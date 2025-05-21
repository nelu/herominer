from typing import Dict

from py_linq import Enumerable

from .hero.artifacts import Artifacts
from .hero.hero import Hero
from ..heroes.hero_data import HeroData
from app.game.lobby import back_to_lobby
from app.game import  play_action
from app.utils.log import logger
from app.utils.session import daily

log = logger(__name__)

DATA = daily()


class HeroManager:
    def __init__(self, prefix=None):
        self.heroes = None
        self.heroes: Dict[str, Hero] = {}

    def get_heroes(self):
        if self.heroes:
            return self.heroes

        self.heroes = self.all_heroes(available=True)

        return self.heroes

    def get_by_slugs(self, hero_slugs):
        return (self.all_heroes(available=False)
                .where(lambda h: h._slug in hero_slugs)
                )

    def all_heroes(self, available=True) -> Enumerable:
        hdata = HeroData()

        heroes = Enumerable(hdata.list_heroes()).select(lambda h: Hero.load(h))
        if available:
            heroes = heroes.where(lambda h: h.is_available())
            self.heroes = heroes

        return heroes

    def update_heroes_stats(self):
        heroes = self.get_heroes()

        # old_stats_heroes = heroes.where(lambda h: h.is_old())
        # if not old_stats_heroes:
        #     return False

        u = 0
        log.info(f"update_heroes_stats: for {heroes.count()} heroes")

        Artifacts.set_open_settings(True)
        for hero in heroes:
            log.debug(f"update_heroes_stats: updating {hero._slug}")
            hero.set_search(True)

            update_result = play_action('heroes/update-stats')

            if update_result:
                hero.update_stats()
                hero.skins.update_from_screen()
                hero.artifacts.update_from_screen()

            # retry failure
            if not update_result:
                log.error(
                    f"update_heroes_stats: cannot reopen heroes manager menu for {hero._slug} -> {update_result}")
                if not back_to_lobby():
                    # smth is very wrong with the driver
                    break


            log.debug(f"update_heroes_stats: stats for {hero._slug} -> {update_result}")
            hero.save()
            u += 1

        back_to_lobby()
        return u

    def run_management(self):
        # once a day
        DATA.is_complete("update_heroes_stats") or (
                self.update_heroes_stats() and DATA.mark_complete("update_heroes_stats")
        )

        # pick old heroes to update stats
        # self.update_heroes_stats()


instance = HeroManager()

def run_tasks():
    return instance.run_management()
