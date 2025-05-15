"""Player profile, levels, energy, and hero management"""
from app.game import game_stats
from app.game.heroes.stats import StatusData
from app.utils.log import logger
from app.utils.session import status
from parse import search

DATA = status("player")

log = logger(__name__)


class PlayerStats(StatusData):
    skin_colors = ["red", "pink", "blue"]

    @staticmethod
    def set_artifact_coins(coins):
        """Stores the player's artifact coins in Redis"""

        if coins is None:
            coins = 0

        elif isinstance(coins, str):
            # Strip spaces and remove all non-digit characters (e.g., commas, letters)
            cleaned = ''.join(filter(str.isdigit, coins))

            if not cleaned:
                log.warning(f"🟡 Invalid coin string: {coins!r}")
                coins = 0
            else:
                coins = int(cleaned)

        elif not isinstance(coins, int):
            log.warning(f"🟡 Unexpected coin type: {type(coins)} → {coins!r}")
            coins = 0

        return DATA.set('artifact_coins', coins)

    @staticmethod
    def get_artifact_coins():
        return DATA.get('artifact_coins')

    def parse_skill_points(self, skill_points):
        if skill_points is None:
            return skill_points

        result = search("{count:d}", skill_points)
        return result and self.set_skill_points(result['count'])

    @staticmethod
    def set_skill_points(points):
        """Stores the player's level in Redis"""
        return DATA.set('skill_points', points)

    @staticmethod
    def get_skill_points():
        value = DATA.get_count('skill_points')
        return value is not None and DATA.get_count('skill_points') or value

    @staticmethod
    def get_data():
        return game_stats.get_data("userGetInfo") or {}

    def get_player_level(self):
        local = DATA.get('player_level') or 0
        level = int(self.get_data().get('level', 0))

        if level > local:
            DATA.set('player_level', level)
            local = level

        return local

    @staticmethod
    def set_energy(level):
        """Stores the player's energy in Redis"""
        result = search("{count:d}", level)
        return DATA.set('energy', result and int(result['count']) or 0)

    @staticmethod
    def get_energy():
        """Retrieves the player's energy from Redis"""
        return DATA.get_count('energy')

    def has_energy(self, energy_threshold=200):
        energy = self.get_energy()
        return energy > energy_threshold and energy

    @staticmethod
    def has_gold(threshold=5000000):
        gold = DATA.get_count('gold')
        return gold > threshold and gold

    @staticmethod
    def get_skin_coins(skin_type=None):
        types = PlayerStats.skin_colors
        count = 0
        for t in types:
            count += DATA.get_count(f"skin_coins_{t}")
            if skin_type == t:
                break

        return count

    def has_skin_coins(self, skin_type=None, threshold=5000):
        c = self.get_skin_coins(skin_type)
        return c > threshold and c


player_stats = PlayerStats()
