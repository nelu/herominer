from parse import search

from app import settings
from app.utils import session

import json
import os
import redis

from app.utils.log import logger

log = logger(__name__)


class JSONConfig(dict):
    """A dictionary-like class to handle reading and writing configuration files with Redis fallback."""

    def __init__(self, file_name):
        super().__init__()
        self.file_path = os.path.join(settings.APP_ACTIONS_CONFIG_DIR, file_name)
        self.store = session.status("config_data")
        self.redis_key = os.path.basename(file_name)  # Use file name as Redis key
        self._load_config()

    def _load_config(self):
        """Load the configuration data from Redis first, then fallback to the filesystem if not found."""
        try:
            config_data = self.store.get(self.redis_key)
            if config_data:
                self.update(config_data)
                return
        except (redis.RedisError, json.JSONDecodeError) as e:
            log.error(f"Warning: Failed to retrieve config from Redis. Reason: {e}")

        # If Redis retrieval fails, try loading from file
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    if self.file_path.endswith(".json"):
                        self.update(json.load(file))  # Load JSON data
                        r = self.store.set(self.redis_key, self)
                    else:
                        self._load_text_file(file)  # Load non-JSON format
            except json.JSONDecodeError:
                print(f"Warning: {self.file_path} contains invalid JSON. Loading empty config.")
        else:
            log.info(f"File not found: {self.file_path}")
            # self.save()  # Create the file if it doesn't exist

    def _load_text_file(self, file):
        """Load configuration from a non-JSON file (store as raw text)."""
        self["content"] = file.read()  # Store entire content as a string

    def save(self, write_file=True):
        """Save the current config state to both the file and Redis."""
        write_file and self.save_as(self.file_path)
        r = False
        try:
            r = self.store.set(self.redis_key, self)
        except redis.RedisError as e:
            log.error(f"Warning: Failed to save config to Redis. Reason: {e}")

        return r

    def save_as(self, new_file_path):
        r = False
        """Save the current config state to a separate file."""
        with open(new_file_path, "w", encoding="utf-8") as file:
            if new_file_path.endswith(".json"):
                r = json.dump(self, file, indent=4)
            else:
                r = file.write(self.get("content", ""))
        return r

    # Dictionary-like behavior
    def __getitem__(self, key):
        return super().get(key, None)  # Default to None if the key doesn't exist

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save()  # Auto-save changes

    def __delitem__(self, key):
        if key in self:
            super().__delitem__(key)
            self.save()  # Auto-save after deletion

    def reset(self):
        """Reset the configuration file to an empty JSON object in both Redis and filesystem."""
        self.clear()
        self.save()


def parse_coords(value):
    return isinstance(value, str) and search("{x:d}x{y:d}", value) or {}


def write_coords(coords, name="coords"):
    x_list = []
    y_list = []

    if isinstance(coords, str):
        coords = [coords]

    for xy in coords:
        coords = parse_coords(xy)  # Convert directly to integers
        if not coords:
            log.error(f"Invalid format: {xy}. Expected format 'NxM' (e.g., '222x111').")
            return False

        x_list.append(str(coords['x']))
        y_list.append(str(coords['y']))

    session.persist(f"{name}.x", "\n".join(x_list))
    session.persist(f"{name}.y", "\n".join(y_list))

    return True
