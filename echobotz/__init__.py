import asyncio
from uvloop import install
from logging import (
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    StreamHandler,
    basicConfig,
    getLogger,
)

from config import Config

install()

bot_loop = asyncio.new_event_loop()
asyncio.set_event_loop(bot_loop)

from config import Config

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

getLogger("pyrogram").setLevel(ERROR)
getLogger("pymongo").setLevel(WARNING)

LOGGER = getLogger(__name__)

install()

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

user_data = {}
auth_chats = {}
sudo_users = set(Config.SUDO_USERS)
