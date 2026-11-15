"""Automates battle logic - Arena, Campaign, Grand Arena"""

from ..utils.session import read_session, write

def start_battle(battle_type):
    """Starts a battle of a given type and stores in Redis"""
    write(f"battle:{battle_type}:status", "started")
    print(f"Started {battle_type} battle.")

def get_battle_status(battle_type):
    """Retrieves the status of a battle from Redis"""
    return read_session(f"battle:{battle_type}:status")
