from app.driver import player as driver
from app.driver.config import write_coords
from app.game.heroes.stats import StatusData
from app.utils.log import logger
from . import play
from .sanctuary import set_run_config as sanctuary_run_config
from app.utils.session import status

from app.game import open_game
from app.game.chat import send_chat_msg
from app.game.lobby import back_to_lobby

log = logger(__name__)
d = status()


class Adventure:
    def __init__(self, adventure_id):
        self.adventure_id = adventure_id

    @staticmethod
    def get_route_config(adv_id):
        from .adventures import config
        return config()['level_routes'][f"{adv_id}"]

    def set_missions_config(self, start_position):
        write_coords(self.get_route_config(self.adventure_id), name="adventure-lvl-route")
        return driver.set_run_inputs({"adventure_lvl_position.txt": start_position})

    def play_missions(self, start_position):
        self.set_missions_config(start_position)
        return play(f"guild/adventures/mission-player")

    def started_adventure(self, position=1):
        # d.set("adventure_started_id", int(self.adventure_id))
        d.set("adventure_started_time")
        d.set("adventure_lvl_position", position)
        # return self

    @staticmethod
    def finish_adventure(adv_id):
        d.set("adventure_started_id", 0)
        d.set("adventure_started_time", 0)
        d.set("adventure_lvl_position", 0)
        log.info(f"finish_adventure: {adv_id}")

    @staticmethod
    def create_adventure(adv=None):
        """Start an adventure level from the main lobby screen"""
        log.info(f"start_adventure: {adv.adventure_id}")
        # driver.to_clipboard(update_stats and "update" or "")
        sanctuary_run_config(menu_name='adventures')
        r = play("guild/adventures/start-adventure")
        if r:
            log.info(f"start_adventure: {adv.adventure_id} started ")
            adv.increase_played("adventures_started")
            adv.started_adventure()
        else:
            log.error(f"start_adventure: {adv.adventure_id} Failed")

        return r

    @staticmethod
    def join_adventure(adv):
        log.info(f"join_adventure: {adv.adventure_id}")
        # driver.to_clipboard(update_stats and "update" or "")
        adv.set_run_config(adv.adventure_id)
        # send_chat_msg(f"Trying to join adventure {adv.adventure_id}")
        r = play("guild/adventures/join-adventure")
        if r:
            log.info(f"join_adventure: {adv.adventure_id} joined")
            adv.increase_played("adventures_joined")
            adv.started_adventure()
        else:
            log.error(f"join_adventure: {adv.adventure_id} failed ")
            # send_chat_msg(f"Failed to join adventure {adv.adventure_id}")

        return r

    @staticmethod
    def set_run_config(adv_id, levels=None):
        from .adventures import config
        lvl_cfg = config()['levels']
        if levels is None:
            levels = lvl_cfg.keys()

        regex_name = lvl_cfg[adv_id].split(" ")[0]

        return driver.set_run_inputs({
            'adventure-id.txt': adv_id,
            'adventure-name.txt': regex_name,
            # 'adventures-available.txt': "\n".join(levels)
        })

    @staticmethod
    def increase_played(field_name):
        StatusData.increase_stats(f"{field_name}")
        StatusData.increase_stats("adventures_played")
