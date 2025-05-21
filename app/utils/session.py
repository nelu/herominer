import json
import os
import time
from datetime import datetime
from pytimeparse import parse

import app.utils.redis_helpers as storage
from app import settings
from app.utils.log import logger
log = logger(__name__)


def has_session(what):
    return storage.redis_client.exists(what)


def has_valid_flag(name):
    value = read_session(name)

    return value and int(value) > 0


def remove_entry(name):
    return storage.delete_value(name)


def persist_path(name, directory=settings.APP_DATA_CACHE_DIR):
    return os.path.normpath(os.path.join(directory, name))


def persist(name, data, directory=settings.APP_DATA_CACHE_DIR):
    path = persist_path(name, directory)
    to_write = isinstance(data, str) and (data or "\n") or data
    with open(path, "w") as file:
        r = file.write(str(to_write))

    r or log.error(f"fail to write: {path}")
    return r


# $1 filename
# $2 reference variable
def read_session(name):
    return storage.get_value(name)


def read_session_mtime(name):
    return int(time.time() - storage.redis_client.ttl(name))


def remove_file(file, directory=settings.APP_DATA_CACHE_DIR):
    """Removes the file if it exists."""
    path = os.path.join(directory, file)

    return file and os.path.exists(path) and os.remove(path)  # Delete file


# $1 filename
# $2 data
def write(name, value, ttl=None):
    return storage.set_value(name, value, ttl)


class BaseSessionManager:
    """
    Manages daily session flags using Redis Hashes.
    Each day's session is stored under a unique key with a custom prefix.
    """

    def __init__(self, prefix, redis_client):
        """
        Initializes the session manager with a Redis connection and a session prefix.

        :param prefix: Required prefix for session keys (e.g., "game_session").
        :param redis_client: A Redis connection instance.
        """
        self.prefix = prefix
        self.redis = redis_client

    @classmethod
    def entry(cls, prefix, redis_client=storage.redis_client):
        """
        Factory method to create a session manager with a given prefix.

        :param prefix: Required prefix for session keys (e.g., "game_session").
        :param redis_client: Optional external Redis instance (overrides redis_config).
        :return: An instance of DailySessionManager.
        """

        return cls(prefix, redis_client)

    def count(self) -> int:
        """
        Returns the number of fields (flags) in the current session's Redis hash.

        :return: Integer count of flags set in the hash.
        """
        session_key = self._get_session_key()
        return self.redis.hlen(session_key)

    def _get_session_key(self):
        """
        Constructs the Redis key for today's session flags.

        :return: A formatted Redis key (e.g., "game_session:2025-02-11").
        """

        return f"{self.prefix}"

    def set(self, flag_name=None, value=None, mapping=None):
        """
        Sets a session flag inside a Redis hash with an optional custom value.

        :param flag_name: The unique flag name for the task.
        :param value: Optional value to store (default is the timestamp).
        """

        session_key = self._get_session_key()

        if mapping:
            return self.redis.hset(session_key, mapping=mapping)

        # Store either the provided value or just the timestamp
        flag_data = value if value is not None else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Set flag with custom value in Redis Hash
        return self.redis.hset(session_key, flag_name, json.dumps(flag_data))

    def is_complete(self, name):
        return self.exists(f"completed_{name}")

    def get_count(self, name):

        r = self.get(name)
        if r:
            if isinstance(r, str):
                if r.isdigit():
                    r = int(r)
                else:
                    r = 0
        else:
            r = 0

        return r

    def increment(self, flag_name, amount=1):
        """
          Increments a numeric flag value by a floating-point number inside the Redis hash.

          :param flag_name: The flag to increment.
          :param amount: The amount to increment by (default is 1.0).
          :return: The new incremented value.
          """
        session_key = self._get_session_key()
        current = self.redis.hget(session_key, flag_name)
        try:
            current = int(current)
        except (Exception):
            current = 0

        return self.set(flag_name, current + amount)

    def mark_complete(self, name):
        return self.set(f"completed_{name}")

    def get(self, flag_name):
        """
        Retrieves the stored value of a flag from today's session.

        :param flag_name: The flag to retrieve.
        :return: The stored value or None if not found.
        """
        session_key = self._get_session_key()
        value = self.redis.hget(session_key, flag_name)

        return json.loads(value) if value else None

    def exists(self, flag_name):
        """
        Checks if a specific flag exists in today's session.

        :param flag_name: The flag to check.
        :return: True if the flag exists, False otherwise.
        """
        session_key = self._get_session_key()
        return self.redis.hexists(session_key, flag_name)

    def wait_for_entry(self, name, timeout=1000):
        while not self.exists(name):
            time.sleep(0.1)

        return self.get(name)

    def get_all(self):
        """
        Retrieves all flags stored for today along with their values.

        :return: Dictionary of flags and their values.
        """
        session_key = self._get_session_key()
        flags = self.redis.hgetall(session_key)
        return {key: json.loads(value) for key, value in flags.items()}

    def remove(self, flag_name):
        """
        Removes a specific flag from today's session.

        :param flag_name: The flag to remove.
        """
        session_key = self._get_session_key()
        return self.redis.hdel(session_key, flag_name)

    def clear_all(self):
        """
        Clears all session flags for today.
        """
        session_key = self._get_session_key()
        return self.redis.delete(session_key)


class DailySessionManager(BaseSessionManager):
    """
    Session manager for daily tasks using Redis Hashes.
    """

    def set(self, flag_name, value=None, mapping=None):
        r = super().set(flag_name, value, mapping)
        session_key = self._get_session_key()

        # Ensure the hash expires in 48 hours
        self.redis.expire(session_key, parse("48 hours"))

        return r

    def _get_session_key(self):
        """
        Generates a Redis key specific to today's date.

        :return: A formatted Redis key (e.g., "game_session:2025-02-11").
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{self.prefix}:{today}"


def publish_event_old(event_type, data):
    message = {
        "event": event_type,
        "data": data
    }

    storage.redis_client.publish(event_type, json.dumps(message))


def has_event(event_type):
    message = storage.redis_client.pubsub().subscribe(event_type).get_message()
    if message["type"] == "message":
        try:
            payload = json.loads(message["data"])
            print(payload["event"], payload.get("data", {}))
        except Exception as e:
            print(f"Error processing event: {e}")
    return


def on_event(event_type, handler, timeout=None):
    """
    Subscribes to a Redis event and invokes the handler when that event is received.

    :param event_type: Redis channel/event name (e.g., "exit_status")
    :param handler: function to call when event is received (handler(data_dict))
    :param timeout: optional timeout in seconds
    :return: True if handled, False if timed out
    """
    pubsub = storage.redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(event_type)

    start_time = time.time()

    while True:
        message = pubsub.get_message()
        if message and message["type"] == "message":
            try:
                payload = json.loads(message["data"])
                event = payload.get("event")
                data = payload.get("data", {})

                if event == event_type:
                    handler(data)
                    pubsub.close()
                    return True
            except Exception as e:
                print(f"[on_event] Error processing message: {e}")

        if timeout is not None and (time.time() - start_time) > timeout:
            print(f"[on_event] Timeout waiting for '{event_type}'")
            pubsub.close()
            return False

        time.sleep(0.25)  # tighter than 1s polling, still lightweight


def status(entry="status"):
    return BaseSessionManager.entry(entry)


def daily(entry="status"):
    return DailySessionManager.entry(entry)
