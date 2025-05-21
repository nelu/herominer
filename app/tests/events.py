import time
import unittest

from app import result
from app.utils.events import one_time_handler, run_handle_events
from app.utils.service import wait


class MyTestCase(unittest.TestCase):
    exit_result = None

    def handle_exit_flag(self, r):
        print("handle_exit_flag")
        print(r)
        self.exit_result = r

    def wait_for_response(self):
        print("wait_for_response")
        while self.exit_result is None:
            run_handle_events()

            time.sleep(0.25)

    def test_string(self):
        test_response = "x"
        one_time_handler(result.PLAY_RESULT, self.handle_exit_flag)
        wait(1)
        result.action(test_response)
        self.wait_for_response()

        self.assertEqual(test_response, self.exit_result)  # add assertion here
    def test_int(self):
        test_response = "0"
        one_time_handler(result.PLAY_RESULT, self.handle_exit_flag)
        wait(1)
        result.action(test_response)
        self.wait_for_response()

        self.assertEqual(int(test_response), self.exit_result)  # add assertion here


if __name__ == '__main__':
    unittest.main()
