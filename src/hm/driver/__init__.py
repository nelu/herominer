import asyncio
import re
import json
from multiprocessing import Process, Queue, Event

import psutil
import win32gui
import win32process

from .. import settings
from .macrorecorder import MacroRecorderDriver
from .config import JSONConfig
from seleniumwire import SeleniumWireOptions
from seleniumwire.utils import decode
from seleniumwire_gpl import UndetectedChrome
from undetected_chromedriver import ChromeOptions

from ..utils.log import logger

log = logger(__name__)


async def _cancel_pending_proxy_tasks():
    current_task = asyncio.current_task()
    pending_tasks = [
        task for task in asyncio.all_tasks()
        if task is not current_task
    ]
    for task in pending_tasks:
        task.cancel()
    if pending_tasks:
        await asyncio.gather(*pending_tasks, return_exceptions=True)


class ManagedUndetectedChrome(UndetectedChrome):
    def quit(self):
        backend = getattr(self, 'backend', None)
        try:
            super().quit()
        finally:
            if backend and not getattr(self, '_wire_backend_stopped', False):
                try:
                    try:
                        backend._shutdown_mitmproxy()
                    finally:
                        backend.storage.cleanup()
                finally:
                    event_loop = getattr(backend, 'event_loop', None)
                    thread = getattr(backend, 'thread', None)
                    if event_loop and event_loop.is_running():
                        cleanup = asyncio.run_coroutine_threadsafe(_cancel_pending_proxy_tasks(), event_loop)
                        try:
                            cleanup.result(timeout=5)
                        except Exception:
                            log.exception('Failed to drain Selenium Wire proxy tasks')
                        finally:
                            event_loop.call_soon_threadsafe(event_loop.stop)
                    if thread and thread.is_alive():
                        thread.join(timeout=5)
                    if event_loop and not event_loop.is_running() and not event_loop.is_closed():
                        event_loop.close()
                    self._wire_backend_stopped = True


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

        options = ChromeOptions()
        if conf.get('binary_location'):
            options.binary_location = conf["binary_location"]

        options.add_argument("--enable-unsafe-webgpu")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        wire_options = SeleniumWireOptions(**conf['seleniumwire_options'])
        driver = ManagedUndetectedChrome(
            version_main=conf['driver_version'],
            headless=conf['headless'],
            user_data_dir=conf['user_data_dir'],
            options=options,
            seleniumwire_options=wire_options,
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

    def do_request(self, runable_wrapper, timeout, *args):
        queue = Queue()

        self.stop_event = Event()
        self.selenium_worker = Process(target=self.wait_for_shutdown,
                                       args=(runable_wrapper, queue, self.stop_event, timeout, *args))
        self.selenium_worker.start()
        try:
            # Wait for result with 5*second timeout
            response = queue.get(timeout=5*timeout)
        except Exception as e:
            print(f"[do_request] Timeout waiting for worker response: {e}")
            # No response in time, try to shut down
            self.stop_event.set()
            self.selenium_worker.join(timeout=5)

            if self.selenium_worker.is_alive():
                print("[do_request] Worker still alive after join, terminating...")
                self.selenium_worker.terminate()
                self.selenium_worker.join()

            return False

        # Got response
        if response.get('error'):
            # Response has error, still need to clean up
            self.stop_event.set()
            self.selenium_worker.join(timeout=5)

            if self.selenium_worker.is_alive():
                print("[do_request] Worker alive after error, forcing terminate...")
                self.selenium_worker.terminate()
                self.selenium_worker.join()

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
        # from main thread
        if player.selenium_worker:
            self.stop_event.set()
            player.selenium_worker.join(timeout=10)
            self.selenium_worker = None

        # from selenium worker thread/process
        if self.selenium:
            try:
                # Close the browser and terminate the WebDriver session
                self.close_selenium()
                self.selenium.quit()
            except Exception as e:
                log.exception(f"Error closing driver: {e}")
            self.selenium = None

        else:
            # from main thread
            super().stop()


    @staticmethod
    def get_window_title(pid):
        """Find window title for a given PID."""
        titles = []

        def enum_windows_callback(hwnd, pid_to_title):
            try:
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        pid_to_title.append(title)
            except Exception:
                pass  # Some windows may not allow access

        win32gui.EnumWindows(enum_windows_callback, titles)
        return titles

    @staticmethod
    def check_process_and_window(executable_name = 'brave.exe', word = "Hero"):
        """Check if the process is running and window title contains the word."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == executable_name.lower():
                    #print(f"Process {executable_name} found with PID {proc.pid}")
                    titles = DriverInterface.get_window_title(proc.pid)
                    for title in titles:
                        if word.lower() in title.lower():
                            #print(f"Window title containing '{word}': {title}")
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False


player = DriverInterface()
