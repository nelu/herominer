from .stats import GameStats
from ..driver import player as driver, JSONConfig
from app.utils.log import logger
from ..utils import session

log = logger(__name__)
GAME_IS_OPEN = False
current_view = None


def config():
    return JSONConfig('game.json')


def set_view(name):
    global current_view
    current_view = name


def back_views(count=1):
    return driver.to_clipboard(count).start(action="go-back")

def game_is_opened():
    global GAME_IS_OPEN
    game_running = GAME_IS_OPEN and driver.browser().title and "Hero" in driver.browser().title
    return game_running

def open_game():
    global GAME_IS_OPEN
    from .lobby import is_on_main_screen, back_to_lobby
    """Open the game in the browser."""

    if game_is_opened() and is_on_main_screen():
        return True
    elif not game_is_opened():
        # anomaly checks
        if GAME_IS_OPEN:
            log.error(f"not game_is_opened: Game found in invalid state {GAME_IS_OPEN} - GAME_IS_OPEN")
            close_game()

        GAME_IS_OPEN = (game_stats.update_stats()
                        and driver.start(action="0_open-browser-game-lobby")
                        and back_to_lobby())

        GAME_IS_OPEN or log.error('open_game: failed to open game lobby')
    else:
        log.debug('open_game: already open')

    return GAME_IS_OPEN


def close_game():
    global GAME_IS_OPEN
    from . import lobby
    lobby.ON_LOBBY_SCREEN = 0
    GAME_IS_OPEN = False
    close_result = driver.close_selenium()
    game_stats.reset_stats()
    return close_result


game_stats = GameStats()


# nice for task scheduling
def play_action(file):
    return open_game() and driver.start(file)


def check_complete(item, complete_macro, daily=True):
    """Checks for arena battles if they haven't been completed today."""
    if not (daily and session.daily() or session.status()).is_complete(item):
        log.debug(f"check_complete: {item} completing with {complete_macro}")
        return play_action(complete_macro)
    else:
        log.debug(f"check_complete: {item} already completed")
