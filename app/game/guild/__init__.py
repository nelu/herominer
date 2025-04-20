from .menu import GuildMenus
from ...driver import JSONConfig

guild_menus = GuildMenus()

def config():
    return JSONConfig('guild.json')

def is_disabled():
    return has_daily_session_flag("has-guild-disabled")


def guild_open(target=None):
    """
    Opens the guild menu or a specific section.
    """
    if target:
        write_session("guild-menu-not-found", "0")
        action = f"open-{target}"
    else:
        action = "waitclose"

    log(f"Guild: Trying to switch to guild lobby {action}")
    play_action("guild/guild-open")

    if has_guild_disabled():
        log("Guild: Cannot open guild. Seems disabled.")
        return False

    if target and has_daily_session_flag("guild-menu-not-found"):
        log(f"Guild: Cannot open guild menu - {target}")
        return False

    return True

def guild_close():
    """
    Closes the guild menu and returns to the lobby.
    """
    log("Guild: Switching lobby to city heroes")
    play_action("guild/guild-close")