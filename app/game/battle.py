"""Automates battle logic - Arena, Campaign, Grand Arena"""

import redis_helpers

def start_battle(battle_type):
    """Starts a battle of a given type and stores in Redis"""
    write_session(f"battle:{battle_type}:status", "started")
    print(f"Started {battle_type} battle.")

def get_battle_status(battle_type):
    """Retrieves the status of a battle from Redis"""
    return read_session(f"battle:{battle_type}:status")
