"""Automates Tower mode"""
from app.driver import player as driver
from app.utils.log import logger
from app.utils.session import status, daily as daily_session
from . import menus
from .. import open_game

log = logger(__name__)


def open_airship():
    return menus.open_menu(name="airship")


# Open one airship chest daily for hero artifacts
def check_chest_opens():
    return get_opened_chests() <= 1 or open_chest()

def get_opened_chests(today=True):
    data = today and daily_session() or status()
    """Checks if an airship chest has been opened today."""
    return data.get_count("airship-open-chests")


def open_chest():
    """Runs airship open chests."""
    log.info("Opening airship chests")
    r = driver.start("lobby/airship/open-chests")

    # r and StatusData.increase_stats("airship-open-chests")

    # back_to_lobby()

    return r


def check_expeditions():
    """Checks airship expeditions"""
    log.info("check_expeditions")
    r = open_airship() and driver.start("lobby/airship/expeditions-check")

    return r

