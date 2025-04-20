import unittest

from app.driver import player
from app.driver.config import write_coords
from app.settings import APP_GAME_URL


class MyTestCase(unittest.TestCase):

    def test_click(self):
        r = player.click("333x444")

    def test_write_coordinates(self):
        r = write_coords("333x444")
        self.assertIsNotNone(r)
        r = write_coords(["111x222", "333x444", "555x666"], name="adventure-lvl-route")
        self.assertIsNotNone(r)

    def test_selenium(self):
        browser = player.browser()
        browser.get(APP_GAME_URL)
        window_title = browser.title

        print(f"Page title: {window_title}")
        browser.quit()

        self.assertRegex(window_title, "Hero Wars")




    def test_clipboard(self):
        player.to_clipboard("From driver test case")
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
