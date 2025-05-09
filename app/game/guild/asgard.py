"""Handles Tournament of Elements battles"""
from app.game import open_game


def run_tasks(join_start=False):
    # game_stats.update_stats()
    # make sure game is open
    open_game()