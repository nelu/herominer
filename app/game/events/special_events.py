from app.driver import player as driver
from app.settings import logger
from app.utils.session import status, daily as daily_session
from app.game.lobby import back_to_lobby
log = logger(__name__)

DATA = status()
# Define session keys
ONGOING_SPECIAL_EVENTS_SESSION = "events-ongoing"


def check_for_special_events():
    """
    Clears the special events session file and checks if special events are ongoing.
    """
    remove_session_file(ONGOING_SPECIAL_EVENTS_SESSION)
    return play_action("events/has-events") == 0


def has_special_event_ongoing():
    """
    Checks if an ongoing special event exists.

    :return: True if an event is ongoing, False otherwise.
    """
    has_ongoing = read_session(ONGOING_SPECIAL_EVENTS_SESSION)
    return has_ongoing != "0"


def get_ongoing_special_event():
    """
    Retrieves the current ongoing special event type.

    :return: Event type as a string.
    """
    return read_session(ONGOING_SPECIAL_EVENTS_SESSION)


def has_lost_special_event_battle():
    """
    Checks if the user has lost a special event battle.

    :return: True if the user has lost a battle, False otherwise.
    """
    value = int(read_daily_session_file("events-has-lost-battle") or 0)
    return value > 0


def has_astral_season():
    """
    Checks if an astral season event is ongoing.

    :return: True if the astral season is ongoing, False otherwise.
    """
    value = int(read_daily_session_file("has-astral-season") or 0)
    return value > 0


def has_campaign_play_missions_for_arachne_soulstones():
    """
    Checks if there are campaign play missions for Arachne soulstones.

    :return: True if missions are available, False otherwise.
    """
    value = int(read_daily_session_file("has-event-arachne-campaign-missions") or 0)
    return value > 0




def run_special_events():
    """Executes special event actions if any are ongoing."""
    log("Special events: Checking for ongoing events")
    check_for_special_events()

    if has_special_event_ongoing():
        event_type = get_ongoing_special_event()
        log(f"Special events: {event_type} detected")

        # Handle known event types
        known_events = {"king-of-eternal-snow", "tristan-crusade", "spooky-halloween"}
        if event_type in known_events:
            play_action(f"events/{event_type}")
        else:
            log(f"Special events: Error - Unknown event type: {event_type}")

    # Handle Astral Season event
    if has_astral_season():
        log("Events check: Astral Season found ongoing")
        play_action("events/astral-season-claim")
        play_action("events/astral-season")

    # Handle Arachne Soulstones event
    if has_campaign_play_missions_for_arachne_soulstones():
        log("Events: Playing missions for Arachne Soulstones")
        played = 0

        while played < 1600:
            play_next_campaign_mission(1, 7)
            played = read_count_file("events-arachne-won-missions")

        back_to_lobby()