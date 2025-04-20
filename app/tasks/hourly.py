from .helper import set_last_run
from app.settings import logger

log = logger(__name__)

def run_all_tasks():
    """Runs daily tasks including prioritized hero upgrades"""
    log.info("Starting hourly tasks automation...")

    # rewards.collect_daily_rewards()
    # quests.complete_quests()
    # heroes.upgrade_heroes()  # Upgrading heroes based on priority

    # lobby.close_game()

    log.info("All hourly tasks completed!")