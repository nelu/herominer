import unittest

from app.game.lobby.outland import check_free

class MyTestCase(unittest.TestCase):

    def test_free_claim(self):
        r = check_free()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
