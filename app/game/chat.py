from jinja2 import Template

from app.driver import player as driver, JSONConfig
from app.game.lobby import back_to_lobby
from app.utils.log import logger
from app.game import social, open_game, play_action
from app.utils import session

log = logger(__name__)


def config():
    return JSONConfig('chat.json')


# TODO: Implement chat
def send_chat_msg(message):
    # session.persist("chat-sendmsg.txt", message)
    # Execute chatbot message action
    r = open_game() and driver.to_clipboard(message).start("chat/chatbot-send-message")
    driver.to_clipboard("")

    back_to_lobby()
    return r


def announce_bonus_links():
    # Check for new bonus links
    links = social.get_valid_bonus_links()

    if links:
        links = isinstance(links, list) and links or [links]
        log.info(f"announce_bonus_links: new links - {links}")
        templates = config().get('templates', {})
        message = Template(templates['announce_chat_msg']).render(links=links)

        send_chat_msg(message)

        # Cleanup
        social.delete_valid_bonus_links()


def send_chat_image():
    """Handles automated chat interactions, sending images and bonus links if applicable."""
    log.info("send_chat_image: Sending chat image.")
    r = play_action("chat/send-chat-img")
    return r
