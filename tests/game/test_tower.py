from tests import require_integration

require_integration()

import unittest

from hm.game.lobby.tower import run_tower

class MyTestCase(unittest.TestCase):

    def test_run(self):
        r = run_tower()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
