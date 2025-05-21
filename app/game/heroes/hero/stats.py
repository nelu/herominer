from app.game.heroes.stats import StatusData
from app.utils.session import status

# session data
SD = status('hero')


class Stats(StatusData):
    def __init__(self, hero, agility=1, strength=1, intelligence=1):
        super().__init__()

        self.agility = agility
        self.strength = strength
        self.intelligence = intelligence
        self.health = strength * 50
        self.physical_attack = agility * 4
        self.magic_attack = intelligence * 3
        self.armor = strength * 2
        self.magic_defense = intelligence * 2
        self.armor_penetration = agility * 1.5
        self.update(hero._data.get('stats', {}))

    def open(self):
        return True
