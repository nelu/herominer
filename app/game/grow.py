from py_linq import Enumerable

from app.driver import player as driver
from app.driver import JSONConfig
from app.game import play_action
from app.game.heroes.manager import instance as hero_manager
from app.game.lobby import back_to_lobby, campaign
from app.game.player import player_stats
from app.utils.log import logger
from app.utils import session

log = logger(__name__)


def config(element=None):
    conf = JSONConfig('grow.json')
    if element:
        return conf and conf.get(element)
    return conf


def hero_soulstones(hero_slugs=None, no_lvl=False):
    """Play a hero's soulstones missions"""
    energy = player_stats.has_energy()
    if not energy:
        log.warning(f"hero_soulstones: No energy available {energy}")
        return False

    campaign_heroes = campaign.config()['heroes']

    heroes = (hero_slugs
              and hero_manager.get_by_slugs(hero_slugs).where(lambda h, ch=campaign_heroes: h._slug in ch)
              or hero_manager.get_by_slugs(campaign_heroes))

    filtered_heroes = heroes.where(lambda h: h.level and h.stars < 6)

    if not filtered_heroes and no_lvl:
        log.warning(f"hero_soulstones: all heroes maxxed up?!")
        filtered_heroes = hero_manager.get_by_slugs(campaign_heroes)

    sorted_heroes = filtered_heroes.order_by(lambda h: h.stars)

    if not sorted_heroes.count():
        log.warning("hero_soulstones: No heroes available")
        return False

    log.info(f"hero_soulstones: Heroes available - {sorted_heroes.count()}")

    driver.set_run_inputs({
        "soulstone-heroes.txt": "\n".join(sorted_heroes.select(lambda h: h.name.split()[0]).to_list())
    })

    return play_action("grow/soulstones", True)


def grow_hero(hero):
    if not hero.open_hero():
        return False

    grow_conf = config('heroes').get(hero._slug, {
        "skills": 1,
        "skins": 1,
        "artifacts": [2],
        "levels": 1,
        "items": 1,
        "do_evolution": False
    })

    skills = grow_conf.get("skills") and hero.skills.upgrade_any(grow_conf["skills"])
    skins = grow_conf.get("skins") and hero.skins.upgrade_any(grow_conf["skins"])
    level = hero.level < 130 and grow_conf.get("levels") and hero.upgrade_xp(grow_conf["levels"])

    artifact_upgrades = grow_conf.get("artifacts", [])
    artifacts = artifact_upgrades and upgrade_artifacts(hero, artifact_upgrades) or 0

    slots = grow_conf.get("items") and hero.slots.upgrade_all(grow_conf["items"])

    log.info(
        f"grow_hero: Done - {hero._slug} skills: {skills}, skins: {skins}, artifacts: {artifacts}, level: {level}, slots: {slots}")
    back_to_lobby()


def upgrade_artifacts(hero, artifact_upgrades):
    """Upgrades a hero's artifacts"""
    if not hero.artifacts.open():
        return False

    artifacts = (Enumerable(artifact_upgrades)
                 .where(lambda a, h=hero: h.artifacts.upgrade_artifact(artifact_id=str(a), evolution=True))
                 .count())
    return artifacts


def upgrade_pet(pet_name, level_increase=1):
    """Upgrades a pet by increasing its level"""
    current_pet_level = session.read_session(f"pet:{pet_name}:level") or 1
    new_pet_level = current_pet_level + level_increase
    session.write(f"pet:{pet_name}:level", new_pet_level)
    log.info(f"Upgraded pet {pet_name} to level {new_pet_level}.")


def run_tasks():
    """Runs tasks for a hero"""
    pass
    grow_heroes()
    # grow titans
    # grow pets


def grow_heroes(hero_slugs=None):
    # create or get hero items
    # just to have them on inventory for later upgrades
    hero_slugs = hero_slugs or config('heroes').keys()
    heroes = hero_manager.get_by_slugs(hero_slugs)
    sorted_heroes = (heroes.where(lambda h: h.slots.has_items_create and h.level and h.level > 40)
                     .order_by(lambda h: h.level)
                     )

    log.info(f"grow_heroes: Heroes available - {sorted_heroes.count()}")

    for hero in sorted_heroes:
        log.debug(f"grow_heroes: Trying - {hero._slug}")
        grow_hero(hero) or log.error(f"grow_heroes: Grow hero failed - {hero._slug}")


def acquire_hero_items(hero_slugs=None, energy_threshold=400):
    # create or get hero items
    # just to have them on inventory for later upgrades
    heroes = hero_slugs and hero_manager.get_by_slugs(hero_slugs) or hero_manager.all_heroes()
    sorted_heroes = (heroes
                     .where(lambda h: h.level and h.level > 40)
                     .order_by(lambda h: h.level)
                     )
    if not hero_slugs:
        sorted_heroes = sorted_heroes.where(lambda h: h.slots.has_items_create)

    log.info(f"acquire_hero_items: Heroes available - {sorted_heroes.count()}")

    for hero in sorted_heroes:
        energy = player_stats.has_energy()
        if energy:
            log.debug(f"acquire_hero_items: Trying - {hero._slug}")
            result = hero.open_hero() and hero.slots.has_items_create and hero.slots.acquire_items()
            back_to_lobby()
            result or log.warning(f"acquire_hero_items: Failed - {hero._slug}")
        else:
            log.warning(f"acquire_hero_items: Not enough energy - {energy} - {hero._slug}")
            break
