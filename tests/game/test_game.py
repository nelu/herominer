from tests import require_integration

require_integration()

import unittest

from hm.driver import player
from hm.game import game_stats, open_game
from hm.game.chat import announce_bonus_links
from hm.game.events import has_event
from hm.game.social import set_valid_bonus_links

from hm.game import config as game_config


class GameTestCase(unittest.TestCase):

    def test_get_game_stats(self):
        stats = game_stats.get_stats()
        print(f"Game stats: {stats}")
        player.stop()

    def test_chat(self):
        set_valid_bonus_links(["http://ungabunga.com", "http://google.com"])
        announce_bonus_links()

    def test_open_game(self):

        r = open_game()
        self.assertEqual(r, 1)  # add assertion here

    def test_heroes_stats(self):
        stats = game_stats.heroes_stats()
        print(f"Game heroes stats: {stats}")

        hero_stats = game_stats.heroes_stats(2)
        print(f"Game hero 2 stats: {hero_stats}")
        player.stop()

    def test_special_events(self):
        r = has_event(game_config().get('low_interval_special_events'))
        self.assertEqual(True, r )  # add assertion here


    def test_clipboard(self):
        player.to_clipboard("From driver test case")
        self.assertEqual(True, False)  # add assertion here

    def tearDown(self):
        pass
        #player.stop()

if __name__ == '__main__':
    unittest.main()
