import unittest
from app.game.heroes.hero import Hero

class ArtifactsTestCase(unittest.TestCase):

    def test_open_artifacts(self):
        # data =  load_fixture("skills.json")
        hero = Hero.load('markus')

        o = hero.open_hero() and hero.artifacts.open()
        self.assertEqual(o, True)  # add assertion here

    def test_stats_update(self):
        hero = Hero.load('cornelius')
        r = hero.artifacts.check_stats()
        self.assertEqual(r, True)

    def test_random_upgrade(self):
        hero = Hero.load('astrid-and-lucas')
        r = hero.artifacts.get_random_artifact()

        r = hero.artifacts.upgrade_any()
        self.assertEqual(r, True)
