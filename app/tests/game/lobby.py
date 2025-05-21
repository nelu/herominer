import unittest

from app.game.lobby import menus


class MyTestCase(unittest.TestCase):
    def test_open_menu(self):

        r = menus.open_menu('arena')
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
