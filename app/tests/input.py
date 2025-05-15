import unittest

from app.result import complete, day, stats, append, file
from app.utils.session import daily, status, persist_path


class InputTestCase(unittest.TestCase):
    test_key = "InputTestCase"
    td = None

    def setUp(self):
        self.dd = daily(self.test_key)

    def test_result_complete(self):
        complete("testinput", self.test_key)

        self.assertEqual(True, self.dd.is_complete("testinput"))
        self.assertEqual(False, self.dd.is_complete("testinput2"))

    def test_result_daily(self):
        day(self.test_key, "key1", "value1", "key2", "value2", "key3", "1")
        day(self.test_key, "key2", "")

        self.assertEqual("value1", self.dd.get("key1"))
        self.assertNotEqual("value2", self.dd.get("key2"))
        self.assertEqual(1, self.dd.get("key3"))  # converted to int

    def test_result_stats(self):
        stats(self.test_key, "stat1", "value1", "stat2", "value2")

        self.assertEqual(status(self.test_key).get("stat2"), "value2")

    def test_result_append(self):
        stats(self.test_key, "append1", "value1", "append2", "value2")
        append(self.test_key, "append2", "appended", "2")
        self.assertEqual("value2appended 2", status(self.test_key).get("append2"))

    def test_result_file(self):
        file("test_file1.txt", "test_file1 contents")
        with open(persist_path("test_file1.txt"), 'r', encoding='utf-8') as f:
            self.assertEqual("test_file1 contents", f.read())


if __name__ == '__main__':
    unittest.main()
