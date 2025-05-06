import unittest

import schedule

from app.game import game_stats
from app.game.tasks import schedule_game_tasks
from app.tasks.helper import schedule_from_config, execute_task, schedule_task
from app.tasks.scheduler import check_idle


class TasksTestCase(unittest.TestCase):
    def test_execute_tasks(self):
        schedule_task("test_execute_tasks",
                      {
                          "interval": "1 second",
                          "once": True,
                          "function": "game.guild.sanctuary.adventures.manager.join_or_start_adventure",
                          "args": ["8"]
                      })
        schedule.run_all()

        self.assertEqual(True, False)

    def test_check_idle(self):
        # schedule_game_tasks()
        schedule_from_config({__name__: {
            "function": lambda: print(f"from scheduled task"),
            "interval": "24 hours"
        }
        })
        check_idle()
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
