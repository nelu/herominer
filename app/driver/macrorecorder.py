import os
import subprocess
import time

import pyperclip
import re

import app
from app import settings, result
from .config import JSONConfig, write_coords
from app.utils import session
from app.utils.service import check_shutdown, GracefulExit
from app.utils.session import persist_path
from ..utils.events import one_time_handler, run_handle_events
from app.utils.log import logger

log = logger(__name__)


def write_action_config():
    filename = 'cli.path'
    c = JSONConfig(filename)
    # c['content'] = settings.APP_ACTIONS_ENTRYPOINT_PATH

    return c.save(False) is not False and c.save_as(persist_path(filename))


class MacroRecorderDriver:
    def __init__(self):
        write_action_config()
        self.run_inputs = {}
        self.process = None
        self.exit_result = None

    def close_browser(self):
        return self.play_action(action="0_close-browser", timeout=10)

    def start(self, action):
        """Start the macro recorder with an action."""
        return self.play_action(action, timeout=settings.ACTION_DRIVER_PLAY_TIMEOUT)

    def stop(self):
        log.debug("stop: Closing macro recorder.")
        self.close_browser()

        r = self.close()
        if r:
            if self.process:
                self.process.terminate()

                try:
                    if self.process.stdout:
                        self.process.stdout.close()
                    if self.process.stderr:
                        self.process.stderr.close()
                    if self.process.stdin:
                        self.process.stdin.close()
                except Exception as e:
                    log.warning(f"stop: Failed to close process I/O streams: {e}")

            still_running = self.is_running()
            if still_running:
                log.warning("stop: Macro recorder is still running, terminating.")
                still_running.terminate()

            log.debug("stop: Macro recorder closed.")
            self.process = None

        return r

    def is_running(self):
        import psutil
        """Check if the process is running based on its executable path."""
        for process in psutil.process_iter(['exe', 'pid']):
            try:
                if process.info['exe'] and process.info['exe'].lower() == settings.ACTION_DRIVER_LOCATION.lower():
                    return process
            except psutil.ZombieProcess as e:
                log.warning(f"is_running: Zombie process found: {e}")
                return process
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue  # Skip processes we can't access
        return None

    def restart(self, action="0_close_browser"):
        """Restart the macro recorder."""
        self.stop()
        return self.start(action)

    def click(self, coords):

        r = write_coords(coords) and self.start("click")
        r or log.warning("click: Macro recorder click failed.")
        return r

    def get_regex_pattern(self, text):
        # Split into words to insert flexible punctuation and spacing
        words = re.findall(r'\w+', text)

        # Build pattern with optional punctuation and whitespace between words
        pattern = r'[.,!?]*\s*'.join(map(re.escape, words))

        # Optionally allow punctuation at the end too
        pattern = rf"{pattern}[.,!?]*"

        return pattern

    def to_clipboard(self, content):
        pyperclip.copy(content)
        return self

    def write_run_inputs(self, entries):
        for file, data in entries.items():
            session.persist(file, data)
        return self

    def set_run_inputs(self, entries):
        self.run_inputs.update(entries)
        return self

    def close(self):
        """Close the macro recorder."""
        r = subprocess.run([f"{settings.ACTION_DRIVER_LOCATION}", "-close"])
        time.sleep(1)
        return r

    def play_file(self, filename):
        """Play a macro file."""
        FILE = os.path.normpath(os.path.join(settings.APP_ACTIONS_DIR, f"{filename}.mrf"))
        if not os.path.isfile(FILE):
            raise FileNotFoundError(f"Macro file not found: {FILE}")

        cmd = [f"{settings.ACTION_DRIVER_LOCATION}", "-play", FILE]

        log.debug(f"playback: {filename} - {cmd}")

        DETACHED_PROCESS = 0x00000008

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=DETACHED_PROCESS,
            universal_newlines=True,
            bufsize=1,
            text=True
        )

    def handle_exit_flag(self, data):
        self.exit_result = data
        log.info(f"handle_exit_flag: received exit_flag with data: {data}")

    def play_action(self, action="0_close_browser", timeout=900):
        if app.STOP_SIGNALED:
            return False

        #session.remove_entry(result.PLAY_RESULT)
        self.write_run_inputs(self.run_inputs)

        # well it seems this fella might write self.exit_result with something else than None / reset state
        # for now we run handle events so we have clean env for exit_result to get populated
        # after the actual playback has started
        run_handle_events() # execute any stray handles registered for handle_exit_flag
        one_time_handler(result.PLAY_RESULT, self.handle_exit_flag)

        try:
            self.exit_result = None

            self.process = self.play_file(action)
            start_time = time.time()

            while self.exit_result is None:
                run_handle_events()

                elapsed_time = time.time() - start_time

                if elapsed_time > timeout:
                    log.warning(
                        f"play_action: {action} timed out - {elapsed_time:.1f}s. Terminating process {self.process.pid}")
                    self.process.terminate()
                    return False

                #if self.process and self.process.poll() is not None:
                #   log.debug(f"play_action: {action} process {self.process.pid} exited early.")

                time.sleep(0.25)

            self.run_inputs = {}

            return (isinstance(self.exit_result, str)
                    and (self.exit_result.isnumeric() and int(self.exit_result) or self.exit_result)
                    or self.exit_result)

        except GracefulExit:
            log.exception(f"play_action: GracefulExit {action} - Shutdown from service. driver pid: {self.process.pid}")
            raise
        except KeyboardInterrupt:
            log.exception(f"play_action: KeyboardInterrupt {action} - received. driver pid: {self.process.pid}")
            raise
        except Exception as e:
            log.exception(f"play_action: {action} - {self.run_inputs} err {e}")
            raise

    def play_action_key_check(self, action="0_close_browser", timeout=900):
        if app.STOP_SIGNALED:
            return False
        """Play a macro action."""
        session.remove_entry(result.PLAY_RESULT)
        self.write_run_inputs(self.run_inputs)

        try:
            self.process = self.play_file(action)
            # log.debug(f"play_action: {action} process started PID {self.process.pid}, timeout {timeout}")
            start_time = time.time()
            notify_exit = False
            elapsed_time = None

            while not session.has_session(result.PLAY_RESULT):
                elapsed_time = time.time() - start_time

                if self.process.poll() is not None:
                    # (not notify_exit or int(elapsed_time) % 60 == 0) and log.debug(
                    #     f"play_action: {action} process {self.process.pid} exited early.")
                    notify_exit = True

                if elapsed_time > timeout:
                    log.warning(
                        f"play_action: {action} timed out - {elapsed_time}s. Terminating process {self.process.pid}")
                    self.process.terminate()
                    return False

                check_shutdown()

                time.sleep(1)

            exit_result = session.read_session(result.PLAY_RESULT)

            log.info(f"play_action: {action} - result: {exit_result} <- elapsed {elapsed_time}s")

            self.run_inputs = {}

            return (isinstance(exit_result, str)
                    and (exit_result.isnumeric() and int(exit_result) or exit_result)
                    or exit_result)

        except GracefulExit:
            log.exception(f"play_action: GracefulExit {action} - Shutdown from service. driver pid: {self.process.pid}")
            raise
        except KeyboardInterrupt as e:
            log.exception(f"play_action: KeyboardInterrupt {action} - received. driver pid: {self.process.pid}")
            raise
        except Exception as e:
            log.exception(f"play_action: {action} - {self.run_inputs} err {e}")
            raise
            # return False
