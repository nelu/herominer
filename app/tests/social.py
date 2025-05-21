import unittest

from app.driver import player
from app.game import game_stats, open_game
from app.game.social import check_bonus_links, open_latest_links

from app.tests import load_fixture
from app.utils.service import wait


class SocialTestCase(unittest.TestCase):

    def test_open_latest_links(self):
        open_latest_links()

    def test_check_social(self):
        r= check_bonus_links()



    def tearDown(self):
        player.stop()

if __name__ == '__main__':
    unittest.main()
