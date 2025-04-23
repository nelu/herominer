import threading
from app.driver import player
import time

class SeleniumWorker(threading.Thread):
    def __init__(self, driver_options=None):
        super().__init__()
        self.driver_options = driver_options
        self.driver = None
        self._stop_event = threading.Event()
        self.result = None
        self._lock = threading.Lock()

    def run(self):
        try:
            self.driver = webdriver.Chrome(options=self.driver_options)
            self.driver.get("https://example.com")

            # Simulate doing some work and getting a result
            title = self.driver.title

            with self._lock:
                self.result = title

            while not self._stop_event.is_set():
                time.sleep(1)

        finally:
            if self.driver:
                self.driver.quit()
            print("[SeleniumWorker] Driver quit and thread exiting.")

    def stop(self):
        self._stop_event.set()

    def get_result(self):
        with self._lock:
            return self.result
