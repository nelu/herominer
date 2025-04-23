from app.driver import player as driver
from app.game import play_action
from app.utils.log import logger
from app.game.lobby import back_to_lobby, menus
from app.utils.session import status

log = logger(__name__)
DATA = status()

def check_season_events():
    o = None
    if menus.open_menu_notification('season-events'):
        log.info('check_season_events: found events')
        o = driver.play_action(f"season-events/check")
        back_to_lobby()

    return o


def check_special_events():
    o = play_action(f"events/check")
    back_to_lobby()
    return o
