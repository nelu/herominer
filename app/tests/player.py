import unittest

from app.game.player import player_stats


class MyTestCase(unittest.TestCase):

    def test_get_player_level(self):
        lvl = player_stats.get_player_level()
        self.assertIsNotNone(lvl)

    def test_get_skin_coins(self):

        all = player_stats.get_skin_coins()
        has_available = player_stats.has_skin_coins()
        self.assertIsNotNone(all)
        self.assertIsNotNone(has_available)

    def test_set_artifact_coins(self):
        lvl = player_stats.set_artifact_coins("upgrade")
        lvl = player_stats.set_artifact_coins(0)
        lvl = player_stats.set_artifact_coins(None)
        lvl = player_stats.set_artifact_coins("")
        lvl = player_stats.set_artifact_coins("100 0000 000 1")
        self.assertIsNotNone(lvl)

    def test_parse_data(self):
        for data in ["20/20", "20/2fdsfdsfdsfds", "20/", "2ddd22sfds", "           20"]:
            r = player_stats.parse_skill_points(data)
            self.assertIsNotNone(r)

        for data in ["", None]:
            r = player_stats.parse_skill_points(data)
            self.assertIsNone(r)


if __name__ == '__main__':
    unittest.main()
