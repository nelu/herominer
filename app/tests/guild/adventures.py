import unittest

from app.game.guild.adventures import run_adventures, Adventure, manager, get_available_levels


class MyTestCase(unittest.TestCase):

    def test_adventure(self):

        adv = Adventure(11)
        self.assertEqual(adv.adventure_id, 11)  # add assertion here

    def test_get_available_levels(self):
        available_all = get_available_levels()

        with_routes = get_available_levels(True)

        self.assertEqual(available_all, 11)  # add assertion here

    def test_run_adventures(self):
        r = run_adventures()
        self.assertEqual(True, True)  # add assertion here

    def test_join_or_start_adventure(self):
        r = manager.join_or_start_adventure()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
