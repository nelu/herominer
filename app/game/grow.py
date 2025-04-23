from py_linq import Enumerable

from app.driver import JSONConfig
from app.game.heroes.manager import instance as hero_manager
from app.game.lobby.menu import back_to_lobby
from app.utils.log import logger
from app.utils import session

log = logger(__name__)


def config(element=None):
    conf = JSONConfig('grow.json')
    if element:
        return conf and conf.get(element)
    return conf


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

    artifacts = (Enumerable(grow_conf.get("artifacts", []))
                 .where(lambda a, h=hero: h.artifacts.upgrade_artifact(artifact_id=str(a), evolution=True))
                 .count())

    slots = grow_conf.get("items") and hero.slots.upgrade_all(grow_conf["items"])

    log.info(
        f"grow_hero: Done - {hero._slug} skills: {skills}, skins: {skins}, artifacts: {artifacts}, level: {level}, slots: {slots}")
    back_to_lobby()


def upgrade_rune(hero_name, rune_type, level_increase=1):
    """Upgrades a hero's rune"""
    current_rune_level = session.read_session(f"hero:{hero_name}:rune:{rune_type}") or 1
    new_rune_level = current_rune_level + level_increase
    session.write(f"hero:{hero_name}:rune:{rune_type}", new_rune_level)
    log.info(f"Upgraded {hero_name}'s {rune_type} rune to level {new_rune_level}.")


def upgrade_artifact(hero_name, artifact_name, level_increase=1):
    """Upgrades a hero's artifact"""
    current_artifact_level = session.read_session(f"hero:{hero_name}:artifact:{artifact_name}") or 1
    new_artifact_level = current_artifact_level + level_increase
    session.write(f"hero:{hero_name}:artifact:{artifact_name}", new_artifact_level)
    log.info(f"Upgraded {hero_name}'s {artifact_name} artifact to level {new_artifact_level}.")


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



def acquire_hero_items():
    # create or get hero items
    # just to have them on inventory for later upgrades
    heroes = hero_manager.all_heroes()
    sorted_heroes = (heroes.where(lambda h: h.slots.has_items_create and h.level and h.level > 40)
                     .order_by(lambda h: h.level)
                     )

    log.info(f"acquire_hero_items: Heroes available - {sorted_heroes.count()}")

    for hero in sorted_heroes:
        log.debug(f"acquire_hero_items: Trying - {hero._slug}")
        result = hero.open_hero() and hero.slots.acquire_items()
        back_to_lobby()
        if result:
            return result
        else:
            log.warning(f"acquire_hero_items: Failed - {hero._slug}")
