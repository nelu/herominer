# driver/external.py
import subprocess
from app.utils.log import logger

log = logger(__name__)

class ExternalDriver:
    def __init__(self, command=""):
        self.command = command
        self.process = None

    def start(self, command=None):
        """Start an external application."""
        if command:
            self.command = command
        if not self.command:
            log.warning("⚠️ No command provided for External driver.")
            return None
        log.info(f"Starting external application: {self.command}")
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return self.process

    def execute(self, command):
        """Execute a command in the external application."""
        if not command:
            log.warning("⚠️ No command provided to execute.")
            return ""
        log.info(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

    def stop(self):
        """Stop the external application."""
        if self.process:
            self.process.terminate()
            log.info("External application stopped.")
            self.process = None

    def status(self):
        """Check if the external process is running."""
        return self.process.poll() is None if self.process else False

    def restart(self, command=None):
        """Restart the external application."""
        self.stop()
        return self.start(command)
