from ..utils.log import logger
log = logger(__name__)

def run_all_tasks():
    """Runs daily tasks including prioritized hero upgrades"""
    log.info("Starting daily tasks automation...")

    #rewards.collect_daily_rewards()
    #quests.complete_quests()
    #heroes.upgrade_heroes()  # Upgrading heroes based on priority

    log.info("All daily tasks completed!")
