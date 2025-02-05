import logging

from telegram import Bot
from telegram.request import HTTPXRequest

from Cloud_Stock.settings import BASE_DIR
from config.django_config import TGLOGGER, TGLOGGERKEY

if TGLOGGER:
    API_TOKEN = TGLOGGERKEY[0]
    CHAT_ID = TGLOGGERKEY[1]

    trequest = HTTPXRequest(connection_pool_size=100)
    bot = Bot(token=API_TOKEN, request=trequest)


async def tglog(message: str):
    if TGLOGGER:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        pass


# DEBUG=10, INFO=20, WARNING=30
logging.addLevelName(21, "MARKET_API")


def market_api(self, message, *args, **kwargs):
    if self.isEnabledFor(21):
        self._log(21, message, args, **kwargs)


logging.addLevelName(22, "POLLER")


def poller(self, message, *args, **kwargs):
    if self.isEnabledFor(22):
        self._log(22, message, args, **kwargs)


logging.addLevelName(23, "DB_LAYER")


def db_layer(self, message, *args, **kwargs):
    if self.isEnabledFor(23):
        self._log(23, message, args, **kwargs)


logging.Logger.market_api = market_api
logging.Logger.poller = poller
logging.Logger.db_layer = db_layer


log = logging.getLogger("api_logger")
log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d.%m.%y %H:%M:%S")

log_file_path = BASE_DIR / f"logs/api_logs.log"
file_handler = logging.handlers.RotatingFileHandler(
    log_file_path,
    mode="a",
    encoding="UTF-8",
    maxBytes=1024 * 1024 * 1024,
)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
