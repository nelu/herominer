from datetime import datetime

from .. import GAME_IS_OPEN
from .menu import Menus
from app.utils.log import logger
from app.driver import player as driver, JSONConfig
from app.utils import session

log = logger(__name__)

ON_LOBBY_SCREEN = 0


def config():
    return JSONConfig('main-lobby.json')


def check_menus():
    """Runs the lobby menus at
     the appropriate time intervals."""
    for menu_name in config()['active_menus']:
        (menus.has_menu_notification(menu_name)
         and menus.process_menu(menu_name)
         and menus.screen_data.remove(menu_name))


def is_on_main_screen():
    global ON_LOBBY_SCREEN

    if not GAME_IS_OPEN:
        return GAME_IS_OPEN

    # cache the value for 5 mins
    expired = (datetime.now().timestamp() - int(ON_LOBBY_SCREEN)) > 300

    return not expired


def back_to_lobby():
    """Navigate back to the game lobby."""
    global ON_LOBBY_SCREEN
    from .. import set_view

    session.remove_entry("is_on_main_screen")
    r = driver.play_action(action="lobby/back-to-lobby", timeout=60)

    ON_LOBBY_SCREEN = r and datetime.now().timestamp() or 0

    r and set_view(f"lobby")
    r or log.error("back_to_lobby: failed to return to main lobby screen")

    return ON_LOBBY_SCREEN


menus = Menus()
