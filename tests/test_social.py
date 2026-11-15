from tests import require_integration

require_integration()

import unittest

from hm.driver import player
from hm.game import game_stats, open_game
from hm.game.social import check_bonus_links, open_latest_links

from .helpers import load_fixture
from hm.utils.service import wait


class SocialTestCase(unittest.TestCase):

    def test_open_latest_links(self):
        open_latest_links()

    def test_check_social(self):
        r= check_bonus_links()



    def tearDown(self):
        player.stop()

if __name__ == '__main__':
    unittest.main()
