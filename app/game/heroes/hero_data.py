from app.utils.data_model import DataModel


class HeroData(DataModel):
    def __init__(self):
        super().__init__(data_key="heroes", config_file="heroes.json")

    def get_hero(self, key): return self.get_item(key)
    def update_hero(self, key, updates): return self.update_item(key, updates)
    def add_hero(self, key, data): return self.add_item(key, data)
    def delete_hero(self, key): return self.delete_item(key)
    def list_heroes(self): return self.list_items()
    def get_random_hero(self): return self.random_item()

hero_data = HeroData()