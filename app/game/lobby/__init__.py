from datetime import datetime

from .menu import Menus
from app.utils.log import logger
from app.driver import player as driver, JSONConfig
from app.utils import session

log = logger(__name__)

ON_LOBBY_SCREEN = 0


def config():
    return JSONConfig('main-lobby.json')


def run_if_notification(name, back=True):
    from .. import play_action
    o = menus.has_menu_notification(name) and play_action(f"lobby/menu-{name}", back)
    o or log.warning(
        f"run_if_notification: failed {name}"
    )
    return o


def process_menu(menu_name):
    log.debug(f"process_menu: {menu_name}")

    r = run_if_notification(menu_name)
    r and menus.screen_data.remove(menu_name)
    return r


def check_menus():
    """Runs the lobby menus at
     the appropriate time intervals."""
    i = 0
    for menu_name in config()['active_menus']:
        if process_menu(menu_name):
            i += 1

    return i


def is_on_main_screen():
    global ON_LOBBY_SCREEN
    from .. import GAME_IS_OPEN

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
