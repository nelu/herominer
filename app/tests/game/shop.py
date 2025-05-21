import unittest

from app.game.shop import buy_heroes, shop_config, buy_items


class MyTestCase(unittest.TestCase):

    def test_buy_arena_items(self):
        buy_items('arena')
        self.assertEqual(True, True)  # add assertion here

    def test_buy_grand_arena_heroes(self):
        buy_heroes("grand-arena", shop_config('grand.*arena')['items'])
        self.assertEqual(True, True)  # add assertion here

    def test_buy_outland_heroes(self):
        buy_heroes("outland", shop_config('outland')['items'])
        self.assertEqual(True, True)  # add assertion here

if __name__ == '__main__':
    unittest.main()
