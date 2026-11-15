from tests import require_integration

require_integration()

import unittest

from hm.game.inventory import check_inventory
from hm.game.grow import acquire_hero_items, grow_heroes, hero_soulstones


class MyTestCase(unittest.TestCase):

    def test_create_items(self):
        acquire_hero_items()
    def test_grow_heroes(self):
        grow_heroes()

    def test_soulstone_play_missions(self):
        hero_soulstones(['astaroth'])

        hero_soulstones()


if __name__ == '__main__':
    unittest.main()
