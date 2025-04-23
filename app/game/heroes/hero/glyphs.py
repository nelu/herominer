from app.utils.log import logger
from app.game.heroes.stats import StatusData
from app.driver import player as driver
log = logger(__name__)


class GlyphSystem(StatusData):
    glyph_upgrades = None
    def __init__(self, hero):
        super().__init__()
        self._hero = hero
        self.gift_of_elements = GiftOfElements()

    def upgrade_any(self, stat, level):
        log.info("Daily: Enchanting 1 next hero glyphs")
        # set to 1 glyph open
        r = driver.play_action("heroes/hero-glyph-enchant-1")
        if r:
            self.increase_stats("glyph_upgrades")
            if self.glyph_upgrades is None:
                self.glyph_upgrades = 0
            self.glyph_upgrades += 1

            self._hero.save()

        self.available[stat] = level


class GiftOfElements(StatusData):
    def __init__(self):
        super().__init__()
        self.elements = {}

    def upgrade_element(self, element, power):
        self.elements[element] = power

    def to_dict(self):
        return self.elements
