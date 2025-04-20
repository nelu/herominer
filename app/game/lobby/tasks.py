# the import order matters for the order in which the scheduled tasks are being ran for each module
from . import config
from .. import shop
from ...tasks.helper import schedule_from_config

schedule_from_config(config()['tasks'])
shop.set_tasks()

