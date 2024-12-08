from telegram import Bot
from telegram.request import HTTPXRequest

from config.api_config import TGLOGGERKEY

API_TOKEN = TGLOGGERKEY[0]
CHAT_ID = TGLOGGERKEY[1]

trequest = HTTPXRequest(connection_pool_size=100)
bot = Bot(token=API_TOKEN, request=trequest)


async def tglog(message: str):
    await bot.send_message(chat_id=CHAT_ID, text=message)
