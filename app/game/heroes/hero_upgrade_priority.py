"""Handles prioritized hero upgrades based on user-defined order"""
from app.utils.session import write, read_session

# Configurable priority list stored in Redis
HERO_UPGRADE_PRIORITY_KEY = "hero_upgrade_priority"

def set_hero_upgrade_priority(priority_list):
    """Stores hero upgrade priority list in Redis"""
    write(HERO_UPGRADE_PRIORITY_KEY, priority_list)

def get_hero_upgrade_priority():
    """Retrieves hero upgrade priority list from Redis"""
    return read_session(HERO_UPGRADE_PRIORITY_KEY) or []

def upgrade_heroes():
    """Upgrades heroes based on priority, using available resources"""
    priority_list = get_hero_upgrade_priority()

    for hero in priority_list:
        available_gold = read_session("player:gold") or 0
        available_runes = read_session(f"hero:{hero}:runes") or 0
        available_artifacts = read_session(f"hero:{hero}:artifacts") or 0

        if available_gold >= 5000:
            upgrades.upgrade_hero(hero, 1)
            write("player:gold", available_gold - 5000)

        if available_runes >= 2:
            upgrades.upgrade_rune(hero, "Strength", 1)
            write(f"hero:{hero}:runes", available_runes - 2)

        if available_artifacts >= 1:
            upgrades.upgrade_artifact(hero, "Flame Shield", 1)
            write(f"hero:{hero}:artifacts", available_artifacts - 1)

        print(f"Checked {hero} for upgrades. Resources spent accordingly.")
