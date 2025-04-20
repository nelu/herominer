"""Handles Titan battle automation with Redis tracking"""

import redis_helpers

def start_titan_battle():
    """Initiates a battle with Titans and logs it in Redis"""
    write_session("battle:titans:status", "started")
    print("Titan battle started.")

def get_titan_battle_status():
    """Retrieves the status of the Titan battle from Redis"""
    return read_session("battle:titans:status")
