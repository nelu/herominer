import unittest

from app.game.quests import increase_any_hero_skills, complete_daily_quests, increase_any_hero_skins, \
    increase_any_hero_artifact, increase_any_hero_xp


class MyTestCase(unittest.TestCase):

    def test_increase_any_hero_skills(self):
        r = increase_any_hero_skills()
        self.assertEqual(r, True)

    def test_upgrade_any_hero_skin(self):
        r = increase_any_hero_skins()
        self.assertEqual(r, True)

    def test_increase_any_hero_artifact(self):
        r = increase_any_hero_artifact()
        self.assertEqual(r, True)

    def test_increase_any_hero_xp(self):
        r = increase_any_hero_xp()
        self.assertEqual(r, True)

    def test_complete_daily_quests(self):
        complete_daily_quests()




if __name__ == '__main__':
    unittest.main()
