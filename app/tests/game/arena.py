import unittest

from app.game.lobby.arena import check_complete


class MyTestCase(unittest.TestCase):

    def test_check_battles(self):
        check_complete(['arena'])


if __name__ == '__main__':
    unittest.main()
