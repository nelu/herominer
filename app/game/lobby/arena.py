from app.driver import player as driver
from app.game import open_game
from app.utils.session import daily
from app.utils.log import logger
from app.game.lobby import back_to_lobby

log = logger(__name__)

DATA = daily()


def play_arena(arena_name):
    log.info(f"play_arena {arena_name} - checking for battles")
    # 120 secs x 3 battles
    o = open_game() and driver.play_action(f"lobby/arena/{arena_name}-play", timeout=400)

    back_to_lobby()
    return o

def check_complete(arenas):
    """Checks for arena battles if they haven't been completed today."""
    for arena_name in arenas:
        if not DATA.is_complete(arena_name):
            log.debug(f"check_battles: {arena_name} points and battles")
            a = play_arena(arena_name)
        else:
            log.debug(f"check_battles: {arena_name} daily free battles finished")
