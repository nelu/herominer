"""Handles Titan battle automation with Redis tracking"""
from app.game.heroes.hero import Hero
from app.utils.data_model import DataModel

titan_data = DataModel('titans', 'titans.json')

class Titan(Hero):

    def __init__(self, slug, data):
        super().__init__(slug, data)

    @classmethod
    def load(cls, slug_name):
        data = titan_data.get_item(slug_name)
        if not data:
            return None

        return cls(slug_name, data)


