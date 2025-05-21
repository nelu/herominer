import unittest
from app.game.heroes.hero import Hero
from app.game.heroes.manager import instance

class HeroesTestCase(unittest.TestCase):

    def test_hero_open(self):
        hero = Hero.load('corvus')
        updated_hero = hero.open_hero()

        self.assertEqual(hero, True)  # add assertion here

    def test_hero_stats_refresh(self):
        hero = Hero.load('andvari')
        hero.update_stats()
        self.assertGreater(hero.level, 1)

    def test_parse_skins_stats(self):
        hero = Hero.load('aidan').skins.update_from_screen()
        self.assertEqual((hero), True)  # add assertion here

    def test_check_skins_stats(self):
        hero = Hero.load('celeste').skins.update_from_screen()
        self.assertEqual((hero), True)  # add assertion here

    def test_hero_evolve(self):
        hero = Hero.load('celeste')
        hero.stats.stars = 5
        self.assertEqual(hero.has_max_evolve(), True)  # add assertion here

        hero.stats.stars = 3
        self.assertEqual(hero.has_max_evolve(), False)

    def test_set_heroes_stats(self):
        h = instance.get_by_slugs(
            ['astaroth', 'arachne', 'aurora', 'celeste', 'corvus', 'dark-star', 'galahad', 'maya', 'mojo', 'rufus'])

        for name, hero in h.items():
            hero.stats.stars = 5
            hero.save()

    def test_get_multiple(self):
        names = ['artemis', 'dark-star']

        heroes = instance.get_by_slugs(names)
        self.assertEqual(names.__len__(), heroes.__len__())  # add assertion here

    def test_hero_save(self):
        from app.game.heroes.hero import Hero

        h = Hero.load('artemis')
        h.slots.equip_item('sukky', 22)
        h.save()
        h.skills.increase_stats('puliver')

        print(f'h: {h}')
        self.assertEqual(h.has_max_evolve(), False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
