from datetime import datetime

from py_linq import Enumerable

from app.driver import JSONConfig
from app.utils.log import logger
from app.utils.session import status, daily
from app.game.lobby import back_to_lobby
from app.game import open_game, game_stats, play_action
from .adventure import Adventure

log = logger(__name__)

DATA = status()


def config():
    return JSONConfig('adventures.json')


def game_status(adv_id=""):
    return {
        "Solo_getActiveData": game_stats.get_data("adventureSolo_getActiveData"),
        "levels": game_stats.get_data("adventure_getPassed"),
        "available": game_stats.get_data("adventure_find"),
        "active": game_stats.get_data("adventure_getActiveData"),
    }


def get_available_levels(playable=False):
    # what levels we defeated the boss
    game_data_levels = game_status()['levels']
    all_levels = config()['levels'].items()

    available = (Enumerable(all_levels)
                 .select(lambda lvl, gdata=game_data_levels: {
        'id': lvl[0],
        'wins': gdata.get(lvl[0], 0),
        'name': lvl[1],
    })
                 .where(lambda lvl: lvl['wins']))

    if playable:
        routed_levels = config()['level_routes'].keys()
        available = available.where(lambda lvl, level_routes=routed_levels: lvl['id'] in level_routes)

    return available


def get_started_adventure():
    """Get started adventure level."""
    lvl = DATA.get("adventure_started_id")
    return lvl and int(lvl) or 0


def has_started_adventure(today=False):
    started = get_started_adventure()
    if started and today:
        timestamp = DATA.get("adventure_started_time")
        if not timestamp:
            return False
        return datetime.fromtimestamp(timestamp).date() == datetime.now().date()

    return started


# manages playing adventures and basic functionality

class AdventureManager:
    def __init__(self):
        pass

    @staticmethod
    def get_preferred(entries, preferred_ids, asc=True):
        # Step 1: Add preferred levels first (with ID and name)
        seen = set()
        ordered = {}

        for lvl_id in preferred_ids:
            if lvl_id in entries and lvl_id not in seen:
                ordered[lvl_id] = entries[lvl_id]
                seen.add(lvl_id)

        # Step 2: Add the rest, sorted by level ID
        for lvl_id in sorted(entries.keys(), key=lambda x: int(x)):
            if lvl_id not in seen:
                ordered[lvl_id] = entries[lvl_id]
                seen.add(lvl_id)

        return ordered

    @staticmethod
    def current_adventure():
        started_id = has_started_adventure()
        if not started_id:
            return started_id

        return Adventure(started_id)

    @staticmethod
    def check_complete(adv):
        current = manager.current_adventure()
        return current and not adv.adventure_id == current.adventure_id

    @staticmethod
    def has_chests_to_claim():
        return game_status()['active']['hasRewards']

    def join_or_start_adventure(self, default_adv_id="1", create_adventure=False):
        conf = config()
        pref = conf.get('join-preferred', [default_adv_id])

        levels_with_routes = get_available_levels(True)

        log.info(f"run_adventures: Join/starting daily preferred adventures: {pref}")

        started = (self.preferred_first(pref, available_levels=levels_with_routes, call=Adventure.join_adventure)
                   or
                   (create_adventure and self.preferred_first(conf.get('start-preferred', pref),
                                                              available_levels=levels_with_routes,
                                                              call=Adventure.create_adventure)
                    )
                   )

        return started

    @staticmethod
    def get_started_adventure_position():
        return status().get("adventure_lvl_position")

    @staticmethod
    def open_chests():
        """Check for complete adventure prizes."""
        adv = manager.current_adventure()
        log.info(f"open_chests: adventure {adv} - checking for prizes")

        run = play_action("guild/adventures/chests-check")

        if not adv:
            log.warning(f"open_chests: No adventure started - {adv}")
            if run:
                new_id = has_started_adventure()
                not new_id and Adventure.finish_adventure(0)
        else:
            manager.check_complete(adv) and adv.finish_adventure(adv.adventure_id)

        (run or log.warning(
            f"open_chests: adventure {adv} - failed to collect chests or finish"))

        return run

    @staticmethod
    def play_level(adventure):
        """Play adventure level missions."""
        start_position = manager.get_started_adventure_position()

        if start_position:
            return adventure.play_missions(start_position)
        else:
            log.warning(f"play_level: No start position saved - {start_position}")
            return False

    @staticmethod
    def preferred_first(pref, call, available_levels=None):
        available_levels = available_levels or get_available_levels()
        sorted_by_preferences = manager.get_preferred(available_levels.to_dictionary(lambda lvl: lvl['id']), pref)

        for adv_id in sorted_by_preferences.keys():
            started_adv = call(Adventure(adv_id))
            if started_adv:
                return started_adv

        return None


manager = AdventureManager()


def run_adventures(create_adventure=False):
    # make sure game is open to have updated api data
    open_game()

    if not get_available_levels().count():
        log.error("run_adventures: seems no adventure level is available")
        return False

    # dont start any adventure if chest are to be claimed - active adventure not finished
    r = manager.has_chests_to_claim() and manager.open_chests()

    r = (not has_started_adventure() and not daily().get_count("adventures_played")
         and manager.join_or_start_adventure(create_adventure=create_adventure))

    r = manager.play_level(manager.current_adventure())

    back_to_lobby()
    return r
