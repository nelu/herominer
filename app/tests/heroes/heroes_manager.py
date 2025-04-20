import unittest
from app.game.heroes.manager import instance
from app.game.heroes.hero import Hero
from app.utils.session import status


class HeroManagerTestCase(unittest.TestCase):
    def test_upgrade_heroes_stats(self):
        r= instance.update_heroes_stats()
        self.assertEqual(r, True)

    def test_parse_skins_stats(self):
        hero = Hero.load('alvanor').skins.update_from_screen(status('hero').get('skins'))
        self.assertEqual((hero), True)  # add assertion here

    def test_check_skins_stats(self):
        hero = Hero.load('celeste').skins.update_from_screen()
        self.assertEqual((hero), True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
