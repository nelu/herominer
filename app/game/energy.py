"""Manages energy spending"""

import redis_storage

def use_energy(amount):
    """Uses energy for battles"""
    current_energy = redis_storage.load_data("player:energy") or 0
    new_energy = max(0, current_energy - amount)
    redis_storage.save_data("player:energy", new_energy)
