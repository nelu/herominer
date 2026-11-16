import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from seleniumwire import SeleniumWireOptions
from seleniumwire import backend as wire_backend
from undetected_chromedriver import ChromeOptions

from hm.driver import DriverInterface, ManagedUndetectedChrome, UndetectedChrome


class DriverConfigurationTestCase(unittest.TestCase):
    def test_builds_lw_undetected_driver(self):
        conf = {
            'driver_version': 135,
            'headless': True,
            'binary_location': r'C:\Browser\brave.exe',
            'user_data_dir': r'C:\Browser\profile',
            'seleniumwire_options': {
                'auto_config': True,
                'disable_capture': False,
                'exclude_hosts': [],
                'request_storage': 'memory',
                'request_storage_max_size': 100,
                'storage_base_dir': r'C:\HeroMiner\data',
                'verify_ssl': False,
            },
        }
        driver = MagicMock()

        with patch('hm.driver.ManagedUndetectedChrome', return_value=driver) as driver_class:
            result = DriverInterface.get_selenium(conf)

        self.assertIs(result, driver)
        driver.maximize_window.assert_called_once_with()

        kwargs = driver_class.call_args.kwargs
        self.assertEqual(kwargs['version_main'], 135)
        self.assertTrue(kwargs['headless'])
        self.assertEqual(kwargs['user_data_dir'], conf['user_data_dir'])
        self.assertIsInstance(kwargs['options'], ChromeOptions)
        self.assertEqual(kwargs['options'].binary_location, conf['binary_location'])

        wire_options = kwargs['seleniumwire_options']
        self.assertIsInstance(wire_options, SeleniumWireOptions)
        self.assertTrue(wire_options.auto_config)
        self.assertFalse(wire_options.disable_capture)
        self.assertEqual(wire_options.exclude_hosts, [])
        self.assertEqual(wire_options.request_storage, 'memory')
        self.assertEqual(wire_options.request_storage_max_size, 100)
        self.assertFalse(wire_options.verify_ssl)

    def test_quit_stops_proxy_backend_once(self):
        driver = ManagedUndetectedChrome.__new__(ManagedUndetectedChrome)
        driver.backend = MagicMock()
        driver.backend.event_loop = None
        driver.backend.thread = None

        with patch.object(UndetectedChrome, 'quit') as uc_quit:
            driver.quit()
            driver.quit()

        self.assertEqual(uc_quit.call_count, 2)
        driver.backend._shutdown_mitmproxy.assert_called_once_with()
        driver.backend.storage.cleanup.assert_called_once_with()

    def test_quit_closes_real_proxy_event_loop(self):
        with TemporaryDirectory() as temp_dir:
            backend = wire_backend.create(SeleniumWireOptions(
                request_storage='memory',
                storage_base_dir=temp_dir,
            ))
            ca_path = Path(backend.storage.home_dir) / 'mitmproxy-ca.pem'
            self.assertTrue(ca_path.is_file())

            driver = ManagedUndetectedChrome.__new__(ManagedUndetectedChrome)
            driver.backend = backend
            with patch.object(UndetectedChrome, 'quit'):
                driver.quit()

            self.assertFalse(backend.thread.is_alive())
            self.assertTrue(backend.event_loop.is_closed())


if __name__ == '__main__':
    unittest.main()
