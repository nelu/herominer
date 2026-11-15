from tests import require_integration

require_integration()

import unittest

from hm.game.lobby.airship import check_expeditions, get_opened_chests, open_chest


class MyTestCase(unittest.TestCase):

    def test_airship_run(self):
        check_expeditions()

    def test_open_chest(self):
        get_opened_chests() or open_chest()

if __name__ == '__main__':
    unittest.main()
