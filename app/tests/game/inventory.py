import unittest

from app.game.inventory import check_inventory
from app.game.grow import acquire_hero_items


class MyTestCase(unittest.TestCase):

    def test_inventory_run(self):
        check_inventory()


if __name__ == '__main__':
    unittest.main()
