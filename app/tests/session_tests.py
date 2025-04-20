import json
import unittest
import time

from app.driver.config import write_coords
from app.utils import session
from app.utils.session import has_event


class MyTestCase(unittest.TestCase):
    def test_event_pool_listen(self):
        event = None
        while not event:
            event = has_event('action')
            print(event)
            time.sleep(1)



    def test_event_listen(self):
        pubsub = session.storage.redis_client.pubsub()
        pubsub.subscribe("action")
        for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    print(payload["event"], payload.get("data", {}))
                except Exception as e:
                    print(f"Error processing event: {e}")

    def session_write(self):
        session.write('end-value', 1)
        self.assertEqual(int(session.read_session('end-value')), 1)  # add assertion here

    def test_exists(self):
        self.session_write()
        self.assertEqual(session.has_session('end-value'), True)  # add assertion here

    def test_get_write_time(self):
        self.session_write()
        then = time.time()
        session.conn.set(name='end-value', value=1)

        self.assertEqual(round(session.read_session_mtime('end-value'), -1), round(then, -1))  # add assertion here

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()


