import glob
import os
from urllib.parse import urlparse
from app import settings
from app.driver import player as driver
from app.utils import session
from . import close_game
from app.utils.log import logger

log = logger(__name__)


def is_valid_url(url):
    try:
        # Parse the URL
        parsed = urlparse(url)
        # Check if scheme and netloc are present
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False


def find_most_recent_file_with_prefix(directory, prefix):
    # Use glob to find all files matching the prefix
    pattern = os.path.join(directory, f"{prefix}*")
    files = glob.glob(pattern)

    # If no matching files are found, return None
    if not files:
        return None

    # Find the most recent file based on modification time
    most_recent_file = max(files, key=os.path.getmtime)
    return most_recent_file


def open_link(url):
    session.persist("social-bonus-url.txt", f"--start-maximized \"{url}\"", settings.APP_SOCIAL_DIR)
    r = driver.start("social/open-bonus-link")
    driver.close_browser()

    r or log.info(f"open_link: invalid link - {url}")

    return r


def parse_urls(lines):
    valid_urls = []

    for line in lines:
        url = line.strip()  # Remove whitespace and newline characters
        url and is_valid_url(url) and valid_urls.append(url)

    return valid_urls


def open_latest_links():
    latest_file = find_most_recent_file_with_prefix(settings.APP_SOCIAL_DIR, "latest-links-")
    log.info(f"open_latest_links: {latest_file}")

    if not latest_file:
        return False

    valid_urls = []

    # Read the file line by line
    with open(latest_file, 'r') as file:
        for url in parse_urls(file):
            open_link(url) and valid_urls.append(url)

    set_valid_bonus_links(valid_urls)

    log.info(f"open_latest_links: Found links {len(valid_urls)}")

    remove_file(os.path.basename(latest_file))

    return len(valid_urls)


def get_valid_bonus_links():
    return session.read_session('social_valid_links')


def set_valid_bonus_links(valid_urls):
    return session.write('social_valid_links', valid_urls)


def delete_valid_bonus_links():
    return session.remove_entry('social_valid_links')


def remove_file(name):
    log.info(f"remove_file: {name}")
    return session.remove_file(name, settings.APP_SOCIAL_DIR)


def check_bonus_links():
    log.info("check_bonus_links: Social pages for bonus links")
    # we are not using selenium
    close_game()
    has_new = driver.start("social/collect-fb-bonuses")

    log.debug(f"check_bonus_links: has new links - {has_new}")

    # wait for chat announce to finish removing the previous links
    # before processing another dontloaded links file
    if not get_valid_bonus_links():
        open_latest_links() and log.info("check_bonus_links: Got new social bonus links to announce")

    close_game()
