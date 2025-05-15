from app.game import open_game, play_action
from app.game.lobby import back_to_lobby
from app.utils.log import logger
from app.driver import player as driver, JSONConfig
from app.game.heroes.stats import StatusData
from app.utils.session import daily, status

log = logger(__name__)


def config():
    return JSONConfig('sanctuary.json')


def set_run_config(menu_name=""):
    return driver.set_run_inputs({'pet-sanctuary_open.txt': menu_name and menu_name or "exit"})


def sanctuary_open(menu_name=None):
    log.debug(f"sanctuary_open: {menu_name}")
    # driver.to_clipboard(update_stats and "update" or "")

    r = open_game() and set_run_config(menu_name).play_action("guild/sanctuary/open")
    if not r:
        # back_to_lobby()
        log.error(f"sanctuary_open: Failed {menu_name}")

    return r


def summon_count(today=True):
    return (today and daily() or status()).get_count("sanctuary-open-eggs")

def summon_pets():
    return play_action("guild/sanctuary/open-pet-eggs")


def buy_from_merchant():
#    return play_action("guild/sanctuary/open-pet-eggs")

    r = sanctuary_open("merchant")
    if r:
        StatusData.increase_stats("pet_merchant_buys")

    return r


def has_activities():
    return daily().get_count("pet_merchant_buys") < 1 or not summon_count()


def run_sanctuary():
    if has_activities():
        sanctuary_open()
        daily().get_count("pet_merchant_buys") < 1 and buy_from_merchant()  # 1 per day
        #not summon_count() and summon_pets()  # 1 per day
        back_to_lobby()
