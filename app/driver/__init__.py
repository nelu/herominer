import platform
import re
import json
from multiprocessing import Process, Queue, Event

from app import settings
from .macrorecorder import MacroRecorderDriver
from .config import JSONConfig
from seleniumwire.utils import decode
from selenium.webdriver.chrome.options import Options
from mixed_chromedriver import Driver

from ..utils.log import logger

log = logger(__name__)


# we dont need no sandbox on windows
# https://github.com/SeleniumHQ/selenium/issues/13837
class SafeOptions(Options):
    def add_argument(self, arg):
        if arg == "--no-sandbox" and platform.system() == "Windows":
            return  # Skip it
        super().add_argument(arg)


class DriverInterface(MacroRecorderDriver):
    def __init__(self, **kwargs):
        super().__init__()
        self.selenium_worker = None
        self.selenium = None
        self.stop_event = None

    def browser(self):
        if not self.selenium:
            self.selenium = self.get_selenium()
        return self.selenium

    @staticmethod
    def get_selenium(conf=settings.SELENIUM_DRIVER):

        options = SafeOptions()
        if conf.get('binary_location'):
            options.binary_location = conf["binary_location"]

        options.add_argument("--enable-unsafe-webgpu")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        # Separate wire configuration

        driver = Driver(
            version_main=conf['driver_version'],
            headless=conf['headless'],
            undetected=conf['undetected'],
            wire=conf['wire'],
            user_data_dir=conf['user_data_dir'],
            options=options,
            seleniumwire_options=conf['seleniumwire_options']  # <-- KEY LINE
        )

        driver.maximize_window()  # force max

        return driver

    @staticmethod
    def wait_for_shutdown(runable_wrapper, queue: Queue, stop_event: Event, *a):
        resp = runable_wrapper(queue, stop_event, *a)

        if resp:
            queue.put({"data": resp})  # ✅ Send result to parent process
            # Wait for shutdown signal
            log.info("[do_request] Waiting for worker stop_event...")
            stop_event.wait()  # ⏳ blocks here until parent sets it
        else:
            queue.put({"error": 'invalid', "success": resp})

        player.stop()

    def do_request(self, runable_wrapper, *args):
        queue = Queue()

        self.stop_event = Event()
        self.selenium_worker = Process(target=self.wait_for_shutdown,
                                       args=(runable_wrapper, queue, self.stop_event, *args))
        self.selenium_worker.start()
        response = queue.get()
        if response.get('error'):
            self.selenium_worker.join(10)
            return False

        return response

    def ajax_requests(self,
                      content_type_filter='application/json',
                      url_pattern=None,
                      body_pattern=None,
                      status_code=None,
                      pretty_print=False,
                      limit=None):
        ajax = []
        for req in self.selenium.requests:
            if not req.response:
                continue

            content_type = req.response.headers.get('Content-Type', '')
            if content_type_filter and content_type_filter not in content_type:
                continue

            if url_pattern and not re.compile(url_pattern).match(req.url):
                continue

            if status_code and req.response.status_code != status_code:
                continue

            req_body = req.body.decode('utf-8', errors='ignore')
            if body_pattern and not re.compile(body_pattern).match(req_body):
                continue

            body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            ajax.append({
                'url': req.url,
                'status': req.response.status_code,
                'data': json.loads(body)

            })

            if limit and len(ajax) >= limit:
                break

        return ajax

    def close_selenium(self):
        """Gracefully resets Selenium by opening a fresh tab and closing all others."""
        try:
            # Step 1: Open a new tab and switch to it
            self.selenium.switch_to.new_window('tab')
            new_tab_handle = self.selenium.current_window_handle

            # Step 2: Close all other tabs/windows
            for handle in self.selenium.window_handles:
                if handle != new_tab_handle:
                    self.selenium.switch_to.window(handle)
                    self.selenium.close()

            # Step 3: Ensure we're on the new blank tab
            self.selenium.switch_to.window(new_tab_handle)
            self.selenium.get("about:blank")  # Optional: reset to a clean state

        except Exception as e:
            log.exception(f"close_browser: during tab cleanup: {e}")

        finally:
            # Quit to fully terminate WebDriver session and process
            try:
                # self.selenium.quit()
                log.debug("close_browser: WebDriver session terminated successfully.")
            except Exception as e:
                log.exception(f"close_browser: during close(): {e}")

    def stop(self):
        if self.selenium:
            try:
                # Close the browser and terminate the WebDriver session
                self.close_selenium()
                self.selenium.quit()
            except Exception as e:
                log.exception(f"Error closing driver: {e}")
            self.selenium = None

        if player.selenium_worker:
            self.stop_event.set()
            player.selenium_worker.join(timeout=10)
            super().stop()
            self.selenium_worker = None


player = DriverInterface()
