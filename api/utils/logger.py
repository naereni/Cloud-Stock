import logging

from telegram import Bot
from telegram.request import HTTPXRequest

from Cloud_Stock.settings import BASE_DIR
from config.django_config import LOG_FILE, TGLOGGER, TGLOGGERKEY

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


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5
    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


# DEBUG=10, INFO=20, WARNING=30
# addLoggingLevel("MARKET", 30)
# addLoggingLevel("POLLER", logging.INFO + 2)
# addLoggingLevel("DATABASE", logging.INFO + 3)


logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

from datetime import datetime, timedelta
from time import timezone

class UTC3Formatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt + timedelta(hours=3)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%d.%m.%y %H:%M:%S")

formatter = UTC3Formatter("[%(asctime)s] - %(levelname)s - %(message)s", datefmt="%d.%m.%y %H:%M:%S")

log_file_path = BASE_DIR / LOG_FILE
file_handler = logging.handlers.RotatingFileHandler(
    log_file_path,
    mode="a",
    encoding="utf-8",
    maxBytes=1024 * 1024 * 1024,
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
