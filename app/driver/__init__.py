import re
import json
from app import settings
from .macrorecorder import MacroRecorderDriver
from .config import JSONConfig
from seleniumwire.utils import decode


class DriverInterface(MacroRecorderDriver):
    def __init__(self, **kwargs):
        super().__init__()
        self.selenium = None

    def browser(self):
        if not self.selenium:
            self.selenium = self.get_selenium()
        return self.selenium

    @staticmethod
    def get_selenium(conf=settings.SELENIUM_DRIVER):
        from selenium.webdriver.chrome.options import Options
        from mixed_chromedriver import Driver

        options = Options()
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

    def stop(self):
        if self.selenium:
            try:
                # Close the browser and terminate the WebDriver session
                self.selenium.close()
                self.selenium.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")

            self.selenium = None

        macro_stop = super().stop()

        return macro_stop


player = DriverInterface()
