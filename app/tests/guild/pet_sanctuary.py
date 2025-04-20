import unittest

from app.game.guild.sanctuary import summon_pets, buy_from_merchant


class MyTestCase(unittest.TestCase):

    def test_buy_merchant(self):
        r = buy_from_merchant()
        self.assertEqual(True, True)  # add assertion here

    def test_summon_pets(self):
        r = summon_pets()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
