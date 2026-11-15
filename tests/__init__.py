import os
import unittest


def require_integration():
    if os.environ.get('HM_RUN_INTEGRATION_TESTS') != '1':
        raise unittest.SkipTest(
            'Set HM_RUN_INTEGRATION_TESTS=1 to run live automation tests.'
        )
