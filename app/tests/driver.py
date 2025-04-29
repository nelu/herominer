import unittest

from app.driver import player
from app.driver.config import write_coords
from app.settings import APP_GAME_URL
from app.utils.service import wait


class MyTestCase(unittest.TestCase):

    def test_click(self):
        r = player.click("333x444")

    def test_process_detections(self):
        r  = player.check_process_and_window()
        self.assertIsNotNone(r)

    def test_write_coordinates(self):
        r = write_coords("333x444")
        self.assertIsNotNone(r)
        r = write_coords(["111x222", "333x444", "555x666"], name="adventure-lvl-route")
        self.assertIsNotNone(r)

    def test_selenium(self):
        browser = player.browser()
        #browser.switch_to.new_window('window')

        #browser.reconnect()

        browser.get(APP_GAME_URL)
        window_title = browser.title

        print(f"Page title: {window_title}")

        self.assertRegex(window_title, "Hero Wars")

    def test_persistent_instance(self):
        for _ in range(100000):
            self.test_selenium()
            player.close_selenium()
            wait(3)

    def tearDown(self):
        player.stop()


    def test_clipboard(self):
        player.to_clipboard("From driver test case")
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
