from app.game import play_action, config as game_config
from app.utils.log import logger
from app.utils.session import status

log = logger(__name__)
DATA = status()


def has_event(ev_names, ev_type="special-events"):
    ongoing = DATA.get(f"{ev_type}")
    if ongoing:
        for ev_name in ev_names:
            if ev_name in ongoing:
                return True
    return False


def has_low_interval_special_events():
    return has_event(game_config().get('short_interval_special_events'))


def check_special_events():
    return play_action(f"events/check", True)
