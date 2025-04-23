from app.utils import session
from app.utils.log import logger

log = logger(__name__)

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


def upgrade_titan(titan_name, level_increase=1):
    """Upgrades a Titan by increasing its level"""
    current_titan_level = session.read_session(f"titan:{titan_name}:level") or 1
    new_titan_level = current_titan_level + level_increase
    session.write(f"titan:{titan_name}:level", new_titan_level)
    print(f"Upgraded Titan {titan_name} to level {new_titan_level}.")
