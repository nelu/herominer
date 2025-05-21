import unittest

from app.game.lobby.airship import run_tasks, open_chest, get_opened_chests


class MyTestCase(unittest.TestCase):

    def test_airship_run(self):
        run_tasks()

    def test_open_chest(self):
        get_opened_chests() or open_chest()

if __name__ == '__main__':
    unittest.main()
