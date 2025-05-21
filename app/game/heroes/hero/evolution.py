from app.driver import player as driver
from app.game.heroes.stats import StatusData


class HeroEvolution(StatusData):
    has_evolve = None

    def __init__(self, hero):
        super().__init__()
        self._hero = hero

    def has_max_evolve(self):
        return self._hero.stars >= 6

    def do_evolve(self):
        r = driver.play_action("heroes/hero-level-increase")
        return r

    def is_evolution_possible(self):
        if self._hero.has_max_evolve():
            return False

        # too many pilled up and no upgrades
        if self._hero.souls >= 300 and self.has_evolve:
            return False

        return True

    def update_from_screen(self):
        return self.upgrade_target_flags([
            "has_evolve"
        ])