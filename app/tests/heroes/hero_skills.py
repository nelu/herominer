import json
import os
import unittest
from app.game.heroes.hero import Hero
from app.utils.session import daily
from app.tests import load_fixture
temp = daily('tests')

class SkillsTestCase(unittest.TestCase):

    def test_parse_skills_stats(self):
        data =  load_fixture("hero.json")
        hero = Hero.load('aidan')

        r = hero.skills.update_from_screen()
        self.assertIsNotNone(r)

        temp.set('skills', "|Titan's Fist\nLevel: 1\n\n@\u00c2\u00ae 100 \u00c2\u00ae|Living Earth\n\na\n{3 Available at Green rank|Stone Grasp\n\na\n3 Available at Blue rank|Nature's Barrier\n\nA\n{73 Available at Violet rank")
        r = hero.skills.update_from_screen()
        self.assertIsNotNone(r)

        self.assertEqual((hero), True)  # add assertion here

    def test_hero_skill_stats(self):
        hero = Hero.load('aidan')
        hero.open_hero() and hero.skills.upgrade_any()
        r = hero.skills.refresh(self)
        self.assertEqual(r, True)

    def test_skill_upgrade(self):
        hero = Hero.load('astrid-and-lucas')
        r = hero.skills.upgrade_any()
        self.assertEqual(r, True)
