"""Handles collecting daily and event rewards with Redis tracking"""

from app.utils.session import write, read_session


def collect_daily_rewards():
    """Simulates collecting daily login rewards and stores in Redis"""
    write("rewards:daily", "collected")
    print("Daily rewards collected.")

def check_daily_rewards():
    """Checks if daily rewards have been collected from Redis"""
    return read_session("rewards:daily")
