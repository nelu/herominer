from app.driver import player as driver
from app.game.lobby import back_to_lobby
from app.utils.log import logger
from app.game import social, open_game
from app.utils import session

log = logger(__name__)


# TODO: Implement chat
def send_chat_msg(message):
    #session.persist("chat-sendmsg.txt", message)
    # Execute chatbot message action
    r = open_game() and driver.to_clipboard(message).start("chat/chatbot-send-message")
    back_to_lobby()
    driver.to_clipboard("")
    return r


def announce_bonus_links():
    # Check for new bonus links
    links = social.get_valid_bonus_links()
    if links:
        links = "\n".join(links)
        log.info(f"announce_bonus_links: Found new Facebook free links. {links}")
        message = f"Bonus links available on FB: {links} -- HeroMiner"

        send_chat_msg(message)

        # Cleanup
        social.delete_valid_bonus_links()


def send_chat_image():
    """Handles automated chat interactions, sending images and bonus links if applicable."""

    log.info("Daily: Sending chat image.")
    r = open_game() and driver.start("chat/send-chat-img")
    back_to_lobby()
    return r

