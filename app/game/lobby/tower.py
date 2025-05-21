"""Automates Tower mode"""
from app.driver import player as driver, JSONConfig
from .. import game_stats, open_game
from app.utils.session import daily
from app.utils.log import logger
from . import back_to_lobby, menus

log = logger(__name__)

DATA = daily()


def config():
    return JSONConfig('tower.json')

def set_level(level = None):

    if level is None:
        level = game_stats.get_data("towerGetInfo")
        level = level and level.get('floorNumber', 0)

    return DATA.set("tower-level", level)

def is_complete():
    return DATA.get_count("tower-level") >= 50 or DATA.is_complete("tower-battles")

def get_level():
    return game_stats.get_data("towerGetInfo")


def is_disabled():
    disabled = DATA.get("tower-disabled")
    match disabled:
        case "required":
            log.debug("run_tower: not available at current level. Skipping.")
        case "no-heroes":
            log.debug("run_tower: No heroes are available. Seems we lost all battles for today. Skipping.")
        case _:
            disabled = False

    return disabled


def collect_chests(count=1):
    r = []
    # Attempt to advance tower levels
    for i in range(1, count):
        log.info(f"play_battles: Attempting round {i}/{count}.")
        battle_result = driver.play_action("lobby/tower/play-battles")
        battle_result and DATA.increment("tower-level")
        r.append(battle_result)

        if is_complete() or is_disabled():
            log.debug("play_battles: Tower seems complete. Skipping next rounds.")
            break
    return r


def run_tower():
    """Executes the daily tower runs based on session conditions."""

    if is_disabled():
        log.warning("run_tower: Tower disabled. Skipping.")
        return False

    if (menus.open_menu_notification("tower")
            or (not is_complete() and menus.open_menu("tower"))):
        log.info("run_tower: Collecting points and checking battles.")
        set_level()
        log.debug("Tower: Collecting points")
        open_game() and driver.play_action(f"lobby/tower/collect-points")
        if not (is_disabled() or is_complete()):
            log.debug("Tower: Collecting chests")
            collect_chests(config()['battles_per_run'])
        back_to_lobby()
    else:
        log.debug("run_tower: No tower notifications available. Skipping.")
