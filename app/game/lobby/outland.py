"""Handles Outland """

from app.utils.log import logger
from . import  process_menu

log = logger(__name__)


def fight_outland_boss():
    """Starts an Outland Boss fight"""
    pass


def check_free():
    log.debug("check_free: Outland points and battles")

    o = process_menu('outland')
    o or log.error(
        f"check_free: failed to claim daily bonus"
    )

    log.debug("check_free: Finished")


