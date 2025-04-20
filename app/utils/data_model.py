import random
from app.driver import JSONConfig
from app.utils.session import status


class DataModel:
    def __init__(self, data_key: str, config_file: str = None):
        """
        Base data model with optional JSON config fallback.
        :param data_key: Key used for in-memory/session storage.
        :param config_file: Optional JSON config file for fallback.
        """
        self.store = status(data_key)
        self.data_key = data_key
        self.config = JSONConfig(config_file) if config_file else None

    def get_item(self, key: str):
        """
        Retrieve an item by key.
        """
        item = self.store.get(key)
        if item is not None:
            return item
        if self.config:
            return self.config.get(self.data_key, {}).get(key)
        return None

    def update_item(self, key: str, updates: dict) -> bool:
        """
        Update an item by key.
        """
        item = self.get_item(key)
        if item:
            item.update(updates)
            self.store.set(key, item)
            return True
        return False

    def add_item(self, key: str, data: dict) -> bool:
        """
        Add a new item by key.
        """
        return not self.store.exists(key) and self.store.set(key, data)

    def delete_item(self, key: str):
        """
        Delete an item by key.
        """
        item = self.store.get(key)
        if item:
            self.store.delete(key)
            return item
        return None

    def all(self):
        return self.store.get_all()

    def list_items(self):
        """
        List all item keys.
        """
        if self.config:
            return self.config.get(self.data_key, {}).keys()
        return self.all().keys()


    def random_item(self):
        """
        Get a random item key.
        """
        items = list(self.list_items())
        return random.choice(items) if items else None
