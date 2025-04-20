"""Helper functions for interacting with Redis backend"""

import redis
import json

from app import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def set_value(key, value, expire=None):
    """Stores a value in Redis with an optional expiration time"""
    r = redis_client.set(key, json.dumps(value))
    if expire:
        redis_client.expire(key, expire)
    return r

def get_value(key):
    """Retrieves a value from Redis"""
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_value(key):
    """Deletes a key from Redis"""
    return redis_client.delete(key)

def increment_value(key, amount=1):
    """Increments a numerical value in Redis"""
    current_value = get_value(key) or 0
    return set_value(key, current_value + amount)

def decrement_value(key, amount=1):
    """Decrements a numerical value in Redis"""
    current_value = get_value(key) or 0
    return set_value(key, max(0, current_value - amount))

def list_push(key, value):
    """Pushes a value onto a Redis list"""
    return redis_client.rpush(key, json.dumps(value))

def list_pop(key):
    """Pops the last value from a Redis list"""
    data = redis_client.lpop(key)
    return json.loads(data) if data else None

def list_get_all(key):
    """Retrieves all items from a Redis list"""
    return [json.loads(item) for item in redis_client.lrange(key, 0, -1)]
