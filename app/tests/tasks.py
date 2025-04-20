import unittest

from app.game import game_stats
from app.game.tasks import schedule_game_tasks
from app.tasks.helper import schedule_from_config
from app.tasks.scheduler import check_idle


class TasksTestCase(unittest.TestCase):
    def test_check_idle(self):
        #schedule_game_tasks()
        schedule_from_config({__name__: {
            "function": lambda : print(f"from scheduled task"),
            "interval": "24 hours"
        }
        })
        check_idle()
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
