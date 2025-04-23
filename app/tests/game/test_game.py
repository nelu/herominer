import unittest

from app.driver import player
from app.game import game_stats, open_game

from app.tests import load_fixture
from app.utils.service import wait


class GameTestCase(unittest.TestCase):

    def test_get_game_stats(self):
        stats = game_stats.get_stats()
        print(f"Game stats: {stats}")
        player.browser.quit()

    def test_open_game(self):

        r = open_game()
        self.assertEqual(r, 1)  # add assertion here

    def test_heroes_stats(self):
        stats = game_stats.heroes_stats()
        print(f"Game heroes stats: {stats}")

        hero_stats = game_stats.heroes_stats(2)
        print(f"Game hero 2 stats: {hero_stats}")
        player.browser.quit()

    def test_pool_game_stats(self):
        for _ in range(100000):
            game_stats.get_stats(close_tab=False)
            wait(60)
            player.stop()
            wait(5)

    def test_clipboard(self):
        player.to_clipboard("From driver test case")
        self.assertEqual(True, False)  # add assertion here

    def tearDown(self):
        player.stop()

if __name__ == '__main__':
    unittest.main()
