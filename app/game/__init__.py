from .stats import GameStats
from app.driver import player as driver, JSONConfig
from app.utils.log import logger
from app.utils import session

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


def game_is_open():
    global GAME_IS_OPEN
    # game_running = GAME_IS_OPEN and driver.browser().title and "Hero" in driver.browser().title
    return GAME_IS_OPEN and driver.check_process_and_window()


def open_game():
    global GAME_IS_OPEN
    from .lobby import is_on_main_screen, back_to_lobby
    """Open the game in the browser."""

    if game_is_open() and is_on_main_screen():
        return True
    elif not game_is_open():
        # anomaly checks
        if GAME_IS_OPEN:
            log.error(f"not game_is_opened: Game found in invalid state {GAME_IS_OPEN} - GAME_IS_OPEN")
            close_game()

        GAME_IS_OPEN = bool(game_stats.update_stats()
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
    close_result = driver.stop()
    game_stats.reset_stats()


# nice for task scheduling
def play_action(file, go_back=False):
    from .lobby import back_to_lobby

    r = open_game() and driver.start(file)
    go_back and back_to_lobby()
    return r


def if_daily_count(status_flag, action, count=1):
    return session.daily().get_count(status_flag) < count and play_action(action, False)


def if_daily_action(status_flag, action):
    return not session.daily().get(status_flag) and play_action(action, False)


def check_complete(item, complete_macro, auto = True, daily=True):
    r = False
    sess = (daily and session.daily() or session.status())
    """Checks for arena battles if they haven't been completed today."""
    if not sess.is_complete(item):
        r = play_action(complete_macro, False)
        log.debug(f"check_complete: {item} completing with {complete_macro} - result: {r}")
        auto and r and sess.mark_complete(item) # mark complete automatically if success
    else:
        r = True
        log.debug(f"check_complete: {item} already completed")
    return r

game_stats = GameStats()
