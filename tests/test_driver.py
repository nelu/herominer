from tests import require_integration

require_integration()

import unittest
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from hm.driver import player
from hm.driver.config import write_coords
from hm.settings import APP_GAME_URL
from hm.utils.service import wait


class PlaintextHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"HeroMiner plaintext interception"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


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

    def test_https_traffic_is_decrypted(self):
        browser = player.browser()
        browser.get("https://example.com/")

        request = browser.wait_for_request(r"https://example\.com/", timeout=20)
        self.assertIsNotNone(request.response)
        self.assertTrue(request.certificate_list)

        body = request.response.decompress_body()
        self.assertIn(b"Example Domain", body)

    def test_http_traffic_is_intercepted(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), PlaintextHandler)
        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        url = f"http://127.0.0.1:{server.server_port}/interception-test"

        try:
            browser = player.browser()
            browser.get(url)
            request = browser.wait_for_request(re.escape(url), timeout=20)

            self.assertIsNotNone(request.response)
            self.assertIn(b"HeroMiner plaintext interception", request.response.decompress_body())
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=5)

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
