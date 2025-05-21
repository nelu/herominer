from datetime import datetime
from pytimeparse import parse

import app.game
from .evolution import HeroEvolution
from .stats import Stats
from .skills import Skills
from .skins import Skins
from .slots import Items
from .glyphs import GlyphSystem
from .artifacts import Artifacts
from .ascension import Ascension
from ..hero_data import hero_data
from .. import config
from app.driver import player as driver
from app.utils.session import daily
from app.utils.log import logger
from app.game.lobby import menus
from ..stats import StatusData
from app.game import set_view

log = logger(__name__)

DATA = daily()


class Hero(StatusData):
    id = None
    status = None
    short_name = None
    name = None
    power = 0
    level = 0
    stars = 0
    souls = 0
    xp = 0
    last_update = 0
    slots = None
    stats = None
    skills = None
    skins = None
    glyphs = None
    artifacts = None
    ascension = None

    has_lvl_increase = None

    def __init__(self, name, data):
        super().__init__()
        self._data = data
        self._slug = name

        self.update(data)

        # available upgrades
        self.slots = Items(self)
        self.skills = Skills(self)
        self.skins = Skins(self)
        self.stats = Stats(self)
        self.glyphs = GlyphSystem(self)
        self.artifacts = Artifacts(self)
        self.ascension = Ascension(self)

        self.evolution = HeroEvolution(self)

        hero_game_stats = app.game.game_stats.heroes_stats(self.id)
        if hero_game_stats:
            self.update_from_api(hero_game_stats)
        else:
            self.status = 'not-available'

        self.save()

    # $1 - item ;  ex: rufus
    def has_max_evolve(self):
        return self.stars >= 6

    def has_max_level(self):
        return self.level >= 130

    @classmethod
    def load(cls, slug_name):
        data = hero_data.get_hero(slug_name)
        if not data:
            return None

        return cls(slug_name, data)

    def is_available(self):
        return self.status is None or self.status == "available"

    def is_old(self):
        now_ts = int(datetime.now().timestamp())
        return now_ts - self.last_update >= parse(config()['stats_timeout'])

    def is_open_error(self, log_msg=True):
        disabled = DATA.get("hero-err")
        match disabled:
            case "not-available":
                log_msg and log.error(f"open_hero: Failure -  {self.short_name} not yet available")
            case "not-found":
                log_msg and log.error(f"is_open_error: Failure - {self.short_name} not found on screen")
            case _:
                disabled = False

        return disabled

    def set_search(self, update_stats=True):
        DATA.set("hero-err", None)
        return driver.set_run_inputs({
            'heroes-search.txt': f"{self.name.split()[0]}",
            'heroes-open.txt': self.short_name,
            'heroes-open-update_stats.txt': update_stats and 1 or 0
        })

    def open_hero(self, open_menu=True):

        o = False
        file = "heroes/hero-open"

        if not self.is_available():
            return o

        o = open_menu and menus.open_menu("heroes") or True

        if o:
            log.info(f"open_hero: Opening - {self.short_name}")
            o = self.set_search().play_action(file)

            if o:
                (self.update_stats()
                 or log.error(f"open_hero: Failed to refresh stats {self.short_name}")
                 )
            else:
                self.status = self.is_open_error() and DATA.get("hero-err") or None

            self.save()

        o and set_view(f"{file}-{self._slug}")

        return o or self.is_open_error(False)

    @staticmethod
    def set_side_tab(tab_name):
        return driver.set_run_inputs({'hero-tab.txt': f"{tab_name}"})

    @staticmethod
    def open_side_tab(tab_name):
        file = "heroes/open-hero-tab"
        r = Hero.set_side_tab(tab_name).start(file)
        r and set_view(f"{file}-{tab_name}")
        return r

    def update_from_screen(self):
        r = False

        self.upgrade_target_flags([
            "has_lvl_increase"
        ])

        result = self.parse_data('stats', "Level:{lvl:d}{_}Stones:{stones:d}")
        if result:
            self.level = result['lvl']
            self.souls = result['stones']
            r = True

        stars = self._screen_data.get("hero_stars")
        if stars:
            self.stars = stars

        result = self.parse_data('power', "Power:{_}{power:d}")
        if result:
            self.power = result['power']
            r = True

        return r

    @staticmethod
    def random():
        return Hero.load(hero_data.get_random_hero())

    def regex_name(self):
        return f"(?i){self.short_name}"

    def save(self):
        return hero_data.update_hero(self._slug, self.to_dict())

    def update_stats(self):

        log.info(f"update_stats: Updating hero stats {self.short_name}")

        o = self.update_from_screen()
        self.skills.update_from_screen()
        self.slots.update_from_screen()
        self.evolution.update_from_screen()

        o or log.error(f"update_stats: Failed to refresh stats {self.short_name}")

        self.last_update = int(datetime.now().timestamp())

        return o

    def upgrade_xp(self, levels=1):
        o = 0

        for _ in range(levels):
            r = driver.play_action("heroes/hero-level-increase")

            if r:
                self.increase_stats("xp-upgrades")
                if self.xp is None:
                    self.xp = 0
                self.xp += 100
                if self.level is None:
                    self.level = 0
                self.level += 1
                self.skills.reset_skills_cost()
                self.save()

                o += 1
            else:
                log.error(f"upgrade_xp: Failed to upgrade hero {self.short_name} xp lvl ")

        return o

    def update_from_api(self, game_stats):
        self.update({
            'power': game_stats['power'],
            'stars': game_stats['star'],
            'level': game_stats['level'],
            'xp': game_stats['xp'],
            'status': 'available',
        })

        self.slots.update_from_api(game_stats)
        self.artifacts.update_from_api(game_stats)
        # self.skills.update_from_game_stats(game_stats)
