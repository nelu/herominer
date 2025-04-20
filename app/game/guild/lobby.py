from app.driver import player as driver
from app.settings import logger
from app.game import social
from app.utils import session

log = logger(__name__)
DUNGEON_DAILY_LEVELS_PLAY = 23



def has_tournament_raid_disabled():
    """
    Checks if the tournament of elements raid is disabled.
    """
    if int(get_current_hour()) <= 3:
        return True
    return has_daily_session_flag("has-titan-tournament-raid-disabled")

def has_guild_island_activities():
    """
    Checks if there are guild island activities available.
    """
    if not has_open_summon_sphere_today():
        log("Guild Island: Needs to open titan summon sphere")
        return True

    if not has_run_titans_evolve():
        log("Guild Island: Needs to check titans for evolution")
        return True

    if not has_run_titans_artifact_increase():
        log("Guild Island: Needs to increase titan artifacts")
        return True

    if not has_finished_daily_dungeon_levels():
        log("Guild Island: Needs to finish daily dungeon levels")
        return True

    return False

def has_sanctuary_activities():
    """
    Checks if there are sanctuary activities available.
    """
    if has_sanctuary():
        if not has_ran_today("pet-open-free"):
            log("Sanctuary: Needs to open pet egg")
            return True

    return False

def has_titan_valley_activities():
    """
    Checks if there are Titan Valley activities available.
    """
    if has_titan_valley():
        if not has_open_artifact_sphere_today():
            log("Titan Valley: Needs to open titan artifact sphere")
            return True

        if not has_tournament_raid_disabled():
            log("Titan Valley: Has available tournament of elements raid")
            return True

    return False

def has_guild_activities():
    """
    Checks if there are any guild activities available.
    """
    if has_guild_disabled():
        log("Guild: Flagged as disabled")
        return False

    if has_titan_valley_activities():
        log("Guild: Needs to check Titan Valley activities")
        return True

    if has_guild_island_activities():
        log("Guild: Needs to check Guild Island activities")
        return True

    if has_sanctuary_activities():
        log("Guild: Needs to check Sanctuary activities")
        return True

    if has_guild_war_battles():
        log("Guild: Needs to fight in Guild Wars")
        return True

    return False

def has_guild_war_battles():
    """
    Checks if there are guild war battles available.
    """
    local_hour_utc = int(get_current_hour_utc())

    # Guild Wars are active between 15 and 23 UTC
    if not (15 < local_hour_utc < 23):
        return False

    left_to_play = 2 - read_daily_count("guild-wars-battles-played")

    if left_to_play > 0:
        log(f"Guild War: {left_to_play} battles left")
        return True

    return False

def has_sanctuary():
    return has_daily_session_flag("has-adventures-menu")

def has_titan_valley():
    return has_daily_session_flag("has-titan-valley")

def has_lost_dungeon_mission():
    return has_daily_session_flag("has-lost-dungeon-mission")

def collect_dungeon_divination_cards():
    log("Dungeon: Collecting divination cards")
    play_action("guild/dungeon-collect-divination-cards")

def has_finished_daily_dungeon_levels():
    return has_daily_session_flag("has-finished-dungeon-levels")

def get_daily_played_dungeon_levels():
    return read_daily_count("titans-dungeon-played-levels")

def play_daily_dungeon_levels():
    """
    Plays the daily dungeon levels.
    """
    daily_levels = DUNGEON_DAILY_LEVELS_PLAY
    current_level = read_count_file("titans-dungeon-won-levels")

    write_daily_session_file("has-lost-dungeon-mission", 0)
    played_missions = current_level

    for _ in range(1):
        log(f"Dungeon: Playing level {played_missions}/{daily_levels} - {current_level}")
        play_action("guild/dungeon-play-missions")

        level_increment = read_count_file("titans-dungeon-won-levels")
        played_missions = level_increment - current_level

        if has_lost_dungeon_mission():
            log(f"Dungeon: Mission lost at {played_missions}/{daily_levels} - {current_level}")
            break

        if played_missions > 0:
            increment_daily_count("titans-dungeon-played-levels")

        if get_daily_played_dungeon_levels() >= daily_levels:
            log(f"Dungeon: Finished all {daily_levels} levels")
            write_daily_session_file("has-finished-dungeon-levels", 1)
            break

    log(f"Dungeon: Done playing {get_daily_played_dungeon_levels()}/{daily_levels} levels")
    return played_missions > 0

def guild_run():
    """Executes the daily guild run."""
    from datetime import datetime

    current_hour = datetime.now().hour

    if current_hour >= 23:
        return

    log("Daily: Starting Guild run")

    if not has_guild_activities():
        log("Guild: No activities available. Skipping.")
        return

    if guild_open():
        run_script("titans-run")

        if has_sanctuary_activities():
            if guild_open("sanctuary"):
                log("Guild: Opening one pet egg")
                play_action("guild/sanctuary-open-pet")

                log("Guild: Buying items from sanctuary merchant")
                play_action("guild/sanctuary-buy-items")
                back_to_lobby()

        if has_guild_war_battles():
            if guild_open("guild-war"):
                log("Guild: Fighting in Guild Wars")
                play_action("guild/guild-war")
                back_to_lobby()

        guild_close()
    else:
        log("Guild: Failed to open guild lobby")

if __name__ == "__main__":
    guild_run()

