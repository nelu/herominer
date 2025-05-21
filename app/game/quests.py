"""Handles completing daily and event quests with Redis storage"""
from app.driver import JSONConfig
from app.game.guild.sanctuary import summon_pets, summon_count
from app.game.lobby import airship
from app.game.player import player_stats
from app.utils.log import logger
from app.utils.session import daily
from app.game.lobby import back_to_lobby
from app.game.heroes.manager import instance

D = daily()

log = logger(__name__)


def config():
    return JSONConfig('quests.json')


def is_complete(name, stats_name=None):
    stats_name = stats_name or name
    return D.get_count(stats_name) >= config()[name]


def increase_any_hero_glyph():
    return True  # Hero.random().glyphs.upgrade_any_glyph('1', 1)


def increase_any_hero_artifact():
    heroes = instance.all_heroes()

    sorted_heroes = (heroes.where(lambda h: h.artifacts.has_upgrades(bellow=130, fresh=True))
                     .order_by(lambda h: h.artifacts.min_value('lvl')))

    for hero in sorted_heroes:
        log.debug(f"increase_any_hero_artifact: Trying - {hero._slug}")

        result = hero.open_hero() and hero.artifacts.upgrade_any()
        #back_to_lobby()
        if result:
            return result
        else:
            log.warning(f"increase_any_hero_artifact: Failed - {hero._slug}")

    return sorted_heroes


def increase_any_hero_skills():
    gold = player_stats.has_gold()
    if not gold:
        log.warning(f"increase_any_hero_skills: No gold available - {gold}")
        return gold

    skill_points = player_stats.get_skill_points()
    if skill_points is not None and not skill_points:
        log.warning(f"increase_any_hero_skills: No skill points available - {skill_points}")
        return skill_points

    heroes = instance.all_heroes()

    sorted_heroes = (heroes.where(lambda h: h.skills.has_skill_increase
                                            or h.skills.has_upgrades(bellow=130, fresh=True)
                                  )
                     .order_by(lambda h: h.skills.min_value('cost'))
                     )

    log.info(f"increase_any_hero_skills: Heroes available - {sorted_heroes.count()}")

    for hero in sorted_heroes:
        log.debug(f"increase_any_hero_skills: Trying - {hero._slug}")
        result = hero.open_hero() and hero.skills.upgrade_any()
        #back_to_lobby()
        if result:
            return result
        else:
            log.warning(f"increase_any_hero_skills: Failed - {hero._slug}")

    return sorted_heroes


def increase_any_hero_skins():
    coins = player_stats.has_skin_coins()
    if not coins:
        log.warning(f"increase_any_hero_skins: No skins points available - {coins}")
        return False

    sorted_heroes = (instance.all_heroes().where(lambda h: h.skins.has_coins() and h.skins.has_upgrades())
                     .order_by(lambda h: h.skins.min_value('lvl'))
                     )

    log.info(f"increase_any_hero_skins: Heroes available - {sorted_heroes.count()}")

    for hero in sorted_heroes:
        log.debug(f"increase_any_hero_skins: Trying - {hero._slug}")

        hero.set_search()
        result = hero.skins.upgrade_any()
        if result:
            return result
        else:
            log.warning(f"increase_any_hero_skins: Failed - {hero._slug}")

    return sorted_heroes


def increase_any_hero_xp():
    heroes = instance.all_heroes()
    sorted_heroes = (heroes.where(lambda h: h.level < 130)
                     .order_by(lambda h: h.xp or 0)
                     )

    log.info(f"increase_any_hero_xp: Heroes available - {sorted_heroes.count()}")

    for hero in sorted_heroes:
        log.debug(f"increase_any_hero_xp: Trying - {hero._slug}")
        result = hero.open_hero() and hero.upgrade_xp()
        # back_to_lobby()
        if result:
            return result
        else:
            log.warning(f"increase_any_hero_xp: Failed - {hero._slug}")


def complete_daily_quests():
    """Executes all required daily quests."""

    conf = config()

    if not is_complete("skill-upgrades"):
        # Upgrade skills 3 times per day
        log.info(
            f"run_daily_quests: ({D.get_count('skill-upgrades') + 1}/{conf['skill-upgrades']}) Upgrading any hero's skill")
        increase_any_hero_skills()

    if not is_complete("skin-upgrades"):
        # Upgrade 1 skin per day for daily quest
        log.info("run_daily_quests: Upgrading 1 hero skin")
        increase_any_hero_skins()

    if not is_complete("artifact-upgrades"):
        # Upgrade hero artifact if not done today
        log.info("run_daily_quests: Upgrading 1 hero artifact")
        increase_any_hero_artifact()

    if not is_complete("xp-upgrades"):
        # Upgrade hero artifact if not done today
        log.info("run_daily_quests: Upgrading 1 hero XP potion")
        increase_any_hero_xp()

    # if not summon_count():
    #     # Upgrade hero artifact if not done today
    #     summon_pets() and back_to_lobby()

    # Open one airship chest daily for hero artifacts
    airship.check_chest_opens()

    # Enchant a hero glyph
    # increase_any_hero_glyph()

    # Return to the main lobby
    back_to_lobby()
