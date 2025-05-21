from app.driver import player as driver, JSONConfig
from app.game import open_game, play_action, player
from app.game.heroes.manager import instance as hero_manager
from app.utils.log import logger
from app.tasks.helper import schedule_tasks

log = logger(__name__)


def get_shop_coins(shop_name):
    conf = shop_config(shop_name)
    coins_name = conf.get("coin")
    return player.DATA.get_count(f"{coins_name}")


def shop_config(shop_name=None):
    conf = JSONConfig('shop.json')
    if shop_name:
        return conf and conf['lobby_shop'].get(shop_name)

    return conf


def set_shopping_items(what=None, shop_name=None):
    d = {}
    shop_name and d.update({'shop-open.txt': f"{shop_name}"})
    what and d.update({'shop-buy-target.txt': "\n".join(what)})
    return d and driver.set_run_inputs(d)


def buy_item(shop_name, item):
    # r = open_shop(shop_name) and driver.start(f"shop/shop-buy")
    set_shopping_items([item], shop_name)
    return play_action("shop/buy-merchant", True)


def buy_heroes(shop_name, hero_slugs):
    r = None
    heroes = hero_manager.get_by_slugs(hero_slugs)
    # Buy first hero that hasn't max evolved in Arena
    for hero in heroes:
        if hero.evolution.is_evolution_possible():
            log.info(f"buy_heroes: Buying {hero._slug} souls from {shop_name} Shop.")
            r = buy_item(shop_name, hero.short_name)
            r or log.error(f'buy_heroes: {hero._slug} - failed to buy  {hero.short_name} from {shop_name} Shop.')
            break  # Stop after first purchase
        else:
            log.warning(f"buy_heroes: {hero._slug}  has max evolved")

    log.info(f"buy_heroes: Finished {shop_name} {r}")
    return r


def buy_items(shop_name, names=None):
    r = None
    if names is None:
        # items = shop_config()[shop_name].get("heroes", [])
        names = shop_config(shop_name).get("items", [])

    shop_coins = get_shop_coins(shop_name)

    if shop_coins < 500:
        log.warning(f"buy_items: No coins available {shop_name} - {shop_coins}")
        return False

    # for name in names:
    #     r = buy_item(shop_name, name)
    return shop_name == "town" and buy_town(names) or buy_heroes(shop_name, names)


def buy_town(names):
    log.info("Buy from town shop")
    # open_shop('town') and driver.start(action="shop/town-shop-buy-cash")
    return play_action("shop/town-shop-buy-cash", True)


def open_shop(shop):
    if open_game():
        log.info(f"Opening merchant shop: {shop}")
        # regex format
        set_shopping_items(None, shop)
        return driver.start("shop/open-shop")

    return False


def set_tasks(tasks=None):
    if not tasks:
        tasks = {}

    shops = shop_config()
    for task_name, conf in shops['lobby_shop'].items():
        conf["function"] = lambda shop_name=task_name: buy_items(shop_name)
        tasks[f"lobby_shop.buy_items-{task_name}"] = conf

    schedule_tasks(tasks)
    return schedule_tasks(shops['tasks'])
