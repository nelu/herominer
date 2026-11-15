import os
from dotenv import load_dotenv
import sys
from pathlib import Path

IS_COMPILED = getattr(sys, 'frozen', False) or '__compiled__' in globals()
PACKAGE_DIR = Path(__file__).resolve().parent
PACKAGE_CONFIG_DIR = PACKAGE_DIR / 'config'


def get_app_dir():
    """Return the runtime root for source and compiled execution."""
    if IS_COMPILED:
        return Path(__file__).resolve().parent.parent

    source_root = PACKAGE_DIR.parents[1]
    if (source_root / 'pyproject.toml').is_file():
        return source_root
    local_app_data = Path(os.environ.get('LOCALAPPDATA', Path.home()))
    return local_app_data / 'HeroMiner'


BASE_DIR = get_app_dir()  # Path(os.getcwd()).resolve()

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
APP_DIR = os.environ.get('HM_DIR', BASE_DIR)

APP_GAME_URL = os.environ.get('HM_GAME_URL', "https://apps.facebook.com/mobaheroes/")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

RESOLUTION = os.environ.get('HM_RESOLUTION', "1440x900")

APP_SHARE_DIR = os.environ.get('HM_SHARE_DIR', os.path.join(APP_DIR, "share"))  # "/z/persist"
APP_DATA_DIR = os.environ.get('HM_DATA_DIR', os.path.join(APP_DIR, 'data'))
APP_DATA_CACHE_DIR = os.environ.get('HM_DATA_CACHE_DIR', os.path.join(APP_SHARE_DIR, "session"))

#APP_LOG_FILE = os.environ.get('HM_LOG_FILE', os.path.join(APP_SHARE_DIR, "logs/herominer.log"))
APP_LOG_FILE = os.environ.get('HM_LOG_FILE')
APP_LOG_VERBOSITY = os.environ.get('HM_VERBOSITY', 1)
APP_SOCIAL_DIR = os.path.join(APP_SHARE_DIR, "social")
APP_ACTIONS_ENTRYPOINT_PATH = os.environ.get('HM_ENTRYPOINT_PATH',
                                             getattr(sys, 'frozen', False) and sys.executable or "c:\\hm\\cli\\input.exe")
APP_ACTIONS_DIR = os.path.join(APP_DATA_DIR, RESOLUTION)
#APP_ACTIONS_CONFIG_DIR = os.path.join(APP_DATA_DIR, 'config')
if IS_COMPILED:
    DEFAULT_CONFIG_DIR = BASE_DIR / 'config'
elif (BASE_DIR / 'pyproject.toml').is_file():
    DEFAULT_CONFIG_DIR = PACKAGE_CONFIG_DIR
else:
    DEFAULT_CONFIG_DIR = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'HeroMiner' / 'config'
APP_ACTIONS_CONFIG_DIR = os.environ.get('HM_CONFIG_DIR', str(DEFAULT_CONFIG_DIR))
ACTION_DRIVER_LOCATION = os.path.normpath(os.environ.get('HM_DRIVER_PATH',
                                                         os.path.join(APP_DATA_DIR, 'drivers',
                                                                      "MacroRecorder/MacroRecorder.exe"))
                                          )
ACTION_DRIVER_PLAY_TIMEOUT = int(os.environ.get('HM_DRIVER_PLAY_TIMEOUT', 700))
ACTION_DRIVER_IDLE_CLOSE = int(os.environ.get('HM_DRIVER_IDLE_CLOSE', 180))

SELENIUM_DRIVER = {
    "driver_version": int(os.environ.get('HM_BROWSER_VER', "135")),
    "headless": False,
    "undetected": True,
    "wire": True,
    "binary_location": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "user_data_dir": os.environ.get('HM_SELENIUM_DATA',
                                    # os.path.join(APP_SHARE_DIR, 'selenium')
                                    os.path.join(os.environ['LOCALAPPDATA'], 'BraveSoftware\\Brave-Browser\\User Data')
                                    ),
    "seleniumwire_options": {
        'request_storage': 'memory',
        'request_storage_max_size': 100,  # Store no more than 100 requests in memory
        'ca_cert': os.path.join(BASE_DIR, 'config/ca.crt'),
        'ca_key': os.path.join(BASE_DIR, 'config/ca.key')
    }
}

REDIS_URL = os.environ.get('HM_REDIS', "redis://localhost:6379/0")



def check_settings():
    # # Ensure the directories exists
    paths = [
        APP_DATA_CACHE_DIR, APP_SOCIAL_DIR, SELENIUM_DRIVER['user_data_dir']
    ]
    for path in paths:
        os.path.exists(path) or os.makedirs(path, exist_ok=True)


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Bucharest'

USE_TZ = True
