"""Handles Campaign mode automation"""
from app.driver import player as driver, JSONConfig
from app.utils.log import logger
from app.utils.session import daily

log = logger(__name__)

DATA = daily()


def config():
    return JSONConfig('campaign.json')


def start_campaign_mission(mission_id):
    """Starts a campaign mission"""
    actions.perform_action(f"start-campaign-{mission_id}")
