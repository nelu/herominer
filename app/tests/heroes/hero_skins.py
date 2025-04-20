import unittest
from app.game.heroes.hero import Hero
from app.utils.session import status


class SkinsTestCase(unittest.TestCase):
    def test_skin_upgrade(self):
        hero = Hero.load('aidan')
        r = hero.skins.upgrade_any()
        self.assertEqual(r, True)

    def test_parse_skins_stats(self):
        hero = Hero.load('alvanor').skins.update_from_screen(status('hero').get('skins'))
        self.assertEqual((hero), True)  # add assertion here

    def test_check_skins_stats(self):
        hero = Hero.load('cornelius').skins.update_from_screen()
        self.assertEqual((hero), True)  # add assertion here



if __name__ == '__main__':
    unittest.main()
