"""Player profile, levels, energy, and hero management"""
from app.game import game_stats
from app.game.heroes.stats import StatusData
from app.settings import logger
from app.utils.session import status
from parse import search

DATA = status("player")

log = logger(__name__)


class PlayerStats(StatusData):

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

    def set_player_energy(self, level):
        """Stores the player's energy in Redis"""
        return DATA.set('player_energy', level)

    def get_player_energy(self):
        """Retrieves the player's energy from Redis"""
        return DATA.get('player_energy')


player_stats = PlayerStats()
